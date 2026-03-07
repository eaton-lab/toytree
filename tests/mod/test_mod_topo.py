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

import toytree
from toytree.utils import ToytreeError
from toytree.utils.src.logger_setup import capture_logs


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
                "support", {i: 100.0 / (i + 10) for i in range(tre.nnodes)}
            )

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
        select = ["r0", "r4"]
        for tre in self.trees:
            new = tre.mod.rotate_node(*select)
            new_cset = [
                set(i.get_leaf_names()) for i in new.get_mrca_node(*select).children
            ]
            old_cset = [
                set(i.get_leaf_names()) for i in tre.get_mrca_node(*select).children
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
            "a",
            "b",
            require_root=True,
            preserve_dists=True,
        )
        self.assertAlmostEqual(self.tree.treenode.height, tree1.treenode.height)

        tree2 = self.tree.mod.prune(
            "a",
            "b",
            require_root=False,
            preserve_dists=True,
        )
        self.assertAlmostEqual(
            self.tree.get_nodes("ab")[0].height, tree2.treenode.height
        )

    def test_prune_preserve_dists(self):
        """Prune sums removed internal node dists onto retained edges, or not."""
        tree1 = self.tree.mod.prune(
            "a",
            "b",
            "c",
            require_root=False,
            preserve_dists=True,
        )
        self.assertAlmostEqual(
            toytree.distance.get_node_distance(self.tree, "a", "c"),
            toytree.distance.get_node_distance(tree1, "a", "c"),
        )
        tree2 = self.tree.mod.prune(
            "a",
            "b",
            "c",
            require_root=False,
            preserve_dists=False,
        )
        self.assertAlmostEqual(
            toytree.distance.get_node_distance(self.tree, "a", "c") - 1,
            toytree.distance.get_node_distance(tree2, "a", "c"),
        )


class TestModRemoveUnaryNodes(unittest.TestCase):
    def setUp(self):
        self.itree = toytree.rtree.imbtree(ntips=10, treeheight=10, seed=123)
        self.btree = toytree.rtree.baltree(ntips=10, treeheight=10, seed=123)
        self.trees = [self.itree, self.btree]

    def test_remove_unary_nodes_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [
            i.strip() for i in self.itree.mod.remove_unary_nodes.__doc__.split("\n")
        ]
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

    def test_remove_unary_nodes_preserves_polytomies(self):
        """Unary removal should not collapse multifurcating internal nodes."""
        tree = toytree.tree("((a,b,c),d);")
        tree = tree.mod.add_internal_node("d", name="u1", dist=0.2)
        out = tree.mod.remove_unary_nodes()
        self.assertEqual(set(out.get_tip_labels()), {"a", "b", "c", "d"})
        self.assertEqual(out.ntips, 4)

    def test_remove_unary_nodes_regression_on_deep_backbone(self):
        """Regression: deep unary backbones should not drop sibling tips."""
        nwk = (
            "(((((((((((((((((((((((((((((((((((((((Phtheirospermum_ott721193)"
            "mrcaott75219ott981070)mrcaott36252ott75219)mrcaott1452ott36252)"
            "mrcaott1452ott25297)mrcaott1452ott23465)mrcaott1452ott131884)"
            "mrcaott1452ott51396)mrcaott1452ott110151)mrcaott1452ott305916)"
            "mrcaott1452ott5518258)mrcaott1452ott1605)mrcaott1452ott39175)"
            "mrcaott1452ott432231,broken_Pedicularis_mrcaott1452ott33561)"
            "mrcaott1452ott33561)mrcaott1016ott1452)mrcaott1016ott5046)"
            "mrcaott1016ott10430)mrcaott1016ott295840)mrcaott1016ott55260)"
            "mrcaott1016ott22352)mrcaott1016ott108502)mrcaott248ott1016,"
            "broken_Castilleja_'Core_Lamialesott5263556',"
            "broken_Orobanche_'Core_Lamialesott5263556')"
            "'Core_Lamialesott5263556')mrcaott248ott55259)mrcaott248ott11341)"
            "Lamiales_ott23736)mrcaott248ott1191)mrcaott248ott101831)"
            "mrcaott248ott68444)mrcaott248ott5942)mrcaott248ott320)"
            "mrcaott248ott650)mrcaott248ott308117)mrcaott248ott67236)"
            "mrcaott2ott248)mrcaott2ott10053)mrcaott2ott8379)mrcaott2ott969,"
            "(((((((((((((Aquilegia_ott964055)mrcaott38573ott7049099)"
            "mrcaott38573ott949642)mrcaott34125ott38573)Thalictroideae_ott5479017)"
            "mrcaott2441ott22673)mrcaott2441ott203150)mrcaott2441ott1072050)"
            "Ranunculaceae_ott387826)mrcaott2441ott21786)mrcaott2441ott3773)"
            "mrcaott2441ott92057)mrcaott2441ott3851)Ranunculales_ott872975)"
            "mrcaott2ott2441;"
        )
        expected = {
            "Phtheirospermum_ott721193",
            "broken_Pedicularis_mrcaott1452ott33561",
            "broken_Castilleja_'Core_Lamialesott5263556'",
            "broken_Orobanche_'Core_Lamialesott5263556'",
            "Aquilegia_ott964055",
        }
        out = toytree.tree(nwk).mod.remove_unary_nodes()
        self.assertEqual(set(out.get_tip_labels()), expected)


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
        self.assertEqual(
            cap[0], "Only tip Nodes are removed. See `mod.remove_nodes`.\n"
        )


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


class TestModResolveNode(unittest.TestCase):
    def setUp(self):
        self.tree = toytree.tree("((a,b),c,d,e)X;")
        self.tree2 = toytree.tree("(((a,b),c,d,e)X,(x,y)Y)R;")

    def test_resolve_node_api_exposure(self):
        """Method is exposed in mod APIs but not on ToyTree directly."""
        self.assertTrue(hasattr(toytree.mod, "resolve_node"))
        self.assertTrue(hasattr(self.tree.mod, "resolve_node"))
        self.assertFalse(hasattr(self.tree, "resolve_node"))

    def test_resolve_node_docs_match(self):
        """API and submodule documentations updated to match."""
        adoc = [i.strip() for i in self.tree.mod.resolve_node.__doc__.split("\n")]
        sdoc = [i.strip() for i in toytree.mod.resolve_node.__doc__.split("\n")]
        self.assertEqual(adoc, sdoc)

    def test_resolve_node_with_remainder_group(self):
        """Unspecified tips are auto-added as one trailing remainder group."""
        out = self.tree.mod.resolve_node("X", splits=[["~[ab]$"], ["c"]])
        node = out.get_nodes("X")[0]
        leaves = [{str(i.name) for i in child.iter_leaves()} for child in node.children]
        self.assertEqual(leaves, [{"a", "b"}, {"c"}, {"d", "e"}])

    def test_resolve_node_raises_on_conflict(self):
        """Raise if split divides descendants of one existing child clade."""
        with self.assertRaises(ToytreeError):
            self.tree.mod.resolve_node("X", splits=[["a", "c"], ["b", "d"]])

    def test_resolve_node_raises_on_overlap(self):
        """Raise if tip is assigned to multiple user groups."""
        with self.assertRaises(ToytreeError):
            self.tree.mod.resolve_node("X", splits=[["a", "b"], ["b", "c"]])

    def test_resolve_node_raises_on_tips_outside_target(self):
        """Raise if split group includes tips outside selected clade."""
        with self.assertRaises(ToytreeError):
            self.tree2.mod.resolve_node("X", splits=[["a", "x"], ["b"]])

    def test_resolve_node_noop_on_non_polytomy(self):
        """Return unchanged topology when selected node is not a polytomy."""
        out = self.tree.mod.resolve_node("a", "b", splits=[["a"], ["b"]])
        self.assertEqual(out.get_topology_id(), self.tree.get_topology_id())
        self.assertEqual(out.nnodes, self.tree.nnodes)

    def test_resolve_node_inplace_false(self):
        """Copy mode keeps original tree unchanged."""
        start = self.tree.nnodes
        out = self.tree.mod.resolve_node("X", splits=[["~[ab]$"], ["c"]], inplace=False)
        self.assertEqual(self.tree.nnodes, start)
        self.assertGreater(out.nnodes, start)

    def test_resolve_node_inplace_true(self):
        """Inplace mode mutates and returns original tree object."""
        tree = self.tree.copy()
        start = tree.nnodes
        out = tree.mod.resolve_node("X", splits=[["~[ab]$"], ["c"]], inplace=True)
        self.assertIs(out, tree)
        self.assertGreater(tree.nnodes, start)


if __name__ == "__main__":
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
        load.loadTestsFromTestCase(TestModResolveNode),
        # l.loadTestsFromTestCase(TestModResolvePolytomies),
        load.loadTestsFromTestCase(TestModAddInternalNode),
    )

    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite(tests))

    #### DO ALL TESTS #########################################
    # unittest.main()
