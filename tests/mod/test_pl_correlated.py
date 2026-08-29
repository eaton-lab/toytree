from unittest.mock import patch

import numpy as np
from conftest import PytestCompat
from scipy.optimize import OptimizeResult

from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    _correlated_penalty,
    edges_make_ultrametric_correlated,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    get_tree_with_correlated_rates,
)
from toytree.utils import ToytreeError


class TestPenalizedLikelihoodCorrelated(PytestCompat):
    """Regression tests for the corrected correlated-rate model."""

    def test_basal_edges_contribute_to_penalty(self):
        """Basal rates are shrunk toward a profiled root log-rate."""
        rates = np.array([1.0, 4.0, 1.0, 4.0])
        parent_edges = np.array([-1, -1, 0, 1])
        expected = 2.0 * np.log(2.0) ** 2
        self.assertTrue(np.isclose(_correlated_penalty(rates, parent_edges), expected))

    def test_penalty_is_invariant_to_rate_units(self):
        """A common rate multiplier must not change log-rate roughness."""
        rates = np.array([1.0, 4.0, 2.0, 8.0])
        parent_edges = np.array([-1, -1, 0, 1])
        observed = _correlated_penalty(rates, parent_edges)
        scaled = _correlated_penalty(rates * 1e-6, parent_edges)
        self.assertTrue(np.isclose(observed, scaled))

    def test_correlated_pl_makes_ultrametric(self):
        """The fit returns an ultrametric tree and consistent metadata."""
        tree = get_tree_with_correlated_rates(ntips=12, mean=3, sigma=2, seed=123)
        result = edges_make_ultrametric_correlated(
            tree,
            lam=0.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=2_000,
            max_fun=2_000,
            max_refine=4,
        )
        new_tree = result["tree"]
        heights = new_tree.get_node_data("height").values
        tip_heights = heights[: new_tree.ntips]
        self.assertTrue(np.allclose(tip_heights, tip_heights[0]))
        self.assertEqual(result["model"], "correlated")
        self.assertEqual(result["penalty_model"], "summed_log_rate_autocorrelation")
        self.assertTrue(result["scale_invariant"])
        self.assertNotIn("PHIIC", result)
        self.assertTrue(
            np.isclose(
                result["penalized_pseudologlik"],
                result["pseudologlik"] - result["lam"] * result["penalty"],
            )
        )

    def test_correlated_rejects_invalid_lambda_directly(self):
        """The direct public function validates its own lambda argument."""
        tree = get_tree_with_correlated_rates(ntips=8, mean=1.0, sigma=1.0, seed=123)
        for value in (0.0, -0.1, np.nan, True):
            with self.assertRaises(ToytreeError):
                edges_make_ultrametric_correlated(tree, lam=value)

    def test_final_joint_polish_defines_convergence(self):
        """A successful block/initial fit cannot mask failed joint convergence."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=1.0, seed=123)
        calls = 0

        def fake_minimize(fun, x0, args, **kwargs):
            nonlocal calls
            calls += 1
            value = fun(np.asarray(x0), *args)
            if isinstance(value, tuple):
                value = value[0]
            return OptimizeResult(
                x=np.asarray(x0).copy(),
                fun=float(value),
                success=calls == 1,
                message="initial converged" if calls == 1 else "joint failed",
                nfev=calls + 1,
                nit=calls,
                jac=np.zeros_like(x0, dtype=float),
            )

        with patch(
            "toytree.mod._src.penalized_pseudolikelihood.correlated.minimize",
            side_effect=fake_minimize,
        ):
            result = edges_make_ultrametric_correlated(
                tree,
                lam=0.5,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
            )

        self.assertEqual(calls, 2)
        self.assertFalse(result["converged"])
        self.assertFalse(result["final_joint_converged"])
        self.assertEqual(result["optimizer_message"], "joint failed")
        self.assertEqual(result["nfev"], 5)
        self.assertEqual(result["nit"], 3)
        self.assertEqual(result["refinement_cycles"], 0)
        self.assertEqual(result["gradient_max_abs"], 0.0)

    def test_correlated_full_result_exposes_joint_diagnostics(self):
        """Full results report aggregate effort and final-joint diagnostics."""
        tree = get_tree_with_correlated_rates(ntips=8, mean=1.0, sigma=1.0, seed=321)
        result = edges_make_ultrametric_correlated(
            tree,
            lam=1.0,
            calibrations={-1: 1.0},
            full=True,
            max_iter=1_000,
            max_fun=2_000,
            max_refine=2,
        )
        for key in (
            "nfev",
            "nit",
            "refinement_cycles",
            "final_joint_converged",
            "gradient_max_abs",
        ):
            self.assertIn(key, result)
            self.assertIn(key, result["starts"][0])
        self.assertGreaterEqual(result["nfev"], result["starts"][0]["nfev"])

    def test_analytic_joint_gradient_matches_central_difference(self):
        """The optimized joint gradient matches a numerical reference."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=1.0, seed=456)
        scaled_errors = []

        def checking_minimize(fun, x0, args, **kwargs):
            x0 = np.asarray(x0, dtype=float)
            value, gradient = fun(x0, *args)
            if not scaled_errors:
                epsilon = 1e-6
                numerical = np.empty_like(x0)
                for idx in range(x0.size):
                    delta = np.zeros_like(x0)
                    delta[idx] = epsilon
                    upper = fun(x0 + delta, *args)[0]
                    lower = fun(x0 - delta, *args)[0]
                    numerical[idx] = (upper - lower) / (2.0 * epsilon)
                scale = np.maximum(1.0, np.maximum(abs(gradient), abs(numerical)))
                scaled_errors.append(float(np.max(abs(gradient - numerical) / scale)))
            return OptimizeResult(
                x=x0.copy(),
                fun=float(value),
                success=True,
                message="converged",
                nfev=1,
                nit=0,
                jac=np.asarray(gradient),
            )

        with patch(
            "toytree.mod._src.penalized_pseudolikelihood.correlated.minimize",
            side_effect=checking_minimize,
        ):
            edges_make_ultrametric_correlated(
                tree,
                lam=3.0,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
            )
        self.assertLess(scaled_errors[0], 1e-5)
