#!/usr/bin/env python

import argparse
import sys
import os
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
    Var.temperature_2m: "2m_temperature"
}


#   recognized file extensions should be specified in lower case
ext_to_file_type = {
    ".grib": "grib",
    ".nc": "netcdf",
}


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

    if frequency == 'monthly':
        c.retrieve(
            'reanalysis-era5-land-monthly-means',
            {
                'product_type': 'monthly_averaged_reanalysis',
                'variable': variables,
                'year': years,
                'month': months,
                'time': '00:00',
                'area': [vals[0], vals[1], vals[2], vals[3]],
                'format': file_format,
            },
            file_path)
        
    elif frequency == 'daily':

        prefix = file_path.replace('.nc','')

        # lat and lon should be float
        vals = [float(v) for v in vals]

        def merge(files,topath):
            coords = ['time','lat','lon']
            def open_ds(f):
                with xr.open_dataset(f) as ds:
                    rtn = ds.load()

                os.remove(f)
                return rtn.drop_vars([i for i in list(ds.coords) if not i in coords])
            dses = [open_ds(f) for f in files]
            xr.merge(dses).to_netcdf(topath)

        ymfiles=[]
        
        # TODO JC - don't do all years and months, only within requested timeframe
        for yr in list(set(years)):
            for mn in list(set(months)):

                datestr = str(yr) + str(mn)
                fn_yrmn = prefix + '_{}.nc'.format(datestr)

                if not os.path.isfile(fn_yrmn):
                    varfiles=[]
                    for var in variables:
                        fn_var = prefix + '_{}_{}.nc'.format(var,datestr)
                        
                        if not os.path.isfile(fn_var):

                            result = c.service(
                                "tool.toolbox.orchestrator.workflow",
                                params={
                                    "realm": "user-apps",
                                    "project": "app-c3s-daily-era5-statistics",
                                    "version": "master",
                                    "kwargs": {
                                        "dataset": "reanalysis-era5-single-levels",
                                        "product_type": "reanalysis",
                                        "variable": var,
                                        "statistic": "daily_mean",
                                        "year": str(yr),
                                        "month": str(mn),
                                        "time_zone": "UTC+00:0",
                                        "frequency": "1-hourly",
                                        "area": {"lat": [vals[2], vals[0]], "lon": [vals[1], vals[3]]}
                                    },
                                "workflow_name": "application"
                                })
                            c.download(result)

                            oldfn = result[0]['location'][-39:]
                            os.rename(oldfn, fn_var)
                            varfiles.append(fn_var)
                    
                    # merge all variables into single file
                    merge(varfiles,fn_yrmn)
                    ymfiles.append(fn_yrmn)

        # merge all months and years into single file
        merge(ymfiles,file_path)

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
    else:
        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': variables,
                'year': years,
                'month': months,
                'day': days,
                'time': times,
                'format': file_format,
            },
            file_path)

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

    if len(times) == 0:
        print("Missing 'times' argument.")
        return 1

    # Optional area
    if not args.area:
        args.area = [0, 0, 0, 0]

    try:
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
