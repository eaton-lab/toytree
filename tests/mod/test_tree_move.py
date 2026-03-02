#!/usr/bin/env python

"""Tests for depth-N NNI/SPR move utilities."""

import unittest

import toytree


class TestTreeMoveDepthN(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.rtree.unittree(ntips=7, seed=123)

    def test_iter_nni_n_exact_one_unique(self):
        trees = list(toytree.mod.iter_nni_n(self.tree, n=1, order="sorted"))
        tids = [i.get_topology_id() for i in trees]
        self.assertTrue(trees)
        self.assertEqual(len(tids), len(set(tids)))

    def test_iter_spr_n_exact_one_unique(self):
        trees = list(toytree.mod.iter_spr_n(self.tree, n=1, order="sorted"))
        tids = [i.get_topology_id() for i in trees]
        self.assertTrue(trees)
        self.assertEqual(len(tids), len(set(tids)))

    def test_iter_order_random_seed_reproducible(self):
        t0 = [i.get_topology_id() for i in toytree.mod.iter_nni_n(self.tree, n=1, order="random", seed=5)]
        t1 = [i.get_topology_id() for i in toytree.mod.iter_nni_n(self.tree, n=1, order="random", seed=5)]
        self.assertEqual(t0, t1)

    def test_move_nni_n_walk_and_sample(self):
        t_walk = toytree.mod.move_nni_n(self.tree, n=2, mode="walk", seed=11)
        t_samp = toytree.mod.move_nni_n(self.tree, n=2, mode="sample", seed=11)
        self.assertIsInstance(t_walk, toytree.ToyTree)
        self.assertIsInstance(t_samp, toytree.ToyTree)
        self.assertIsNone(t_walk.treenode.up)
        self.assertIsNone(t_samp.treenode.up)

    def test_tree_mod_api_methods_exist(self):
        trees = list(self.tree.mod.iter_nni_n(n=1, order="sorted"))
        self.assertTrue(trees)
        moved = self.tree.mod.move_spr_n(n=1, mode="walk", seed=2)
        self.assertIsInstance(moved, toytree.ToyTree)


if __name__ == "__main__":
    unittest.main()
