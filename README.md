# pixutils
Pixalytics python utilities - useful python code

To install:
- download git repository
- pip install .

To upgrade: pip install . --upgrade

To use: from pixutils import date_conversion
- year,month,day = date_conversion.ymd(year,jday)
- year,jday = date_conversion.doy(year,month,day)

# Utilities

## ceres_download.py

Contains functions to download NetFlux data from NASA's CERES sensor.

### Usage

* As a standalone command line application:
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

* As an import in to Python code
```python
import os
from pixutils import download_ceres_netflux

daily_filename = download_ceres_netflux(output_dir=os.path.expanduser("~"), year=2020, month=1, day=1)
print("Daily NetFlux product was downloaded to '{}'.".format(daily_filename))

monthly_filename = download_ceres_netflux(output_dir=os.path.expanduser("~"), year=2020, month=1)
print("Monthly NetFlux product was downloaded to '{}'.".format(monthly_filename))
```