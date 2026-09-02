#!/usr/bin/env python

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
    return tree.mod.edges_make_ultrametric_discrete_gamma(
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


def test_scale_normalized_gamma_component_formula():
    """Gamma components use shape=CV^-2 and scale=mean/shape."""
    rates = np.array([0.5, 2.0])
    ages = np.array([0.0, 0.0, 0.0, 0.0, 0.4, 0.6, 1.0])
    edges = _tree().get_edges("idx")
    observed = np.array([0.21, 0.42, 0.51, 0.73, 0.31, 0.23])
    weights = np.array([0.35, 0.65])
    cv = 0.2
    shape = 1.0 / cv**2
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    means = rates[:, None] * times[None, :]
    components = (
        shape * np.log(observed)[None, :]
        - shape * observed[None, :] / means
        - gammaln(shape)
        - shape * np.log(means / shape)
    )
    expected = np.sum(
        np.logaddexp(
            np.log(weights[0]) + components[0],
            np.log(weights[1]) + components[1],
        )
    )
    observed_value = discrete._discrete_gamma_branch_pseudologlik(
        rates, ages, edges, observed, weights, branch_cv=cv
    )
    assert np.isclose(observed_value, expected, atol=1e-12)


@pytest.mark.parametrize("value", [True, 0, -0.1, np.inf, np.nan, "0.1"])
def test_branch_cv_validation(value):
    """Invalid branch CV values are rejected."""
    with pytest.raises(ToytreeError):
        _fit(_tree(), branch_cv=value)


def test_gamma_requires_strictly_positive_branches():
    """The multiplicative Gamma density rejects zero branches."""
    tree = toytree.tree("((a:0,b:0.4):0.3,(c:0.5,d:0.7):0.2);")
    with pytest.raises(ToytreeError, match="strictly positive"):
        _fit(tree)


def test_dispatcher_and_direct_api_return_identifiable_mixture():
    """Direct and dispatcher APIs expose an identifiable mixture."""
    direct = _fit(_tree())
    wrapped = _tree().mod.edges_make_ultrametric(
        method="discrete_gamma",
        ncategories=2,
        calibrations={-1: 1.0},
        full=True,
        max_iter=2_000,
        max_fun=4_000,
        max_refine=4,
        nstarts=2,
        seed=123,
    )
    for result in (direct, wrapped):
        assert result["model"] == "discrete_gamma"
        assert result["observation_model"] == "multiplicative_gamma"
        assert result["branch_cv"] == 0.1
        assert np.isclose(result["gamma_shape"], 100.0)
        assert result["input_branch_scale_invariant"] is True
        assert result["calibration_time_unit_invariant"] is True
        assert np.all(np.diff(result["rates"]) > 0)
        assert np.all(np.asarray(result["weights"]) > 0)
        assert np.isclose(np.sum(result["weights"]), 1.0)
        assert result["tree"].is_ultrametric()
        assert result["final_joint_converged"]
        assert "gradient_max_abs" in result
        assert "solution_stable" in result
    assert np.allclose(direct["rates"], wrapped["rates"])
    assert np.allclose(direct["weights"], wrapped["weights"])


def test_gamma_parallel_multistart_is_seed_reproducible():
    """Serial and parallel workers return the same seeded Gamma fit."""
    serial = _fit(_tree(), ncores=1)
    parallel = _fit(_tree(), ncores=2)
    assert serial["best_start"] == parallel["best_start"]
    assert np.isclose(serial["pseudologlik"], parallel["pseudologlik"])
    assert np.allclose(serial["rates"], parallel["rates"])
    assert np.allclose(serial["weights"], parallel["weights"])


def test_gamma_score_remains_finite_at_extreme_positive_scale():
    """Stable log scoring supports very small positive branch units."""
    tree = _tree()
    edges = tree.get_edges("idx")
    ages = np.array([0.0, 0.0, 0.0, 0.0, 0.4, 0.6, 1.0])
    value = discrete._discrete_gamma_branch_pseudologlik(
        np.array([1e-100, 3e-100]),
        ages,
        edges,
        np.full(tree.nedges, 1e-100),
        np.array([0.4, 0.6]),
        branch_cv=0.1,
    )
    assert np.isfinite(value)


def test_gamma_k1_is_supported_without_delegating_to_poisson_clock():
    """One Gamma category remains a Gamma observation model."""
    result = _tree().mod.edges_make_ultrametric_discrete_gamma(
        ncategories=1,
        calibrations={-1: 1.0},
        full=True,
        max_iter=1_000,
        max_fun=2_000,
        max_refine=2,
        nstarts=1,
        seed=3,
    )
    assert result["model"] == "discrete_gamma"
    assert result["observation_model"] == "multiplicative_gamma"
    assert len(result["rates"]) == 1
    assert result["weights"] == [1.0]


def test_joint_analytic_gradient_matches_central_difference():
    """The joint analytic gradient matches central differences."""
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
        "multiplicative_gamma",
        100.0,
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


def test_gamma_is_invariant_to_input_and_calibration_units():
    """Gamma fits are invariant to both supported unit rescalings."""
    baseline = _fit(_tree())

    input_scaled_tree = _tree()
    for node in input_scaled_tree[:-1]:
        node._dist *= 1e6
    input_scaled = _fit(input_scaled_tree)

    calibration_scaled = _fit(_tree(), calibration=1e6)

    base_ages = baseline["tree"].get_node_data("height").to_numpy()
    input_ages = input_scaled["tree"].get_node_data("height").to_numpy()
    calibration_ages = (
        calibration_scaled["tree"].get_node_data("height").to_numpy() / 1e6
    )
    assert np.allclose(input_ages, base_ages, atol=2e-4, rtol=2e-4)
    assert np.allclose(calibration_ages, base_ages, atol=2e-4, rtol=2e-4)
    assert np.allclose(
        np.asarray(input_scaled["rates"]) / 1e6,
        baseline["rates"],
        atol=2e-3,
        rtol=2e-3,
    )
    assert np.allclose(
        np.asarray(calibration_scaled["rates"]) * 1e6,
        baseline["rates"],
        atol=2e-3,
        rtol=2e-3,
    )
    assert np.allclose(input_scaled["weights"], baseline["weights"], atol=2e-3)
    assert np.allclose(calibration_scaled["weights"], baseline["weights"], atol=2e-3)


def test_finalized_solution_is_rescored_and_exposes_accumulated_diagnostics():
    """Returned scores and diagnostics describe the finalized fit."""
    result = _fit(_tree())
    ages = result["tree"].get_node_data("height").to_numpy()
    edges = _tree().get_edges("idx")
    observed = _tree().get_node_data("dist").to_numpy(dtype=float)[:-1]
    rescored = discrete._discrete_gamma_branch_pseudologlik(
        np.asarray(result["rates"]),
        ages,
        edges,
        observed,
        np.asarray(result["weights"]),
        branch_cv=result["branch_cv"],
    )
    assert np.isclose(result["pseudologlik"], rescored, atol=1e-9)
    assert result["nfev"] > 0
    assert result["nit"] >= 0
    assert result["refinement_cycles"] >= 0
    assert all("final_joint_converged" in start for start in result["starts"])


def test_iteration_limited_final_joint_fit_is_retried():
    """An effort-limited final joint optimization gets one retry."""
    tree = _tree()
    real = discrete._run_joint_fit
    calls = []

    def force_first_final_limit(x0, args, max_iter, max_fun):
        calls.append((max_iter, max_fun))
        result = real(x0, args, max_iter, max_fun)
        # Initial joint call is first; with max_refine=0 the second is final.
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
        result = tree.mod.edges_make_ultrametric_discrete_gamma(
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


def test_branch_cv_rejected_for_other_dispatcher_models():
    """branch_cv is model-specific in the dispatcher."""
    with pytest.raises(ToytreeError, match="only valid"):
        _tree().mod.edges_make_ultrametric(
            method="discrete",
            ncategories=2,
            branch_cv=0.2,
        )
