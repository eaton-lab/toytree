#!/usr/bin/env python
# ruff: noqa: D103

from unittest.mock import patch

import numpy as np
import pytest
from scipy.optimize import OptimizeResult
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_pseudolikelihood import discrete
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    _encode_age_params,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _normalize_calibrations,
)
from toytree.utils import ToytreeError


def _tree():
    return toytree.tree("((a:0.21,b:0.42):0.31,(c:0.51,d:0.73):0.23);")


def _fit(tree, calibration=1.0, **kwargs):
    return tree.mod.edges_make_ultrametric_discrete(
        ncategories=2,
        calibrations={-1: calibration},
        full=True,
        max_iter=2_000,
        max_fun=4_000,
        max_refine=4,
        nstarts=2,
        seed=123,
        **kwargs,
    )


def test_public_discrete_fitter_returns_valid_diagnostics():
    result = _fit(_tree())
    assert result["model"] == "discrete"
    assert result["observation_model"] == "fractional_poisson"
    assert result["calibration_time_unit_invariant"] is True
    assert result["input_branch_scale_invariant"] is False
    assert np.all(np.diff(result["rates"]) > 0)
    assert np.all(np.asarray(result["weights"]) > 0)
    assert np.isclose(np.sum(result["weights"]), 1.0)
    assert result["tree"].is_ultrametric()
    assert result["final_joint_converged"]
    assert result["requested_ncategories"] == 2
    assert result["effective_ncategories"] in {1, 2}
    assert "mixture_identified" in result
    assert "boundary_reasons" in result
    assert "solution_stable" in result


def test_parallel_multistart_is_seed_reproducible():
    serial = _fit(_tree(), ncores=1)
    parallel = _fit(_tree(), ncores=2)
    assert serial["best_start"] == parallel["best_start"]
    assert np.isclose(serial["pseudologlik"], parallel["pseudologlik"])
    assert np.allclose(serial["rates"], parallel["rates"])
    assert np.allclose(serial["weights"], parallel["weights"])


def test_one_category_delegates_to_clock_likelihood():
    result = _tree().mod.edges_make_ultrametric_discrete(
        ncategories=1,
        calibrations={-1: 1.0},
        full=True,
        nstarts=1,
        seed=3,
    )
    assert result["model"] == "discrete"
    assert result["observation_model"] == "fractional_poisson"
    assert result["rates"] == [pytest.approx(result["rates"][0])]
    assert result["weights"] == [1.0]


def test_joint_analytic_gradient_matches_central_difference():
    tree = _tree()
    calibrations = _normalize_calibrations(tree, {-1: 1.0})
    ages, _ = _get_init_ages(tree, calibrations)
    _, bounds_by_idx = _get_params_bounds(tree, calibrations)
    edges = tree.get_edges("idx")
    observed = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    edata = np.vstack([observed, gammaln(observed + 1.0)]).T
    ages_idxs = np.array(sorted(bounds_by_idx), dtype=int)
    ages_bounds = [bounds_by_idx[idx] for idx in ages_idxs]
    children = _get_children_map_from_edges(edges)
    age_params = _encode_age_params(ages, ages_idxs, ages_bounds, children)
    rates = np.quantile(
        observed / (ages[edges[:, 1]] - ages[edges[:, 0]]), [0.25, 0.75]
    )
    params = np.concatenate(
        (
            discrete._pack_ordered_rates(rates),
            age_params,
            discrete._pack_simplex_weights(np.array([0.4, 0.6])),
        )
    )
    args = (
        ages,
        ages_idxs,
        ages_bounds,
        children,
        edges,
        edata,
        np.ones(tree.nedges, dtype=bool),
        2,
        -10.0,
    )
    _, analytic = discrete._mixture_objective_with_gradient(params, *args)
    numerical = np.empty_like(params)
    for idx in range(params.size):
        step = 1e-6 * max(1.0, abs(params[idx]))
        delta = np.zeros_like(params)
        delta[idx] = step
        upper = discrete._mixture_objective_with_gradient(params + delta, *args)[0]
        lower = discrete._mixture_objective_with_gradient(params - delta, *args)[0]
        numerical[idx] = (upper - lower) / (2.0 * step)
    scale = np.maximum(1.0, np.maximum(abs(analytic), abs(numerical)))
    assert np.max(abs(analytic - numerical) / scale) < 2e-5


def test_calibration_time_unit_invariance():
    baseline = _fit(_tree())
    scaled = _fit(_tree(), calibration=1e6)
    base_ages = baseline["tree"].get_node_data("height").to_numpy()
    scaled_ages = scaled["tree"].get_node_data("height").to_numpy() / 1e6
    assert np.allclose(scaled_ages, base_ages, atol=2e-4, rtol=2e-4)
    assert np.allclose(
        np.asarray(scaled["rates"]) * 1e6,
        baseline["rates"],
        atol=2e-3,
        rtol=2e-3,
    )
    assert np.allclose(scaled["weights"], baseline["weights"], atol=2e-3)


def test_finalized_solution_is_rescored_and_exposes_diagnostics():
    result = _fit(_tree())
    ages = result["tree"].get_node_data("height").to_numpy()
    edges = _tree().get_edges("idx")
    observed = _tree().get_node_data("dist").to_numpy(dtype=float)[:-1]
    edata = np.column_stack((observed, gammaln(observed + 1.0)))
    rescored = discrete._discrete_branch_pseudologlik(
        np.asarray(result["rates"]),
        ages,
        edges,
        edata,
        np.asarray(result["weights"]),
        None,
    )
    assert np.isclose(result["pseudologlik"], rescored, atol=1e-9)
    assert result["nfev"] > 0
    assert result["nit"] >= 0
    assert all("final_joint_converged" in start for start in result["starts"])


def test_iteration_limited_final_joint_fit_is_retried():
    tree = _tree()
    real = discrete._run_joint_fit
    calls = []

    def force_first_final_limit(x0, args, max_iter, max_fun):
        calls.append((max_iter, max_fun))
        result = real(x0, args, max_iter, max_fun)
        if len(calls) == 2:
            return OptimizeResult(
                x=result.x,
                fun=result.fun,
                jac=result.jac,
                success=False,
                message="STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT",
                nfev=result.nfev,
                nit=result.nit,
            )
        return result

    with patch.object(discrete, "_run_joint_fit", side_effect=force_first_final_limit):
        result = tree.mod.edges_make_ultrametric_discrete(
            ncategories=2,
            calibrations={-1: 1.0},
            full=True,
            max_iter=500,
            max_fun=1_000,
            max_refine=0,
            nstarts=1,
            seed=4,
        )
    assert result["optimizer_retries"] == 1
    assert len(calls) == 3
    assert calls[-1] == (2_000, 4_000)


def test_discrete_gamma_is_removed():
    assert not hasattr(toytree.mod, "edges_make_ultrametric_discrete_gamma")
    assert not hasattr(discrete, "_edges_make_ultrametric_discrete_gamma_experimental")
    with pytest.raises(ToytreeError, match="invalid method"):
        _tree().mod.edges_make_ultrametric(method="discrete_gamma", ncategories=2)


def test_em_initializer_does_not_decrease_fixed_age_likelihood():
    tree = _tree()
    edges = tree.get_edges("idx")
    ages = np.array([0.0, 0.0, 0.0, 0.0, 0.4, 0.6, 1.0])
    observed = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    edata = np.column_stack((observed, gammaln(observed + 1.0)))
    rates = np.array([0.4, 2.4])
    weights = np.array([0.8, 0.2])
    mask = np.ones(tree.nedges, dtype=bool)
    initial = discrete._discrete_branch_pseudologlik(
        rates, ages, edges, edata, weights, None, mask
    )
    fitted_rates, fitted_weights, iterations, fitted = discrete._em_initialize_mixture(
        rates, weights, ages, edges, edata, mask
    )
    assert iterations > 0
    assert fitted >= initial - 1e-10
    assert np.all(np.diff(fitted_rates) >= 0.0)
    assert np.all(fitted_weights > 0.0)
    assert np.isclose(fitted_weights.sum(), 1.0)


def test_projected_gradient_recognizes_outward_boundary_directions():
    params = np.array([-30.0, 0.0, 30.0, -30.0, 30.0])
    gradient = np.array([2.0, 3.0, -4.0, -5.0, 6.0])
    projected = discrete._projected_gradient(params, gradient)
    assert np.array_equal(projected, np.array([0.0, 3.0, 0.0, -5.0, 6.0]))


def test_boundary_diagnostics_report_effective_category_collapse():
    diagnostics = discrete._mixture_boundary_diagnostics(
        np.array([1.0, 1.0 + 1e-6, 2.0]),
        np.array([0.5, 1e-9, 0.5 - 1e-9]),
        np.array([0.0, 0.5, 1.0]),
        np.array([[0, 2], [1, 2]], dtype=int),
    )
    assert diagnostics["boundary_solution"]
    assert not diagnostics["mixture_identified"]
    assert diagnostics["effective_ncategories"] == 2
    assert "near_zero_weight" in diagnostics["boundary_reasons"]
    assert "coincident_rates" in diagnostics["boundary_reasons"]


def test_multistart_selection_prefers_stationary_equivalent_fit():
    stationary = {"objective": 10.0, "converged": True}
    nonstationary = {"objective": 9.99995, "converged": False}
    selected = discrete._select_best_discrete_start([nonstationary, stationary])
    assert selected is stationary
    assert not selected["unresolved_better_start"]
