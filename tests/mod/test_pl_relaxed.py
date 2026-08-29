#!/usr/bin/env python

# ruff: noqa: D102

import numpy as np
from conftest import PytestCompat
from scipy import stats

from toytree.mod._src.penalized_pseudolikelihood.relaxed import (
    _relaxed_penalty,
    edges_make_ultrametric_relaxed,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    get_tree_with_uncorrelated_rates,
)
from toytree.utils import ToytreeError


class TestPenalizedPseudolikelihoodRelaxed(PytestCompat):
    """Regression tests for the ape::chronos Gamma-CDF penalty."""

    def test_relaxed_penalty_matches_definition(self):
        rates = np.array([0.5, 1.0, 2.0, 4.0])
        expected = np.sum(
            (
                np.arange(1, rates.size + 1) / rates.size
                - stats.gamma.cdf(np.sort(rates), a=rates.mean(), scale=1.0)
            )
            ** 2
        )
        self.assertTrue(np.isclose(_relaxed_penalty(rates), expected))

    def test_relaxed_penalty_depends_on_rate_units(self):
        rates = np.array([0.5, 1.0, 2.0, 4.0])
        self.assertFalse(
            np.isclose(_relaxed_penalty(rates), _relaxed_penalty(rates / 1e6))
        )

    def test_relaxed_fit_is_bound_and_reports_objective(self):
        tree = get_tree_with_uncorrelated_rates(ntips=10, seed=123)
        result = tree.mod.edges_make_ultrametric_relaxed(
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=5_000,
            max_fun=5_000,
            max_refine=5,
        )
        self.assertTrue(result["tree"].is_ultrametric())
        self.assertEqual(result["model"], "relaxed")
        self.assertEqual(result["penalty_model"], "chronos_gamma_cdf")
        self.assertFalse(result["scale_invariant"])
        self.assertNotIn("PHIIC", result)
        self.assertTrue(
            np.isclose(
                result["penalized_pseudologlik"],
                result["pseudologlik"] - result["lam"] * result["penalty"],
            )
        )

    def test_relaxed_rejects_nonpositive_lambda(self):
        tree = get_tree_with_uncorrelated_rates(ntips=8, seed=123)
        for value in (0.0, -0.1, np.nan, True):
            with self.assertRaises(ToytreeError):
                edges_make_ultrametric_relaxed(tree, lam=value)
