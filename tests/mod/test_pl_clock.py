# ruff: noqa: D103

from unittest.mock import patch

import numpy as np
from scipy.optimize import OptimizeResult
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_pseudolikelihood import clock
from toytree.mod._src.penalized_pseudolikelihood.optimization import (
    assess_solution_stability,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    _encode_age_params,
    _get_children_map_from_edges,
    _get_init_ages,
    _get_params_bounds,
    _normalize_calibrations,
    get_tree_with_categorical_rates,
)


def _profiled_objective_inputs(tree, calibrations):
    calibrations = _normalize_calibrations(tree, calibrations)
    ages_init, _ = _get_init_ages(tree, calibrations)
    rate_bounds, age_bounds = _get_params_bounds(tree, calibrations)
    age_idxs = np.array(sorted(age_bounds))
    age_bounds = [age_bounds[idx] for idx in age_idxs]
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    children_map = _get_children_map_from_edges(edges)
    age_params = _encode_age_params(
        ages_init,
        age_idxs,
        age_bounds,
        children_map,
        dist_floor=clock.DIST_FLOOR,
    )
    observed = tree.get_node_data("dist").to_numpy(dtype=float)[:-1]
    edata = np.column_stack([observed, gammaln(observed + 1.0)])
    mask = np.ones(tree.nedges, dtype=bool)
    rate_bound = rate_bounds[0]
    rate = clock._profile_clock_rate(ages_init, edges, observed, mask, rate_bound)
    valid_loglik = clock._poisson_branch_pseudologlik(
        rate, ages_init, edges, edata, None, mask
    )
    args = (
        ages_init,
        age_idxs,
        age_bounds,
        children_map,
        edges,
        edata,
        rate_bound,
        valid_loglik,
        mask,
    )
    return age_params, args


def test_profile_clock_rate_is_conditional_mle_and_respects_mask():
    ages = np.array([0.0, 0.0, 2.0])
    edges = np.array([[0, 2], [1, 2]], dtype=int)
    observed = np.array([2.0, 6.0])
    bounds = (1e-8, 1e8)
    both = clock._profile_clock_rate(
        ages, edges, observed, np.array([True, True]), bounds
    )
    first = clock._profile_clock_rate(
        ages, edges, observed, np.array([True, False]), bounds
    )
    zeros = clock._profile_clock_rate(
        ages, edges, np.zeros(2), np.array([True, True]), bounds
    )
    assert np.isclose(both, 2.0)
    assert np.isclose(first, 1.0)
    assert zeros == bounds[0]


def test_profiled_clock_gradient_matches_central_difference():
    tree = get_tree_with_categorical_rates(ntips=8, nrates=1, seed=456)
    params, args = _profiled_objective_inputs(tree, {-1: 2.0})
    params = params + np.linspace(-0.08, 0.08, params.size)
    _, gradient = clock.objective_clock_profiled_with_gradient(params, *args)
    epsilon = 1e-6
    numerical = np.empty_like(params)
    for idx in range(params.size):
        delta = np.zeros_like(params)
        delta[idx] = epsilon
        upper = clock.objective_clock_profiled_with_gradient(params + delta, *args)[0]
        lower = clock.objective_clock_profiled_with_gradient(params - delta, *args)[0]
        numerical[idx] = (upper - lower) / (2.0 * epsilon)
    scale = np.maximum(1.0, np.maximum(abs(gradient), abs(numerical)))
    assert np.max(abs(gradient - numerical) / scale) < 1e-5


def test_fully_fixed_clock_profiles_rate_without_optimizer():
    tree = toytree.tree("(a:0.2,b:0.3);")
    with patch.object(clock, "minimize", side_effect=AssertionError("not called")):
        result = tree.mod.edges_make_ultrametric_clock(
            calibrations={-1: 1.0}, full=True, nstarts=3
        )
    assert result["converged"]
    assert result["rate_profiled"]
    assert result["requested_nstarts"] == 3
    assert result["nstarts"] == 1
    assert result["nfev"] == 1
    assert np.isclose(result["rate"], 0.25)


def test_clock_retries_iteration_limited_profile_fit():
    tree = get_tree_with_categorical_rates(ntips=6, nrates=1, seed=123)
    calls = 0

    def fake_minimize(fun, x0, args, **kwargs):
        nonlocal calls
        calls += 1
        value, gradient = fun(np.asarray(x0), *args)
        return OptimizeResult(
            x=np.asarray(x0).copy(),
            fun=float(value),
            success=calls == 2,
            message=(
                "STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT"
                if calls == 1
                else "converged"
            ),
            nfev=calls + 1,
            nit=calls,
            jac=np.asarray(gradient),
        )

    with patch.object(clock, "minimize", side_effect=fake_minimize):
        result = tree.mod.edges_make_ultrametric_clock(
            calibrations={-1: 1.0},
            full=True,
            max_refine=20,
        )
    assert calls == 2
    assert result["converged"]
    assert result["final_joint_converged"]
    assert result["optimizer_retries"] == 1
    assert result["nfev"] == 5
    assert result["nit"] == 3
    assert result["refinement_cycles"] == 0
    assert result["max_refine_used"] == 0


def test_clock_reports_multistart_chronogram_stability():
    tree = get_tree_with_categorical_rates(ntips=10, nrates=1, seed=321)
    result = tree.mod.edges_make_ultrametric_clock(
        calibrations={-1: 1.0},
        full=True,
        max_iter=2_000,
        max_fun=4_000,
        nstarts=3,
        seed=19,
    )
    assert result["optimizer_strategy"] == "profiled_clock_rate"
    assert result["stability_assessed"]
    assert result["solution_stable"]
    assert result["converged_starts"] == 3
    for key in (
        "nfev",
        "nit",
        "final_joint_converged",
        "gradient_max_abs",
        "optimizer_retries",
    ):
        assert key in result
        assert key in result["starts"][0]


def test_generic_stability_detects_different_near_optimal_clock_ages():
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
    result = assess_solution_stability(starts, starts[0], ntips=2)
    assert result["stability_assessed"]
    assert not result["solution_stable"]
    assert np.isclose(result["max_near_optimal_age_difference"], 0.5)


def test_profiled_clock_is_calibration_time_unit_invariant():
    tree = toytree.tree("((a:0.2,b:0.4):0.3,(c:0.5,d:0.7):0.2);")
    mrca = tree.get_mrca_node("a", "b").idx
    base = tree.mod.edges_make_ultrametric_clock(
        calibrations={-1: 2.0, mrca: (0.4, 1.4)}, full=True
    )
    scaled = tree.mod.edges_make_ultrametric_clock(
        calibrations={-1: 2e6, mrca: (0.4e6, 1.4e6)}, full=True
    )
    base_ages = base["tree"].get_node_data("height").to_numpy(dtype=float)
    scaled_ages = scaled["tree"].get_node_data("height").to_numpy(dtype=float)
    assert np.allclose(
        base_ages[tree.ntips :] / base_ages[-1],
        scaled_ages[tree.ntips :] / scaled_ages[-1],
        atol=2e-5,
    )
    assert np.isclose(base["rate"] / 1e6, scaled["rate"], rtol=2e-5)


def test_profiled_clock_accepts_and_rescales_arbitrary_input_units():
    base_tree = toytree.tree(
        "((a:0.2,b:0.4):0.3,(c:0.5,d:0.7):0.2);"
    )
    scaled_tree = toytree.tree(
        "((a:20,b:40):30,(c:50,d:70):20);"
    )
    base = base_tree.mod.edges_make_ultrametric_clock(
        calibrations={-1: 2.0}, full=True
    )
    scaled = scaled_tree.mod.edges_make_ultrametric_clock(
        calibrations={-1: 2.0}, full=True
    )
    base_ages = base["tree"].get_node_data("height").to_numpy(dtype=float)
    scaled_ages = scaled["tree"].get_node_data("height").to_numpy(dtype=float)
    assert np.allclose(base_ages, scaled_ages, atol=2e-5)
    assert np.isclose(base["rate"] * 100.0, scaled["rate"], rtol=2e-5)


def test_uncalibrated_clock_returns_root_age_one_relative_time():
    tree = toytree.tree(
        "((a:2,b:4):3,(c:5,d:7):2);"
    )
    result = tree.mod.edges_make_ultrametric_clock(full=True)
    ages = result["tree"].get_node_data("height").to_numpy(dtype=float)
    assert result["converged"]
    assert np.isclose(ages[-1], 1.0)
    assert np.allclose(ages[:tree.ntips], 0.0)
    assert result["tree"].is_ultrametric()
