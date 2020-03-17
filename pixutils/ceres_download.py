import os
import logging
import http.client
import argparse
from datetime import datetime
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ceres_download")


def date_to_netflux_format(date: datetime.date) -> str:
    """
    Convenience function for presenting date times in a specified format
    :param date: the date to be represented as a string
    :return: date returned as a string formatted for NETFLUX filenames
    """
    return date.strftime("%Y-%m-%d")


def get_ceres_download_filename(date: datetime.date) -> str:
    """
    Return the filename of the CERES NetFlux product to be downloaded for the specified date
    :return: a string with an absolute path to the file in the 'working' directory
    """
    return "CERES_NETFLUX_D_{}.FLOAT.TIFF".format(date_to_netflux_format(date))


def download_ceres_netflux(date: datetime.date, output_dir: str) -> str:
    """
    Attempts to download CERES data for the date being processed
    :param date: the date of the data to be downloaded
    :type date: datetime.date
    :param output_dir: the location to write the downloaded data to
    :type output_dir: str
    :return: a string containing the filename of the requested NDVI data.
    :rtype: str
    :raises RuntimeError: if the remote server doesn't return a 200 OK response or if the output file can't be created
    """
    filename = get_ceres_download_filename(date)

    local_file_path = os.path.join(output_dir, filename)
    date_str = date_to_netflux_format(date)
    logger.info("Downloading CERES NETFLUX data for {}.".format(date_str))

    # Connect to server
    logger.debug('Connecting to CERES NETFLUX Monthly Average Data')
    https = http.client.HTTPSConnection('neo.sci.gsfc.nasa.gov')

    # Open and retrieve file
    https.request('GET', os.path.join('/archive/geotiff.float/CERES_NETFLUX_D/', filename))
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
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("date", help="Date of data to be obtained (format: YYYY-MM-DD)")
    arg_parser.add_argument("output_dir", help="Destination directory for downloaded data")
    args = arg_parser.parse_args()

    date = datetime.strptime(args.date, format="%Y-%m-%d")
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    try:
        downloaded_file = download_ceres_netflux(date, output_dir=args.output_dir)
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
