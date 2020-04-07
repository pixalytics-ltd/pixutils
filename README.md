# pixutils
Pixalytics python utilities - useful python code

# Install

## Manual install
- download git repository
- pip install .

To upgrade: pip install . --upgrade

## Install using `pip`

This repository can also be installed as a `pip` module

### Using http authentication

This will require the user to enter their username and github password:

- Install from `master` branch: 
```bash
$ python3 -m pip install git+https://github.com/pixalytics-ltd/pixutils.git
```
- Install from a specific branch:
```bash
$ python3 -m pip install git+https://github.com/pixalytics-ltd/pixutils.git@feature/7
```
 
### Using ssh authentication

This will not require the user to enter credentials, providing ssh authentication has been set up for the users
 development system on github.

- Install from `master` branch: 
```bash
$ python3 -m pip install git+ssh://git@github.com/pixalytics-ltd/pixutils.git
``` 

- Install from a specific branch:
```bash
$ python3 -m pip install git+ssh://git@github.com/pixalytics-ltd/pixutils.git@feature/7
```


# Utilities

To use: from pixutils import date_conversion
- year,month,day = date_conversion.ymd(year,jday)
- year,jday = date_conversion.doy(year,month,day)

## ceres_download.py

Contains functions to download NetFlux data from NASA's CERES sensor.

### Usage

Use as a standalone application or as part of a larger program.

#### As a standalone command line application:
```bash
usage: ceres_download.py [-h] date output_dir

Download CERES NetFlux data from the NASA servers. Daily and monthly products
are currently supported.

positional arguments:
  date        Date of data to be obtained (format: YYYY-MM-DD or YYYY-MM)
  output_dir  Destination directory for downloaded data

optional arguments:
  -h, --help  show this help message and exit
```

#### As an import in to Python code
```python
import os
from pixutils import download_ceres_netflux

daily_filename = download_ceres_netflux(output_dir=os.path.expanduser("~"), year=2020, month=1, day=1)
print("Daily NetFlux product was downloaded to '{}'.".format(daily_filename))

monthly_filename = download_ceres_netflux(output_dir=os.path.expanduser("~"), year=2020, month=1)
print("Monthly NetFlux product was downloaded to '{}'.".format(monthly_filename))
```

## era_download.py

Provides a wrapper around the `cdsapi` library for downloading data from Copernicus Climate Data Store.

### Usage

Use as a standalone application or as part of a larger program.

#### As a standalone command line application:

```bash
usage: era_download.py [-h] [-d DATES [DATES ...]] [-t TIMES [TIMES ...]]
                       [-v VARIABLES [VARIABLES ...]]

optional arguments:
  -h, --help            show this help message and exit
  -d DATES [DATES ...], --dates DATES [DATES ...]
                        Date of the data set to be downloaded (format: YYYY-
                        MM-DD)
  -t TIMES [TIMES ...], --times TIMES [TIMES ...]
                        Time of the data set to be downloaded (format: HH:MM)
  -v VARIABLES [VARIABLES ...], --variables VARIABLES [VARIABLES ...]
                        Specify one or more variables to be downloaded.
                        Supported variables: [10m_u_component_of_wind,
                        10m_v_component_of_wind, skin_temperature,
                        soil_temperature_level_1, soil_temperature_level_2,
                        soil_temperature_level_3, soil_temperature_level_4,
                        volumetric_soil_water_layer_1,
                        volumetric_soil_water_layer_2,
                        volumetric_soil_water_layer_3,
                        volumetric_soil_water_layer_4, total_precipitation,
                        2m_temperature]
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

#### As an import in to Python code
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