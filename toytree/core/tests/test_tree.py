#!/usr/bin/env python

"""unittest tests for core module.

"""

import unittest
import numpy as np
import toytree
from toytree.utils import ToytreeError


class TestToyTreeGetNodes(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_get_nodes_by_name(self):
        """Ladderize mirrors node rotations reversibly."""
        select = ['r0', 'r1', 'r3', 'r4', 'r5']
        res0 = self.itree.get_nodes(*select)
        self.assertEqual(set(i.name for i in res0), set(select))

    def test_get_nodes_by_idx(self):
        """Ladderize mirrors node rotations reversibly."""
        select = [0, 1, 2, 3, 4]
        res0 = self.itree.get_nodes(*select)
        self.assertEqual(set(i.idx for i in res0), set(select))

    def test_get_nodes_by_node(self):
        """Ladderize mirrors node rotations reversibly."""
        select = [self.itree[i] for i in [0, 1, 2, 3, 4]]
        res0 = self.itree.get_nodes(*select)
        self.assertEqual(set(res0), set(select))
    
    def test_get_nodes_raise_exception_on_other_trees_nodes(self):
        """Raise ValueError if queried with Nodes from a different tree."""
        with self.assertRaises(ValueError):
            self.itree.get_nodes(self.btree[5])

    def test_get_nodes_raises_exception_on_bad_regex(self):
        """Bad regex raises a ToytreeError from re.error."""
        with self.assertRaises(ToytreeError):
            self.itree.get_nodes("*r*", regex=True)

    def test_get_nodes_raises_exception_on_no_matched_input(self):
        """Bad regex raises a ToytreeError from re.error."""
        with self.assertRaises(ToytreeError):
            self.itree.get_nodes("*r*", regex=True)




class TestToyTreeSetNodeData(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)

    def test_set_node_data(self):
        """..."""
        # colors = {0: 'red', 1: 'green', 2: 'orange'}
        # ints = {0: 3, 1: 2, 2: 0}
        # floats = {0: 2e-9, 1: 3.03253859, 2: 10 / 3.}
        # mixed = {0: "red", 1: 3.03253859, 2: 0}
        # complex_types = {
        #     0: {"red", "blue"}, 1: [3.03253859, 2.0], 2: np.array([0, 1])
        # }

        # self.tree.set_node_data("colors", colors, inplace=True)
        # self.tree.set_node_data("ints", ints, inplace=True)
        # self.tree.set_node_data("floats", floats, inplace=True)        
        # self.tree.set_node_data("mixed", mixed, inplace=True)        
        # self.tree.set_node_data("complex_types", complex_types, inplace=True)

    def test_todo(self):
        """Create tests..."""
            

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


if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()
