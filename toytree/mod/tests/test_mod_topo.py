#!/usr/bin/env python

"""unittest tests for mod_topo module.

- toytree.mod.ladderize
- toytree.mod.collapse_nodes
- toytree.mod.rotate_node
- toytree.mod.prune
- toytree.mod.remove_unary_nodes
- toytree.mod.add_internal_node
- toytree.mod.drop_tips
"""

import unittest
from loguru import logger
from toytree.utils.src.logger_setup import capture_logs
import toytree

# logger.bind(name="toytree")


class TestModLadderize(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_ladderize_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.ladderize.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.ladderize.__doc__.split("\n")]        
        self.assertEqual(adoc, sdoc)

    def test_ladderize_api_defaults(self):
        """API returns same defaults as the submodule."""
        for tre in self.trees:
            order1 = tre.mod.ladderize().get_tip_labels()
            order2 = toytree.mod.ladderize(tre).get_tip_labels()
            self.assertEqual(order1, order2)

    def test_ladderize(self):
        """Ladderize 0 returns larger first child, 1 larger last child."""
        for tre in self.trees:
            new = tre.mod.ladderize(direction=0)
            for node in new:
                if node.children:
                    child0, child1 = node.children
                    self.assertLessEqual(len(child0), len(child1))
            new = tre.mod.ladderize(direction=1)
            for node in new.traverse():
                if node.children:
                    self.assertGreaterEqual(*[len(i) for i in node.children])

    def test_ladderize_symmetry(self):
        """Ladderize mirrors node rotations reversibly."""
        for tre in self.trees:
            new = tre.mod.ladderize(1).mod.ladderize(0)
            self.assertEqual(tre.get_topology_id(), new.get_topology_id())
            new = tre.mod.ladderize(0).mod.ladderize(1)
            self.assertEqual(tre.get_topology_id(), new.get_topology_id())


class TestModCollapseNodes(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)
        self.trees = [self.itree, self.btree]
        for tre in self.trees:
            tre.set_node_data(
                "support", 
                {i: 100. / (i + 10) for i in range(tre.nnodes)})

    def test_collapse_nodes_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.collapse_nodes.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.collapse_nodes.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_collapse_nodes_api_defaults(self):
        """API returns same default results as the submodule."""
        for tre in self.trees:
            tre0 = tre.mod.collapse_nodes(min_support=15)
            tre1 = toytree.mod.collapse_nodes(tre, min_support=15)
            self.assertEqual(tre0.get_topology_id(), tre1.get_topology_id())

            tre0 = tre.mod.collapse_nodes(min_dist=2)
            tre1 = toytree.mod.collapse_nodes(tre, min_dist=2)
            self.assertEqual(tre0.get_topology_id(), tre1.get_topology_id())

            tre0 = tre.mod.collapse_nodes(1, 2, 3, min_dist=2)
            tre1 = toytree.mod.collapse_nodes(tre, 1, 2, 3, min_dist=2)
            self.assertEqual(tre0.get_topology_id(), tre1.get_topology_id())

    def test_collapse_nodes_custom(self):
        """Collapse nodes by custom selection."""
        self.assertEqual(
            self.itree.nnodes - 3, 
            self.itree.mod.collapse_nodes(13, 14, 15).nnodes,
        )

    # TODO
    # def test_collapse_nodes_support(self):
    #     """Collapse nodes ... min dist."""

    # def test_collapse_nodes_dist(self):
    #     pass


class TestModRotateNode(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_rotate_node_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.rotate_node.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.rotate_node.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_rotate_root(self):
        """Rotate one node."""
        for tre in self.trees:
            new = tre.mod.rotate_node(tre.treenode)
            new_cset = [set(i.get_leaf_names()) for i in new.treenode.children]
            old_cset = [set(i.get_leaf_names()) for i in tre.treenode.children]
            self.assertEqual(new_cset, old_cset[::-1])

    def test_rotate_one_node_by_mrca(self):
        """Rotate one node."""
        select = ['r0', 'r4']
        for tre in self.trees:
            new = tre.mod.rotate_node(*select)
            new_cset = [
                set(i.get_leaf_names()) for i 
                in new.get_mrca_node(*select).children
            ]
            old_cset = [
                set(i.get_leaf_names()) for i 
                in tre.get_mrca_node(*select).children
            ]
            self.assertEqual(new_cset, old_cset[::-1])


class TestModPrune(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_prune_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.prune.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.prune.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_prune_orig_root_height(self):
        """Prune maintains root node at its original height."""
        select = [0, 1, 2, 3, 4]
        for tre in self.trees:
            new = tre.mod.prune(*select, require_root=True, preserve_branch_length=True)
            self.assertAlmostEqual(tre.treenode.height, new.treenode.height)

    def test_prune_new_root_height(self):
        """Prune to new MRCA as root node with its orig height."""
        select = [0, 1, 2, 3, 4]
        for tre in self.trees:
            mrca_height_on_orig_tree = tre.get_mrca_node(*select).height            
            new = tre.mod.prune(*select, require_root=False, preserve_branch_length=True)
            self.assertAlmostEqual(mrca_height_on_orig_tree, new.treenode.height)

    def test_prune_preserve_branch_lengths(self):
        """Prune sums removed internal node dists onto retained edges, or not."""
        select = ['r0', 'r1', 'r3', 'r4', 'r5']
        tre = self.itree
        tips_x = ('r0', 'r1') # height retained, dist changed.
        tips_y = ('r0', 'r1', 'r2') # node is removed.
        tips_z = ('r0', 'r1', 'r3') # height and dist retained
        new = tre.mod.prune(*select, require_root=True, preserve_branch_length=True)
        self.assertAlmostEqual(tre.treenode.height, new.treenode.height)
        self.assertAlmostEqual(
            tre.get_mrca_node(*tips_x).height, 
            new.get_mrca_node(*tips_x).height,
        )
        self.assertNotAlmostEqual(
            tre.get_mrca_node(*tips_x).dist,
            new.get_mrca_node(*tips_x).dist,
        )
        self.assertAlmostEqual(
            tre.get_mrca_node(*tips_z).height,
            new.get_mrca_node(*tips_z).height,
        )
        self.assertAlmostEqual(
            tre.get_mrca_node(*tips_z).dist,
            new.get_mrca_node(*tips_z).dist,
        )
        self.assertRaises(ValueError, new.get_mrca_node, *tips_y)

    def test_prune_not_preserve_branch_lengths(self):
        """Prune sums removed internal node dists onto retained edges, or not."""
        select = ['r0', 'r1', 'r3', 'r4', 'r5']
        tre = self.itree
        tips_x = ('r0', 'r1') # height changed, dist retained.
        tips_y = ('r0', 'r1', 'r2') # node is removed.
        tips_z = ('r0', 'r1', 'r3') # height and dist retained
        new = tre.mod.prune(*select, require_root=True, preserve_branch_length=False)
        # the root height may or may not change, depending on which nodes are removed.
        # self.assertAlmostEqual(tre.treenode.height, new.treenode.height)
        self.assertNotAlmostEqual(
            tre.get_mrca_node(*tips_x).height,
            new.get_mrca_node(*tips_x).height,
        )
        self.assertAlmostEqual(
            tre.get_mrca_node(*tips_x).dist,
            new.get_mrca_node(*tips_x).dist,
        )
        self.assertAlmostEqual(
            tre.get_mrca_node(*tips_z).height,
            new.get_mrca_node(*tips_z).height,
        )
        self.assertAlmostEqual(
            tre.get_mrca_node(*tips_z).dist,
            new.get_mrca_node(*tips_z).dist,
        )
        self.assertRaises(ValueError, new.get_mrca_node, *tips_y)

    def test_prune_inplace(self):
        """Inplace pruning has same result as prune copy."""
        select = ['r0', 'r1', 'r3', 'r4', 'r5']        
        new = self.itree.mod.prune(*select)
        ctre = self.itree.copy()
        ctre.mod.prune(*select, inplace=True)
        self.assertEqual(ctre.get_topology_id(), new.get_topology_id())

    # def test_prune_new_root_height(self):
    #     """Prune to get new MRCA root maintained at its original height."""
    #     select = [0, 1, 2, 3, 4]

    #     new = self.tree.mod.prune(*select, require_root=False, preserve_branch_length=True)
    #     self.assertAlmostEqual(new.treenode.height, mrca_height_on_orig_tree)

    # def test_prune_new_root_height(self):
    #     """Prune to get new MRCA root maintained at its original height."""
    #     select = [0, 1, 2, 3, 4]
    #     mrca_height_on_orig_tree = self.tree.get_mrca_node(*select).height
    #     new = self.tree.mod.prune(*select, require_root=False, preserve_branch_length=True)
    #     self.assertAlmostEqual(new.treenode.height, mrca_height_on_orig_tree)

    # def test_prune_2(self):
    #     select = [0, 1, 2, 3, 4]        
    #     newtre = self.tree.mod.prune(*select)
    #     new_tips = sorted(newtre.get_tip_labels())
    #     select_tips = sorted([i.name for i in self.tree.get_nodes(*select)])
    #     self.assertEqual(new_tips, select_tips)


    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


class TestModRemoveUnaryNodes(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_remove_unary_nodes_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.remove_unary_nodes.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.remove_unary_nodes.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_remove_unary_nodes(self):
        """Remove one unary node from a tree."""
        new1 = self.itree.mod.add_internal_node("r0", name="unary", dist=1)
        new2 = new1.mod.remove_unary_nodes()
        self.assertEqual(self.itree.nnodes, new2.nnodes)
        # self.assertEqual(new.get_nodes("r0")[0].up.name, "unary")


class TestModAddInternalNode(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_add_internal_node_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.add_internal_node.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.add_internal_node.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_add_terminal_unary_node(self):
        """Add unary node by node name."""
        new = self.itree.mod.add_internal_node("r0", name="unary", dist=1)
        new_node = new.get_nodes("r0")[0]
        self.assertEqual(new_node.up.name, "unary")
        self.assertAlmostEqual(new_node.up.height, 1)

    def test_add_internal_unary_node_by_mrca(self):
        """Add a unary node at location by mrca."""
        new = self.itree.mod.add_internal_node("r0", "r3", name="unary", dist=1)
        new_node = new.get_mrca_node("r0", "r3")
        self.assertEqual(new_node.up.name, "unary")
        self.assertAlmostEqual(new_node.up.height, new_node.height + 1)

    def test_add_internal_unary_node_by_node(self):
        """Add a unary node at location by mrca."""
        new = self.itree.mod.add_internal_node(self.itree[8], name="unary", dist=1)
        new_node = new.get_mrca_node(*[i.idx for i in self.itree[8].get_descendants()])
        self.assertEqual(new_node.up.name, "unary")
        self.assertAlmostEqual(new_node.up.height, new_node.height + 1)

    def test_add_internal_node_raise_value_error_on_bad_dist(self):
        """Remove one unary node from a tree."""
        with self.assertRaises(ValueError):
            self.itree.mod.add_internal_node("r0", "r3", dist=100)


class TestModDropTips(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)        
        self.trees = [self.itree, self.btree]

    def test_drop_tips_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.drop_tips.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.drop_tips.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_drop_tips(self):
        """..."""

    def test_drop_tips_log_warning_on_non_tip_selection(self):
        """Logger warning if tip Nodes are selected."""
        with capture_logs(format="{message}") as cap:
            self.itree.mod.drop_tips(15)
        self.assertEqual(cap[0], "No tips selected. Matched query: [Node(idx=15)]\n")



if __name__ == '__main__':

    toytree.set_log_level("ERROR")
    unittest.main()
