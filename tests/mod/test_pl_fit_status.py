#!/usr/bin/env python

"""Regression tests for the public penalized-fit usability contract."""

import pytest

import toytree
from toytree.mod._src.penalized_pseudolikelihood.utils import _finalize_fit_result
from toytree.utils import ToytreeError


def _result(candidate, **updates):
    result = {
        "model": "clock",
        "tree": candidate,
        "converged": True,
        "optimizer_message": "converged",
    }
    result.update(updates)
    return result


@pytest.mark.parametrize(
    ("updates", "expected_reasons"),
    [
        ({"converged": False}, ["optimizer_not_converged"]),
        ({"solution_stable": False}, ["solution_unstable"]),
        (
            {"converged": False, "solution_stable": False},
            ["optimizer_not_converged", "solution_unstable"],
        ),
    ],
)
def test_full_result_preserves_unusable_candidate_and_diagnostics(
    updates, expected_reasons
):
    """Full results expose failed candidates without presenting them as usable."""
    source = toytree.tree("(a:1,b:2);")
    before = source.write()
    candidate = toytree.tree("(a:1,b:1);")

    result = _finalize_fit_result(
        _result(candidate, **updates), source, full=True, inplace=True
    )

    assert result["tree"] is candidate
    assert result["fit_usable"] is False
    assert result["failure_reasons"] == expected_reasons
    assert source.write() == before


@pytest.mark.parametrize("solution_stable", [None, True])
def test_unassessed_or_stable_solution_is_usable(solution_stable):
    """Only an explicit false stability result is fatal."""
    source = toytree.tree("(a:1,b:2);")
    candidate = toytree.tree("(a:1,b:1);")
    updates = {}
    if solution_stable is not None:
        updates["solution_stable"] = solution_stable

    result = _finalize_fit_result(
        _result(candidate, **updates), source, full=True, inplace=False
    )

    assert result["fit_usable"] is True
    assert result["failure_reasons"] == []


def test_boundary_diagnostic_alone_is_not_a_fit_failure():
    """A replicated converged discrete boundary optimum remains usable."""
    source = toytree.tree("(a:1,b:2);")
    candidate = toytree.tree("(a:1,b:1);")
    result = _finalize_fit_result(
        _result(
            candidate,
            model="discrete",
            solution_stable=True,
            boundary_solution=True,
            optimum_replicated=True,
        ),
        source,
        full=True,
        inplace=False,
    )
    assert result["fit_usable"] is True
    assert result["failure_reasons"] == []


def test_tree_only_failure_raises_and_does_not_mutate_source():
    """Tree-only mode cannot silently return or apply a failed candidate."""
    source = toytree.tree("(a:1,b:2);")
    before = source.write()
    candidate = toytree.tree("(a:1,b:1);")

    with pytest.raises(ToytreeError, match="full=True"):
        _finalize_fit_result(
            _result(candidate, converged=False),
            source,
            full=False,
            inplace=True,
        )
    assert source.write() == before


def test_successful_inplace_fit_applies_candidate_only_after_status_check():
    """A usable fit applies candidate heights to and returns the source tree."""
    source = toytree.tree("(a:1,b:2);")
    candidate = toytree.tree("(a:1,b:1);")

    result = _finalize_fit_result(_result(candidate), source, full=True, inplace=True)

    assert result["tree"] is source
    assert source.is_ultrametric()
    assert result["fit_usable"] is True


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("clock", {}),
        ("discrete", {"ncategories": 2}),
        ("relaxed", {"lam": 0.5}),
        ("uncorrelated_lognormal", {"lam": 0.5}),
        ("correlated", {"lam": 0.5}),
    ],
)
def test_every_public_model_full_result_declares_fit_usability(method, kwargs):
    """All five public fitters expose the standardized status fields."""
    tree = toytree.tree("(a:0.2,b:0.3);")
    result = tree.mod.edges_make_ultrametric(
        method=method,
        calibrations={-1: 1.0},
        full=True,
        max_iter=100,
        max_fun=100,
        max_refine=2,
        **kwargs,
    )
    assert result["fit_usable"] is True
    assert result["failure_reasons"] == []


@pytest.mark.parametrize(
    ("name", "kwargs"),
    [
        ("edges_make_ultrametric_clock", {}),
        ("edges_make_ultrametric_discrete", {"ncategories": 2}),
        ("edges_make_ultrametric_relaxed", {"lam": 0.5}),
        ("edges_make_ultrametric_uncorrelated_lognormal", {"lam": 0.5}),
        ("edges_make_ultrametric_correlated", {"lam": 0.5}),
    ],
)
def test_every_direct_model_full_result_declares_fit_usability(name, kwargs):
    """Direct model functions use the same status contract as the dispatcher."""
    tree = toytree.tree("(a:0.2,b:0.3);")
    result = getattr(toytree.mod, name)(
        tree,
        calibrations={-1: 1.0},
        full=True,
        max_iter=100,
        max_fun=100,
        max_refine=2,
        **kwargs,
    )
    assert result["fit_usable"] is True
    assert result["failure_reasons"] == []
