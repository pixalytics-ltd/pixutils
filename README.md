# pixutils
Pixalytics python utilities - useful python code

To install:
- download git repository
- pip install .

To upgrade: pip install . --upgrade

To use: from pixutils import date_conversion
- year,month,day = date_conversion.ymd(year,jday)
- year,jday = date_conversion.doy(year,month,day)
