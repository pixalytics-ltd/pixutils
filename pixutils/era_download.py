#!/usr/bin/env python

import argparse
import sys
import os
import shutil
import glob
import zipfile
import cdsapi
import xarray as xr
from pathlib import Path
from datetime import date, time, datetime
from typing import List, Union
from enum import Enum, unique, auto


#   data sources recognized by the download script.  Further fields can be supported by adding them to the 'Var' enum
#   and the 'map_var_names' dictionary
@unique
class Var(Enum):
    skin_temperature = auto()
    soil_temperature_level_1 = auto()
    soil_temperature_level_2 = auto()
    soil_temperature_level_3 = auto()
    soil_temperature_level_4 = auto()
    volumetric_soil_water_layer_1 = auto()
    volumetric_soil_water_layer_2 = auto()
    volumetric_soil_water_layer_3 = auto()
    volumetric_soil_water_layer_4 = auto()
    total_precipitation = auto()
    wind_10m_u_component = auto()
    wind_10m_v_component = auto()
    temperature_2m = auto()
    depoint_2m = auto()
    longwave_down = auto()
    shortwave_down = auto()
    longwave_net = auto()
    shortwave_net = auto()

#   map a data source to the string used in the remote API call
map_var_names = {
    Var.wind_10m_u_component: "10m_u_component_of_wind",
    Var.wind_10m_v_component: "10m_v_component_of_wind",
    Var.skin_temperature: "skin_temperature",
    Var.soil_temperature_level_1: "soil_temperature_level_1",
    Var.soil_temperature_level_2: "soil_temperature_level_2",
    Var.soil_temperature_level_3: "soil_temperature_level_3",
    Var.soil_temperature_level_4: "soil_temperature_level_4",
    Var.volumetric_soil_water_layer_1: "volumetric_soil_water_layer_1",
    Var.volumetric_soil_water_layer_2: "volumetric_soil_water_layer_2",
    Var.volumetric_soil_water_layer_3: "volumetric_soil_water_layer_3",
    Var.volumetric_soil_water_layer_4: "volumetric_soil_water_layer_4",
    Var.total_precipitation: "total_precipitation",
    Var.temperature_2m: "2m_temperature",
    Var.depoint_2m: "2m_dewpoint_temperature",
    Var.longwave_down: "mean_surface_downward_long_wave_radiation_flux",
    Var.shortwave_down: "mean_surface_downward_short_wave_radiation_flux",
    Var.longwave_net: "mean_surface_net_long_wave_radiation_flux",
    Var.shortwave_net: "mean_surface_net_short_wave_radiation_flux"
}


#   recognized file extensions should be specified in lower case
ext_to_file_type = {
    ".grib": "grib",
    ".nc": "netcdf",
}

# Merge NetCDF files
def merge(files, topath, latitude = False, day_merge = False, time_merge = False, file_merge = False, month_merge = False):

    if latitude:
        coords = ['valid_time', 'latitude', 'longitude']
    else:
        coords = ['time', 'lat', 'lon']

    if time_merge:
        for i,file in enumerate(files):
            if i == 0:
                marray = xr.open_dataset(file)
            else:
                ds_add = xr.open_dataset(file)
                ds_new = xr.concat([marray, ds_add], coords[0])
                marray = ds_new.copy()
                del ds_new, ds_add

    else:
        def open_ds(f):
            with xr.open_dataset(f) as ds:
                rtn = ds.load()

            return rtn.drop_vars([i for i in list(ds.coords) if not i in coords])

        dses = [open_ds(f) for f in files]
        if file_merge:
            marray = xr.merge(dses)
        elif month_merge:
            marray = xr.combine_nested(dses, concat_dim=[coords[0]])
        else:
            marray = xr.concat(dses, coords[0])
        if latitude:
            marray = marray.rename(name_dict={'valid_time':'time'})
        if day_merge:
            # Convert to daily values (input hourly)
            marray = marray.resample(time="1D").max()

    marray.to_netcdf(topath)


def download_utci_data(dates: Union[date, List[date]],
                                  area: str,
                                  file_path: str) -> None:
    """
    Download data from the the Copernicus Climate Data Store for UTCI
    :param dates: a single date or list of dates to be included in the file
    :param area: an area of interest to be included in the file
    :param file_path: a path to the output file containing all of the downloaded data
    :return: a Boolean value; true, if the download completed successfully
    """
    path = Path(file_path)

    #   make sure the output directory exists
    Path(path.parent).mkdir(parents=True, exist_ok=True)

    #   determine output format from the output file extension
    extension = path.suffix.lower()
    if extension not in ext_to_file_type:
        raise ValueError("Unable to determine file type from extension '{}'.".format(extension))

    # convert each parameter into unique lists
    years = list({_date.year for _date in dates}) if isinstance(dates, List) else [dates.year]
    months = list({'{:02}'.format(_date.month) for _date in dates}) if isinstance(dates, List) else [dates.month]
    days = list({'{:02}'.format(_date.day) for _date in dates}) if isinstance(dates, List) else [dates.day]

    # Extract AOI box values
    vals = area.replace('[','').replace(']','').split(',')
    area_box = False
    for val in vals:
        if float(val) != 0:
            area_box = True

    # Run C3S API
    c = cdsapi.Client()

    # Download year by year
    mfiles = []
    yfolder,ext = os.path.splitext(file_path)
    if not os.path.exists(yfolder):
        os.mkdir(yfolder)
    for year in years:
        request = {
                "variable": ["universal_thermal_climate_index","mean_radiant_temperature"],
                "version": "1_1",
                "product_type": "consolidated_dataset",
                "year": [str(year)],
                "month": sorted(months),
                "day": sorted(days),
                "area": [vals[0], vals[1], vals[2], vals[3]]
            }
        print("Requesting: {}".format(request))
        fpath = os.path.join(yfolder,str(year)+ext)
        print("Aborting as API request has issues")
        return
        try:
            c.retrieve('derived-utci-historical',
                request, fpath)
        except:
            os.rmdir(yfolder)
            print("Request to CDS for UTCI failed")
            return
        if os.path.exists(fpath):
            print("Downloaded: {}".format(fpath))
            # Check if zip file rather than NetCDF
            if zipfile.is_zipfile(fpath):
                # Try to extract zip and merge if more than one file
                stem, ext = os.path.splitext(os.path.basename(fpath))
                zfolder = fpath.replace(ext,"")
                if not os.path.exists(zfolder):
                    os.mkdir(zfolder)
                with zipfile.ZipFile(fpath, "r") as zip_ref:
                    zip_ref.extractall(zfolder)
                ymfiles = glob.glob(os.path.join(zfolder,"*"+ext))
                print("Merging {} {} files".format(len(ymfiles),ext))
                os.remove(fpath)
                merge(ymfiles, fpath, day_merge = True)
                shutil.rmtree(zfolder)
            mfiles.append(fpath)
    print("Processed data: {}".format(mfiles))
    if len(mfiles) > 1:
        merge(mfiles, file_path, time_merge = True)
    elif len(mfiles) == 1:
        os.rename(mfiles[0],file_path)

    if not os.path.isfile(file_path):
        raise RuntimeError("Unable to locate output file '{}'.".format(file_path))

    print("Downloaded data was saved to '{}'.".format(file_path))


def download_era5_reanalysis_data(variables: Union[Var, List[Var], List[str]],
                                  dates: Union[date, List[date]],
                                  times: Union[time, List[time]],
                                  area: str,
                                  frequency: str,
                                  file_path: str) -> None:
    """
    Download data from the the Copernicus Climate Data Store
    :param variables: a list of fields to be downloaded on the specified dates and times
    :param dates: a single date or list of dates to be included in the file
    :param times: a single time or list of times to be included in the file
    :param area: an area of interest to be included in the file
    :param frequency: 'monthly','daily' or 'hourly'
    :param file_path: a path to the output file containing all of the downloaded data
    :return: a Boolean value; true, if the download completed successfully
    """
    path = Path(file_path)

    #   make sure the output directory exists
    Path(path.parent).mkdir(parents=True, exist_ok=True)

    #   determine output format from the output file extension
    extension = path.suffix.lower()
    if extension not in ext_to_file_type:
        raise ValueError("Unable to determine file type from extension '{}'.".format(extension))

    def time_str(t: time) -> str:
        return t.strftime("%H:%M")

    def parse_variables() -> List[str]:
        if isinstance(variables, List):
            result = set()
            for variable in variables:
                if isinstance(variable, Var):
                    #   if item is an Enum (preferred) lookup the string representation
                    result.add(map_var_names[variable])
                elif isinstance(variable, str):
                    #   if item is a string (generally passed from command line) check the variable name is valid
                    #   and add to list
                    if variable in map_var_names.values():
                        result.add(variable)
                    else:
                        print("'{}' is not a valid variable identifier.".format(variable))
            return list(result)
        elif isinstance(variables, str):
            return map_var_names[variables]

    #   convert each parameter into unique lists
    years = list({_date.year for _date in dates}) if isinstance(dates, List) else [dates.year]
    months = list({_date.month for _date in dates}) if isinstance(dates, List) else [dates.month]
    days = list({_date.day for _date in dates}) if isinstance(dates, List) else [dates.day]
    times = list({time_str(_time) for _time in times}) if isinstance(times, List) else [time_str(times)]
    variables = parse_variables()
    file_format = ext_to_file_type[extension]

    # Extract AOI box values
    vals = area.replace('[','').replace(']','').split(',')
    area_box = False
    for val in vals:
        if float(val) != 0:
            area_box = True

    # Run C3S API
    c = cdsapi.Client()

    if frequency != 'monthly':
        # for UTCI restrict daily & hourly to summer months
        utci = False
        if any("dewpoint" in var for var in variables):
            utci = True
            #months = ["5", "6", "7", "8", "9"]

    if frequency == 'monthly' or frequency == 'wmonthly':
        request = {
                'product_type': 'monthly_averaged_reanalysis',
                'variable': variables,
                'year': years,
                'month': months,
                'time': ['00:00'],
                'data_format': file_format,
                'download_format': 'unarchived',
                'area': [vals[0], vals[1], vals[2], vals[3]]
            }
        if not os.path.exists(file_path):
            if any("radiation" in var for var in variables) or frequency == 'wmonthly':
                print("Requesting ERA5: {}".format(request))
                c.retrieve('reanalysis-era5-single-levels-monthly-means',
                    request, file_path)
            else:
                print("Requesting ERA5-Land: {}".format(request))
                c.retrieve('reanalysis-era5-land-monthly-means',
                    request, file_path)

    elif frequency == 'daily' or frequency == 'hourly':
        # prefix for downloading parts
        prefix = file_path.replace('.nc', '')
        if os.path.exists(file_path):
            print("{} already downloaded".format(file_path))
        else:
            # lat and lon should be float
            vals = [float(v) for v in vals]
            yfiles=[]

            # for UTCI restrict to summer months
            utci = False
            if any("dewpoint" in var for var in variables):
                utci = True
                #months = ["5","6","7","8","9"]

            # Loop for all requested years and months
            for yr in list(set(years)):
                for mn in list(set(months)):

                    datestr = str(yr) + str(mn)

                    # Adjust to be more flexible in search
                    fn_yrmn = prefix + '_{}.nc'.format(datestr)

                    dirname, fname = os.path.split(fn_yrmn)
                    splits = fname.split("-")
                    searchstr = os.path.join(dirname, splits[0][:-8] + "*" + splits[1][8:] + "-" + splits[2] + "-" + splits[3])
                    files = glob.glob(searchstr)
                    if not os.path.isfile(fn_yrmn):
                        if len(files) > 0:
                            fn_yrmn = files[0]
                        else:
                            if frequency == 'daily':
                                request = {
                                    'product_type': 'reanalysis',
                                    'variable': variables,
                                    'daily_statistic': 'daily_mean',
                                    'year': str(yr),
                                    'month': str(mn),
                                    'day': sorted(days),
                                    'time_zone': "utc+00:00",
                                    'frequency': "1_hourly",
                                    'area': [vals[0], vals[1], vals[2], vals[3]]}
                                print("Requesting: {}".format(request))
                                c.retrieve('derived-era5-single-levels-daily-statistics', request ,fn_yrmn)
                            else: # hourly

                                request =  {
                                    'product_type': 'reanalysis',
                                    'variable': variables,
                                    'year': str(yr),
                                    'month': str(mn),
                                    'day': days,
                                    'time': times,
                                    'format': file_format,
                                    'area': [vals[0], vals[1], vals[2], vals[3]]}
                                print("Requesting: {}".format(request))
                                c.retrieve(                                'reanalysis-era5-single-levels', request, fn_yrmn)

                            # Check if zip file rather than NetCDF
                            if zipfile.is_zipfile(fn_yrmn):
                                # Try to extract zip and merge if more than one file
                                stem, ext = os.path.splitext(os.path.basename(fn_yrmn))
                                zfolder = file_path.replace(ext, "")
                                if not os.path.exists(zfolder):
                                    os.mkdir(zfolder)
                                with zipfile.ZipFile(fn_yrmn, "r") as zip_ref:
                                    zip_ref.extractall(zfolder)
                                ymfiles = glob.glob(os.path.join(zfolder, "*" + ext))
                                print("Extraction of {} and merging {} {} files: {}".format(zfolder, len(ymfiles), ext,ymfiles))
                                os.remove(fn_yrmn)

                                # merge according to time
                                merge(ymfiles, fn_yrmn, latitude=True, file_merge=True)
                                del ymfiles
                                shutil.rmtree(zfolder)

                    # add each date to the merge list
                    if os.path.exists(fn_yrmn):
                        yfiles.append(fn_yrmn)

            # merge all months and years into single file
            if utci:
                ds = xr.open_dataset(fn_yrmn)
                lat = ds.latitude.values
                lon = ds.longitude.values
                del ds
                merge(yfiles,file_path,month_merge=True)
                ds = xr.open_dataset(file_path)
                ds['latitude'] = lat
                ds.latitude.attrs["units"] = 'degrees_north'
                ds['longitude'] = lon
                ds.longitude.attrs["units"] = 'degrees_east'
                ds.d2m.attrs["units"] = 'K'
                ds.t2m.attrs["units"] = 'K'
                ds.u10.attrs["units"] = 'm s**-1'
                ds.v10.attrs["units"] = 'm s**-1'
                ds.msdwlwrf.attrs["units"] = 'W m**-2'
                ds.msdwswrf.attrs["units"] = 'W m**-2'
                ds.msnlwrf.attrs["units"] = 'W m**-2'
                ds.msnswrf.attrs["units"] = 'W m**-2'
                os.remove(file_path)
                ds.to_netcdf(file_path)
                del ds
            else:
                merge(yfiles, file_path, latitude=True, month_merge=True)

    elif area_box:
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': variables,
                'year': years,
                'month': months,
                'day': days,
                'time': times,
                'area': [vals[0], vals[1], vals[2], vals[3]],
                'format': file_format,
            },
            file_path)

    # Check if zip file rather than NetCDF
    if zipfile.is_zipfile(file_path):
        # Try to extract zip and merge if more than one file
        stem, ext = os.path.splitext(os.path.basename(file_path))
        zfolder = file_path.replace(ext,"")
        if not os.path.exists(zfolder):
            os.mkdir(zfolder)
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(zfolder)
        ymfiles = glob.glob(os.path.join(zfolder,"*"+ext))
        print("Extraction of {} and merging {} {} files: {}".format(zfolder,len(ymfiles),ext,ymfiles))
        os.remove(file_path)
        if "multi" in zfolder:
            # merge according to time
            merge(ymfiles, file_path, latitude=True, file_merge=True)
        else:
            merge(ymfiles, file_path, latitude=True)
        shutil.rmtree(zfolder)
    else:
        marray = xr.open_dataset(file_path)
        marray = marray.rename(name_dict={'valid_time': 'time'})
        os.remove(file_path)
        marray.to_netcdf(file_path)

    if not os.path.isfile(file_path):
        raise RuntimeError("Unable to locate output file '{}'.".format(file_path))

    print("Downloaded data was saved to '{}'.".format(file_path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("variables", nargs="+", help="Specify one or more variables to be downloaded."
                                                     "  Supported variables: [{}]"
                        .format(", ".join(map_var_names.values())))
    parser.add_argument("-a", "--area", nargs="+", help="Area to be downloaded (format: [x, x, x, x])")
    parser.add_argument("-d", "--dates", nargs="+", help="Date of the data set to be downloaded (format: YYYY-MM-DD)")
    parser.add_argument("-t", "--times", nargs="+", help="Time of the data set to be downloaded (format: HH:MM)")
    parser.add_argument("-u", "--utci", action="store_true", default=False, help="Download UTCI rather than ERA5")
    parser.add_argument("-f", "--frequency", dest="frequency", default='monthly', help="Define frequency of accessed ECMWF data")
    parser.add_argument("-o", "--out_file", nargs=1, help="Filename for the downloaded data.")

    args = parser.parse_args()
    #print("Args: {}".format(args))

    dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in args.dates] if args.dates is not None else []
    times = [datetime.strptime(t, "%H:%M").time() for t in args.times] if args.times is not None else []
    file_path = os.path.expanduser(args.out_file[0]) if args.out_file is not None else None

    if file_path is None:
        print("Missing 'out_file' argument.")
        return 1

    if len(dates) == 0:
        print("Missing 'dates' argument.")
        return 1

    if not args.utci and len(times) == 0:
        print("Missing 'times' argument.")
        return 1

    # Optional area
    if not args.area:
        args.area = [0, 0, 0, 0]

    try:
        if args.utci:
            download_utci_data(dates=dates, area=args.area, file_path=file_path)
            print("Downloaded UTCI complete")

        else:
            download_era5_reanalysis_data(dates=dates, times=times, variables=args.variables, area=args.area, frequency=args.frequency, file_path=file_path)

        return 0
    except ValueError as ex:
        print("Program failed due to an invalid parameter.  {}".format(ex))
        return 1
    except RuntimeError as ex:
        print("Program failed due to a run time error.  {}".format(ex))
        return 2


if __name__ == "__main__":
    sys.exit(main())
