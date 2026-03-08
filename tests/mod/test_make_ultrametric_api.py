#!/usr/bin/env python


from toytree.utils import ToytreeError
from toytree.mod._src.penalized_likelihood.pl_utils import (
    get_tree_with_categorical_rates,
    get_tree_with_uncorrelated_relaxed_rates,
)



from conftest import PytestCompat

class TestMakeUltrametricAPI(PytestCompat):
    def test_discrete_estimate_returns_best_and_search(self):
        tree = get_tree_with_categorical_rates(ntips=10, nrates=2, seed=123)
        res = tree.mod.edges_make_ultrametric(
            method="discrete",
            calibrations={-1: 1.0},
            estimate=4,
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertEqual(res["estimated_parameter"], "ncategories")
        self.assertIn("estimated_value", res)
        self.assertTrue(len(res["search"]) >= 1)
        self.assertTrue(res["tree"].is_ultrametric())

    def test_relaxed_estimate_returns_lam(self):
        tree = get_tree_with_uncorrelated_relaxed_rates(ntips=10, mean=3, sigma=3, seed=123)
        res = tree.mod.edges_make_ultrametric(
            method="relaxed",
            calibrations={-1: 1.0},
            estimate=3,
            full=True,
            max_iter=500,
            max_fun=500,
            max_refine=2,
        )
        self.assertEqual(res["estimated_parameter"], "lam")
        self.assertGreaterEqual(float(res["estimated_value"]), 0.0)
        self.assertLessEqual(float(res["estimated_value"]), 1.0)

    def test_estimate_invalid_for_clock(self):
        tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=123)
        with self.assertRaises(ToytreeError):
            tree.mod.edges_make_ultrametric(
                method="clock",
                calibrations={-1: 1.0},
                estimate=3,
                full=True,
            )


