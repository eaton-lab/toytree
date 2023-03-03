#!/usr/bin/env python

"""

"""

import unittest
import numpy as np
import toyplot
from toytree.color import ToyColor


class TestColorMethods(unittest.TestCase):

    def setUp(self):

        # lists of colors
        self.palette = toyplot.color.brewer.palette("BlueRed")
        self.map = toyplot.color.brewer.map("BlueRed")

        self.mixed_single_colors = [
            "RED",
            "red",
            "rgba(100.0%,50.0%,25.0%,0.500)",
            "rgb(100%,50%,25%)",
            (1.0, 0.5, 0.25, 0.5),
            (1.0, 0.5, 0.25),
            np.array((1.0, 0.5, 0.25, 0.5), dtype=toyplot.color.dtype),
            ToyColor("red"),
            toyplot.color.Palette()[0],
        ]
        self.mixed_multi_colors = [
            ['blue', 'red'],
            ['blue', (1, 0, 0, 0.5)],
            [ToyColor((1, 0.5, 0.2, 1)), "blue"],
            np.array([ToyColor('blue'), ToyColor('red')]),
            self.palette,
            self.map.colors([0, 0.1, 0.5, 0.9]),
        ]

    # ...
    def test_css_to_css(self):
        self.assertEqual(ToyColor("red").css, "rgba(100.0%,0.0%,0.0%,1.000)")

    def test_css_to_rgba(self):
        self.assertEqual(ToyColor("red").rgba, (1, 0, 0, 1))
        self.assertEqual(ToyColor("rgba(100.0%,0.0%,0.0%,1.000)").rgba, (1, 0, 0, 1))

    # ...
    def test_rgb_to_css(self):
        self.assertEqual(ToyColor((1, 0, 0)).css, "rgba(100.0%,0.0%,0.0%,1.000)")

    def test_rgb_to_rgba(self):
        self.assertEqual(ToyColor((1, 0.2, 0.3)).rgba, (1, 0.2, 0.3, 1))

    # ...
    def test_rgba_to_css(self):
        self.assertEqual(ToyColor((1, 0, 0, 1)).css, "rgba(100.0%,0.0%,0.0%,1.000)")

    def test_rgba_to_rgba(self):
        self.assertEqual(ToyColor((1, 0.2, 0.3, 0.7)).rgba, (1, 0.2, 0.3, 0.7))

    def test_rgba_to_arr(self):
        self.assertEqual(ToyColor((1, 0.2, 0.3, 0.7)), np.array((1, 0.2, 0.3, 0.7), dtype=toyplot.color.dtype))

    # ...
    def test_arr_to_css(self):
        self.assertEqual(ToyColor(self.palette[0]).css, "rgba(2.0%,18.8%,38.0%,1.000)")

    def parse_multi(self):
        pass


if __name__ == '__main__':

    unittest.main()