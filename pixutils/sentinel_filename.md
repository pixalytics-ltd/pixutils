# sentinel_filename.py

Utility function to extract information from Sentinel satellite image files

## Usage

Use as part of a larger program.

### As an import in to Python code

These functions can be reused in multiple projects, as follows:

#### parse_sentinel_filename

Extracts details from a Sentinel filename using the schema defined at:
    https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1-product-formatting
    
```python
from pixutils import sentinel_filename

filename = "S1A_IW_GRDH_1SDV_20200421T063750_20200421T063815_032222_03BA21_8760.dim"

s = sentinel_filename(filename)

#   prints the full filename
print(s.filename)

# prints the start datetime "20200421T063750"
print(s.start_date_time)

# prints the start date "20200421"
print(s.start_date)

# prints the start time "063750"
print(s.start_time)

# prints the orbit number "032222"
print(s.absolute_orbit_number)
```
