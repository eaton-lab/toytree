from unittest.mock import patch

import numpy as np
from conftest import PytestCompat
from scipy.optimize import OptimizeResult

from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    _assess_correlated_solution_stability,
    _correlated_branch_pseudologlik,
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

    def test_near_equivalent_starts_with_different_ages_are_unstable(self):
        """Equivalent objectives cannot hide materially different chronograms."""
        starts = [
            {
                "start": 0,
                "objective": 10.0,
                "converged": True,
                "ages": np.array([0.0, 0.0, 1.0]),
            },
            {
                "start": 1,
                "objective": 10.000001,
                "converged": True,
                "ages": np.array([0.0, 0.0, 0.5]),
            },
        ]
        result = _assess_correlated_solution_stability(
            starts,
            best=starts[0],
            ntips=2,
        )
        self.assertTrue(result["stability_assessed"])
        self.assertFalse(result["solution_stable"])
        self.assertEqual(result["near_optimal_starts"], 2)
        self.assertTrue(np.isclose(result["max_near_optimal_age_difference"], 0.5))

    def test_warm_start_is_compared_with_an_independent_start(self):
        """A continuation seed augments rather than replaces initialization."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=0.5, seed=123)
        edges = np.asarray(tree.get_edges("idx"), dtype=int)
        ages = tree.get_node_data("height").to_numpy(dtype=float)
        times = ages[edges[:, 1]] - ages[edges[:, 0]]
        dists = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
        result = edges_make_ultrametric_correlated(
            tree,
            lam=1.0,
            calibrations={-1: float(ages[-1])},
            full=True,
            max_iter=500,
            max_fun=1_000,
            max_refine=2,
            nstarts=1,
            seed=17,
            _initial_rates=dists / times,
            _initial_ages=ages,
        )
        self.assertEqual(result["requested_nstarts"], 1)
        self.assertEqual(result["nstarts"], 2)
        self.assertEqual(
            {item["start_kind"] for item in result["starts"]},
            {"independent", "continuation"},
        )
        self.assertTrue(result["stability_assessed"])

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

    def test_multiplicative_gamma_loss_is_branch_scale_invariant(self):
        """Gamma working loss is unchanged by a common branch-rate scale."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=0.5, seed=19)
        edges = np.asarray(tree.get_edges("idx"), dtype=int)
        ages = tree.get_node_data("height").to_numpy(dtype=float)
        times = ages[edges[:, 1]] - ages[edges[:, 0]]
        rates = np.linspace(0.7, 1.3, tree.nedges)
        observed = times * rates * np.linspace(0.9, 1.1, tree.nedges)
        edata = np.column_stack([observed, np.zeros(tree.nedges)])
        parents = {int(child): idx for idx, (child, _) in enumerate(edges)}
        parent_edges = np.asarray(
            [parents.get(int(parent), -1) for _, parent in edges], dtype=int
        )
        baseline = _correlated_branch_pseudologlik(
            rates,
            ages,
            edges,
            edata,
            parent_edges,
            2.0,
            None,
            observation_loss="multiplicative_gamma",
        )
        scaled = _correlated_branch_pseudologlik(
            rates * 1e3,
            ages,
            edges,
            np.column_stack([observed * 1e3, np.zeros(tree.nedges)]),
            parent_edges,
            2.0,
            None,
            observation_loss="multiplicative_gamma",
        )
        self.assertTrue(np.isclose(baseline, scaled))

    def test_multiplicative_gamma_gradient_matches_central_difference(self):
        """The private Gamma working loss has a correct analytic gradient."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=0.5, seed=457)
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
            result = edges_make_ultrametric_correlated(
                tree,
                lam=3.0,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
                _observation_loss="multiplicative_gamma",
            )
        self.assertEqual(result["observation_loss"], "multiplicative_gamma")
        self.assertLess(scaled_errors[0], 1e-5)

    def test_multiplicative_gamma_rejects_zero_observation(self):
        """The validation-only Gamma loss never clips or hides zero branches."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=0.5, seed=22)
        tree = tree.set_node_data("dist", {0: 0.0}, inplace=False)
        with self.assertRaisesRegex(ValueError, "strictly positive"):
            edges_make_ultrametric_correlated(
                tree, lam=1.0, _observation_loss="multiplicative_gamma"
            )

    def test_iteration_limit_polish_is_retried_once(self):
        """An iteration-limited final polish resumes with a larger budget."""
        tree = get_tree_with_correlated_rates(ntips=6, mean=1.0, sigma=0.5, seed=23)
        calls = 0

        def fake_minimize(fun, x0, args, **kwargs):
            nonlocal calls
            calls += 1
            value, gradient = fun(np.asarray(x0), *args)
            limited = calls == 2
            return OptimizeResult(
                x=np.asarray(x0).copy(),
                fun=float(value),
                success=not limited,
                message=(
                    "STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT"
                    if limited
                    else "converged"
                ),
                nfev=1,
                nit=1,
                jac=np.asarray(gradient),
            )

        with patch(
            "toytree.mod._src.penalized_pseudolikelihood.correlated.minimize",
            side_effect=fake_minimize,
        ):
            result = edges_make_ultrametric_correlated(
                tree,
                lam=1.0,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
            )
        self.assertEqual(calls, 3)
        self.assertTrue(result["converged"])
        self.assertEqual(result["optimizer_retries"], 1)
