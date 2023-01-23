# s2_retrieval.py

Retrieves Sentinel-2A imagery from Copernicus Hub

## Usage

Use as standalone product or as part of another program

### As a standalone command line application:
```bash
usage: s2_retrieval.py [-h] [-v] [-c CLOUD CLOUD] [-a AUTH] [-p PRODUCT]
                       sdate edate zip_folder dl_folder tiles footprint

positional arguments:
  sdate                 Start Date
  edate                 End Date
  zip_folder            Start Date
  dl_folder             Start Date
  tiles                 Filename of tiles csv
  footprint             Filename of footprint geojson

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose
  -c, --cloud           Range of percentage cloud cover allowed
  -a, --auth            Filename containing copernicus login information
  -p, --product         Product type to query for S2MS12[1C][2A][Ap]
```


##### Example
```bash
python s2_retrieval.py 20200617 20200617 /home/user/output/s2_zipped /home/user/output/s2_extracted /home/seadas/sajh/pixinternal/EcoProMIS-local/Ecopromis-inputs/Ecopromis_Farmdata_S2.csv /home/seadas/sajh/pixinternal/EcoProMIS-local/Ecopromis-inputs/Ecopromis_Colombia-bounding-box_EPSG-4326.geojson -c 0 60
```

### As an import into another program:

```bash
# Import
from pixutils.s2_retrieval import *

s2_download(sdate, edate, zip_folder, dl_folder, cloud_cover, authentication_filename, tile_filename, geo_path, product, logger)
```

