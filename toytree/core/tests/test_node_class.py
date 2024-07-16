#!/usr/bin/env python

"""unittest tests for core module.

"""

import unittest
from math import isnan
import toytree
from toytree.utils import ToytreeError


def get_connected_nodes_ABC():
    nodeA = toytree.Node("A")
    nodeB = toytree.Node("B")
    nodeC = toytree.Node("C")
    nodeAB = toytree.Node("AB")
    nodeABC = toytree.Node("ABC")
    nodeAB._add_child(nodeA)
    nodeAB._add_child(nodeB)
    nodeABC._add_child(nodeAB)
    nodeABC._add_child(nodeC)


class TestToyTreeNodeMethods(unittest.TestCase):

    def setUp(self):
        self.node = toytree.Node()
        self.tree1 = toytree.tree("((a,b),c);")
        self.tree2 = toytree.tree("((a:1,b:2)AB:2,C:2):2;")

    def test_node_defaults(self):
        """Default node attributes."""
        self.assertEqual(self.node.name, "")
        self.assertEqual(self.node.dist, 0.0)
        self.assertTrue(isnan(self.node.support))
        self.assertEqual(self.node.idx, -1)
        self.assertEqual(self.node.up, None)

    def test_node_args(self):
        """Default node attributes."""
        node = toytree.Node(name="A", dist=2.1, support=100)
        self.assertEqual(node.name, "A")
        self.assertEqual(node.dist, 2.1)
        self.assertEqual(node.support, 100.)
        self.assertTrue(isinstance(node.support, float))

    def test_node_height(self):
        """Node height returns a float and dynamically changes."""
        self.assertEqual(self.tree1.treenode.height, 2.0)
        self.assertEqual(self.tree1.get_nodes('a')[0].height, 0.0)
        self.assertEqual(self.tree1.get_nodes('b')[0].height, 0.0)
        self.assertEqual(self.tree1.get_mrca_node('a', 'b').height, 1.0)

        # cannot set height directly
        with self.assertRaises(toytree.utils.src.exceptions.TreeNodeError):
            self.node.height = 10

        # can modify height by modifying a tree
        tmp = self.tree1.mod.edges_set_node_heights({'b': 2})
        self.assertEqual(tmp.get_nodes('b')[0].height, 2)

    def test_node_idxs(self):
        """Node idx returns an int and dynamically changes."""
        self.assertEqual(self.tree1.treenode.idx, 4)
        self.assertEqual(self.tree1.get_nodes('a')[0].idx, 0)
        self.assertEqual(self.tree1.get_nodes('b')[0].idx, 1)
        self.assertEqual(self.tree1.get_mrca_node('a', 'b').idx, 3)

        # cannot set idx directly
        with self.assertRaises(toytree.utils.src.exceptions.TreeNodeError):
            self.node.idx = 10

        # modifications to tree topology change idxs
        tmp = self.tree1.mod.rotate_node(3)
        self.assertEqual(tmp.get_nodes('b')[0].idx, 0)

    def test_node_children(self):
        """Node children returns Tuple of Nodes and changes dynamically"""
        child_idxs = [i.idx for i in self.tree1.treenode.children]
        self.assertEqual(child_idxs, [3, 2])

        # cannot set children directly
        with self.assertRaises(toytree.utils.src.exceptions.TreeNodeError):
            self.node.children = ()

        # tips have no children
        self.assertEqual(self.node.children, ())


    def test_node_method_copy_single_node(self):
        """Test Node.copy() method."""

        # copy a singular Node
        cnode = self.node.copy()

        # it is a different object
        self.assertNotEqual(self.node, cnode)

        # copy has same basic attribute values (name, dist, support)
        self.assertEqual(self.node.name, cnode.name)
        self.assertEqual(self.node.dist, cnode.dist)        
        self.assertEqual(isnan(self.node.support), isnan(cnode.support))

        # copy has ... Nodes
        self.assertEqual(self.node.up, cnode.up)

        # returns a copy of all Nodes
        cnode = self.node.copy()
        self.assertNotEqual(self.node, cnode)


    def test_node_method_copy_connected_node(self):
        """Test Node.copy() method."""
        node = self.tree1.get_mrca_node('a', 'b')
        cnode = node.copy()
        dnode = node.copy(detach=True)

        # Node objects should be different
        self.assertNotEqual(node, cnode)
        self.assertNotEqual(node.up, cnode.up)

        # number of descendants should be the same
        self.assertEqual(
            sum(1 for i in node.traverse()),
            sum(1 for i in cnode.traverse()))

        # number of ancestors should be the same if not detached
        self.assertEqual(
            sum(1 for i in node.iter_ancestors()),
            sum(1 for i in cnode.iter_ancestors()))

        # number of ancestors should be diff if detached (and not root)
        self.assertNotEqual(
            sum(1 for i in node.iter_ancestors()),
            sum(1 for i in dnode.iter_ancestors()))

    def test_node_method_detach(self):
        """detach should ..."""
        nodeA = toytree.Node("A")
        nodeB = toytree.Node("B")
        nodeC = toytree.Node("C")
        nodeAB = toytree.Node("AB")
        nodeABC = toytree.Node("ABC")
        nodeAB._add_child(nodeA)
        nodeAB._add_child(nodeB)
        nodeABC._add_child(nodeAB)
        nodeABC._add_child(nodeC)        

        # if nodeAB is detached then 
        nodeAB._detach()
        self.assertEqual(nodeAB.up, None)
        self.assertEqual(nodeAB.children[0], nodeA)
        self.assertEqual(nodeA.up, nodeAB)
        self.assertEqual(nodeABC.children, (nodeC,))

        # if a detached nodes edge spans the root inherit the full edge
        # ... No, just unroot the tree for this to happen.


    def test_node_method_delete(self):
        nodeA = toytree.Node("A")
        nodeB = toytree.Node("B")
        nodeC = toytree.Node("C")
        nodeAB = toytree.Node("AB")
        nodeABC = toytree.Node("ABC")
        nodeAB._add_child(nodeA)
        nodeAB._add_child(nodeB)
        nodeABC._add_child(nodeAB)
        nodeABC._add_child(nodeC)        

        # if nodeAB is deleted then others are connected
        nodeAB._delete()
        self.assertEqual(nodeA.up, nodeABC)
        self.assertEqual(nodeB.up, nodeABC)        
        self.assertEqual(nodeC.up, nodeABC)

        # deleted Node object should have no connections
        self.assertEqual(nodeAB.idx, -1)
        self.assertEqual(nodeAB.up, None)        
        self.assertEqual(nodeAB.children, ())




    # def test_get_nodes_by_idx(self):
    #     """Ladderize mirrors node rotations reversibly."""
    #     select = [0, 1, 2, 3, 4]
    #     res0 = self.itree.get_nodes(*select)
    #     self.assertEqual(set(i.idx for i in res0), set(select))

    # def test_get_nodes_by_node(self):
    #     """Ladderize mirrors node rotations reversibly."""
    #     select = [self.itree[i] for i in [0, 1, 2, 3, 4]]
    #     res0 = self.itree.get_nodes(*select)
    #     self.assertEqual(set(res0), set(select))

    # def test_get_nodes_raise_exception_on_other_trees_nodes(self):
    #     """Raise ValueError if queried with Nodes from a different tree."""
    #     with self.assertRaises(ValueError):
    #         self.itree.get_nodes(self.btree[5])

    # def test_get_nodes_raises_exception_on_bad_regex(self):
    #     """Bad regex raises a ToytreeError from re.error."""
    #     with self.assertRaises(ToytreeError):
    #         self.itree.get_nodes("~*r*")

    # def test_get_nodes_raises_exception_on_no_matched_input(self):
    #     """Bad regex raises a ToytreeError from re.error."""
    #     with self.assertRaises(ToytreeError):
    #         self.itree.get_nodes("~*r*")


if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()
