import cdsapi
from pathlib import Path
from datetime import date, time
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
    "grib": "grib",
    "nc": "netcdf",
}


def download_era5_reanalysis_data(variables: Union[Var, List[Var]],
                                  dates: Union[date, List[date]],
                                  times: Union[time, List[time]],
                                  file_path: str) -> bool:
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

    #   convert each parameter into unique lists
    years = list({_date.year for _date in dates}) if isinstance(dates, List) else [dates.year]
    months = list({_date.month for _date in dates}) if isinstance(dates, List) else [dates.month]
    days = list({_date.day for _date in dates}) if isinstance(dates, List) else [dates.day]
    times = list({time_str(_time) for _time in times}) if isinstance(times, List) else [time_str(times)]
    vars = list({map_var_names[variable] for variable in variables}) if isinstance(variables, List) else [map_var_names[variables]]
    format = ext_to_file_type[extension]

    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': vars,
            'year': years,
            'month': months,
            'day': days,
            'time': times,
            'format': format,
        },
        file_path)

    return True
