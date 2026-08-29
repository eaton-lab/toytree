# ruff: noqa: D102

import numpy as np
from conftest import PytestCompat

from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _uncorrelated_lognormal_penalty,
    edges_make_ultrametric_uncorrelated_lognormal,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    get_tree_with_uncorrelated_rates,
)
from toytree.utils import ToytreeError


class TestPenalizedPseudolikelihoodUncorrelated(PytestCompat):
    """Regression tests for centered log-rate dispersion."""

    def test_centered_log_rate_penalty_matches_definition(self):
        rates = np.array([0.5, 1.0, 2.0, 4.0])
        logs = np.log(rates)
        expected = np.sum((logs - logs.mean()) ** 2)
        self.assertTrue(np.isclose(_uncorrelated_lognormal_penalty(rates), expected))

    def test_penalty_is_invariant_to_rate_units(self):
        rates = np.array([0.5, 1.0, 2.0, 4.0])
        self.assertTrue(
            np.isclose(
                _uncorrelated_lognormal_penalty(rates),
                _uncorrelated_lognormal_penalty(rates / 1e6),
            )
        )

    def test_uncorrelated_fit_is_bound_and_reports_objective(self):
        tree = get_tree_with_uncorrelated_rates(
            ntips=10, mean=3, sigma=3, seed=123
        )
        result = tree.mod.edges_make_ultrametric_uncorrelated_lognormal(
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=5_000,
            max_fun=5_000,
            max_refine=5,
        )
        self.assertTrue(result["tree"].is_ultrametric())
        self.assertEqual(result["model"], "uncorrelated_lognormal")
        self.assertEqual(
            result["penalty_model"], "summed_centered_log_rate_dispersion"
        )
        self.assertTrue(result["scale_invariant"])
        self.assertEqual(result["observation_model"], "fractional_poisson")
        self.assertNotIn("PHIIC", result)
        self.assertTrue(
            np.isclose(
                result["penalized_pseudologlik"],
                result["pseudologlik"] - result["lam"] * result["penalty"],
            )
        )

    def test_legacy_direct_names_are_removed(self):
        tree = get_tree_with_uncorrelated_rates(ntips=8, seed=123)
        self.assertFalse(hasattr(tree.mod, "edges_make_ultrametric_pl_relaxed"))
        self.assertFalse(
            hasattr(tree.mod, "edges_make_ultrametric_pl_gamma_relaxed")
        )
        self.assertFalse(hasattr(tree.mod, "edges_make_ultrametric_uncorrelated"))

    def test_uncorrelated_rejects_nonpositive_lambda(self):
        tree = get_tree_with_uncorrelated_rates(ntips=8, seed=123)
        for value in (0.0, -0.1, np.nan, True):
            with self.assertRaises(ToytreeError):
                edges_make_ultrametric_uncorrelated_lognormal(tree, lam=value)
