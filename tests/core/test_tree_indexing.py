#!/usr/bin/env python

"""unittest tests for core module.

"""

import unittest
import toytree
import numpy as np
from toytree.utils import ToytreeError


class TestToyTreeGetNodes(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)

    def test_index_by_idx(self):
        node0 = self.tree[0]
        self.assertEqual(node0.idx, 0)

    def test_index_by_negative_idx(self):
        root = self.tree[-1]
        self.assertEqual(root.idx, self.tree.nnodes - 1)

    def test_index_by_list(self):
        select = [0, 1, 2, 3, 4]
        nodes = self.tree[select]
        self.assertEqual([i.idx for i in nodes], select)

    def test_index_by_array(self):
        select = np.array([0, 1, 2, 3, 4])
        nodes = self.tree[select]
        self.assertEqual([i.idx for i in nodes], list(select))

    def test_index_by_slice(self):
        nodes = self.tree[2:4]
        self.assertEqual([i.idx for i in nodes], [2, 3])

    def test_index_by_slice_fancy(self):
        nodes = self.tree[2::2]
        self.assertEqual([i.idx for i in nodes], list(range(2, self.tree.nnodes, 2)))

    def test_index_by_bad_idx_raises_exception(self):
        with self.assertRaises(ToytreeError):
            _ = self.tree[80]

    def test_index_by_name_raises_exception(self):
        with self.assertRaises(ToytreeError):
            _ = self.tree['a']


if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()
