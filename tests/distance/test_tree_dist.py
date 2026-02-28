#!/usr/bin/env python

"""Tests for tree distance metrics."""

import math
import unittest

import numpy as np

import toytree
from toytree.distance import (
    get_treedist_kf_branch_score,
    get_treedist_rf,
    get_treedist_rfg_mci,
    get_treedist_rfg_ms,
    get_treedist_rfg_msi,
    get_treedist_rfg_spi,
    get_treedist_rfi,
)
from toytree.distance._src.treedist_utils import (
    get_trees_matching_split_info_dist,
    get_trees_mutual_clust_info_dist,
    get_trees_mutual_clust_info_dist_from_biparts,
)
from toytree.utils import ToytreeError


class TestTreeDistances(unittest.TestCase):
    def setUp(self):
        # same tip set, one internal split differs.
        self.t1 = toytree.tree("(((a,b),c),(d,e));")
        self.t2 = toytree.tree("(((a,c),b),(d,e));")

    def test_identity_is_zero_for_distance_metrics(self):
        funcs = [
            get_treedist_rf,
            get_treedist_rfi,
            get_treedist_rfg_ms,
            get_treedist_rfg_msi,
            get_treedist_rfg_spi,
            get_treedist_rfg_mci,
        ]
        for func in funcs:
            with self.subTest(metric=func.__name__):
                self.assertTrue(
                    np.isclose(func(self.t1, self.t1, normalize=False), 0.0)
                )

    def test_msi_and_mci_are_distinct_metrics(self):
        msi = get_treedist_rfg_msi(self.t1, self.t2, normalize=False)
        mci = get_treedist_rfg_mci(self.t1, self.t2, normalize=False)
        expected_msi = get_trees_matching_split_info_dist(
            self.t1, self.t2, normalize=False
        )
        self.assertTrue(np.isclose(msi, expected_msi))
        self.assertFalse(np.isclose(msi, mci))

    def test_matching_split_dist_normalize_rejected(self):
        with self.assertRaises(ToytreeError):
            get_treedist_rfg_ms(self.t1, self.t2, normalize=True)

    def test_mci_dist_from_biparts_matches_tree_api(self):
        b1 = list(self.t1.iter_bipartitions())
        b2 = list(self.t2.iter_bipartitions())
        via_biparts = get_trees_mutual_clust_info_dist_from_biparts(
            b1, b2, normalize=False
        )
        via_tree = get_trees_mutual_clust_info_dist(self.t1, self.t2, normalize=False)
        self.assertTrue(np.isclose(via_biparts, via_tree))

    def test_four_tip_conflicting_trees_match_definition_values(self):
        # Single informative split per tree:
        # t1: AB|CD and t2: AC|BD (fully conflicting).
        t1 = toytree.tree("((a,b),(c,d));")
        t2 = toytree.tree("((a,c),(b,d));")
        info_2v2 = math.log2(3)  # -log2(1/3)

        # RF: symmetric diff count of splits.
        self.assertTrue(np.isclose(get_treedist_rf(t1, t2, normalize=False), 2.0))
        self.assertTrue(np.isclose(get_treedist_rf(t1, t2, normalize=True), 1.0))

        # RFI: each tree has one 2|2 split with info log2(3), no shared split info.
        self.assertTrue(
            np.isclose(get_treedist_rfi(t1, t2, normalize=False), 2.0 * info_2v2)
        )
        self.assertTrue(np.isclose(get_treedist_rfi(t1, t2, normalize=True), 1.0))

        # Matching split distance: 2 taxa must move between conflicting 2|2 splits.
        self.assertTrue(np.isclose(get_treedist_rfg_ms(t1, t2, normalize=False), 2.0))

        # MSI/SPI distances on conflicting 2|2 splits reduce to full info difference.
        self.assertTrue(
            np.isclose(get_treedist_rfg_msi(t1, t2, normalize=False), 2.0 * info_2v2)
        )
        self.assertTrue(np.isclose(get_treedist_rfg_msi(t1, t2, normalize=True), 1.0))
        self.assertTrue(
            np.isclose(get_treedist_rfg_spi(t1, t2, normalize=False), 2.0 * info_2v2)
        )
        self.assertTrue(np.isclose(get_treedist_rfg_spi(t1, t2, normalize=True), 1.0))

        # MCI distance: each 2|2 split has entropy 1 bit, conflicting shared MCI is 0.
        self.assertTrue(np.isclose(get_treedist_rfg_mci(t1, t2, normalize=False), 2.0))
        self.assertTrue(np.isclose(get_treedist_rfg_mci(t1, t2, normalize=True), 1.0))

    def test_five_tip_rf_matches_split_count_definition(self):
        # Rooted 5-tip trees have two informative internal splits each.
        # Here one split is shared and one differs -> symmetric diff = 2.
        t1 = toytree.tree("(((a,b),c),(d,e));")
        t2 = toytree.tree("(((a,c),b),(d,e));")
        self.assertTrue(np.isclose(get_treedist_rf(t1, t2, normalize=False), 2.0))
        self.assertTrue(np.isclose(get_treedist_rf(t1, t2, normalize=True), 0.5))

    def test_kf_branch_score_identity_is_zero(self):
        t1 = toytree.tree("((a:1,b:2):3,(c:4,d:5):6);")
        self.assertTrue(np.isclose(get_treedist_kf_branch_score(t1, t1), 0.0))

    def test_kf_branch_score_shared_topology_branch_length_difference(self):
        t1 = toytree.tree("((a:1,b:1):1,(c:1,d:1):1);")
        t2 = toytree.tree("((a:2,b:1):3,(c:1,d:1):1);")
        # Differences on two shared branches: a-tip (1) and internal AB|CD split (2)
        expected = math.sqrt((2 - 1) ** 2 + (3 - 1) ** 2)
        self.assertTrue(np.isclose(get_treedist_kf_branch_score(t1, t2), expected))

    def test_kf_branch_score_conflicting_topology_unit_lengths(self):
        t1 = toytree.tree("((a:1,b:1):1,(c:1,d:1):1);")
        t2 = toytree.tree("((a:1,c:1):1,(b:1,d:1):1);")
        # Terminal splits match with equal lengths. Each tree has one unique
        # internal split. After unrooting, each unique internal split length is 2
        # because the two root-adjacent edges are collapsed into one edge.
        self.assertTrue(
            np.isclose(get_treedist_kf_branch_score(t1, t2), math.sqrt(8.0))
        )

    def test_kf_branch_score_ignores_root_placement(self):
        t1 = toytree.tree("(((a:1,b:1):2,c:3):4,d:5);")
        t2 = t1.root("a")
        self.assertTrue(np.isclose(get_treedist_kf_branch_score(t1, t2), 0.0))

    def test_kf_branch_score_requires_identical_tip_sets(self):
        t1 = toytree.tree("((a:1,b:1),(c:1,d:1));")
        t2 = toytree.tree("((a:1,b:1),(c:1,e:1));")
        with self.assertRaises(AssertionError):
            get_treedist_kf_branch_score(t1, t2)


if __name__ == "__main__":
    unittest.main()
