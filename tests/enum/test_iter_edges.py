#!/usr/bin/env python

"""

"""

import unittest
import numpy as np
import toytree

ITER_EDGES = np.array([
    [0, 9],
    [1, 9],
    [2, 6],
    [3, 6],
    [4, 7],
    [5, 7],
    [6, 8],
    [7, 8],
])


class TestEdges(unittest.TestCase):
    def setUp(self):
        """Six tip tree three clades of two."""
        self.tree = toytree.tree("(a,b,((c,d)CD,(e,f)EF)X)AB;")
        self.utree = self.tree.unroot()
        self.rtree = self.utree.root("a", "b")

    def test_iter_edges_rooting(self):
        """Rooted trees return (Node(child), Node(root))."""
        e0 = sorted(self.utree.iter_edges('name'))
        e1 = sorted(self.rtree.iter_edges('name'))
        self.assertNotEqual(e0, e1)

    def test_iter_edges_default_type(self):
        """Iter_edges defaults to returning Node objects.

        This is different from iter_bipartitions because most of the
        result of iter_edges composes internal nodes which have no
        name attribute.
        """
        for node, _ in self.tree.iter_edges():
            self.assertIsInstance(node, toytree.Node)

    def test_iter_edges_idx(self):
        for node, _ in self.tree.iter_edges('idx'):
            self.assertIsInstance(node, int)
        for node, _ in self.tree.iter_edges('name'):
            self.assertIsInstance(node, str)



if __name__ == "__main__":

    unittest.main()
