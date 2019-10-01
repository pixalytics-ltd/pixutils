import unittest
from pixutils.sentinel_filename import *


class TestSentinelFilename(unittest.TestCase):
    def test_positive(self):
        #   valid Sentinel filename
        result = parse_sentinel_filename("/home/pixalytics/Desktop/batch_calibrate/in/S1A_IW_GRDH_1SDV_20190925T062938_20190925T063003_029174_035008_F845.SAFE.zip")

        self.assertEqual(result.filename,
                         "S1A_IW_GRDH_1SDV_20190925T062938_20190925T063003_029174_035008_F845.SAFE.zip")
        self.assertEqual(result.mission_identifier,
                         "S1A")
        self.assertEqual(result.mode_beam_identifier,
                         "IW")
        self.assertEqual(result.product_type,
                         "GRD")
        self.assertEqual(result.resolution_class,
                         "H")
        self.assertEqual(result.processing_level,
                         "1")
        self.assertEqual(result.product_class,
                         "S")
        self.assertEqual(result.polarisation,
                         "DV")
        self.assertEqual(result.start_date_time,
                         "20190925T062938")
        self.assertEqual(result.start_date,
                         "20190925")
        self.assertEqual(result.start_time,
                         "062938")
        self.assertEqual(result.stop_date_time,
                         "20190925T063003")
        self.assertEqual(result.stop_date,
                         "20190925")
        self.assertEqual(result.stop_time,
                         "063003")
        self.assertEqual(result.absolute_orbit_number,
                         "029174")
        self.assertEqual(result.mission_data_take_id,
                         "035008")
        self.assertEqual(result.product_unique_identifier,
                         "F845")
        self.assertEqual(result.product_format_extension,
                         "SAFE.zip")

    def test_negative(self):
        #   shouldn't parse - is a modis filename
        self.assertRaises(ValueError,
                          parse_sentinel_filename,
                          "LC08_L1TP_200023_20180505_20180517_01_T1.tar")


if __name__ == '__main__':
    unittest.main()
