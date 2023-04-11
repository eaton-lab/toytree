#!/usr/bin/env python

"""Test rooting/unrooting functions and the maintenance of tree data.

Function
--------
tree.root(
    *query: 'Query',
    root_dist: 'Optional[float]' = None,
    edge_features: 'Optional[Sequence[str]]' = None,
    inplace: 'bool' = False,
) -> 'ToyTree'

Note
----
Uses get_mrca_node(*query) to get new root edge.
"""

import unittest
import numpy as np
import toytree
from toytree.utils import ToytreeError


class TestRoot(unittest.TestCase):
    def setUp(self):
        self.czech = toytree.io.parse_newick_string("((C,D)1,(A,(B,X)3)2,E)R;", internal_labels="name")
        """: Example dataset with inner labels as edge data."""
        self.supp = toytree.tree("(a,b,((c,d)CD[&support=100],(e,f)EF[&support=80])X[&support=90])AB;")
        """: Tree w/ internal names and supports"""
        self.itree = toytree.rtree.imbtree(10, seed=123, treeheight=10)
        self.btree = toytree.rtree.baltree(10, seed=123, treeheight=10)
        self.utree = toytree.rtree.unittree(10, seed=123, treeheight=10)
        self.trees = [self.itree, self.btree, self.utree]

    def test_czech_2017_test_case(self):
        """Edge features are transferred on re-rooting."""
        # set a color feature to Nodes as 'ecolor' and 'ncolor' where
        # only ecolor will be treated as an edge feature.
        colors = {'1': 'red', '2': 'green', '3': 'orange'}
        tree = self.czech
        tree.set_node_data("ecolor", colors, inplace=True)
        tree.set_node_data("ncolor", colors, inplace=True)

        # style to draw the tree (used in docs example)
        kwargs = {
            'layout': 'd',
            'use_edge_lengths': False,
            'node_sizes': 10,
            'node_labels': 'name',
            'node_labels_style': {
                'font-size': 20,
                'baseline-shift': 10,
                '-toyplot-anchor-shift': 10,
            }}

        # draw original tree
        tree.draw(
            node_colors=tree.get_node_data('ncolor', missing='black'),
            edge_colors=tree.get_node_data('ecolor', missing='black'),
            **kwargs,
        )

        # re-root, treating 'ecolor' but not 'ncolor' as an edge
        # feature.
        rtree = tree.root("X", edge_features=["ecolor"])
        rtree.draw(
            node_colors=rtree.get_node_data('ncolor', missing='black'),
            edge_colors=rtree.get_node_data('ecolor', missing='black'),
            **kwargs,
        )

        self.assertEqual(rtree.get_nodes("R")[0].ecolor, "green")
        self.assertEqual(rtree.get_nodes("1")[0].ecolor, "red")
        self.assertEqual(rtree.get_nodes("2")[0].ecolor, "orange")
        self.assertEqual(hasattr(rtree.get_nodes("3")[0], "ecolor"), False)

    def test_raise_exception_on_root_on_non_monophyletic_clade(self):
        """Raise ToytreeError on non-monophyletic outgroup."""
        for tre in self.trees:
            with self.assertRaises(ToytreeError):
                tre.root("r1", "r7")

        for tre in self.trees:
            with self.assertRaises(ToytreeError):
                tre.root("~r[1,7]")

    def test_root_on_internal_node(self):
        """Raise ToytreeError on non-monophyletic outgroup."""
        for tre in self.trees:
            mrca = tre.get_mrca_node("r1", "r2")
            tre.root(mrca)

    def test_root_unroot_transferrable(self):
        """Default edge features such as 'support' are properly transferable
        among edges during rooting, unrooting, and re-rooting.
        """
        s1 = self.supp
        s2 = s1.root("EF")  # unroot -> root
        s3 = s2.unroot()    # root -> unroot
        s4 = s3.root("AB")  # diff unroot to diff root
        s5 = s4.root("EF")  # root -> diff root

        # for each internal Node in the original tree
        for inode in s1[s1.ntips:-1]:

            # get the descendants
            tips = inode.get_leaf_names()
            # print(f"tips={tips}")

            # for each unrooted or re-rooted tree
            for tree in (s1, s2, s3, s4, s5):

                # get tips mrca on the new tree
                mrca = tree.get_mrca_node(*tips)

                # check that node has same support value still
                if mrca.is_root():
                    clade = tree.get_ancestors(*tips)
                    other = tree.get_mrca_node(*set(tree[:tree.ntips]) - set(clade))
                    # print(f"mrca={mrca} root {other}")
                    self.assertEqual(inode.support, other.support)
                else:
                    # print(f"mrca={mrca}")
                    self.assertEqual(inode.support, mrca.support)

    def test_support_value_of_root_node_is_nan(self):
        """The root Node support value should be nan by default."""
        self.assertTrue(np.isnan(self.itree.root("r0").treenode.support))

    def test_unroot_child_dist_data(self):
        """Unrooting removes treeNode while maintaining all other dist info."""
        for tree in self.trees:
            rtre = tree
            utre = tree.unroot()
            sum_child_dists = sum([i.dist for i in rtre.treenode.children])
            new_child_dist = utre.treenode.children[-1]._dist
            self.assertAlmostEqual(sum_child_dists, new_child_dist)

    def test_root_on_current_root_on_rooted_tree(self):
        """Rooting on the root Node is allowed for rooted trees, which
        simply returns the same tree, but not for unrooted trees, since
        no edge exists to create a new root on.
        """
        rtre = self.itree.root("r0")
        rtre.root("r0")

    def test_raise_exception_on_current_root_on_unrooted_tree(self):
        """Rooting on the root Node is allowed for rooted trees, which
        simply returns the same tree, but not for unrooted trees, since
        no edge exists to create a new root on.
        """
        utre = self.itree.unroot()
        with self.assertRaises(ToytreeError):
            utre.root(utre.treenode)

    def test_root_child_dist_data(self):
        """The dist between the two root children should be maintained."""
        for tree in self.trees:
            rtre = tree
            c1, c2 = [i.get_leaf_names() for i in rtre.treenode.children]

            utre = tree.unroot()
            retre = utre.root(*c1)

            m1 = rtre.get_mrca_node(*c1)
            m2 = rtre.get_mrca_node(*c2)
            odist = rtre.distance.get_node_distance(m1, m2)

            for tre in (utre, retre):
                m1 = tre.get_mrca_node(*c1)
                m2 = tre.get_mrca_node(*c2)
                tre.get_mrca_node(m1.idx, m2.idx)
                dist = tre.distance.get_node_distance(m1, m2)
                self.assertAlmostEqual(odist, dist)

    def test_root_dist_midpoint_default(self):
        """The root_dist arg uses midpoint as default."""

    def test_root_dist_user_setting(self):
        """The root_dist arg can be set by the user."""



    # def test_root_rooted_tree_on_current_root(self):
    #     """User attempts to root tree on current root or one of its children."""
    #     for tre in self.trees:
    #         new1 = tre.root(tre.treenode)
    #         new2 = tre.root(tre.treenode.children[0])
    #         new3 = tre.root(tre.treenode.children[1])


    # def test_root_tree_single_tip(self):
    #     """..."""
    #     for tre in self.trees:
    #         new = tre.root("r0")
    #         new

    # def test_root_tree_two_tips(self):
    #     """..."""
    #     for tre in self.trees:
    #         tre.root("r0", "r1")
    #         # self.assertEqual(new1.get_tip_labels(), new2.get_tip_labels())

    # def test_root_tree_inplace(self):
    #     """..."""
    #     for tre in self.trees:
    #         new1 = tre.root("r0", "r1")
    #         new2 = tre.copy()
    #         new2.root("r0", "r1", inplace=True)
    #         self.assertEqual(new1.get_tip_labels(), new2.get_tip_labels())

    # def test_root_tree_support_values_transfer(self):
    #     """..."""
    #     for tre in self.trees:
    #         tre.root('r0', "r3")

    # def test_root_tree_dist_values_transfer(self):
    #     """..."""
    #     for tre in self.trees:
    #         tre.root('r0', "r3")

    # def test_root_tree_extra_edge_features_transfer(self):
    #     """..."""
    #     for tre in self.trees:
    #         tre[0].feature1 = 3.0
    #         tre[1].feature2 = "A"
    #         tre.root('r0', "r3", edge_features=["feature1", "feature2"])



if __name__ == "__main__":

    toytree.set_log_level("CRITICAL")
    unittest.main()
