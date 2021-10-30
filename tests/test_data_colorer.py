import unittest

from timetracker.chart.data_colorer import *
import datetime


class data_colorer_test(unittest.TestCase):
    def test_gradient(self):
        a = Gradient([0, 1], lambda x: x, (255, 0, 0), (0, 255, 0))
        g = a.from_fraction_base(0.5)
        self.assertEqual(g, (128, 128, 0))

    def test_multi_gradient(self):
        # TODO implement test for this.
        pass


if __name__ == '__main__':
    unittest.main()
