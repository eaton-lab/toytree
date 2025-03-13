#!/usr/bin/env python

"""Unittests for NJ tree inference."""


import unittest
import toytree
import numpy as np
import pandas as pd


class TestNeighborJoining(unittest.TestCase):


    def test_binary_tree_arr(self):
        dist = np.array([
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 2],
            [6, 6, 6, 2, 0],
        ], dtype=float)
        tree = toytree.infer.neighbor_joining_tree(dist)
        distr = tree.distance.get_tip_distance_matrix()


    def test_binary_tree_df(self):
        dist = np.array([
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 2],
            [6, 6, 6, 2, 0],
        ], dtype=float)
        df = pd.DataFrame(dist, index=list("abcde"))
        tree = toytree.infer.neighbor_joining_tree(df)


    def test_equal_dists_tree(self):
        # two clades with equal distances
        dist = np.array([
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 3],
            [6, 6, 6, 3, 0],
        ], dtype=float)
        df = pd.DataFrame(dist, index=list("abcde"))
        tree = toytree.infer.neighbor_joining_tree(df)


    def test_polytomy_tree(self):
        dist = np.array([
            [0, 2, 2, 4, 4],
            [2, 0, 2, 4, 4],
            [2, 2, 0, 4, 4],
            [4, 4, 4, 0, 2],
            [4, 4, 4, 2, 0],
        ], dtype=float)
        tree = toytree.infer.neighbor_joining_tree(dist)


    def test_polytomy_and_equal_dists_tree(self):
        dist = np.array([
            [0, 2, 2, 4, 4],
            [2, 0, 2, 4, 4],
            [2, 2, 0, 4, 4],
            [4, 4, 4, 0, 2],
            [4, 4, 4, 2, 0],
        ], dtype=float)
        tree = toytree.infer.neighbor_joining_tree(dist)


    def test_identical_names(self):
        dist = np.array([
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 2],
            [6, 6, 6, 2, 0],
        ], dtype=float)
        df = pd.DataFrame(dist, index=list("abcdd"))
        tree = toytree.infer.neighbor_joining_tree(df)


if __name__ == "__main__":
    toytree.set_log_level("CRITICAL")
    unittest.main()



