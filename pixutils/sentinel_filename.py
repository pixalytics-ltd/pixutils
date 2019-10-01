import re
from collections import namedtuple

#   https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1-product-formatting
SENTINEL_FILENAME_PATTERN = \
    r"(\w{3})_(\w{2})_(\w{3})(\w)_(\d)(\D)(\D{2})_((\d{8})T(\d{6}))_((\d{8})T(\d{6}))_(\d{6})_(\d{6})_(\w{4})\.(.*)"
_SENTINEL_FILENAME_REGEX = re.compile(SENTINEL_FILENAME_PATTERN, re.IGNORECASE)

_SENTINEL_IDENTIFIER_TO_GROUP_ID = {
    "filename": 0,
    "mission_identifier": 1,
    "mode_beam_identifier": 2,
    "product_type": 3,
    "resolution_class": 4,
    "processing_level": 5,
    "product_class": 6,
    "polarisation": 7,
    "start_date_time": 8,
    "start_date": 9,
    "start_time": 10,
    "stop_date_time": 11,
    "stop_date": 12,
    "stop_time": 13,
    "absolute_orbit_number": 14,
    "mission_data_take_id": 15,
    "product_unique_identifier": 16,
    "product_format_extension": 17
}

"""Contains named fields extracted from a Sentinel filename"""
SentinelProductInfo = namedtuple("SentinelProductInfo", sorted(_SENTINEL_IDENTIFIER_TO_GROUP_ID))


def parse_sentinel_filename(filename):
    """
    Extracts details from a Sentinel filename using the schema defined at:
    https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1-product-formatting
    :param filename: a filename string that can include a full path
    :type filename: str
    :return: a SentinelProductInfo object containing all fields extracted from the filename
    :rtype: SentinelProductInfo
    :raises ValueError: if the filename doesn't appear to match the schema
    """
    match = _SENTINEL_FILENAME_REGEX.search(filename)

    if match:
        #   produce the output dictionary by matching field names to their respective regex groups
        d = dict((k, match.group(v)) for (k, v) in _SENTINEL_IDENTIFIER_TO_GROUP_ID.items())

        #   use the output dictionary to build the output class
        return SentinelProductInfo(**d)
    else:
        raise ValueError("'{}' does not appear to be a valid Sentinel filename pattern.".format(filename))

