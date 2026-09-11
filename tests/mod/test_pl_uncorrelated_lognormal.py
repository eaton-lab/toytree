# ruff: noqa: D102

from unittest.mock import patch

import numpy as np
from conftest import PytestCompat
from pl_test_helpers import (
    get_tree_with_uncorrelated_rates,
)
from scipy.optimize import OptimizeResult

import toytree
from toytree.mod._src.penalized_pseudolikelihood import (
    optimization as pl_optimization,
)
from toytree.mod._src.penalized_pseudolikelihood import (
    uncorrelated_lognormal as ucln,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _uncorrelated_lognormal_penalty,
    edges_make_ultrametric_uncorrelated_lognormal,
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
        tree = get_tree_with_uncorrelated_rates(ntips=10, mean=3, sigma=3, seed=123)
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
        self.assertEqual(result["penalty_model"], "summed_centered_log_rate_dispersion")
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
        self.assertFalse(hasattr(tree.mod, "edges_make_ultrametric_pl_gamma_relaxed"))
        self.assertFalse(hasattr(tree.mod, "edges_make_ultrametric_uncorrelated"))

    def test_uncorrelated_rejects_nonpositive_lambda(self):
        tree = get_tree_with_uncorrelated_rates(ntips=8, seed=123)
        for value in (0.0, -0.1, np.nan, True):
            with self.assertRaises(ToytreeError):
                edges_make_ultrametric_uncorrelated_lognormal(tree, lam=value)

    def test_boundary_clock_start_falls_back_to_interior_ages(self):
        """A boundary clock optimum cannot invalidate an otherwise valid fit."""
        tree = get_tree_with_uncorrelated_rates(ntips=6, seed=123)
        original = ucln._encode_age_params
        calls = 0

        def fail_clock_encode(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ToytreeError("clock start lies on an exact age boundary")
            return original(*args, **kwargs)

        with patch.object(ucln, "_encode_age_params", side_effect=fail_clock_encode):
            result = edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=1.0,
                calibrations={-1: 1.0},
                full=True,
                nstarts=1,
                max_iter=1_000,
                max_fun=2_000,
            )
        self.assertGreater(calls, 1)
        self.assertFalse(result["clock_warm_start_used"])
        self.assertTrue(result["converged"])
        self.assertTrue(result["tree"].is_ultrametric())

    def test_profiled_start_survives_joint_transform_saturation(self):
        """A valid direct-age result survives joint-transform saturation."""
        tree = get_tree_with_uncorrelated_rates(ntips=6, seed=124)
        original_decode = ucln._decode_age_params
        original_minimize = ucln.minimize_profiled_ages
        profile_started = False
        decode_calls = 0

        def track_profile(*args, **kwargs):
            nonlocal profile_started
            profile_started = True
            return original_minimize(*args, **kwargs)

        def decode_only_after_profile(*args, **kwargs):
            nonlocal decode_calls
            self.assertTrue(profile_started)
            decode_calls += 1
            if decode_calls == 1:
                raise ToytreeError("synthetic joint-transform saturation")
            return original_decode(*args, **kwargs)

        with (
            patch.object(
                ucln,
                "minimize_profiled_ages",
                side_effect=track_profile,
            ),
            patch.object(
                ucln,
                "_decode_age_params",
                side_effect=decode_only_after_profile,
            ),
        ):
            result = edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=1.0,
                calibrations={-1: 1.0},
                full=True,
                nstarts=1,
                max_iter=1_000,
                max_fun=2_000,
            )
        self.assertTrue(result["converged"])
        self.assertFalse(result["final_joint_converged"])
        self.assertIn("joint-polish age transform", result["optimizer_message"])
        self.assertTrue(result["tree"].is_ultrametric())
        self.assertTrue(profile_started)
        self.assertGreaterEqual(decode_calls, 1)

    def test_analytic_joint_gradient_matches_central_difference(self):
        """The UCLN joint gradient matches a numerical reference."""
        tree = get_tree_with_uncorrelated_rates(ntips=6, mean=1.0, sigma=0.5, seed=456)
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

        with patch.object(ucln, "minimize", side_effect=checking_minimize):
            edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=3.0,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
                nstarts=1,
            )
        self.assertLess(scaled_errors[0], 1e-5)

    def test_final_joint_polish_defines_convergence(self):
        """Initial success cannot mask a failed final joint optimization."""
        tree = get_tree_with_uncorrelated_rates(ntips=6, mean=1.0, sigma=0.5, seed=22)
        calls = 0

        def fake_minimize(fun, x0, args, **kwargs):
            nonlocal calls
            calls += 1
            value, gradient = fun(np.asarray(x0), *args)
            return OptimizeResult(
                x=np.asarray(x0).copy(),
                fun=float(value),
                success=calls == 1,
                message="initial converged" if calls == 1 else "joint failed",
                nfev=calls + 1,
                nit=calls,
                jac=np.asarray(gradient),
            )

        with (
            patch.object(ucln, "minimize", side_effect=fake_minimize),
            patch.object(pl_optimization, "minimize", side_effect=fake_minimize),
        ):
            result = edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=1.0,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
                nstarts=1,
            )
        self.assertEqual(calls, 2)
        self.assertFalse(result["converged"])
        self.assertFalse(result["final_joint_converged"])
        self.assertEqual(result["optimizer_message"], "joint failed")
        self.assertGreaterEqual(result["nfev"], 5)
        self.assertGreaterEqual(result["nit"], 3)

    def test_iteration_limit_polish_is_retried_once(self):
        """An effort-limited final UCLN polish resumes with a larger budget."""
        tree = get_tree_with_uncorrelated_rates(ntips=6, mean=1.0, sigma=0.5, seed=23)
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

        with (
            patch.object(ucln, "minimize", side_effect=fake_minimize),
            patch.object(pl_optimization, "minimize", side_effect=fake_minimize),
        ):
            result = edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=1.0,
                calibrations={-1: 1.0},
                full=True,
                max_refine=0,
                nstarts=1,
            )
        self.assertEqual(calls, 3)
        self.assertTrue(result["converged"])
        self.assertTrue(result["final_joint_converged"])
        self.assertEqual(result["optimizer_retries"], 1)

    def test_full_result_reports_stability_and_implied_sigma(self):
        """Full UCLN output exposes interpretable penalty and fit diagnostics."""
        tree = get_tree_with_uncorrelated_rates(ntips=8, mean=1.0, sigma=0.4, seed=321)
        result = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=2.0,
            calibrations={-1: 1.0},
            full=True,
            max_iter=2_000,
            max_fun=4_000,
            max_refine=2,
            nstarts=3,
            seed=19,
        )
        self.assertEqual(result["optimizer_strategy"], "profiled_rates_joint_polish")
        self.assertTrue(result["clock_warm_start_used"])
        self.assertTrue(result["interior_multistart_included"])
        self.assertTrue(np.isclose(result["implied_sigma_log"], 0.5))
        self.assertTrue(result["stability_assessed"])
        self.assertEqual(result["converged_starts"], 3)
        for key in (
            "nfev",
            "nit",
            "refinement_cycles",
            "final_joint_converged",
            "gradient_max_abs",
            "rate_gradient_max_abs",
            "profile_evaluations",
            "outer_profile_converged",
            "profile_rate_converged",
            "optimizer_retries",
        ):
            self.assertIn(key, result)
            self.assertIn(key, result["starts"][0])

    def test_final_result_is_rescored_from_returned_ages_and_rates(self):
        """Reported objective is exactly evaluated at the returned solution."""
        tree = get_tree_with_uncorrelated_rates(ntips=8, mean=1.0, sigma=0.4, seed=99)
        result = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=0.75,
            calibrations={-1: 1.0},
            full=True,
            max_iter=2_000,
            max_fun=4_000,
            max_refine=2,
            nstarts=2,
            seed=7,
        )
        self.assertTrue(
            np.isclose(
                -result["penalized_pseudologlik"],
                result["starts"][result["best_start"]]["objective"],
                rtol=1e-10,
                atol=1e-10,
            )
        )

    def test_calibration_time_unit_invariance(self):
        """Changing years to Myr rescales ages and rates but not the solution."""
        tree = toytree.tree("((a:0.2,b:0.4):0.3,(c:0.5,d:0.7):0.2);")
        mrca = tree.get_mrca_node("a", "b").idx
        kwargs = dict(
            lam=2.0,
            full=True,
            max_iter=3_000,
            max_fun=6_000,
            max_refine=3,
            nstarts=3,
            seed=13,
        )
        base = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            calibrations={-1: 2.0, mrca: (0.4, 1.4)},
            **kwargs,
        )
        scaled = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            calibrations={-1: 2e6, mrca: (0.4e6, 1.4e6)},
            **kwargs,
        )
        base_ages = base["tree"].get_node_data("height").to_numpy(dtype=float)
        scaled_ages = scaled["tree"].get_node_data("height").to_numpy(dtype=float)
        self.assertTrue(np.allclose(base_ages, scaled_ages / 1e6, atol=2e-5))
        self.assertTrue(
            np.allclose(np.asarray(base["rates"]) / 1e6, scaled["rates"], rtol=2e-5)
        )
        self.assertTrue(np.isclose(base["penalty"], scaled["penalty"], rtol=2e-5))

    def test_serial_and_parallel_multistarts_are_reproducible(self):
        """The same seeded starts give the same solution across worker counts."""
        tree = get_tree_with_uncorrelated_rates(ntips=8, mean=1.0, sigma=0.4, seed=101)
        kwargs = dict(
            lam=1.5,
            calibrations={-1: 1.0},
            full=True,
            max_iter=2_000,
            max_fun=4_000,
            max_refine=2,
            nstarts=3,
            seed=88,
        )
        serial = edges_make_ultrametric_uncorrelated_lognormal(tree, ncores=1, **kwargs)
        parallel = edges_make_ultrametric_uncorrelated_lognormal(
            tree, ncores=2, **kwargs
        )
        self.assertEqual(serial["best_start"], parallel["best_start"])
        self.assertTrue(
            np.isclose(
                serial["penalized_pseudologlik"],
                parallel["penalized_pseudologlik"],
                rtol=1e-10,
                atol=1e-10,
            )
        )
        self.assertTrue(np.allclose(serial["rates"], parallel["rates"]))

    def test_public_default_uses_four_starts(self):
        """The supported default reflects the pilot multistart evidence."""
        tree = get_tree_with_uncorrelated_rates(ntips=6, mean=1.0, sigma=0.4, seed=301)
        result = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=1.0,
            calibrations={-1: 1.0},
            full=True,
            max_iter=1_000,
            max_fun=2_000,
            max_refine=2,
            seed=4,
        )
        self.assertEqual(result["requested_nstarts"], 4)
        self.assertEqual(result["nstarts"], 4)

    def test_zero_observed_branch_remains_a_feasible_positive_mean(self):
        """Zero observations may approach, but do not cross, a rate boundary."""
        tree = toytree.tree("(a:0,b:1);")
        result = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=1.0,
            calibrations={-1: 1.0},
            full=True,
            max_iter=2_000,
            max_fun=4_000,
            max_refine=2,
            nstarts=2,
            seed=1,
        )
        self.assertTrue(result["converged"])
        self.assertTrue(np.isfinite(result["penalized_pseudologlik"]))
        self.assertTrue(np.all(np.asarray(result["rates"]) > 0.0))

    def test_conditional_rate_profile_has_unique_solution(self):
        """Widely separated starts reach the same fixed-age rate optimum."""
        tree = toytree.rtree.unittree(6, treeheight=1.0, seed=44)
        ages = tree.get_node_data("height").to_numpy(dtype=float)
        edges = tree.get_edges("idx")
        observed = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
        edata = np.vstack([observed, ucln.gammaln(observed + 1.0)]).T
        mask = np.ones(tree.nedges, dtype=bool)
        bounds = [(np.log(1e-12), np.log(1e12))] * tree.nedges
        valid = ucln._independent_branch_pseudologlik(
            np.ones(tree.nedges),
            ages,
            edges,
            edata,
            2.0,
            None,
            mask,
        )
        low = ucln._fit_profiled_ucln_rates(
            np.full(tree.nedges, -4.0),
            ages,
            bounds,
            edges,
            edata,
            2.0,
            valid,
            mask,
            2_000,
            4_000,
        )
        high = ucln._fit_profiled_ucln_rates(
            np.full(tree.nedges, 4.0),
            ages,
            bounds,
            edges,
            edata,
            2.0,
            valid,
            mask,
            2_000,
            4_000,
        )
        self.assertTrue(low["converged"])
        self.assertTrue(high["converged"])
        self.assertLess(low["projected_gradient_max_abs"], 1e-6)
        self.assertLess(high["projected_gradient_max_abs"], 1e-6)
        self.assertTrue(np.isclose(low["objective"], high["objective"], atol=1e-9))
        self.assertTrue(np.allclose(low["params"], high["params"], atol=1e-7))

    def test_direct_age_constraints_encode_every_edge(self):
        """The profiled age search constrains each free parent-child contrast."""
        tree = toytree.rtree.unittree(8, treeheight=1.0, seed=45)
        ages = tree.get_node_data("height").to_numpy(dtype=float)
        ages_idxs = np.arange(tree.ntips, tree.nnodes - 1, dtype=int)
        constraint = ucln.direct_age_linear_constraint(
            ages,
            ages_idxs,
            tree.get_edges("idx"),
        )
        self.assertIsInstance(constraint, pl_optimization.LinearConstraint)
        self.assertEqual(constraint.A.shape[1], ages_idxs.size)
        self.assertGreaterEqual(constraint.A.shape[0], ages_idxs.size)

    def test_zero_branch_diagnostics_do_not_floor_input(self):
        """Exact zeros retain an independent interior multistart candidate."""
        tree = toytree.tree("((a:0,b:1):0,c:1);")
        clock_options = {}

        def failed_clock_start(*args, **kwargs):
            clock_options.update(kwargs)
            return {"converged": False}

        with patch.object(
            ucln,
            "edges_make_ultrametric_clock",
            side_effect=failed_clock_start,
        ):
            result = edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=1.0,
                calibrations={-1: 1.0},
                full=True,
                max_iter=2_000,
                max_fun=4_000,
                nstarts=2,
                seed=2,
            )
        self.assertEqual(clock_options["max_iter"], 200)
        self.assertEqual(clock_options["max_fun"], 500)
        self.assertEqual(clock_options["_retry_multiplier"], 1)
        self.assertEqual(result["zero_length_branch_count"], 2)
        self.assertEqual(result["zero_length_terminal_branch_count"], 1)
        self.assertEqual(result["zero_length_internal_branch_count"], 1)
        self.assertEqual(result["observed_branch_lengths"].count(0.0), 2)
        self.assertEqual(result["minimum_positive_branch_length"], 1.0)
        self.assertEqual(result["minimum_positive_to_median_ratio"], 1.0)
        self.assertTrue(result["interior_multistart_included"])

    def test_single_best_start_is_not_reported_as_replicated(self):
        """One start cannot establish independent basin replication."""
        tree = toytree.rtree.unittree(6, treeheight=1.0, seed=46)
        one = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=2.0,
            calibrations={-1: 1.0},
            full=True,
            nstarts=1,
            seed=3,
        )
        two = edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=2.0,
            calibrations={-1: 1.0},
            full=True,
            nstarts=2,
            seed=3,
        )
        self.assertFalse(one["best_basin_replicated"])
        self.assertEqual(one["best_basin_replicates"], 1)
        self.assertTrue(two["best_basin_replicated"])
        self.assertGreaterEqual(two["best_basin_replicates"], 2)
        self.assertTrue(two["solution_stable"])

    def test_single_best_basin_triggers_adaptive_confirmation(self):
        """A singly observed winner receives one independent confirmation."""
        tree = toytree.rtree.unittree(6, treeheight=1.0, seed=47)
        original = ucln.assess_solution_stability
        calls = 0

        def force_unreplicated_first_call(*args, **kwargs):
            nonlocal calls
            calls += 1
            result = original(*args, **kwargs)
            if calls == 1:
                result["near_optimal_starts"] = 1
            return result

        with patch.object(
            ucln,
            "assess_solution_stability",
            side_effect=force_unreplicated_first_call,
        ):
            result = edges_make_ultrametric_uncorrelated_lognormal(
                tree,
                lam=2.0,
                calibrations={-1: 1.0},
                full=True,
                nstarts=2,
                seed=5,
            )
        self.assertTrue(result["basin_confirmation_run"])
        self.assertEqual(result["evaluated_starts"], 3)
        self.assertEqual(len(result["starts"]), 3)
