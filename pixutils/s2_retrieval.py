#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 16:10:58 2019

@author: cdoyle
"""

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 13:54:54 2018

@author: ubuntu
"""
# This code enables the downloading of Sentinel-2 data which covers specific tiles
# in a given date range and only downloads morning data. This is achieved with
# the sentinel sat library located at https://pypi.org/project/sentinelsat/
#
# An external shapefile which represents the search area in a rectangular polygon
# is required for this program to work alongside a password file s2dl.txt, both are stored
# in the ecopomris_inputs, the former file acts as a search geojson and the latter
# acts as a password storage file
#
##############################################################################
#
#                                     USAGE
#
# python3 ./s2_retrieval.py sdate edate zipfoler dlfolder tiles footprint [-v] [-c]
#
# sdate - Start date string formatted as YYYYMMDD
# edate - End date string formatted as YYYYMMDD
# zipfolder - Folder where Sentinel-2 files stored as zip files are downloaded to
# dlfolder - Folder path where extracted Sentinel-2 files are stored by folder
# tiles - Filename of tiles csv
# geo_path - Filename of footprint geojson
# -v (Verbose) - Enables a more verbose output
# -c (Cloud Cover) - Sets cloud cover range for query
##############################################################################

# Import section
import argparse  # Use this over optparse as the latter is depreceated
import os
import sys
import shutil
import traceback
import glob
import zipfile
import datetime
import logging
import pandas as pd # todo - fix import
import sentinelsat as sla
# DFMS libraries
# import ls8_lst_ndvi_convert as llc
# from dfms_sharedutils import config_logger
from dfms_sharedutils import eo_utilities as eou

# logger = config_logger.configure_logging(__name__)
logger = logging.getLogger(__name__)


def get_tiles(tile_filename):
    try:
        s2_tiles = pd.read_csv(tile_filename)
        tiles_src = s2_tiles['Scenes'].values.tolist()
        print(tiles_src)
        tiles = list(set([a.split("A")[1] for a in tiles_src]))
    except Exception as e:
        print("Error: unable to read tiles csv. {}".format(e))

    return tiles


def get_time_epochs():
    stime_epoch = datetime.datetime(1900, 1, 1, 6, 30, 0)
    etime_epoch = datetime.datetime(1900, 1, 1, 19, 30, 0)
    return stime_epoch.time(), etime_epoch.time()


# Core downloading function where all downloading is intialised from
def s2_download(sdate, edate, zip_folder, dl_folder, cloud_cover, authentication_filename, tile_filename, geo_path, product, logger):
    logger.info("tile_filename: {}".format(tile_filename))

    if not os.path.exists(zip_folder):
        os.mkdir(zip_folder)

    logger.info("Sentinel-2 dowloading code initialised")
    # Download Sentinel-2 using sentinelsat
    # https://pypi.org/project/sentinelsat/

    # Here the allowed orbits are set up and also a time delta of 24 hours is added
    # to the end date to allow for succesful requests to the server api, this
    # is also set up alongside variables for program use
    logger.info("Setting up variables")
    tiles = get_tiles(tile_filename)
    edate_dt = datetime.datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]))
    edate_dt = edate_dt + datetime.timedelta(hours=24)
    if edate_dt.month < 10:
        edate_month = "0" + str(edate_dt.month)
    else:
        edate_month = str(edate_dt.month)
    if edate_dt.day < 10:
        edate_day = "0" + str(edate_dt.day)
    else:
        edate_day = str(edate_dt.day)
    edate = "{}{}{}".format(str(edate_dt.year), edate_month, edate_day)

    fs2files = []
    ids = []    # list of ids of sentinel-2 files

    # Time epochs for searches
    stime_epoch, etime_epoch = get_time_epochs()

    logger.info("Parameters set up")

    # Here login details are parsed
    logger.info("Reading in login details")

    with open(authentication_filename, 'r') as f1:
        first_line = f1.readline().rstrip("\n")
    credentials = first_line.split(",")
    logger.info("Login details retrieved")

    # Connection attempt is made to the Copernicus open access hub and will exit if fails
    try:
        api = sla.SentinelAPI(credentials[0], credentials[1], 'https://scihub.copernicus.eu/dhus')
    except Exception as e:
        logger.error("Can't login to Copernicus open access hub. {}".format(e))
        traceback.print_exc()
        sys.exit()

    # Here a footprint is set up to pass along to the search query
    footprint = sla.geojson_to_wkt(sla.read_geojson(geo_path))

    # Here the search query is started and a large dictionary is returned
    products = api.query(footprint,
                         date=(sdate, edate),
                         platformname='Sentinel-2',
                         producttype=product,
                         cloudcoverpercentage=(float(cloud_cover[0]), float(cloud_cover[1]))
                         )

    logger.info("Query complete. {} products found".format(len(products)))

    # Information on the query is returned here
    if len(products) == 0:
        logger.error("Didn't find any files")
        return

    # Here the files returned are filtered out by metadata filtering via morning
    # overpass time windows and also by relative orbit number to ensure desired
    # data coverage
    logger.info("Starting metadata filtering loops")
    already_downloaded = 0
    s2files = []
    safe_dirs = []
    for key in products:
        try:
            info = api.get_product_odata(key)
        except Exception as e:
            logger.warning("key {} failed,skipping to next key. {}".format(key, e))
            traceback.print_exc()
            continue

        # Here the core information is recieved about the file and then it is
        # used in filtering the file based on the orbit number and also the
        # overpass time if it falls within the morning overpass window
        filestem = info['title']
        f_sdate = filestem.split("_")[2].split("T")[0]
        f_stime = filestem.split("_")[2].split("T")[1]
        dt_1 = datetime.datetime(int(f_sdate[0:4]), int(f_sdate[4:6]), int(f_sdate[6:8]), int(f_stime[0:2]),
                                 int(f_stime[2:4]), int(f_stime[4:6]))
        tile_number = filestem.split("_")[5]

        # Here files which pass the orbit number and date time overpass check
        # are appended to a list and used in the downloading iteration
        # only if they don't exist in the zip or final folders
        aclogfile = os.path.join(dl_folder, filestem + "-acfail.txt")
        safefile = os.path.join(dl_folder, filestem + ".SAFE")
        if tile_number in tiles and dt_1.time() >= stime_epoch:  # and dt_2.time() <= etime_epoch:
            check = glob.glob(os.path.join(zip_folder, filestem))
            if len(check) == 0: #and not os.path.exists(safefile) and not os.path.exists(aclogfile):
                ids.append(key)
                fs2files.append(info['title'])
            else:
                s2files.append(os.path.join(dl_folder, filestem + ".SAFE"))
                already_downloaded = 1

    logger.info("Metadata filtering complete")

    # Information is set up to detail what files are being downloaded
    logger.info("Number of files to download is {}".format(len(ids)))
    if len(ids) == 0:
        if already_downloaded == 0:
            logger.warning("No files were found which covered the tiles of interest")
            return
        else:
            logger.info("Files already downloaded")
            return s2files

    # Download all results from the search and place into the zip folder
    logger.info("Starting data download retrieval")
    count = (-1)

    # Downloading is iterated over after it has been filtered through
    for id in ids:
        count += 1
        try:
            api.download(id, directory_path=zip_folder)
        except Exception as e:
            logger.warning("Download failed for {}. {}".format(fs2files[count], e))
            traceback.print_exc()

    logger.info("All available data downloaded")

    # The netcdf files and folders are extracted into the final folder
    logger.info("Starting extraction of data")
    if sdate == edate:
        zip_files = glob.glob(os.path.join(zip_folder, "*" + sdate + "*.zip"))
    else:
        dates_s2 = eou.daterange(sdate, edate, 0)   # todo - find dfms shared utils folder
        zip_files = []
        for dates in dates_s2:
            zips = glob.glob(os.path.join(zip_folder, "*" + dates + "*.zip"))
            if len(zips) > 0:
                for zip in zips:
                    zip_files.append(zip)

    for a in zip_files:
        with zipfile.ZipFile(a, "r") as zip_ref:
            zip_ref.extractall(dl_folder)
    logger.info("Data extracted from zip files")

    # Here the final cleanup is done
    logger.info("Sentinel-2 data download program completed for duration of {} to {}".format(sdate, edate))
    # If downloaded at least 1 file return downloaded list
    if count > (-1):
        return s2files
    else:
        return


##################################################

# This main function is intended to contain the command line initialisers
# derived from argparse and any other needed input parameters
def main():
    head_tail = os.path.split(__file__)
    parser = argparse.ArgumentParser()
    parser.add_argument("sdate", help="Start Date")
    parser.add_argument("edate", help="End Date")
    parser.add_argument("zip_folder", help="Start Date")
    parser.add_argument("dl_folder", help="Start Date")
    parser.add_argument("tiles", help="Filename of tiles csv")
    parser.add_argument("geo_path", help="Filename of footprint geojson")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False)
    parser.add_argument("-c", "--cloud", dest="cloud", nargs=2, default=['0', '100'],
                        help="Range of percentage cloud cover allowed")
    parser.add_argument("-a", dest="auth", default=(os.path.join(head_tail[0], "s2dl.txt")),
                        help="Filename containing copernicus login information")
    parser.add_argument("-p", "--product", dest="product", default="1C", help="product type: S2MSI[1C][2A][Ap]")
    args = parser.parse_args()

    # Code initalisation goes here alongside error catching

    if args.product == "1C" or args.product == "2A" or args.product == "Ap":
        product = "S2MSI" + args.product
    else:
        raise Exception("Invalid product type.")

    try:
        s2_download(args.sdate, args.edate, args.zip_folder, args.dl_folder, args.cloud, args.auth, args.tiles,
                    args.geo_path, product, logger)
    except Exception as e:
        logger.error("Crash occurred running s2_retrieval.py: {}".format(e))
        traceback.print_exc()
        sys.exit()


if __name__ == "__main__":
    main()
