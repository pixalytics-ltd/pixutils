converts between *year, month, day* and *year, day_of_year*  

To use:

```
from pixutils import date_conversion
- year,month,day = date_conversion.ymd(year,jday)
- year,jday = date_conversion.doy(year,month,day)
```