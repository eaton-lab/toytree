#!/usr/bin/env python

from __future__ import annotations

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


def _make_discrete_candidates(estimate: int, nedges: int) -> list[int]:
    nedges = max(1, int(nedges))
    raw = np.geomspace(1.0, float(nedges), num=int(estimate))
    vals = sorted(set(np.clip(np.rint(raw).astype(int), 1, nedges).tolist()))
    if 1 not in vals:
        vals.insert(0, 1)
    target = min(int(estimate), nedges)
    if len(vals) < target:
        existing = set(vals)
        for cand in range(1, nedges + 1):
            if cand not in existing:
                vals.append(cand)
                existing.add(cand)
            if len(vals) >= target:
                break
        vals = sorted(vals)
    return vals


def _make_lam_candidates(estimate: int) -> list[float]:
    return [float(i) for i in np.linspace(0.0, 1.0, int(estimate))]


def _prepare_candidates(
    tree: ToyTree,
    method: str,
    estimate: int,
    estimate_values: list[int | float] | None,
    ncategories: int | None,
    lam: float | None,
) -> tuple[str, list[int | float]]:
    if method == "discrete":
        if ncategories is not None:
            return "ncategories", [int(ncategories)]
        if estimate_values is not None:
            vals = sorted({int(i) for i in estimate_values if int(i) >= 1})
            return "ncategories", [min(v, tree.nedges) for v in vals]
        return "ncategories", _make_discrete_candidates(estimate, tree.nedges)

    if method in {"relaxed", "correlated"}:
        if lam is not None:
            # explicit lam acts as a fixed candidate under estimate mode.
            return "lam", [float(lam)]
        if estimate_values is not None:
            vals = sorted({float(i) for i in estimate_values if float(i) >= 0.0})
            return "lam", vals
        return "lam", _make_lam_candidates(estimate)

    raise ToytreeError("--estimate is only supported for method='discrete', 'relaxed', or 'correlated'.")


def _select_best_search(records: list[dict[str, Any]]) -> dict[str, Any]:
    finite = [i for i in records if np.isfinite(float(i.get("PHIIC", np.inf)))]
    if not finite:
        raise ToytreeError("all estimate candidates failed to produce finite PHIIC.")
    finite = sorted(finite, key=lambda x: (float(x["PHIIC"]), float(x["candidate"])))
    return finite[0]


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric(
    tree: ToyTree,
    method: Literal["extend", "clock", "discrete", "relaxed", "correlated"],
    calibrations: dict[int, Any] | None = None,
    ncategories: int | None = None,
    lam: float | None = None,
    full: bool = False,
    inplace: bool = False,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
    estimate: int | None = None,
    estimate_values: list[int | float] | None = None,
):
    """Make a tree ultrametric using a selected transformation/model workflow.

    This is a user-facing convenience wrapper that dispatches to one of
    several ultrametricization methods:
    ``"extend"``, ``"clock"``, ``"discrete"``, ``"relaxed"``, or
    ``"correlated"``.

    For penalized-likelihood methods, this function can also estimate a
    tuning parameter by searching candidate values and selecting the best
    fit by minimum PHIIC:
    - ``ncategories`` for ``method="discrete"``
    - ``lam`` for ``method in {"relaxed", "correlated"}``

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
    ncategories: int or None
        Number of rate categories for ``method="discrete"``. Required for
        discrete fitting when ``estimate`` is not used (unless provided via
        ``estimate_values``).
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
    estimate: int or None
        If provided, enable parameter search mode over ``estimate``
        candidates and select the best by PHIIC. Supported only for
        ``method="discrete"``, ``"relaxed"``, and ``"correlated"``.
    estimate_values: list[int | float] or None
        Optional explicit candidate values for search mode. If provided,
        these override automatically generated candidates.

    Returns
    -------
    ToyTree
        Returned when ``full=False``. The transformed ultrametric tree.
    dict[str, Any]
        Returned when ``full=True``. Includes backend model-fit outputs.
        In search mode (``estimate is not None``), also includes:
        ``estimated_parameter``, ``estimated_value``, and ``search``.

    Raises
    ------
    ToytreeError
        Raised for invalid method names, invalid/unsupported estimate mode,
        negative ``lam``, missing required discrete settings, invalid
        candidate sets, or if all search candidates fail to return finite
        PHIIC.

    Notes
    -----
    In search mode, candidate selection is deterministic:
    - Lowest PHIIC wins.
    - Ties are broken by selecting the smaller candidate value.

    Default search candidates:
    - ``discrete``: approximately geometric spacing over ``[1, tree.nedges]``
    - ``relaxed/correlated``: linear spacing over ``[0.0, 1.0]``

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

    Fit a relaxed rate model and estimate lambda parameter
    >>> t4 = tree.mod.edges_make_ultrametric(
    ...     method="relaxed", estimate=5, nstarts=5, ncores=5,
    ... )

    Fit a correlated rates model, estimate, and get full result dict
    >>> res = tree.mod.edges_make_ultrametric(
    ...     method="correlated",
    ...     estimate=4,
    ...     estimate_values=[0.0, 0.25, 0.5, 1.0],
    ...     full=True,
    ... )
    >>> print(res)

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

    if estimate is None:
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

    estimate = int(estimate)
    if estimate < 1:
        raise ToytreeError("estimate must be >= 1.")
    param_name, candidates = _prepare_candidates(
        tree=tree,
        method=method,
        estimate=estimate,
        estimate_values=estimate_values,
        ncategories=ncategories,
        lam=lam if method in {"relaxed", "correlated"} else None,
    )
    if not candidates:
        raise ToytreeError("no valid candidates generated for --estimate.")

    search: list[dict[str, Any]] = []
    best_result: dict[str, Any] | None = None
    for cand in candidates:
        kwargs = dict(
            tree=tree,
            method=method,
            calibrations=calibrations,
            ncategories=int(cand) if param_name == "ncategories" else ncategories,
            lam=float(cand) if param_name == "lam" else lam,
            full=True,
            inplace=False,
            max_iter=max_iter,
            max_fun=max_fun,
            max_refine=max_refine,
            nstarts=nstarts,
            ncores=ncores,
            seed=seed,
        )
        candidate_value = int(cand) if param_name == "ncategories" else float(cand)
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
        if result is not None and (best_result is None or (
            np.isfinite(record["PHIIC"]) and (
                record["PHIIC"] < best_result["PHIIC"] - 1e-9
                or (
                    abs(record["PHIIC"] - best_result["PHIIC"]) <= 1e-9
                    and float(record["candidate"]) < float(best_result["candidate"])
                )
            )
        )):
            best_result = {"PHIIC": record["PHIIC"], "candidate": record["candidate"], "result": result}

    _ = _select_best_search(search)
    assert best_result is not None
    selected = best_result["candidate"]

    if inplace:
        final = _run_one(
            tree=tree,
            method=method,
            calibrations=calibrations,
            ncategories=int(selected) if param_name == "ncategories" else ncategories,
            lam=float(selected) if param_name == "lam" else lam,
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

    final["estimated_parameter"] = param_name
    final["estimated_value"] = selected
    final["search"] = search
    return final
