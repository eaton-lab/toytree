#!/usr/bin/env python

"""Test cases for `ToyTree.get_node_data`."""

import numpy as np
from conftest import PytestCompat

import toytree


class TestToyTreeGetNodeData(PytestCompat):
    """Tests for retrieving node data in tabular form."""

    def setUp(self):
        """Create a tree with several sparse node features."""
        self.tree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)

        colors = {0: "red", 1: "green", 2: "orange"}
        ints = {0: 3, 1: 2, 2: 0}
        floats = {0: 2e-9, 1: 3.03253859, 2: 10 / 3.0}
        mixed = {0: "red", 1: 3.03253859, 2: 0}
        complex_types = {0: {"red", "blue"}, 1: [3.03253859, 2.0], 2: np.array([0, 1])}

        self.tree.set_node_data("colors", colors, inplace=True)
        self.tree.set_node_data("ints", ints, inplace=True)
        self.tree.set_node_data("floats", floats, inplace=True)
        self.tree.set_node_data("mixed", mixed, inplace=True)
        self.tree.set_node_data("complex_types", complex_types, inplace=True)

    def test_single_feature_returns_named_series(self):
        """Single-feature requests should preserve the feature name."""
        data = self.tree.get_node_data("colors")
        self.assertEqual(data.name, "colors")
        self.assertEqual(data.iloc[0], "red")
        self.assertEqual(data.iloc[1], "green")
        self.assertEqual(data.iloc[2], "orange")

    def test_multiple_features_return_dataframe(self):
        """Multi-feature requests should still return a DataFrame."""
        data = self.tree.get_node_data(["colors", "ints"])
        self.assertEqual(list(data.columns), ["colors", "ints"])
        self.assertEqual(data["colors"].iloc[0], "red")
        self.assertEqual(data["ints"].iloc[0], 3)
