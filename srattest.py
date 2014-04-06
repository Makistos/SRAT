__author__ = 'mep'

import unittest
import srat


class SratTester(unittest.TestCase):

    def setUp(self):
        srat.open_files(['test/E02012-2013.csv'])

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
