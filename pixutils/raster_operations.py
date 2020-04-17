import os
from pathlib import Path
from collections import namedtuple
from rsgislib.imagecalc import BandDefn
from rsgislib import imageutils
from rsgislib import imagecalc
from rsgislib.imageutils import maskImage, genValidMask
from rsgislib import TYPE_32FLOAT
import gdal


ValueRange = namedtuple("ValueRange", ["min", "max"])
ValueRange.__doc__ = """
Holds minimum and maximum values
:param min: the minimum value in the range
:param max: the maximum value in the range
"""

DataFormat = namedtuple("DataFormat", ["format", "type"])
DataFormat.__doc__ = """
Used to specify data format for calls to rsgislib functions
:param format: a string representing the file format i.e. "GTIFF"
:param type: the data type used to store the data i.e. rsgislib.TYPE_32FLOAT
"""

DEFAULT_DATA_FORMAT = DataFormat(format="GTIFF", type=TYPE_32FLOAT)


def clamp_raster(input_file_path: str,
                 output_file_path: str,
                 value_range: ValueRange,
                 data_format: DataFormat = DEFAULT_DATA_FORMAT) -> None:
    """
    Clamps the values in the input raster in the specified range.  Values that are below the minimum are set to
    value_range.min, values above the maximum are set to value_range.max.  All other values are left unchanged.
    :param input_file_path: path to the file that will be clamped
    :param output_file_path: path to the output file containing the clamped output
    :param value_range: used to specify the desired minimum and maximum
    :param data_format: can be used to override the default output file format (default: 32bit float geo-tiff)
    :return: nothing
    """
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError("Unable to find input file: '{}'.".format(input_file_path))
    if not value_range.min <= value_range.max:
        raise ValueError("Minimum value must be less than or equal to maximum.")

    #   assign values in the input file the internal identifier 'x'
    band_definitions = [BandDefn('x', input_file_path, 1)]

    #   clamp values between min and max
    norm_expr = '(x>={min} ? (x<={max} ? x : {max}) : {min})'.format(min=value_range.min, max=value_range.max)

    #   perform the normalisation
    imagecalc.bandMath(output_file_path, norm_expr, data_format.format, data_format.type, band_definitions)
    imageutils.popImageStats(output_file_path, False, 0, True)

    if not os.path.isfile(output_file_path):
        raise FileNotFoundError("Unable to locate output file '{}'.".format(output_file_path))


def compress_geotiff(input_file_path: str, output_file_path: str) -> None:
    """
    Compress the specified geotiff using 'gdal.warp'.  This will use LZW compression and also set other options suited
    for minimising the size of the output file.
    :param input_file_path: path to the file that will be compressed
    :param output_file_path: path to the output file containing the compressed output
    :return: nothing
    :raise FileNotFoundError: if the input file cannot be found, or if the expected compressed output could not be
     located.
    :raise RuntimeError: if gdal is unable to create an output file; for example, because the file already exists and
    is open elsewhere.
    """
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError("Unable to find input file: '{}'.".format(input_file_path))

    creation_options = ["BIGTIFF=YES", "SPARSE_OK=TRUE", "TILED=YES", "COMPRESS=LZW"]
    warp_options = gdal.WarpOptions(format="Gtiff", creationOptions=creation_options)

    #   call gdal.Warp, which applies compression in the output file - will potentially throw a 'RuntimeError' if the
    #   file cannot be created
    _ = gdal.Warp(output_file_path, input_file_path, options=warp_options)

    if not os.path.isfile(output_file_path):
        raise FileNotFoundError("Unable to locate output file '{}'.".format(output_file_path))


def apply_mask(input_file_path: str,
               output_file_path: str,
               data_format: DataFormat = DEFAULT_DATA_FORMAT) -> None:
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError("Unable to find input file: '{}'.".format(input_file_path))

    #   parameters used in generating and applying the mask
    no_data_value = 1
    out_value = -9999
    mask_value = 0

    #   temporary file used to hold the mask
    mask_file_path = Path(input_file_path).with_suffix(".mask.tif")

    #   create the mask file and check it exists
    genValidMask(input_file_path, mask_file_path, data_format.format, no_data_value)
    if not os.path.isfile(mask_file_path):
        raise FileNotFoundError("Unable to find generated mask file: '{}'.".format(mask_file_path))

    #   apply the mask file
    maskImage(input_file_path,
              mask_file_path,
              output_file_path,
              data_format.format,
              data_format.type,
              out_value,
              mask_value)
    imageutils.popImageStats(output_file_path, True, out_value, True)

    #   remove the mask file
    mask_file_path.unlink()

    if not os.path.isfile(output_file_path):
        raise FileNotFoundError("Unable to locate output file '{}'.".format(output_file_path))


if __name__ == "__main__":
    pass
    #   initial function testing

    # clamp_raster(input_file_path="/mnt/hgfs/D/potential_evap/intermediate/2mAvgWindSpeedResampled.tif",
    #              output_file_path="/mnt/hgfs/D/clamped.tif",
    #              value_range=ValueRange(min=0, max=5))
    # compress_geotiff(input_file_path="/mnt/hgfs/D/potential_evap/out/ETp_2020-02-01.tif",
    #                  output_file_path="/mnt/hgfs/D/ETp_2020-02-01.compressed.tif")

