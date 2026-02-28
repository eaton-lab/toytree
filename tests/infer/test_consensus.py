#!/usr/bin/env python

"""Test consensus tree functions

TODO
----
# unrooted trees
# rooted trees

# infer MJ-rule unrooted topology from both tree sets
# - test support
# - test min_freq

# map supports and dists to an unrooted tree from utrees
# map supports and dists to an unrooted tree from rtrees

# map supports and dists to a rooted tree from utrees
# - returns ?unrooted tree with dist attrs
# - could root the tree back on orig rooting?

# map supports and dists to a rooted tree from rtrees w/ rooted=True
# - returns rooted tree w/ height attrs

"""

import math
import unittest
import io
import numpy as np
from contextlib import redirect_stderr
import toytree
from toytree.infer import (
    consensus_tree,
    consensus_features,
)


class TestConsensusTree(unittest.TestCase):

    def setUp(self):
        self.utrees = toytree.mtree([
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",  # topo1
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",  # topo1
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",  # topo1            
            "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",  # topo2
            "((a:1,b:1):3,(d:2,(c:3,e:2):1):1);",  # topo3
            "((d:2,(c:3,e:2):1),(a:1,b:1):3):1;",  # topo3
        ])

        # rooted ultrametric trees
        self.rtrees = toytree.mtree([
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",  # topo1
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",  # topo1
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",  # topo1       
            "((a:1,b:1):3,(e:3,(c:2,d:2):1):1);",  # topo2
            "((a:1,b:1):3,(d:3,(c:2,e:2):1):1);",  # topo3            
            "((a:1,b:1):4,(d:3,(c:2,e:2):1):2);",  # topo3 alt blens
        ])

    def test_check_trees_set_for_ultrametric_rtrees(self):
        """Raise exception if tree set is not ultrametric"""
        # with self.assertRaises(ValueError):
        #     ...

    def test_check_trees_set_for_ultrametric_utrees(self):
        """Do not raise exceptoin when trees are ultrametric"""
        # with not self.assertRaises(ValueError):
        #     ...

    def test_get_majority_rule_topology(self):
        """..."""
        tree = consensus_tree(self.utrees)
        self.assertEqual(tree.get_topology_id(), self.utrees[0].get_topology_id())
        self.assertFalse(tree.is_rooted())
        self.assertEqual(tree.nedges, 5 + 2)
        self.assertTrue(math.isnan(tree[-1].support))
        self.assertEqual(tree.get_mrca_node("a", "b").support, 1.0)
        self.assertEqual(tree.get_mrca_node("e", "d").support, 0.5)

    def test_get_majority_rule_topology_minfreq(self):
        """..."""
        tree = consensus_tree(self.utrees, min_freq=0.51)
        self.assertFalse(tree.is_rooted())
        self.assertEqual(tree.nedges, 5 + 1)        
        self.assertTrue(math.isnan(tree[-1].support))
        self.assertEqual(tree.get_mrca_node("a", "b").support, 1.0)
        self.assertEqual(tree.get_mrca_node("e", "d"), tree.get_mrca_node("c", "e", "d"))

    def test_get_majority_rule_topology_equal_freq_collapsed(self):
        """..."""
        treelist = self.utrees.treelist + [self.utrees[-1]]
        tree = consensus_tree(treelist)
        self.assertFalse(tree.is_rooted())
        self.assertEqual(tree.nedges, 5 + 1)
        self.assertTrue(math.isnan(tree[-1].support))
        self.assertEqual(tree.get_mrca_node("a", "b").support, 1.0)
        self.assertEqual(tree.get_mrca_node("e", "d"), tree.get_mrca_node("c", "e", "d"))

    def test_get_consensus_features_requires_requested_features(self):
        ctree = consensus_tree(self.utrees)
        with self.assertRaises(ValueError):
            consensus_features(ctree, self.utrees, conditional=False)

    def test_get_consensus_features_edge_dist(self):
        ctree = consensus_tree(self.utrees)
        ftree = consensus_features(ctree, self.utrees, edge_features=["dist"], conditional=False)
        node = ftree.get_mrca_node("a", "b")
        self.assertTrue(hasattr(node, "dist_mean"))
        self.assertTrue(hasattr(node, "dist_median"))
        self.assertTrue(hasattr(node, "dist_std"))
        self.assertTrue(hasattr(node, "dist_min"))
        self.assertTrue(hasattr(node, "dist_max"))
        self.assertTrue(hasattr(node, "dist_range"))

    def test_get_consensus_features_additional_feature(self):
        trees = [i.copy() for i in self.utrees]
        vals = [1, 2, 3, 4, 5, 6]
        for tree, val in zip(trees, vals):
            tree = tree.set_node_data("rate", {tree.get_mrca_node("a", "b").idx: val}, inplace=True)
        ctree = consensus_tree(trees)
        ftree = consensus_features(ctree, trees, features=["rate"])
        node = ftree.get_mrca_node("a", "b")
        self.assertAlmostEqual(node.rate_mean, float(np.mean(vals)))
        self.assertAlmostEqual(node.rate_median, float(np.median(vals)))
        self.assertAlmostEqual(node.rate_min, float(np.min(vals)))
        self.assertAlmostEqual(node.rate_max, float(np.max(vals)))

    def test_get_consensus_features_ultrametric_includes_height(self):
        ctree = consensus_tree(self.rtrees)
        rtree = ctree.root("a", "b")
        ftree = consensus_features(rtree, self.rtrees, features=["height"], ultrametric=True)
        node = ftree.get_mrca_node("a", "b")
        self.assertTrue(hasattr(node, "height_mean"))
        self.assertTrue(hasattr(node, "height_median"))
        self.assertTrue(hasattr(node, "height_std"))
        self.assertTrue(hasattr(node, "height_min"))
        self.assertTrue(hasattr(node, "height_max"))

    def test_get_consensus_features_raises_on_missing_feature(self):
        ctree = consensus_tree(self.utrees)
        with self.assertRaises(ValueError):
            consensus_features(ctree, self.utrees, features=["not_a_feature"])

    def test_get_consensus_features_warns_and_remaps_wrong_feature_class(self):
        ctree = consensus_tree(self.rtrees).root("a", "b")
        err = io.StringIO()
        with redirect_stderr(err):
            ftree = consensus_features(
                ctree,
                self.rtrees,
                features=["dist"],
                edge_features=["height"],
                ultrametric=True,
            )
        msg = err.getvalue()
        self.assertIn("'dist' was provided in features", msg)
        self.assertIn("'height' was provided in edge_features", msg)
        self.assertTrue(hasattr(ftree.get_mrca_node("a", "b"), "dist_mean"))
        self.assertTrue(hasattr(ftree.get_mrca_node("a", "b"), "height_mean"))

    def test_get_consensus_tree_rejects_min_freq_out_of_bounds(self):
        with self.assertRaises(ValueError):
            consensus_tree(self.utrees, min_freq=1.1)



if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()
