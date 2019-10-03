import unittest
from pixutils.gdl.exec_gdl import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        """
        Tests that the GDL interpreter can compile and then run the 'hello_world.pro' file
        :return:
        """
        result, stdout, stderr = exec_gdl([
            ".compile hello_world.pro",
            "hello",
            "exit"
        ])

        self.assertEqual(0, result)
        self.assertEqual("% Compiled module: HELLO.\nHello world!\n", stdout)


if __name__ == '__main__':
    unittest.main()
