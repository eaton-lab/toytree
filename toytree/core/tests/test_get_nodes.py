#!/usr/bin/env python

"""unittest tests for core module.

"""

import unittest
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
            self.itree.get_nodes("~*r*")

    def test_get_nodes_raises_exception_on_no_matched_input(self):
        """Bad regex raises a ToytreeError from re.error."""
        with self.assertRaises(ToytreeError):
            self.itree.get_nodes("~*r*")


if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()
