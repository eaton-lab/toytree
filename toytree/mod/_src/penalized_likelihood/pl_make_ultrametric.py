#!/usr/bin/env python

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

import numpy as np

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_likelihood.pl_clock import (
    edges_make_ultrametric_pl_clock,
)
from toytree.mod._src.penalized_likelihood.pl_correlated import (
    edges_make_ultrametric_pl_correlated,
)
from toytree.mod._src.penalized_likelihood.pl_discrete import (
    edges_make_ultrametric_pl_discrete,
)
from toytree.mod._src.penalized_likelihood.pl_relaxed import (
    edges_make_ultrametric_pl_relaxed,
)
from toytree.utils import ToytreeError

__all__ = ["edges_make_ultrametric"]


def _validate_method(method: str) -> str:
    method = str(method).lower()
    valid = {"extend", "clock", "discrete", "relaxed", "correlated"}
    if method not in valid:
        raise ToytreeError(f"invalid method '{method}', must be one of {sorted(valid)}")
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
    if method == "extend":
        return tree.mod.edges_extend_tips_to_align(inplace=inplace)
    if method == "clock":
        return edges_make_ultrametric_pl_clock(
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
        if ncategories is None:
            raise ToytreeError("ncategories is required for method='discrete'.")
        return edges_make_ultrametric_pl_discrete(
            tree,
            ncategories=int(ncategories),
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
        return edges_make_ultrametric_pl_relaxed(
            tree,
            lam=1.0 if lam is None else float(lam),
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
    return edges_make_ultrametric_pl_correlated(
        tree,
        lam=1.0 if lam is None else float(lam),
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


def _select_best_search(records: list[dict[str, Any]]) -> dict[str, Any]:
    finite = [i for i in records if np.isfinite(float(i.get("PHIIC", np.inf)))]
    if not finite:
        raise ToytreeError("all candidate fits failed to produce finite PHIIC.")
    finite = sorted(finite, key=lambda x: (float(x["PHIIC"]), float(x["candidate"])))
    return finite[0]


def _coerce_discrete_candidates(
    ncategories: int | Sequence[int] | None,
    nedges: int,
) -> int | list[int] | None:
    """Return validated discrete-rate candidate count(s)."""
    if ncategories is None:
        return None
    if isinstance(ncategories, np.integer):
        return int(min(int(ncategories), int(nedges)))
    if isinstance(ncategories, Sequence) and not isinstance(ncategories, (str, bytes)):
        values: list[int] = []
        seen: set[int] = set()
        for value in ncategories:
            if isinstance(value, bool):
                raise ToytreeError("ncategories candidates must be positive integers.")
            if isinstance(value, np.integer):
                candidate = int(value)
            else:
                try:
                    fval = float(value)
                except (TypeError, ValueError) as exc:
                    raise ToytreeError(
                        "ncategories candidates must be positive integers."
                    ) from exc
                if not np.isfinite(fval) or not fval.is_integer():
                    raise ToytreeError(
                        "ncategories candidates must be positive integers."
                    )
                candidate = int(fval)
            if candidate < 1:
                raise ToytreeError("ncategories candidates must be >= 1.")
            candidate = min(candidate, int(nedges))
            if candidate not in seen:
                values.append(candidate)
                seen.add(candidate)
        if not values:
            raise ToytreeError("ncategories candidate list cannot be empty.")
        return values
    return int(min(int(ncategories), int(nedges)))


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric(
    tree: ToyTree,
    method: Literal["extend", "clock", "discrete", "relaxed", "correlated"],
    calibrations: dict[int, Any] | None = None,
    ncategories: int | Sequence[int] | None = None,
    lam: float | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
):
    """Make a tree ultrametric using a selected transformation/model workflow.

    This is a user-facing convenience wrapper that dispatches to one of
    several ultrametricization methods:
    ``"extend"``, ``"clock"``, ``"discrete"``, ``"relaxed"``, or
    ``"correlated"``.

    For ``method="discrete"``, users can pass multiple ``ncategories``
    candidates and select the best fit by minimum PHIIC.

    Parameters
    ----------
    tree: ToyTree
        Input tree with edge lengths to transform.
    method: str
        Ultrametricization workflow. Must be one of:
        ``"extend"``, ``"clock"``, ``"discrete"``, ``"relaxed"``,
        ``"correlated"``.
    calibrations: dict[int, Any] or None
        Optional calibration constraints mapping node selectors to either a
        fixed age (single numeric value) or an allowed age interval
        ``(min_age, max_age)``. Used by penalized-likelihood methods and
        ignored by ``method="extend"``.
    ncategories: int, sequence of int, or None
        Number of rate categories for ``method="discrete"``. A single
        integer fits one discrete model. A sequence of integers fits each
        candidate and selects the best by minimum PHIIC.
    lam: float or None
        Non-negative smoothing/penalty parameter for
        ``method in {"relaxed", "correlated"}``.
    full: bool
        If ``False`` (default), return only the transformed ``ToyTree``.
        If ``True``, return backend fit details as a dictionary.
    inplace: bool
        If ``True``, modify and return the input tree when possible.
        If ``False``, return a transformed copy.
    max_iter: int
        Maximum optimizer iterations per fit.
    max_fun: int
        Maximum objective evaluations per fit.
    max_refine: int
        Number of alternating refinement rounds (rates vs. ages) used by
        backend optimizers.
    nstarts: int
        Number of random multistart initializations per fit.
    ncores: int
        Number of worker processes for multistart fitting (used when
        ``nstarts > 1``).
    seed: int or None
        Random seed for reproducible multistart initialization.

    Returns
    -------
    ToyTree
        Returned when ``full=False``. The transformed ultrametric tree.
    dict[str, Any]
        Returned when ``full=True``. Includes backend model-fit outputs.
        When ``method="discrete"`` is called with multiple ``ncategories``
        candidates, also includes ``selected_ncategories``,
        ``selection_criterion``, and ``search``.

    Raises
    ------
    ToytreeError
        Raised for invalid method names, negative ``lam``, missing
        required discrete settings, invalid candidate sets, or if all
        discrete candidate fits fail to return finite PHIIC.

    Notes
    -----
    When multiple discrete candidates are supplied, candidate selection is
    deterministic:
    - Lowest PHIIC wins.
    - Ties are broken by selecting the smaller candidate value.

    Examples
    --------
    >>> tree = toytree.rtree.rtree(20, seed=1)

    Fast extend tips to make ultrametric (not model-based)
    >>> t1 = tree.mod.edges_make_ultrametric(method="extend")

    Fit a clock model with a root node calibration
    >>> cal = {tree.treenode.idx: 10.0}
    >>> t2 = tree.mod.edges_make_ultrametric(method="clock", calibrations=cal)

    Fit a multi-rate model
    >>> t3 = tree.mod.edges_make_ultrametric(
    ...     method="discrete", calibrations=cal, ncategories=3)

    Compare several discrete models and select the best by PHIIC
    >>> res = tree.mod.edges_make_ultrametric(
    ...     method="discrete",
    ...     calibrations=cal,
    ...     ncategories=[1, 2, 4],
    ...     full=True,
    ... )
    >>> print(res)

    Fit a correlated rates model with a fixed lambda and inspect PHIIC
    >>> t4 = tree.mod.edges_make_ultrametric(
    ...     method="correlated", lam=0.5, calibrations=cal, full=True)

    See Also
    --------
    edges_extend_tips_to_align
    edges_make_ultrametric_pl_clock
    edges_make_ultrametric_pl_discrete
    edges_make_ultrametric_pl_relaxed
    edges_make_ultrametric_pl_correlated
    """
    method = _validate_method(method)
    calibrations = {} if calibrations is None else calibrations
    if lam is not None and lam < 0:
        raise ToytreeError("lam must be >= 0.")
    if (
        method != "discrete"
        and isinstance(ncategories, Sequence)
        and not isinstance(ncategories, (str, bytes))
    ):
        raise ToytreeError(
            "ncategories candidate lists are only supported for method='discrete'."
        )
    ncat_values = (
        _coerce_discrete_candidates(ncategories, tree.nedges)
        if method == "discrete"
        else ncategories
    )

    if not isinstance(ncat_values, list):
        return _run_one(
            tree=tree,
            method=method,
            calibrations=calibrations,
            ncategories=ncat_values,
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

    search: list[dict[str, Any]] = []
    best_result: dict[str, Any] | None = None
    for cand in ncat_values:
        kwargs = dict(
            tree=tree,
            method=method,
            calibrations=calibrations,
            ncategories=int(cand),
            lam=lam,
            full=True,
            inplace=False,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
        candidate_value = int(cand)
        try:
            result = _run_one(**kwargs)
            record = {
                "candidate": candidate_value,
                "PHIIC": float(result.get("PHIIC", np.inf)),
                "converged": bool(result.get("converged", False)),
                "optimizer_message": str(result.get("optimizer_message", "")),
            }
        except Exception as exc:
            result = None
            record = {
                "candidate": candidate_value,
                "PHIIC": float("inf"),
                "converged": False,
                "optimizer_message": f"{type(exc).__name__}: {exc}",
            }
        search.append(record)
        if result is not None and (
            best_result is None
            or (
                np.isfinite(record["PHIIC"])
                and (
                    record["PHIIC"] < best_result["PHIIC"] - 1e-9
                    or (
                        abs(record["PHIIC"] - best_result["PHIIC"]) <= 1e-9
                        and float(record["candidate"]) < float(best_result["candidate"])
                    )
                )
            )
        ):
            best_result = {
                "PHIIC": record["PHIIC"],
                "candidate": record["candidate"],
                "result": result,
            }

    _ = _select_best_search(search)
    assert best_result is not None
    selected = best_result["candidate"]

    if inplace:
        final = _run_one(
            tree=tree,
            method=method,
            calibrations=calibrations,
            ncategories=int(selected),
            lam=lam,
            full=True,
            inplace=True,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
    else:
        final = best_result["result"]

    if not full:
        return final["tree"]

    final["selected_ncategories"] = int(selected)
    final["selection_criterion"] = "PHIIC"
    final["search"] = search
    return final
