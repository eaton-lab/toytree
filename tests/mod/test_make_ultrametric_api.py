#!/usr/bin/env python

from unittest.mock import patch

import numpy as np
from conftest import PytestCompat
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_likelihood import pl_clock
from toytree.mod._src.penalized_likelihood.pl_utils import (
    get_tree_with_categorical_rates,
    get_tree_with_correlated_relaxed_rates,
    get_tree_with_uncorrelated_relaxed_rates,
)
from toytree.utils import ToytreeError


class TestMakeUltrametricAPI(PytestCompat):
    """Tests for the user-facing ultrametric wrapper API."""

    def test_discrete_candidate_list_returns_best_and_search(self):
        """Discrete candidate lists should expose PHIIC search metadata."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=2, seed=123)
        res = tree.mod.edges_make_ultrametric(
            method="discrete",
            calibrations={-1: 1.0},
            ncategories=[1, 2, 4],
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertEqual(res["selection_criterion"], "PHIIC")
        self.assertIn("selected_ncategories", res)
        self.assertEqual([i["candidate"] for i in res["search"]], [1, 2, 4])
        self.assertTrue(res["tree"].is_ultrametric())

    def test_removed_estimate_argument_raises_type_error(self):
        """Legacy estimate argument should no longer be accepted."""
        tree = get_tree_with_uncorrelated_relaxed_rates(
            ntips=10, mean=3, sigma=3, seed=123
        )
        with self.assertRaises(TypeError):
            tree.mod.edges_make_ultrametric(
                method="relaxed",
                calibrations={-1: 1.0},
                estimate=3,
                full=True,
            )

    def test_relaxed_rejects_ncategories_candidate_list(self):
        """Only discrete mode should accept multiple ncategory candidates."""
        tree = get_tree_with_uncorrelated_relaxed_rates(
            ntips=10, mean=3, sigma=3, seed=123
        )
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(
                method="relaxed",
                calibrations={-1: 1.0},
                ncategories=[1, 2],
                full=True,
            )

    def test_relaxed_reports_raw_and_penalized_scores(self):
        """Relaxed fits should report score components explicitly."""
        tree = get_tree_with_uncorrelated_relaxed_rates(
            ntips=10, mean=3, sigma=3, seed=123
        )
        res = tree.mod.edges_make_ultrametric(
            method="relaxed",
            calibrations={-1: 1.0},
            lam=0.5,
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertGreaterEqual(float(res["loglik"]), float(res["penalized_loglik"]))
        self.assertTrue(
            np.isclose(
                float(res["PHIIC"]),
                -2 * float(res["loglik"])
                + 2 * int(res["k"])
                + 0.5 * float(res["penalty"]),
            )
        )

    def test_correlated_reports_raw_and_penalized_scores(self):
        """Correlated fits should report score components explicitly."""
        tree = get_tree_with_correlated_relaxed_rates(
            ntips=10, mean=1.0, sigma=1.0, seed=123
        )
        res = tree.mod.edges_make_ultrametric(
            method="correlated",
            calibrations={-1: 1.0},
            lam=0.5,
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertGreaterEqual(float(res["loglik"]), float(res["penalized_loglik"]))
        self.assertTrue(
            np.isclose(
                float(res["PHIIC"]),
                -2 * float(res["loglik"])
                + 2 * int(res["k"])
                + 0.5 * float(res["penalty"]),
            )
        )

    def test_clock_ignores_scalar_ncategories(self):
        """Non-discrete modes should still ignore scalar ncategory values."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        res = tree.mod.edges_make_ultrametric(
            method="clock",
            calibrations={-1: 1.0},
            ncategories=3,
            full=True,
        )
        self.assertTrue(res["tree"].is_ultrametric())

    def test_invalid_calibrations_raise_before_fit(self):
        """Incompatible calibrated ages should fail before optimization."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        mrca = tree.get_mrca_node(0, 1).idx
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(
                method="clock",
                calibrations={-1: 1.0, mrca: (1.1, 1.2)},
            )

    def test_clock_recomputes_stats_from_repaired_ages(self):
        """Clock summaries should match the repaired output tree ages."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        valid_ages, _ = pl_clock._get_init_ages(tree, {tree.treenode.idx: (1.0, 1.0)})
        invalid_ages = valid_ages.copy()
        mrca = tree.get_mrca_node("a", "b").idx
        invalid_ages[mrca] = invalid_ages[tree.treenode.idx] + 5e-9

        with patch.object(pl_clock, "_decode_age_params", return_value=invalid_ages):
            res = tree.mod.edges_make_ultrametric(
                method="clock",
                calibrations={-1: 1.0},
                full=True,
                max_iter=50,
                max_fun=50,
                max_refine=1,
            )

        returned_ages = res["tree"].get_node_data("height").values
        edges = tree.get_edges("idx")
        dists = tree.get_node_data("dist").values[:-1]
        edata = np.vstack([dists, gammaln(dists + 1.0)]).T
        expected = pl_clock.log_likelihood_poisson(
            res["rate"],
            returned_ages,
            edges,
            edata,
            valid_loglik=None,
        )

        self.assertTrue(np.all(returned_ages[edges[:, 1]] > returned_ages[edges[:, 0]]))
        self.assertTrue(np.isfinite(res["loglik"]))
        self.assertTrue(np.isclose(res["loglik"], expected))
