#!/usr/bin/env python

"""Map values to colors

- [1, 1, 1, 0, 0, 0]                -> [c0, c0, c0, c1, c1, c1]
- [1, 1, 1, nan, nan, nan]          -> [c0, c0, c0, 0s, 0s, 0s]
- ['a', 'a', 'a', 'b', 'b', 'b']    -> [c0, c0, c0, c1, c1, c1]
- ['a', 1, 2, {3}, 'b', 1.0]        -> [c0, c1, c2, c3, c4, c5]
- [np.nan, 1, 2, {3}, 'b', 1.0]     -> [0s, c1, c2, c3, c4, c5]
- ['a', 1, 2, {3}, 'b', np.nan]     -> [c0, c1, c2, c3, c4, 0s]
"""

import unittest
import numpy as np
import toytree
from toytree.color import ToyColor as c
from toytree.style import get_color_mapped_feature, get_color_mapped_values


class TestColorMapper(unittest.TestCase):

    def setUp(self):
        self.tree = toytree.rtree.unittree(4)
        self.cols = toytree.color.COLORS1

    def test_colormap_int_data(self):
        data = self.tree.set_node_data("x", [2, 2, 2, 0, 0, 0, 0]).get_node_data("x")

        # Categorical
        colors = get_color_mapped_feature(self.tree, 'x', "Set2")
        [self.assertEqual(c(self.cols[1]), c(i)) for i in colors[:3]]
        [self.assertEqual(c(self.cols[0]), c(i)) for i in colors[3:]]

        # Linear
        colors = get_color_mapped_feature('x', "BlueRed")
        rgba_blue = (0.01960784, 0.18823529, 0.38039216, 1.)
        rgba_red = (0.40392157, 0., 0.12156863, 1.)
        for color, expected in zip(colors[0], rgba_red):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[3], rgba_blue):
            self.assertAlmostEqual(color, expected)

        # Palette
        colors = get_color_mapped_feature(data, ['red', 'blue', 'green'])
        tred = toytree.color.ToyColor('red')
        tblue = toytree.color.ToyColor('blue')
        for color, expected in zip(colors[0], tblue.rgba):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[3], tred.rgba):
            self.assertAlmostEqual(color, expected)

    def test_colormap_int_data_w_missing(self):
        data = self.tree.set_node_data("x", [1, 1, 1, np.nan, np.nan, np.nan, np.nan]).get_node_data('x')

        # Categorical
        colors = get_color_mapped_feature(data, "Set2")
        [self.assertEqual(c(self.cols[0]), c(i)) for i in colors[:3]]
        [self.assertEqual(c((0, 0, 0, 0)), c(i)) for i in colors[3:]]

        # Linear
        colors = get_color_mapped_feature(data, "BlueRed")
        rgba_blue = (0.01960784, 0.18823529, 0.38039216, 1.)
        for color, expected in zip(colors[0], rgba_blue):
            self.assertAlmostEqual(color, expected)

        # Palette
        colors = get_color_mapped_feature(data, ['red', 'blue', 'green'])
        tred = toytree.color.ToyColor('red')
        for color, expected in zip(colors[0], tred.rgba):
            self.assertAlmostEqual(color, expected)

    def test_colormap_str_data(self):
        data = self.tree.set_node_data("x", list("aaabbbb")).get_node_data('x')

        # Categorical
        colors = get_color_mapped_feature(data, "Set2")
        [self.assertEqual(c(self.cols[0]), c(i)) for i in colors[:3]]
        [self.assertEqual(c(self.cols[1]), c(i)) for i in colors[3:]]

        # Linear
        colors = get_color_mapped_feature(data, "BlueRed")
        rgba_blue = (0.01960784, 0.18823529, 0.38039216, 1.)
        rgba_red = (0.40392157, 0., 0.12156863, 1.)
        for color, expected in zip(colors[0], rgba_blue):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[3], rgba_red):
            self.assertAlmostEqual(color, expected)

        # Palette
        colors = get_color_mapped_feature(data, ['red', 'blue', 'green'])
        tred = toytree.color.ToyColor('red')
        tblue = toytree.color.ToyColor('blue')
        for color, expected in zip(colors[0], tred.rgba):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[3], tblue.rgba):
            self.assertAlmostEqual(color, expected)

    def test_colormap_str_data_w_missing(self):
        data = self.tree.set_node_data("x", list("aaabb") + [np.nan] * 2).get_node_data('x')

        # Categorical
        colors = get_color_mapped_feature(data, "Set2")
        [self.assertEqual(c(self.cols[0]), c(i)) for i in colors[:3]]
        [self.assertEqual(c(self.cols[1]), c(i)) for i in colors[3:5]]
        [self.assertEqual(c((0, 0, 0, 0)), c(i)) for i in colors[5:]]

        # Linear
        colors = get_color_mapped_feature(data, "BlueRed")
        rgba_blue = (0.01960784, 0.18823529, 0.38039216, 1.)
        rgba_mid = (0.96862745, 0.96862745, 0.96862745, 1.)
        for color, expected in zip(colors[0], rgba_blue):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[3], rgba_mid):
            self.assertAlmostEqual(color, expected)

        # Palette
        colors = get_color_mapped_feature(data, ['red', 'blue', 'green'])
        tred = toytree.color.ToyColor('red')
        tblue = toytree.color.ToyColor('blue')
        for color, expected in zip(colors[0], tred.rgba):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[3], tblue.rgba):
            self.assertAlmostEqual(color, expected)

    def test_colormap_full_mixed(self):
        data = self.tree.set_node_data("x", [np.nan] * 2 + [3] * 2 + ['a'] * 2 + [3.3]).get_node_data('x')

        # Categorical
        colors = get_color_mapped_feature(data, "Set2")
        [self.assertEqual(c((0, 0, 0, 0)), c(i)) for i in colors[:2]]
        [self.assertEqual(c(self.cols[0]), c(i)) for i in colors[2:4]]
        [self.assertEqual(c(self.cols[2]), c(i)) for i in colors[4:6]]
        [self.assertEqual(c(self.cols[1]), c(i)) for i in colors[6:]]

        # Linear
        colors = get_color_mapped_feature(data, "BlueRed")
        c0 = (0., 0., 0., 0.)
        c1 = (0.01960784, 0.18823529, 0.38039216, 1.)
        c2 = (0.96862745, 0.71764706, 0.6, 1.)
        c3 = (0.65490196, 0.81437908, 0.89411765, 1.)
        for color, expected in zip(colors[0], c0):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[2], c1):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[4], c2):
            self.assertAlmostEqual(color, expected)
        for color, expected in zip(colors[6], c3):
            self.assertAlmostEqual(color, expected)


if __name__ == "__main__":

    unittest.main()
