#!/usr/bin/env python

"""Tests for DLC-based gene-tree rooting."""


import toytree



from conftest import PytestCompat

class TestRootOnMinimalDLC(PytestCompat):
    def setUp(self):
        self.sptree = toytree.tree("(((A,B),C),D);")
        self.gtree = toytree.tree("((((a1,a2),b1),c1),d1);")
        self.imap = {"a1": "A", "a2": "A", "b1": "B", "c1": "C", "d1": "D"}

    def test_method_available(self):
        self.assertTrue(hasattr(self.gtree.mod, "root_on_minimal_dlc"))
        self.assertTrue(hasattr(toytree.mod, "root_on_minimal_dlc"))

    def test_requires_rooted_species_tree(self):
        with self.assertRaises(Exception):
            self.gtree.mod.root_on_minimal_dlc(self.sptree.unroot(), self.imap)

    def test_returns_rooted_tree(self):
        rtree = self.gtree.mod.root_on_minimal_dlc(self.sptree, self.imap)
        self.assertIsInstance(rtree, toytree.ToyTree)
        self.assertTrue(rtree.is_rooted())

    def test_return_stats_and_ties(self):
        rtree, stats = self.gtree.mod.root_on_minimal_dlc(
            self.sptree,
            self.imap,
            return_stats=True,
        )
        self.assertTrue(rtree.is_rooted())
        self.assertIn("score_table", stats)
        self.assertIn("tied_best_edge_idxs", stats)
        self.assertIn("best_edge_idx", stats)
        self.assertGreaterEqual(stats["n_candidates"], 1)

    def test_store_scores_features(self):
        rtree = self.gtree.mod.root_on_minimal_dlc(
            self.sptree,
            self.imap,
            store_scores=True,
        )
        ndata = rtree.get_node_data()
        self.assertIn("DLC", ndata.columns)
        self.assertIn("DLC_root_prob", ndata.columns)


