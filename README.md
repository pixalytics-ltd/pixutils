# pixutils
Pixalytics python utilities - useful python code

# Install

Install manually by cloning the git repository or let `pip` handle resolving the download and install process. 

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

Instructions for each module can be found in their respective readme files:

* **ceres_download.py**: 
 [functions to download NetFlux data from NASA's CERES sensor.](./pixutils/ceres_download.md)
* **date_conversion.py**:
 [converts between *year, month, day* and *year, day_of_year*](./pixutils/date_conversion.md)
* **date_utils.py**:
 [various helper functions for working with dates.](./pixutils/date_utils.md)
* **era_download.py**: 
[provides a wrapper around the `cdsapi` library for downloading data from Copernicus Climate Data Store.](./pixutils/era_download.md)
* **nc_utils.py**:
 []()
* **raster_operations.py**:
 [apply operations to raster files](./pixutils/raster_operations.md)
* **sentinel_filename.py**:
 [utility functions to extract information from Sentinel satellite image files](./pixutils/sentinel_filename.md)