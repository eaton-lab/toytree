#!/usr/bin/env python

from unittest.mock import patch

import numpy as np
from conftest import PytestCompat
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_pseudolikelihood import clock
from toytree.mod._src.penalized_pseudolikelihood.discrete import (
    _pack_ordered_rates,
    _pack_simplex_weights,
    _unpack_ordered_rate_params,
    _unpack_simplex_logits,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    get_tree_with_categorical_rates,
    get_tree_with_correlated_rates,
    get_tree_with_uncorrelated_rates,
)
from toytree.utils import ToytreeError


class TestMakeUltrametricAPI(PytestCompat):
    """Tests for the user-facing ultrametric wrapper API."""

    def test_discrete_requires_one_scalar_category_count(self):
        """Discrete mode rejects candidate collections and invalid scalars."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=2, seed=123)
        for value in ([1, 2], (1, 2), True, 0, -1, 2.5):
            with self.assertRaises(ToytreeError):
                tree.mod.edges_make_ultrametric(method="discrete", ncategories=value)

    def test_discrete_parameter_transforms_are_valid_and_roundtrip(self):
        """Mixture transforms preserve valid ordered rates and simplex weights."""
        weights = np.array([0.2, 0.3, 0.5])
        restored_weights, log_weights = _unpack_simplex_logits(
            _pack_simplex_weights(weights)
        )
        self.assertTrue(np.allclose(restored_weights, weights))
        self.assertTrue(np.isclose(restored_weights.sum(), 1.0))
        self.assertTrue(np.all(np.isfinite(log_weights)))

        rates = np.array([0.2, 1.0, 3.0])
        restored_rates = _unpack_ordered_rate_params(_pack_ordered_rates(rates))
        self.assertTrue(np.all(np.diff(restored_rates) > 0.0))
        self.assertTrue(np.allclose(restored_rates, rates))

    def test_discrete_returns_ordered_rates_and_simplex_weights(self):
        """A fitted mixture exposes identifiable rates and valid weights."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=2, seed=123)
        result = tree.mod.edges_make_ultrametric(
            method="discrete",
            calibrations={-1: 1.0},
            ncategories=2,
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertEqual(result["model"], "discrete")
        self.assertTrue(np.all(np.diff(result["rates"]) > 0.0))
        self.assertTrue(np.all(np.asarray(result["weights"]) > 0.0))
        self.assertTrue(np.isclose(np.sum(result["weights"]), 1.0))
        self.assertNotIn("PHIIC", result)

    def test_removed_estimate_argument_raises_type_error(self):
        """The removed estimate keyword is not accepted by the wrapper."""
        tree = get_tree_with_uncorrelated_rates(ntips=10, seed=123)
        with self.assertRaises(TypeError):
            tree.mod.edges_make_ultrametric(
                method="uncorrelated_lognormal", lam=0.5, estimate=3
            )

    def test_old_uncorrelated_model_name_is_rejected(self):
        """The pre-release uncorrelated name is removed by the hard rename."""
        tree = get_tree_with_uncorrelated_rates(ntips=10, seed=123)
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(method="uncorrelated", lam=0.5)

    def test_penalized_models_require_explicit_lambda(self):
        """Penalized models do not silently choose a smoothing value."""
        tree = get_tree_with_uncorrelated_rates(ntips=10, seed=123)
        for method in ("relaxed", "uncorrelated_lognormal", "correlated"):
            with self.assertRaises(ToytreeError):
                tree.mod.edges_make_ultrametric(method=method)

    def test_irrelevant_model_arguments_are_rejected(self):
        """Model-specific arguments are errors outside their model."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(method="clock", ncategories=3)
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(method="clock", lam=0.5)
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(
                method="uncorrelated_lognormal", lam=0.5, ncategories=2
            )

    def test_independent_rate_models_report_objective_components(self):
        """Independent-rate outputs report consistent objective components."""
        tree = get_tree_with_uncorrelated_rates(ntips=10, seed=123)
        for method in ("relaxed", "uncorrelated_lognormal"):
            result = tree.mod.edges_make_ultrametric(
                method=method,
                calibrations={-1: 1.0},
                lam=0.5,
                full=True,
                max_iter=500,
                max_fun=500,
                max_refine=2,
            )
            self.assertTrue(
                np.isclose(
                    result["penalized_pseudologlik"],
                    result["pseudologlik"] - 0.5 * result["penalty"],
                )
            )
            self.assertNotIn("PHIIC", result)

    def test_correlated_reports_raw_and_penalized_scores(self):
        """Correlated output reports consistent objective components."""
        tree = get_tree_with_correlated_rates(
            ntips=10, mean=1.0, sigma=1.0, seed=123
        )
        result = tree.mod.edges_make_ultrametric(
            method="correlated",
            calibrations={-1: 1.0},
            lam=0.5,
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertTrue(
            np.isclose(
                result["penalized_pseudologlik"],
                result["pseudologlik"] - 0.5 * result["penalty"],
            )
        )
        self.assertNotIn("PHIIC", result)

    def test_invalid_calibrations_raise_before_fit(self):
        """Incompatible calibration domains fail before optimization."""
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        mrca = tree.get_mrca_node(0, 1).idx
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(
                method="clock",
                calibrations={-1: 1.0, mrca: (1.1, 1.2)},
            )

    def test_fully_fixed_two_tip_chronogram_skips_empty_age_block(self):
        """All models support a topology with no free internal ages."""
        tree = toytree.tree("(a:0.2,b:0.3);")
        configurations = (
            {"method": "clock"},
            {"method": "discrete", "ncategories": 2},
            {"method": "relaxed", "lam": 0.5},
            {"method": "uncorrelated_lognormal", "lam": 0.5},
            {"method": "correlated", "lam": 0.5},
        )
        for configuration in configurations:
            result = tree.mod.edges_make_ultrametric(
                calibrations={-1: 1.0},
                full=True,
                max_iter=100,
                max_fun=100,
                max_refine=2,
                **configuration,
            )
            self.assertTrue(result["tree"].is_ultrametric())

    def test_clock_recomputes_stats_from_repaired_ages(self):
        """Clock summaries use the finalized chronogram ages."""
        tree = toytree.tree("((a:1,b:1):1,c:1);")
        valid_ages, _ = clock._get_init_ages(tree, {tree.treenode.idx: (1.0, 1.0)})
        invalid_ages = valid_ages.copy()
        mrca = tree.get_mrca_node("a", "b").idx
        invalid_ages[mrca] = invalid_ages[tree.treenode.idx] + 5e-9

        with patch.object(clock, "_decode_age_params", return_value=invalid_ages):
            result = tree.mod.edges_make_ultrametric(
                method="clock",
                calibrations={-1: 1.0},
                full=True,
                max_iter=50,
                max_fun=50,
                max_refine=1,
            )

        returned_ages = result["tree"].get_node_data("height").values
        edges = tree.get_edges("idx")
        dists = tree.get_node_data("dist").values[:-1]
        edata = np.vstack([dists, gammaln(dists + 1.0)]).T
        expected = clock._poisson_branch_pseudologlik(
            result["rate"], returned_ages, edges, edata, valid_loglik=None
        )

        self.assertTrue(np.all(returned_ages[edges[:, 1]] > returned_ages[edges[:, 0]]))
        self.assertTrue(np.isfinite(result["pseudologlik"]))
        self.assertTrue(np.isclose(result["pseudologlik"], expected))
