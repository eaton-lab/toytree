#!/usr/bin/env python

"""...

"""

import unittest
# import numpy as np
import toyplot
import toytree
from toytree.color import ToyColor
from toytree.style import TreeStyle, validate_style
from toytree.utils import ToytreeError


class TestStyles(unittest.TestCase):

    def setUp(self):
        self.tree = toytree.rtree.unittree(10, seed=123)
        self.style = TreeStyle()
        self.cycler = toytree.color.color_cycler()

    def test_style_copy(self):
        """Copying a style should deepcopy (copies of substyles and dicts)."""


    def test_style_set_(self):
        """..."""


    def test_style_validate_single_colors(self):
        """show style in notebook without fail on complex settings."""
        self.style.node_colors = "red"
        self.style.tip_labels_colors = "#262626"
        self.style.node_labels_style.stroke = ToyColor((1, 0, 0.5, 0.5))
        self.style.edge_colors = (1, 0, 0.5, 0.5)
        validate_style(self.tree, self.style)


    def test_style_validate_multi_colors(self):
        """show style in notebook without fail on complex settings."""
        self.style.node_colors = ["red"] + ["blue"] * (self.tree.nnodes - 1)
        self.style.tip_labels_colors = [next(self.cycler) for i in range(self.tree.ntips)]
        # self.style.node_labels_style.stroke = ToyColor((1, 0, 0.5, 0.5))
        # self.style.edge_colors = (1, 0, 0.5, 0.5)
        validate_style(self.tree, self.style)


    def test_style_raise_exception_on_validate_bad_color(self):
        """show style in notebook without fail on complex settings."""
        self.style.node_colors = "..."
        with self.assertRaises(ToytreeError):
            validate_style(self.tree, self.style)


if __name__ == "__main__":
    unittest.main()
