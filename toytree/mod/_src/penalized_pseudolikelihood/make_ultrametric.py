#!/usr/bin/env python

"""Public dispatcher for branch-length pseudolikelihood chronograms."""

from __future__ import annotations

from typing import Any, Literal

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.clock import (
    edges_make_ultrametric_clock,
)
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    edges_make_ultrametric_correlated,
)
from toytree.mod._src.penalized_pseudolikelihood.discrete import (
    edges_make_ultrametric_discrete,
)
from toytree.mod._src.penalized_pseudolikelihood.relaxed import (
    edges_make_ultrametric_relaxed,
)
from toytree.mod._src.penalized_pseudolikelihood.uncorrelated_lognormal import (
    edges_make_ultrametric_uncorrelated_lognormal,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    _validate_lambda,
    _validate_ncategories,
)
from toytree.utils import ToytreeError

__all__ = ["edges_make_ultrametric"]


def _validate_method(method: str) -> str:
    """Return a normalized supported ultrametricization method."""
    method = str(method).lower()
    valid = {
        "clock",
        "discrete",
        "relaxed",
        "uncorrelated_lognormal",
        "correlated",
    }
    if method not in valid:
        raise ToytreeError(f"invalid method {method!r}, must be one of {sorted(valid)}")
    return method


def _run_one(
    tree: ToyTree,
    method: str,
    calibrations: dict[int, Any],
    ncategories: int | None,
    lam: float | None,
    full: bool,
    inplace: bool,
    max_iter: int,
    max_fun: int,
    max_refine: int,
    nstarts: int,
    ncores: int,
    seed: int | None,
):
    """Dispatch one explicitly configured ultrametricization fit."""
    if method == "clock":
        return edges_make_ultrametric_clock(
            tree,
            calibrations=calibrations,
            full=full,
            inplace=inplace,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
    if method == "discrete":
        return edges_make_ultrametric_discrete(
            tree,
            ncategories=ncategories,
            calibrations=calibrations,
            full=full,
            inplace=inplace,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
    if method == "relaxed":
        return edges_make_ultrametric_relaxed(
            tree,
            lam=lam,
            calibrations=calibrations,
            full=full,
            inplace=inplace,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
    if method == "uncorrelated_lognormal":
        return edges_make_ultrametric_uncorrelated_lognormal(
            tree,
            lam=lam,
            calibrations=calibrations,
            full=full,
            inplace=inplace,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
    return edges_make_ultrametric_correlated(
        tree,
        lam=lam,
        calibrations=calibrations,
        full=full,
        inplace=inplace,
        max_iter=max_iter,
        max_fun=max_fun,
        max_refine=max_refine,
        nstarts=nstarts,
        ncores=ncores,
        seed=seed,
    )


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric(
    tree: ToyTree,
    method: Literal[
        "clock",
        "discrete",
        "relaxed",
        "uncorrelated_lognormal",
        "correlated",
    ],
    calibrations: dict[int, Any] | None = None,
    ncategories: int | None = None,
    lam: float | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int | None = None,
    ncores: int = 1,
    seed: int | None = None,
):
    """Make a tree ultrametric using one explicitly configured workflow.

    These fits use a fractional-Poisson branch-length pseudolikelihood. This
    function fits one explicitly configured model. Use
    :meth:`edges_make_ultrametric_correlated_lambda_cv` to select lambda by
    terminal-edge cross-validation within the correlated-rate model.

    Parameters
    ----------
    tree : ToyTree
        Input tree with finite, non-negative edge lengths.
    method : {"clock", "discrete", "relaxed", "uncorrelated_lognormal", "correlated"}
        Ultrametricization workflow.
    calibrations : dict or None
        Internal-node age constraints. With none, penalized-likelihood methods
        fix the root age to 1 and therefore estimate relative time.
    ncategories : int or None
        Required scalar category count for method="discrete" and invalid for
        all other methods.
    lam : float or None
        Required finite, positive penalty multiplier for correlated and
        relaxed, uncorrelated-lognormal, and correlated fits and invalid for
        all other methods.
    full, inplace : bool
        Return fit metadata instead of only a tree, and optionally modify the
        input tree.
    max_iter, max_fun, max_refine : int
        Optimizer and complete refinement-cycle limits.
    nstarts, ncores : int
        Multistart count and worker-process count.
    seed : int or None
        Random seed for multistart initialization.

    Returns
    -------
    ToyTree or dict[str, Any]
        The ultrametric tree, or a model-specific fit dictionary when full.
    """
    method = _validate_method(method)
    if nstarts is None:
        nstarts = 4 if method == "discrete" else 1
    calibrations = {} if calibrations is None else calibrations
    penalized = {"relaxed", "uncorrelated_lognormal", "correlated"}

    if method in penalized:
        if lam is None:
            raise ToytreeError(f"lam is required for method={method!r}.")
        lam = _validate_lambda(lam)
    elif lam is not None:
        raise ToytreeError(f"lam is only valid for methods {sorted(penalized)}.")

    if method == "discrete":
        if ncategories is None:
            raise ToytreeError("ncategories is required for method='discrete'.")
        ncategories = _validate_ncategories(ncategories, tree.nedges)
    elif ncategories is not None:
        raise ToytreeError("ncategories is only valid for method='discrete'.")

    return _run_one(
        tree=tree,
        method=method,
        calibrations=calibrations,
        ncategories=ncategories,
        lam=lam,
        full=full,
        inplace=inplace,
        max_iter=max_iter,
        max_fun=max_fun,
        max_refine=max_refine,
        nstarts=nstarts,
        ncores=ncores,
        seed=seed,
    )
