# era_download.py

Provides a wrapper around the `cdsapi` library for downloading data from Copernicus Climate Data Store.

## Usage

Use as a standalone application or as part of a larger program.

### As a standalone command line application:

```bash
usage: era_download.py [-h] [-d DATES [DATES ...]] [-t TIMES [TIMES ...]]
                       [-o OUT_FILE]
                       variables [variables ...]

positional arguments:
  variables             Specify one or more variables to be downloaded.
                        Supported variables: [10m_u_component_of_wind,
                        10m_v_component_of_wind, skin_temperature,
                        soil_temperature_level_1, soil_temperature_level_2,
                        soil_temperature_level_3, soil_temperature_level_4,
                        volumetric_soil_water_layer_1,
                        volumetric_soil_water_layer_2,
                        volumetric_soil_water_layer_3,
                        volumetric_soil_water_layer_4, total_precipitation,
                        2m_temperature]

optional arguments:
  -h, --help            show this help message and exit
  -d DATES [DATES ...], --dates DATES [DATES ...]
                        Date of the data set to be downloaded (format: YYYY-
                        MM-DD)
  -t TIMES [TIMES ...], --times TIMES [TIMES ...]
                        Time of the data set to be downloaded (format: HH:MM)
  -o OUT_FILE, --out_file OUT_FILE
                        Filename for the downloaded data.
```

* Example:

  Download *10m_v_component_of_wind* and *10m_u_component_of_wind* data sets on 21st and 22nd December 2019 at 9AM
 and 9PM.  
  ```bash
  $ era_download.py 10m_u_component_of_wind 10m_v_component_of_wind --dates 2019-12-21 2019-12-22 --times 09:00 21:00 --out_file "~/wind_speed.grib"
  ```

* Example:

  Download *2m_temperature* data set on 1st January 2020 at 12:00:
  ```bash
  $ era_download.py 2m_temperature --dates 2020-01-01 --times 12:00 --out_file "~/2m_temp.nc"
  ```

### As an import in to Python code
```python
from pixutils import download_era5_reanalysis_data, Var
from datetime import date, time
import os

#   multiple variables can be passed in a list.  Data can be stored in 'grib' files.
download_era5_reanalysis_data(variables=[Var.wind_10m_u_component, Var.wind_10m_v_component],
                              dates=date(2019, 12, 21),
                              times=time(12),
                              file_path=os.path.expanduser("~/Desktop/wind_speed.grib"))

#   multiple dates and times can be passed in a list.  Data can be stored in 'netcdf' files.
download_era5_reanalysis_data(variables=Var.temperature_2m,
                              dates=[date(2019, 12, 21), date(2019, 12, 22)],
                              times=[time(hour=9), time(hour=21)],
                              file_path=os.path.expanduser("~/Desktop/wind_speed.nc"))
```