#!/usr/bin/env python

"""unittest tests for core module.

"""

import unittest
import toytree


class TestGetTopologyID(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=8, treeheight=10, seed=123, random_names=True)
        self.btree = toytree.rtree.baltree(ntips=8, treeheight=10, seed=123, random_names=True)
        self.trees = [self.itree, self.btree]

    def test_same_despite_rooting(self):
        """Tree rooting should not affect default topology_id """
        for tree in self.trees:
            tid = tree.get_topology_id()
            for node in tree[:-1]:
                rtree = tree.root(node)
                self.assertEqual(tid, rtree.get_topology_id())

    def test_diff_when_rooting(self):
        """Tree rooting should not affect default topology_id """
        for tree in self.trees:
            tid = tree.get_topology_id(include_root=True)
            for node in tree[:-1]:
                rtree = tree.root(node)
                if node in tree.treenode.children:
                    self.assertEqual(tid, rtree.get_topology_id(include_root=True))
                else:
                    self.assertNotEqual(tid, rtree.get_topology_id(include_root=True))

    def test_same_despite_rotation(self):
        """Tree rooting should not affect default topology_id """
        for tree in self.trees:
            tid = tree.get_topology_id()
            for node in tree[:-1]:
                rtree = tree.mod.rotate_node(node)
                self.assertEqual(tid, rtree.get_topology_id())


if __name__ == "__main__":
    unittest.main()
