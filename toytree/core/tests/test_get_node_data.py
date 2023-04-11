#!/usr/bin/env python

"""Test cases for `ToyTree.set_node_data`

"""

import unittest
import numpy as np
import toytree


class TestToyTreeGetNodeData(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)

        colors = {0: 'red', 1: 'green', 2: 'orange'}
        ints = {0: 3, 1: 2, 2: 0}
        floats = {0: 2e-9, 1: 3.03253859, 2: 10 / 3.}
        mixed = {0: "red", 1: 3.03253859, 2: 0}
        complex_types = {
            0: {"red", "blue"}, 1: [3.03253859, 2.0], 2: np.array([0, 1])
        }

        self.tree.set_node_data("colors", colors, inplace=True)
        self.tree.set_node_data("ints", ints, inplace=True)
        self.tree.set_node_data("floats", floats, inplace=True)
        self.tree.set_node_data("mixed", mixed, inplace=True)
        self.tree.set_node_data("complex_types", complex_types, inplace=True)

    def test_todo(self):
        """Create tests..."""
        print(self.tree.get_node_data("complex_types"))


if __name__ == "__main__":

    unittest.main()
