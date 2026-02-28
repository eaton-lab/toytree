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
import toytree
from toytree.infer import (
    get_consensus_tree,
    get_consensus_features,
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
        tree = get_consensus_tree(self.utrees)
        self.assertEqual(tree.get_topology_id(), self.utrees[0].get_topology_id())
        self.assertFalse(tree.is_rooted())
        self.assertEqual(tree.nedges, 5 + 2)
        self.assertTrue(math.isnan(tree[-1].support))
        self.assertEqual(tree.get_mrca_node("a", "b").support, 1.0)
        self.assertEqual(tree.get_mrca_node("e", "d").support, 0.5)

    def test_get_majority_rule_topology_minfreq(self):
        """..."""
        tree = get_consensus_tree(self.utrees, min_freq=0.51)
        self.assertFalse(tree.is_rooted())
        self.assertEqual(tree.nedges, 5 + 1)        
        self.assertTrue(math.isnan(tree[-1].support))
        self.assertEqual(tree.get_mrca_node("a", "b").support, 1.0)
        self.assertEqual(tree.get_mrca_node("e", "d"), tree.get_mrca_node("c", "e", "d"))

    def test_get_majority_rule_topology_equal_freq_collapsed(self):
        """..."""
        treelist = self.utrees.treelist + [self.utrees[-1]]
        tree = get_consensus_tree(treelist)
        self.assertFalse(tree.is_rooted())
        self.assertEqual(tree.nedges, 5 + 1)
        self.assertTrue(math.isnan(tree[-1].support))
        self.assertEqual(tree.get_mrca_node("a", "b").support, 1.0)
        self.assertEqual(tree.get_mrca_node("e", "d"), tree.get_mrca_node("c", "e", "d"))



if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()