# raster_operations.py

Apply operations to raster files.

## Usage

Use as part of a larger program.

### As an import in to Python code

These functions can be reused in multiple projects, as follows:

#### clamp_raster

Clamps the values in the input raster in the specified range. 

```python
from pixutils import clamp_raster, DataFormat, ValueRange 
import os 

#   clamp the file '~/a_geotiff.tif' so all values fall between 0 and 10
clamp_raster(input_file_path=os.path.expanduser("~/a_geotiff.tif"),
             output_file_path=os.path.expanduser("~/a_clamped_geotiff.tif"),
             value_range=ValueRange(min=0, max=10))
```

#### compress_geotiff

Compresses a geotiff using LZW compression.

```python
from pixutils import compress_geotiff
import os 

#   compress the file '~/big_geotiff.tif'
compress_geotiff(input_file_path=os.path.expanduser("~/big_geotiff.tif"),
                 output_file_path=os.path.expanduser("~/compressed_geotiff.tif")) 
```

#### apply_mask

Masks a geotiff, to make out-of-range pixels transparent.

```python
from pixutils import apply_mask
import os 

#   mask the file '~/input_geotiff.tif'
apply_mask(input_file_path=os.path.expanduser("~/input_geotiff.tif"),
           output_file_path=os.path.expanduser("~/masked_geotiff.tif")) 
```
