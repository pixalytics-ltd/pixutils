# -*- coding: utf-8 -*-
# Originally DFMS-local Land Surface Temperature and Soil Moisture product utilities

# REVISION HISTORY
# Created on 15 July 2018 
# @author: slavender
#
#
# This code is designed to house a multitude of the functions required for
# processing to function correctly. Tis code is intended to be imported and
# as such can't be run from the command line
#
###############################################################################
#
#                             USAGE
#           Called as functions where needed from other programs
#
###############################################################################
import argparse
import os
import sys
import shutil
import numpy as np
import pylab as plt
import subprocess
import pandas as pd
import logging
import datetime
from osgeo import ogr
from os.path import expanduser
import faulthandler

home = expanduser("~")
faulthandler.enable()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("eo_utilities")
################################################################################

def func_name():
    """
    Returns the name of the most recent function on the stack
    :return: the function name
    :rtype: str
    """
    import sys
    return sys._getframe(1).f_code.co_name


def syscmd(cmd, verb):
    """
    Enables commands to be run from inside the python code with appropriate outputs and error returns when necessary
    
    :param cmd: command to be run
    :type cmd: str
    :param verb: enable more verbose outputs
    :type verb: bool
    """
    args = argparse.Namespace()
    args.verbose = verb
    if verb:
        logger.info("Cmd: {}".format(cmd))
        cmd = cmd.split()
        proc = subprocess.Popen(cmd)  # ,stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
    else:
        cmd = cmd.split()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    out, errors = proc.communicate()
    if out != "" and out is not None:
        logger.info("Cmd Output: {}".format(out))

    if proc.returncode != 0:
        logger.error("Crash encountered when running {}".format(cmd))
        logger.error("Cmd Output: {}".format(out))
        logger.error("Cmd Errors: {}".format(errors))
        sys.exit()


def execmd(cmd, verb):
    """
    Enables commands to be run from inside the python code with the output returned

    :param cmd: command to be run
    :type cmd: str
    :param verb: enable more verbose outputs
    :type verb: bool
    """

    # Replaced due to shell=True being a security hazard
    args = argparse.Namespace()
    args.verbose = verb
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)
    output = p.stdout.read()
    p.stdin.close()
    p.stdout.close()
    # p.communicate()
    if output:
        return output
    else:
        logger.warning("No output returned")
        return None

def daterange(sdate, edate, rtv):
    """
    Generates a list of date strings between two given dates using pandas.  The list is then iterated over and
    reformatted to obtain the list of dates for usage in other programs

    :param sdate: start date string formatted as YYYYMMDD
    :type sdate: str
    :param edate: end date string formatted as YYYYMMDD
    :type edate: str
    :param rtv: integer flag to specify if a conversion to julian day of year is required;
     with value = 1 to generate it (TBC) otherwise default is 0
    :type rtv: int
    :return: list of dates in the specified range
    """

    rng = pd.date_range(start=sdate, end=edate)
    dates = []
    # This first for loop takes the pandas date range and slices the date section
    # into an integer string format i.e 20160101
    for i in range(len(rng)):
        t = str(rng[i])
        if rtv == 0:
            y = t[0:4] + t[5:7] + t[8:10]
        elif rtv == 1:
            fmt = "%Y-%m-%d %H:%M:%S"
            dt = datetime.datetime.strptime(t, fmt)
            tt = dt.timetuple()
            if int(tt[7]) < 100:
                y = t[0:4] + "0" + str(tt[7])
            else:
                y = t[0:4] + str(tt[7])
        dates.append(y)
    return dates

def show_img(array, transpose, reverse=0):
    """Plots an array of choice with the option to transpose the array if need be
  
  Inputs
  array - numpy array to be plotted
  transpose - True/False integer to flip the array 
  reverse - True/False integer to invert colours (TBC)?"""
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    ax.set_axis_off()
    if transpose == 1:
        data = np.transpose(array, (1, 0))  # Transpose
    elif transpose == 2:
        data = np.flipud(array)  # Verically flip
    else:
        data = array
    # Reverse colourmap
    if reverse:
        ax.imshow(data, cmap='Blues_r', origin='lower')
    else:
        ax.imshow(data, cmap='Blues', origin='lower')
    plt.savefig("test.png")
    plt.show()


def path_to_gdal_translate() -> str:
    """
    Checks that 'gdal_translate' can be found on the system path
    :return: a string representing the absolute path to 'gdal_translate'
    """
    gdal_translate_bin = shutil.which("gdal_translate")
    return gdal_translate_bin


def convert_to_geotiff(netcdf_file: str, geotiff_file: str) -> bool:
    """
    Uses the 'gdal_translate' executable to convert a netcdf file to geotiff
    :param netcdf_file: a path to an existing netcdf file
    :param geotiff_file: a pth to the output file
    :return: True if the process succeeds and the file is created, otherwise False
    """
    args = argparse.Namespace()
    args.verbose = False
    assert os.path.exists(netcdf_file), "Input file '{:} does not exist.".format(netcdf_file)
    gdal_translate_bin = path_to_gdal_translate()
    assert gdal_translate_bin != "", "Unable to locate 'gdal_translate'"

    cmd = gdal_translate_bin + ' -a_srs EPSG:4326 -sds ' + netcdf_file + ' ' + geotiff_file
    proc = subprocess.run(cmd, shell=True)

    #   todo: checking if output files exist will fail as duplicate files will automatically be suffixed with '_1' etc
    if proc.returncode == 0:  # and os.path.exists(geotiff_file):
        logger.debug("Wrote geotiff file '{:}'".format(geotiff_file))
        return True
    else:
        logger.warning("Failed to write geotiff file '{:}'".format(geotiff_file))
        return False


def create_wkt_points(swlat, swlon, nelat, nelon, args):
    """
    Creates a WKT string based on bounding box co-ordinates

    :param swlat: bounding box co-ordinates (southwest-latitude)
    :param swlon: bounding box co-ordinates (southwest-longitude)
    :param nelat: bounding box co-ordinates (northeast-latitude)
    :param nelon: bounding box co-ordinates (northeast-longitude)
    :param args: command line arguments
    :return: WKT formatted string of the bounding box
    """

    # Create ring
    logger.info("Creating WKT from {} {} {} {}".format(swlat, swlon, nelat, nelon))
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(swlon, swlat)
    ring.AddPoint(swlon, nelat)
    ring.AddPoint(nelon, nelat)
    ring.AddPoint(nelon, swlat)
    ring.AddPoint(swlon, swlat)
    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    wkt = poly.ExportToWkt()
    return wkt

