__author__ = 'mep'

import unittest
import srat
from elo import elo_calc_change


class SratTester(unittest.TestCase):

    def setUp(self):
        srat.open_files(['test/E02012-2013.csv'])

    def test_elo(self):
        elo = elo_calc_change(630.0, 500.0, False, 2, 2)
        self.assertEqual(round(elo, 2), -3.58)
        elo = elo_calc_change(630.0, 500.0, False, 3, 1)
        self.assertEqual(round(elo, 2), 9.64)


if __name__ == '__main__':
    unittest.main()
