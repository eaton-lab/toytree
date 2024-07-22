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

logger.bind(name="toytree")


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
        self.tree = toytree.tree("((a:2,b:1)ab:1,(c:1,d:2)cd:1)r:2;")
        self.trees = [self.itree, self.btree]

    def test_prune_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.itree.mod.prune.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.prune.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_prune_require_root(self):
        """Prune maintains root node at original height if require_root=True."""
        tree1 = self.tree.mod.prune(
            "a", "b", 
            require_root=True, 
            preserve_dists=True,
        )
        self.assertAlmostEqual(
            self.tree.treenode.height,
            tree1.treenode.height
        )

        tree2 = self.tree.mod.prune(
            "a", "b", 
            require_root=False,
            preserve_dists=True,
        )
        self.assertAlmostEqual(
            self.tree.get_nodes("ab")[0].height,
            tree2.treenode.height
        )

    def test_prune_preserve_dists(self):
        """Prune sums removed internal node dists onto retained edges, or not."""
        tree1 = self.tree.mod.prune(
            "a", "b", "c",
            require_root=False,
            preserve_dists=True,
        )
        self.assertAlmostEqual(
            toytree.distance.get_node_distance(self.tree, 'a', 'c'),
            toytree.distance.get_node_distance(tree1, 'a', 'c'),
        )
        tree2 = self.tree.mod.prune(
            "a", "b", "c",
            require_root=False,
            preserve_dists=False,
        )        
        self.assertAlmostEqual(
            toytree.distance.get_node_distance(self.tree, 'a', 'c') - 1,
            toytree.distance.get_node_distance(tree2, 'a', 'c'),
        )


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

    def test_remove_unary_node(self):
        """Remove one unary node from a tree."""
        new1 = self.itree.mod.add_internal_node("r0", name="unary", dist=1)
        new2 = new1.mod.remove_unary_nodes()
        self.assertEqual(self.itree.nnodes, new2.nnodes)

    def test_remove_unary_nodes(self):
        """Remove one unary node from a tree."""
        new1 = self.itree.mod.add_internal_node("r0", name="u1", dist=0.5)
        new1 = new1.mod.add_internal_node("u1", name="u2", dist=0.1)
        new1 = new1.mod.add_internal_node("r0", name="u3", dist=0.1)
        new2 = new1.mod.remove_unary_nodes()
        self.assertEqual(self.itree.nnodes, new2.nnodes)


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

    def test_drop_tips_one_tip(self):
        """Remove one node."""
        tre = self.trees[0].mod.drop_tips("r1")
        self.assertEqual(self.trees[0].ntips - 1, tre.ntips)

    def test_drop_tips_multiple_tips(self):
        """..."""
        tre = self.itree.mod.drop_tips("r0", "r1")
        self.assertEqual(self.itree.ntips - 2, tre.ntips)
        self.assertEqual(self.itree.nnodes - 4, tre.nnodes)

    def test_drop_tips_log_warning_and_exception_if_no_selection(self):
        """Logger warning if tip Nodes are selected."""
        with capture_logs(format="{message}") as cap:
            with self.assertRaises(ValueError):            
                self.itree.mod.drop_tips()
        self.assertEqual(cap[0], "No nodes selected. Enter a node query.\n")

    def test_drop_tips_log_warning_and_exception_if_all_tips_selected(self):
        """Logger warning if tip Nodes are selected."""
        with self.assertRaises(ValueError):
            with capture_logs(format="{message}") as cap:
                self.itree.mod.drop_tips("~r*")
            self.assertEqual(cap[0], "Cannot drop all tips from the tree.\n")

    def test_drop_tips_log_warning_on_non_tip_selection(self):
        """Logger warning if tip Nodes are selected."""
        with capture_logs(format="{message}") as cap:
            self.itree.mod.drop_tips(15)
        self.assertEqual(cap[0], "Only tip Nodes are removed. See `mod.remove_nodes`.\n")


class TestModExtractSubtree(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.tree("((a:2,b:1)ab:1,(c:1,d:2)cd:1)r:2;")

    def test_extract_subtree_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.tree.mod.extract_subtree.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.extract_subtree.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_extract_subtree_single(self):
        """Remove one node."""
        tree = self.tree.mod.extract_subtree("a")
        self.assertEqual(tree.ntips, 1)
        self.assertEqual(tree.nnodes, 1)
        self.assertEqual(tree[0].dist, 2)

    def test_extract_subtree_multiple(self):
        """Remove one node."""
        tree = self.tree.mod.extract_subtree("a", "b")
        self.assertEqual(tree.ntips, 2)
        self.assertEqual(tree.nnodes, 3)
        self.assertEqual(tree[0].dist, 2)
        self.assertEqual(tree[1].dist, 1)
        self.assertEqual(tree[2].dist, 1)

    def test_extract_subtree_query_internal(self):
        """Remove one node."""
        tree = self.tree.mod.extract_subtree("ab")
        self.assertEqual(tree.ntips, 2)
        self.assertEqual(tree.nnodes, 3)
        self.assertEqual(tree[0].dist, 2)
        self.assertEqual(tree[1].dist, 1)
        self.assertEqual(tree[2].dist, 1)

    def test_extract_subtree_query_treenode(self):
        """Remove one node."""
        tree = self.tree.mod.extract_subtree("r")
        self.assertEqual(tree.ntips, 4)
        self.assertEqual(tree.nnodes, 7)
        self.assertEqual(tree[0].dist, 2)
        self.assertEqual(tree[1].dist, 1)
        self.assertEqual(tree[2].dist, 1)


class TestModBisect(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.tree("((a:2,b:1)ab:1,(c:1,d:2)cd:1)r:2;")

    def test_bisect_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.tree.mod.bisect.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.bisect.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_bisect_single(self):
        sub, tree = self.tree.mod.bisect("a")
        self.assertEqual(sub.ntips, 1)
        self.assertEqual(sub.nnodes, 1)
        self.assertEqual(sub[0].dist, 2)

    def test_bisect_xxx(self):
        tree = self.tree.mod.extract_subtree("a", "b")
        self.assertEqual(tree.ntips, 2)
        self.assertEqual(tree.nnodes, 3)
        self.assertEqual(tree[0].dist, 2)
        self.assertEqual(tree[1].dist, 1)
        self.assertEqual(tree[2].dist, 1)

    def test_bisect_xxx_internal(self):
        tree = self.tree.mod.extract_subtree("ab")
        self.assertEqual(tree.ntips, 2)
        self.assertEqual(tree.nnodes, 3)
        self.assertEqual(tree[0].dist, 2)
        self.assertEqual(tree[1].dist, 1)
        self.assertEqual(tree[2].dist, 1)

    def test_bisect_xxx_treenode(self):
        tree = self.tree.mod.extract_subtree("r")
        self.assertEqual(tree.ntips, 4)
        self.assertEqual(tree.nnodes, 7)
        self.assertEqual(tree[0].dist, 2)
        self.assertEqual(tree[1].dist, 1)
        self.assertEqual(tree[2].dist, 1)


if __name__ == '__main__':

    toytree.set_log_level("CRITICAL")

    #### RUN INDIVIDUAL TESTS #########################################
    load = unittest.TestLoader()
    tests = (
        load.loadTestsFromTestCase(TestModLadderize),
        load.loadTestsFromTestCase(TestModCollapseNodes),
        load.loadTestsFromTestCase(TestModRemoveUnaryNodes),
        load.loadTestsFromTestCase(TestModRotateNode),
        load.loadTestsFromTestCase(TestModExtractSubtree),
        load.loadTestsFromTestCase(TestModPrune),
        load.loadTestsFromTestCase(TestModDropTips),
        load.loadTestsFromTestCase(TestModBisect),
        # l.loadTestsFromTestCase(TestModResolvePolytomies),        

        load.loadTestsFromTestCase(TestModAddInternalNode),

    )

    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite(tests))


    #### DO ALL TESTS #########################################
    # unittest.main()