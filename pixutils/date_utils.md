# date_utils.py

Various helper functions for working with dates.

## Usage

Use as part of a larger program.

### As an import in to Python code

These functions can be reused in multiple projects, as follows:

#### first_day_of_prev_month

Accepts a date and returns the first day of the previous month

```python
from pixutils import first_day_of_prev_month  
from datetime import datetime

# d1 and d2 will each contain a datetime object representing the 1st March 2020
d1 = first_day_of_prev_month("2020-04-03")
d2 = first_day_of_prev_month(datetime(2020, 4, 3))
```


#### last_day_of_prev_month

Accepts a date and returns the final day of the previous month

```python
from pixutils import last_day_of_prev_month

from datetime import datetime

# d1 and d2 will each contain a datetime object representing the 31st March 2020
d1 = last_day_of_prev_month("2020-04-03")
d2 = last_day_of_prev_month(datetime(2020, 4, 3))
```

#### date_iterator

Yields a list of dates as a daily series between the specified start and end date

```python
from pixutils import date_iterator, first_day_of_prev_month, last_day_of_prev_month 

#   will print a iso-formatted date for each day in March 2020 
for d in date_iterator(first_day_of_prev_month("2020-04-03"), last_day_of_prev_month("2020-04-03")):
  print(d.isoformat())
```
