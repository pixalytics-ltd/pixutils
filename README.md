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

positional arguments:
  date        Date of data to be obtained (format: YYYY-MM-DD)
  output_dir  Destination directory for downloaded data

optional arguments:
  -h, --help  show this help message and exit
```

* As an import in to Python code
```python
import os
from datetime import datetime
from pixutils import download_ceres_netflux

filename = download_ceres_netflux(date=datetime(2020, 1, 1).date(), output_dir=os.path.expanduser("~"))
print("File was downloaded to '{}'.".format(filename))
```