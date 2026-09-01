#!/usr/bin/env python

"""Correlated-rate smoothing selection by terminal-edge cross-validation."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Iterable

import numpy as np
from loguru import logger

from toytree.core import ToyTree
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.mod._src.penalized_pseudolikelihood.correlated import (
    _validate_correlated_observation_loss,
    edges_make_ultrametric_correlated,
)
from toytree.mod._src.penalized_pseudolikelihood.utils import (
    _validate_branch_lengths,
    _validate_lambda,
)
from toytree.utils import ToytreeError

__all__ = ["edges_make_ultrametric_correlated_lambda_cv"]

CV_EPS = 1e-12
DEFAULT_LAMBDAS = tuple(float(10**idx) for idx in range(-4, 5))


def _normalize_lambdas(lambdas: Iterable[float]) -> tuple[float, ...]:
    """Return a sorted grid of at least two unique positive lambdas."""
    try:
        values = tuple(_validate_lambda(value) for value in lambdas)
    except TypeError as exc:
        raise ToytreeError("lambdas must be an iterable of positive values.") from exc
    unique = tuple(sorted(set(values)))
    if len(unique) < 2:
        raise ToytreeError("lambdas must contain at least two unique values.")
    return unique


def _validate_parallel_option(value: Any, name: str) -> int:
    """Return a validated positive integer parallel option."""
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ToytreeError(f"{name} must be a positive integer.")
    result = int(value)
    if result < 1:
        raise ToytreeError(f"{name} must be a positive integer.")
    return result


def _prediction_score(observed: float, predicted: float, loss: str) -> float:
    """Return the held-branch score matching one observation loss."""
    expected = max(float(predicted), CV_EPS)
    value = max(float(observed), CV_EPS)
    if loss == "fractional_poisson":
        return float((value - expected) ** 2 / expected)
    ratio = value / expected
    return float(2.0 * (ratio - np.log(ratio) - 1.0))


def _fit_correlated_cv_fold(payload: dict[str, Any]) -> dict[str, Any]:
    """Fit and score one terminal-edge holdout under the correlated model."""
    tree = payload["tree"]
    edge_index = int(payload["edge_index"])
    child_index = int(payload["child_index"])
    observed = float(payload["observed"])
    all_dists = np.asarray(payload["all_dists"], dtype=float)
    observation_loss = payload.get("observation_loss", "fractional_poisson")
    mask = np.ones(tree.nedges, dtype=bool)
    mask[edge_index] = False

    # Exclude the held observation from initialization as well as likelihood.
    training = all_dists[mask]
    positive = training[training > 0.0]
    replacement = float(np.median(positive)) if positive.size else 1.0
    fit_tree = tree.set_node_data("dist", {child_index: replacement}, inplace=False)
    fit_options = dict(payload["fit_options"])
    if payload.get("initial_rates") is not None:
        fit_options["_initial_rates"] = payload["initial_rates"]
        fit_options["_initial_ages"] = payload["initial_ages"]
    try:
        fit = edges_make_ultrametric_correlated(
            fit_tree,
            lam=payload["lam"],
            calibrations=payload["calibrations"],
            full=True,
            inplace=False,
            _observation_mask=mask,
            _observation_loss=observation_loss,
            **fit_options,
        )
        predicted = float(fit["expected_branch_lengths"][edge_index])
        predicted_rate = float(fit["rates"][edge_index])
        edges = np.asarray(tree.get_edges("idx"), dtype=int)
        parent_index = int(edges[edge_index, 1])
        parent_edge = np.flatnonzero(edges[:, 0] == parent_index)
        ancestral_rate = (
            float(fit["rates"][parent_edge[0]]) if parent_edge.size else None
        )
        converged = bool(fit["converged"]) and np.isfinite(predicted)
        score = (
            _prediction_score(observed, predicted, observation_loss)
            if converged
            else float("inf")
        )
        result = {
            "fold": int(payload["fold"]),
            "edge_index": edge_index,
            "child_index": child_index,
            "observed": observed,
            "predicted": predicted,
            "predicted_rate": predicted_rate,
            "ancestral_rate": ancestral_rate,
            "score": score,
            "pseudologlik": float(fit["pseudologlik"]),
            "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
            "penalty": float(fit["penalty"]),
            "converged": converged,
            "optimizer_message": str(fit.get("optimizer_message", "")),
            "optimizer_retries": int(fit.get("optimizer_retries", 0)),
        }
        if payload.get("return_warm_start", False):
            result["_warm_rates"] = list(fit["rates"])
            result["_warm_ages"] = (
                fit["tree"].get_node_data("height").to_numpy(dtype=float).tolist()
            )
        return result
    except Exception as exc:
        return {
            "fold": int(payload["fold"]),
            "edge_index": edge_index,
            "child_index": child_index,
            "observed": observed,
            "predicted": float("nan"),
            "predicted_rate": float("nan"),
            "ancestral_rate": None,
            "score": float("inf"),
            "pseudologlik": None,
            "penalized_pseudologlik": None,
            "penalty": None,
            "converged": False,
            "optimizer_message": f"{type(exc).__name__}: {exc}",
            "optimizer_retries": 0,
        }


def _fit_correlated_cv_path(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fit one held edge over lambda from strong to weak smoothing."""
    results = []
    warm_rates = None
    warm_ages = None
    for payload in sorted(payloads, key=lambda item: float(item["lam"]), reverse=True):
        current = dict(payload)
        current["return_warm_start"] = True
        if warm_rates is not None:
            current["initial_rates"] = warm_rates
            current["initial_ages"] = warm_ages
        result = _fit_correlated_cv_fold(current)
        result["candidate_index"] = payload["candidate_index"]
        if result["converged"]:
            warm_rates = result.pop("_warm_rates")
            warm_ages = result.pop("_warm_ages")
        else:
            result.pop("_warm_rates", None)
            result.pop("_warm_ages", None)
        results.append(result)
    return results


def _run_fold_payloads(
    payloads: list[dict[str, Any]],
    ncores: int,
) -> list[dict[str, Any]]:
    """Fit lambda paths serially or with deterministic fold parallelism."""
    grouped: dict[int, list[dict[str, Any]]] = {}
    for payload in payloads:
        grouped.setdefault(int(payload["fold"]), []).append(payload)
    paths = [grouped[key] for key in sorted(grouped)]

    if ncores == 1:
        results = [item for path in paths for item in _fit_correlated_cv_path(path)]
    else:
        workers = min(ncores, len(paths))
        results = []
        try:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_fit_correlated_cv_path, path) for path in paths]
                for future in as_completed(futures):
                    results.extend(future.result())
        except (PermissionError, OSError) as exc:
            logger.warning(f"ProcessPool unavailable; using serial CV: {exc}")
            results = [item for path in paths for item in _fit_correlated_cv_path(path)]
    results.sort(key=lambda value: (value["candidate_index"], value["fold"]))
    return results


@add_subpackage_method(TreeModAPI)
def edges_make_ultrametric_correlated_lambda_cv(
    tree: ToyTree,
    lambdas: Iterable[float] = DEFAULT_LAMBDAS,
    calibrations: dict[Any, Any] | None = None,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int = 1,
    ncores: int = 1,
    seed: int | None = None,
    _observation_loss: str = "fractional_poisson",
) -> dict[str, Any]:
    """Select correlated-rate smoothing by terminal-edge LOOCV.

    This implements the lineage-pruning prediction criterion described by
    Sanderson (2002). Each terminal branch observation is excluded in turn,
    the correlated-rate model is refitted, and the held branch is predicted
    through its profiled rate under the ancestral log-rate penalty. The
    lambda with minimum mean Pearson prediction error is selected. Exact
    numerical ties favor stronger smoothing.

    Parameters
    ----------
    tree : ToyTree
        Input tree with finite, non-negative edge lengths.
    lambdas : Iterable[float]
        At least two unique finite positive smoothing values.
    calibrations : dict or None
        Internal-node age constraints passed to the correlated-rate fitter.
    max_iter, max_fun, max_refine : int
        Optimizer controls passed unchanged to every fold and the final fit.
    nstarts : int
        Number of starts for every correlated-rate fit.
    ncores : int
        Number of fold worker processes. Individual fold fits remain serial.
    seed : int or None
        Base seed used to derive deterministic fold seeds.

    Returns
    -------
    dict
        Selected lambda and full fit, candidate and fold diagnostics, and
        whether selection occurred at a lambda-grid boundary.
    """
    ncores = _validate_parallel_option(ncores, "ncores")
    nstarts = _validate_parallel_option(nstarts, "nstarts")
    observation_loss = _validate_correlated_observation_loss(_observation_loss)
    if seed is not None and (
        isinstance(seed, bool) or not isinstance(seed, (int, np.integer))
    ):
        raise ToytreeError("seed must be an integer or None.")
    grid = _normalize_lambdas(lambdas)
    calibrations = {} if calibrations is None else dict(calibrations)
    dists = _validate_branch_lengths(tree)
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    terminal = [
        (edge_index, int(child))
        for edge_index, (child, _) in enumerate(edges)
        if int(child) < tree.ntips
    ]
    if len(terminal) < 2:
        raise ToytreeError("terminal-edge CV requires a tree with at least two tips.")

    fit_options = {
        "max_iter": int(max_iter),
        "max_fun": int(max_fun),
        "max_refine": int(max_refine),
        "nstarts": nstarts,
        "ncores": 1,
    }
    payloads = []
    for candidate_index, lam in enumerate(grid):
        for fold, (edge_index, child_index) in enumerate(terminal):
            fold_seed = (
                None
                if seed is None
                else int(seed) + candidate_index * len(terminal) + fold
            )
            payloads.append(
                {
                    "tree": tree,
                    "lam": lam,
                    "candidate_index": candidate_index,
                    "fold": fold,
                    "edge_index": edge_index,
                    "child_index": child_index,
                    "observed": float(dists[edge_index]),
                    "all_dists": dists,
                    "calibrations": calibrations,
                    "fit_options": {**fit_options, "seed": fold_seed},
                    "observation_loss": observation_loss,
                }
            )
    fold_results = _run_fold_payloads(payloads, ncores)

    candidates = []
    for candidate_index, lam in enumerate(grid):
        folds = [
            result
            for result in fold_results
            if result["candidate_index"] == candidate_index
        ]
        values = np.asarray([result["score"] for result in folds], dtype=float)
        valid = bool(
            len(folds) == len(terminal)
            and all(result["converged"] for result in folds)
            and np.all(np.isfinite(values))
        )
        candidates.append(
            {
                "lam": lam,
                "valid": valid,
                "mean_score": float(np.mean(values)) if valid else float("inf"),
                "standard_error": (
                    float(np.std(values, ddof=1) / np.sqrt(values.size))
                    if valid and values.size > 1
                    else (0.0 if valid else float("inf"))
                ),
                "folds": folds,
            }
        )

    finite = [candidate for candidate in candidates if candidate["valid"]]
    if not finite:
        raise RuntimeError("all lambda candidates had a failed CV fold.")
    minimum = min(candidate["mean_score"] for candidate in finite)
    tied = [
        candidate
        for candidate in finite
        if abs(candidate["mean_score"] - minimum) <= CV_EPS
    ]
    selected = max(tied, key=lambda candidate: candidate["lam"])
    selected_lam = float(selected["lam"])
    selected_at_boundary = selected_lam in {grid[0], grid[-1]}
    if selected_at_boundary:
        logger.warning(
            "Selected lambda is at the candidate-grid boundary; expand the "
            "grid and rerun CV to check that the minimum is bracketed."
        )

    selected_fit = edges_make_ultrametric_correlated(
        tree,
        lam=selected_lam,
        calibrations=calibrations,
        full=True,
        inplace=False,
        _observation_loss=observation_loss,
        **{**fit_options, "seed": seed},
    )
    if not selected_fit["converged"]:
        raise RuntimeError(
            "the selected correlated-rate fit failed on the full dataset."
        )
    return {
        "model": "correlated",
        "selection_method": "leave_one_terminal_edge_out",
        "selection_target": "lambda",
        "score": (
            "pearson" if observation_loss == "fractional_poisson" else "gamma_deviance"
        ),
        "observation_loss": observation_loss,
        "selected_lam": selected_lam,
        "selected_fit": selected_fit,
        "mean_score": float(selected["mean_score"]),
        "standard_error": float(selected["standard_error"]),
        "candidates": candidates,
        "folds": fold_results,
        "nfolds": len(terminal),
        "seed": None if seed is None else int(seed),
        "ncores": ncores,
        "selected_at_boundary": selected_at_boundary,
    }
