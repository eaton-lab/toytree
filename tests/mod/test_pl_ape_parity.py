# ruff: noqa: D103

import json
from pathlib import Path

import numpy as np
from scipy.special import gammaln

import toytree
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    _poisson_branch_pseudologlik,
)
from toytree.mod._src.penalized_pseudolikelihood.discrete import (
    _discrete_branch_pseudologlik,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    _independent_branch_pseudologlik,
    _relaxed_penalty,
)

FIXTURE = (
    Path(__file__).parents[1]
    / "data"
    / "penalized_pseudolikelihood"
    / "ape-5.8.1.json"
)


def _load_reference():
    with FIXTURE.open(encoding="utf-8") as stream:
        return json.load(stream)


def _fixed_fit_inputs(reference, model):
    observed = np.asarray(reference["observed_edge_lengths"], dtype=float)
    times = np.asarray(model["time_edge_lengths"], dtype=float)
    nedges = observed.size
    edges = np.column_stack(
        [np.arange(nedges, dtype=int), np.arange(nedges, 2 * nedges, dtype=int)]
    )
    ages = np.concatenate([np.zeros(nedges), times])
    edata = np.column_stack([observed, gammaln(observed + 1.0)])
    return ages, edges, edata


def _edge_time_by_clade(tree):
    result = {}
    for child, _ in tree.get_edges("idx"):
        node = tree[int(child)]
        clade = ",".join(sorted(leaf.name for leaf in node.iter_leaves()))
        result[clade] = float(node.dist)
    return result


def _edge_values_by_clade(tree, values):
    result = {}
    for (child, _), value in zip(tree.get_edges("idx"), values):
        node = tree[int(child)]
        clade = ",".join(sorted(leaf.name for leaf in node.iter_leaves()))
        result[clade] = float(value)
    return result


def test_clock_fixed_objective_matches_ape_5_8_1():
    reference = _load_reference()
    model = reference["models"]["clock"]
    ages, edges, edata = _fixed_fit_inputs(reference, model)
    observed = _poisson_branch_pseudologlik(
        model["rates"][0], ages, edges, edata, valid_loglik=None
    )
    assert np.isclose(observed, model["loglik"], atol=1e-12)


def test_discrete_fixed_objective_matches_ape_5_8_1():
    reference = _load_reference()
    model = reference["models"]["discrete"]
    ages, edges, edata = _fixed_fit_inputs(reference, model)
    observed = _discrete_branch_pseudologlik(
        np.asarray(model["rates"]),
        ages,
        edges,
        edata,
        np.asarray(model["weights"]),
        valid_loglik=None,
    )
    assert np.isclose(observed, model["loglik"], atol=1e-12)


def test_relaxed_fixed_objective_matches_ape_5_8_1():
    reference = _load_reference()
    model = reference["models"]["relaxed"]
    ages, edges, edata = _fixed_fit_inputs(reference, model)
    rates = np.asarray(model["rates"])
    penalty = _relaxed_penalty(rates)
    observed = _independent_branch_pseudologlik(
        rates,
        ages,
        edges,
        edata,
        reference["lambda"],
        valid_loglik=None,
        model="relaxed",
    )
    assert np.isclose(penalty, model["penalty"], atol=1e-12)
    assert np.isclose(observed, model["penalized_loglik"], atol=1e-12)


def test_clock_full_fit_matches_ape_5_8_1():
    reference = _load_reference()
    model = reference["models"]["clock"]
    tree = toytree.tree(reference["newick"])
    fit = tree.mod.edges_make_ultrametric_clock(
        calibrations={-1: 1.0}, full=True, max_refine=20
    )
    expected = dict(zip(reference["edge_clades"], model["time_edge_lengths"]))
    assert fit["converged"]
    assert np.isclose(fit["rate"], model["rates"][0], atol=2e-5)
    assert np.isclose(fit["pseudologlik"], model["loglik"], atol=1e-9)
    for clade, value in _edge_time_by_clade(fit["tree"]).items():
        assert np.isclose(value, expected[clade], atol=2e-5)


def test_discrete_full_fit_matches_ape_5_8_1():
    reference = _load_reference()
    model = reference["models"]["discrete"]
    tree = toytree.tree(reference["newick"])
    fit = tree.mod.edges_make_ultrametric_discrete(
        ncategories=2, calibrations={-1: 1.0}, full=True, max_refine=20
    )
    expected = dict(zip(reference["edge_clades"], model["time_edge_lengths"]))
    assert fit["converged"]
    assert np.isclose(fit["pseudologlik"], model["loglik"], atol=1e-8)
    assert np.isclose(
        np.dot(fit["rates"], fit["weights"]),
        np.dot(model["rates"], model["weights"]),
        atol=2e-4,
    )
    for clade, value in _edge_time_by_clade(fit["tree"]).items():
        assert np.isclose(value, expected[clade], atol=2e-4)


def test_relaxed_full_fit_matches_ape_5_8_1():
    reference = _load_reference()
    model = reference["models"]["relaxed"]
    tree = toytree.tree(reference["newick"])
    fit = tree.mod.edges_make_ultrametric_relaxed(
        lam=reference["lambda"],
        calibrations={-1: 1.0},
        full=True,
        max_refine=20,
    )
    expected_times = dict(zip(reference["edge_clades"], model["time_edge_lengths"]))
    expected_rates = dict(zip(reference["edge_clades"], model["rates"]))
    assert fit["converged"]
    # ToyTree optimizes the same objective in log-rate coordinates and can
    # improve slightly on ape's raw-rate-gradient solution. Require the same
    # fitted basin and an objective no worse than the pinned ape fit.
    assert fit["penalized_pseudologlik"] >= model["penalized_loglik"] - 1e-6
    for clade, value in _edge_time_by_clade(fit["tree"]).items():
        assert np.isclose(value, expected_times[clade], atol=3e-2)
    for clade, value in _edge_values_by_clade(fit["tree"], fit["rates"]).items():
        assert np.isclose(value, expected_rates[clade], rtol=0.12)
