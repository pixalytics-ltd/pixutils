import os
import logging
import http.client
import argparse
import re
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ceres_download")

#   used to extract the day/month/year supplied from the command line
DATE_REGEX_STR = r"(?P<year>(\d{4}))[-]?(?P<month>(\d{2}))[-]?(?P<day>(\d{2}))?"

#   remote filename formats
DAILY_NETFLUX_FILENAME = "CERES_NETFLUX_D_{y:04}-{m:02}-{d:02}.FLOAT.TIFF"
MONTHLY_NETFLUX_FILENAME = "CERES_NETFLUX_M_{y:04}-{m:02}.FLOAT.TIFF"

#   remote filename paths
DAILY_NETFLUX_PATH = "/archive/geotiff.float/CERES_NETFLUX_D/"
MONTHLY_NETFLUX_PATH = "/archive/geotiff.float/CERES_NETFLUX_M/"


def get_ceres_download_filename(year: int, month: int, day: int = None) -> str:
    """
    Return the filename of the CERES NetFlux product to be downloaded for the specified date
    :param year: the year to be downloaded
    :type year: int
    :param month: the month to be downloaded
    :type month: int
    :param day: the day to be downloaded.  Optional, if omitted the monthly product will be downloaded instead of the
    monthly.
    :type year: int
    :return: a string with the filename as expected on the remote server
    """
    return DAILY_NETFLUX_FILENAME.format(y=year, m=month, d=day) \
        if day is not None else MONTHLY_NETFLUX_FILENAME.format(y=year, m=month)


def _date_to_string(year: int, month: int, day: int = None) -> str:
    """
    Convenience function for providing a date string containing an optional day element
    :param year: the year element
    :type year: int
    :param month: the month element
    :type month: int
    :param day: the day element.  Optional, if omitted the string will only contain a year and month
    :return: a formatted date string
    """
    return "{y:04}-{m:02}-{d:02}".format(y=year, m=month, d=day) \
        if day is not None else "{y:04}-{m:02}".format(y=year, m=month)


def download_ceres_netflux(output_dir: str, year: int, month: int, day: int = None) -> str:
    """
    Attempts to download CERES data for the date being processed
    :param output_dir: the location to write the downloaded data to
    :type output_dir: str
    :param year: the year to be downloaded
    :type year: int
    :param month: the month to be downloaded
    :type month: int
    :param day: the day to be downloaded.  Optional, if omitted the monthly product will be downloaded instead of the
    monthly.
    :type year: int
    :return: a string containing the filename of the requested NDVI data.
    :rtype: str
    :raises RuntimeError: if the remote server doesn't return a 200 OK response or if the output file can't be created
    """
    filename = get_ceres_download_filename(year, month, day)

    local_file_path = os.path.join(output_dir, filename)
    logger.info("Downloading CERES NETFLUX data for {}.".format(_date_to_string(year, month, day)))

    # Connect to server
    logger.debug('Connecting to CERES NETFLUX')
    https = http.client.HTTPSConnection('neo.sci.gsfc.nasa.gov')

    # Open and retrieve file
    remote_path = DAILY_NETFLUX_PATH if day is not None else MONTHLY_NETFLUX_PATH
    https.request('GET', os.path.join(remote_path, filename))
    response = https.getresponse()

    # Close connection
    https.close()

    # expect a '200 OK' response from server
    if response.code == 200:
        # download directly to NETFLUX diretory
        with open(local_file_path, 'wb') as netFlux:
            netFlux.write(response.read())
    else:
        raise RuntimeError("Unexpected response ({code}) from server '{reason}'.".format(code=response.code,
                                                                                         reason=response.reason))

    # downloaded file
    if not os.path.isfile(local_file_path):
        raise RuntimeError("There was a problem writing the file to '{}'.".format(local_file_path))
    logger.info("Download of file '{}' complete.".format(local_file_path))

    return local_file_path


def main() -> int:
    arg_parser = argparse.ArgumentParser(description="Download CERES NetFlux data from the NASA servers.  Daily and"
                                                     " monthly products are currently supported.")
    arg_parser.add_argument("date", help="Date of data to be obtained (format: YYYY-MM-DD or YYYY-MM)")
    arg_parser.add_argument("output_dir", help="Destination directory for downloaded data")
    args = arg_parser.parse_args()

    matches = re.match(DATE_REGEX_STR, args.date)
    if matches:
        try:
            year = int(matches.group("year"))
            month = int(matches.group("month"))
            day = int(matches.group("day")) if matches.group("day") is not None else None
        except ValueError:
            logger.exception("An exception was parsing the date string ''.".format(args.date))
            print("Supplied date '{}' could not be correctly parsed."
                  "  Should be in the format YYYY-MM-DD or YYYY-MM.".format(args.date))
            return 1
    else:
        print("Supplied date '{}' could not be correctly parsed."
              "  Should be in the format YYYY-MM-DD or YYYY-MM.".format(args.date))
        return 1

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    try:
        downloaded_file = download_ceres_netflux(output_dir=args.output_dir, year=year, month=month, day=day)
        print("File was downloaded to: '{}'.".format(downloaded_file))
        return 0
    except RuntimeError:
        logger.exception("An exception was thrown whilst trying to download the file.")
        return 1
    except Exception:
        logger.exception("An unexpected exception was thrown whilst trying to download the file.")
        return 255


if __name__ == "__main__":
    exit(main())
