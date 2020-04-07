#!/usr/bin/env python

import argparse
import sys
import os
import cdsapi
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
                                  file_path: str) -> None:
    """
    Download data from the the Copernicus Climate Data Store
    :param variables: a list of fields to be downloaded on the specified dates and times
    :param dates: a single date or list of dates to be included in the file
    :param times: a single time or list of times to be included in the file
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

    c = cdsapi.Client()
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
    parser.add_argument("-d", "--dates", nargs="+", help="Date of the data set to be downloaded (format: YYYY-MM-DD)")
    parser.add_argument("-t", "--times", nargs="+", help="Time of the data set to be downloaded (format: HH:MM)")
    parser.add_argument("-o", "--out_file", nargs=1, help="Filename for the downloaded data.")

    args = parser.parse_args()
    dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in args.dates]
    times = [datetime.strptime(t, "%H:%M").time() for t in args.times]
    file_path = os.path.expanduser(args.out_file[0]) if args.out_file is not None else []

    if file_path is None:
        print("Missing 'out_file' argument.")
        return 1

    if len(dates) == 0:
        print("Missing 'dates' argument.")
        return 1

    if len(times) == 0:
        print("Missing 'times' argument.")
        return 1

    try:
        download_era5_reanalysis_data(dates=dates, times=times, variables=args.variables, file_path=file_path)

        return 0
    except ValueError as ex:
        print("Program failed due to an invalid parameter.  {}".format(ex))
        return 1
    except RuntimeError as ex:
        print("Program failed due to a run time error.  {}".format(ex))
        return 2

if __name__ == "__main__":
    sys.exit(main())

