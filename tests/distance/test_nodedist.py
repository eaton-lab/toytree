#!/usr/bin/env python

"""Test Node distance functions

"""

import unittest
import numpy as np
import toytree


class TestRoot(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(10, seed=123, treeheight=10)
        self.btree = toytree.rtree.baltree(10, seed=123, treeheight=10)
        self.ntree = toytree.rtree.unittree(10, seed=123, treeheight=10)
        self.utree = self.itree.unroot()
        self.trees = [self.itree, self.btree, self.ntree, self.utree]

    def test_get_node_distance_matrix(self):
        for tree in self.trees:

            # check symmetry
            arr = tree.distance.get_node_distance_matrix()
            self.assertTrue(np.allclose(arr, arr.T))

            # check pandas formatting
            f1 = tree.distance.get_node_distance_matrix(df=True)
            f2 = tree.distance.get_node_distance_matrix(df=True, topology_only=True)

            # check distances among tips by name
            for name1 in tree.get_tip_labels():
                for name2 in tree.get_tip_labels():
                    dist = tree.distance.get_node_distance(name1, name2)
                    self.assertAlmostEqual(dist, f1.loc[name1, name2])

            # check distances among tips and/or internals by idx
            print(f1)
            tree._draw_browser(ts='p')
            for idx1 in range(tree.nnodes):
                for idx2 in range(tree.nnodes):
                    dist = tree.distance.get_node_distance(idx1, idx2)
                    print(idx1, idx2, dist, arr[idx1, idx2])
                    self.assertAlmostEqual(dist, arr[idx1, idx2])



if __name__ == "__main__":

    unittest.main()
