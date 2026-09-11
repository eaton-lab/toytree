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

    All supported fits use a fractional-Poisson branch-length
    pseudolikelihood. This function fits one explicitly configured model.
    Correlated and UCLN fits require a user-supplied ``lam``. Development
    studies found that per-tree cross-validation did not identify lambda
    precisely enough for a general estimator, so ToyTree intentionally exposes
    no automatic lambda selector. Choose lambda from external information and
    report sensitivity across scientifically plausible values.

    The strict clock is validated directly, while ``discrete`` is validated
    for ape::chronos compatibility with an explicit category count. The
    ``relaxed`` workflow is compatibility-only and is not recommended over
    UCLN for new uncorrelated-rate analyses. These scoped statuses replace any
    blanket experimental designation for this module.

    Tree-only mode is fail-closed: nonconvergence or an explicitly unstable
    multistart solution raises :class:`ToytreeError` instead of returning a
    candidate tree. Set ``full=True`` to always receive diagnostics and the
    candidate, then inspect ``fit_usable`` and ``failure_reasons``. Unassessed
    stability is not fatal. A converged discrete boundary optimum is also not
    fatal by itself, because it can validly indicate fewer effective than
    requested categories. ``inplace=True`` is applied only to usable fits.


    Input edge lengths may use any consistent, finite, non-negative additive
    unit for which branch length equals elapsed time multiplied by rate;
    expected substitutions per site are common but not required. Calibration
    ages define the returned tree's time unit, while fitted rates use
    input-edge units per calibration unit. Without calibrations, the root age
    is fixed to 1, so returned edge lengths are relative time and fitted rates
    use input-edge units per relative root-age unit. The ``relaxed`` method is
    provided for ape::chronos parity; ``uncorrelated_lognormal`` is recommended
    for continuous uncorrelated rates.

    Parameters
    ----------
    tree : ToyTree
        Input tree with finite, non-negative edge lengths in a consistent
        additive unit. Values must not be support values or unrelated edge
        weights.
    method
        One of `clock`, `discrete`, `relaxed`, `uncorrelated_lognormal`,
        or `correlated`.
        Ultrametricization workflow.
    calibrations : dict or None
        Internal-node age constraints whose unit becomes the returned tree's
        time unit. With none, the root age is fixed to 1 and all methods
        estimate relative time.
    ncategories : int or None
        Required scalar category count for method="discrete"; invalid for all
        other methods.
    lam : float or None
        Required finite, positive penalty multiplier for relaxed,
        uncorrelated-lognormal, and correlated fits and invalid for
        all other methods. For UCLN this fixes the assumed log-rate dispersion;
        it is not automatically estimated from the input tree.
    full, inplace : bool
        Return fit metadata instead of only a tree, and optionally modify the
        input tree.
    max_iter, max_fun, max_refine : int
        Optimizer and complete refinement-cycle limits.
    nstarts, ncores : int
        Multistart count and worker-process count. When ``nstarts`` is omitted,
        discrete uses eight starts, UCLN and correlated use four, and other
        methods use one.
    seed : int or None
        Random seed for multistart initialization.

    Returns
    -------
    ToyTree or dict[str, Any]
        The ultrametric tree, or a model-specific fit dictionary when full.
        Returned rates use input-edge units per calibration unit, or per
        relative root-age unit when no calibration is supplied.
    """
    method = _validate_method(method)
    if nstarts is None:
        nstarts = {
            "discrete": 8,
            "uncorrelated_lognormal": 4,
            "correlated": 4,
        }.get(method, 1)
    calibrations = {} if calibrations is None else calibrations
    penalized = {"relaxed", "uncorrelated_lognormal", "correlated"}

    if method in penalized:
        if lam is None:
            raise ToytreeError(f"lam is required for method={method!r}.")
        lam = _validate_lambda(lam)
    elif lam is not None:
        raise ToytreeError(f"lam is only valid for methods {sorted(penalized)}.")

    discrete_methods = {"discrete"}
    if method == "discrete":
        if ncategories is None:
            raise ToytreeError(f"ncategories is required for method={method!r}.")
        ncategories = _validate_ncategories(ncategories, tree.nedges)
    elif ncategories is not None:
        raise ToytreeError(
            f"ncategories is only valid for methods {sorted(discrete_methods)}."
        )
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
