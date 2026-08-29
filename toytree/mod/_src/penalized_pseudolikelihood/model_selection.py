#!/usr/bin/env python

"""Terminal-edge cross-validation for ultrametric model selection."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Iterable, Literal

import numpy as np
from loguru import logger

from toytree.core import ToyTree
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
    _validate_branch_lengths,
    _validate_lambda,
    _validate_ncategories,
)
from toytree.utils import ToytreeError

__all__: list[str] = []

DEFAULT_NCATEGORIES = (2, 3, 4)
DEFAULT_LAMBDAS = tuple(float(10**i) for i in range(-4, 5))
METHOD_ORDER = {
    "clock": 0,
    "discrete": 1,
    "relaxed": 2,
    "uncorrelated_lognormal": 3,
    "correlated": 4,
}
CV_EPS = 1e-12

SCORE_NAMES = ("pearson", "poisson_deviance", "relative_squared")
SELECTION_RULES = ("one_se", "minimum")


def _prediction_score(observed: float, predicted: float, score: str) -> float:
    """Return one held-observation prediction score."""
    expected = max(float(predicted), CV_EPS)
    value = float(observed)
    if score == "pearson":
        return float((value - expected) ** 2 / expected)
    if score == "poisson_deviance":
        if value == 0.0:
            return float(2.0 * expected)
        return float(2.0 * (value * np.log(value / expected) - (value - expected)))
    if score == "relative_squared":
        return float((value - expected) ** 2 / expected**2)
    raise ToytreeError(f"score must be one of {list(SCORE_NAMES)}.")


def _minimum_tie_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    """Return the historical deterministic ordering for exact CV ties."""
    config = candidate["config"]
    return (
        candidate["nparams"],
        METHOD_ORDER[config["method"]],
        config.get("ncategories", config.get("lam", 0.0)),
    )


def _simplicity_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    """Return deterministic nominal complexity ordering for one-SE selection."""
    config = candidate["config"]
    method = config["method"]
    if method == "discrete":
        hyperparameter = int(config["ncategories"])
    elif method in {"relaxed", "uncorrelated_lognormal", "correlated"}:
        hyperparameter = -float(config["lam"])
    else:
        hyperparameter = 0
    return (
        candidate["nparams"],
        METHOD_ORDER[method],
        hyperparameter,
    )


def _candidate_label(config: dict[str, Any]) -> str:
    """Return a stable, human-readable candidate label."""
    method = config["method"]
    if method == "discrete":
        return f"discrete(K={config['ncategories']})"
    if method in {"relaxed", "uncorrelated_lognormal", "correlated"}:
        return f"{method}(lam={config['lam']:g})"
    return "clock"


def _normalize_candidates(
    tree: ToyTree,
    candidate_configs: Iterable[dict[str, Any]] | None,
    ncategories: Iterable[int],
    lambdas: Iterable[float],
) -> list[dict[str, Any]]:
    """Return validated candidate configurations in deterministic order."""
    if candidate_configs is None:
        configs: list[dict[str, Any]] = [{"method": "clock"}]
        configs.extend(
            {"method": "discrete", "ncategories": value} for value in ncategories
        )
        for method in ("uncorrelated_lognormal", "correlated"):
            configs.extend({"method": method, "lam": value} for value in lambdas)
    else:
        configs = [dict(value) for value in candidate_configs]
    if not configs:
        raise ToytreeError("candidate_configs must contain at least one model.")

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for raw in configs:
        method = str(raw.get("method", "")).lower()
        if method not in METHOD_ORDER:
            raise ToytreeError(
                f"invalid CV candidate method {method!r}; expected one of "
                f"{list(METHOD_ORDER)}."
            )
        if method == "clock":
            config = {"method": method}
            key = (method,)
        elif method == "discrete":
            value = _validate_ncategories(raw.get("ncategories"), tree.nedges)
            config = {"method": method, "ncategories": value}
            key = (method, value)
        else:
            value = _validate_lambda(raw.get("lam"))
            config = {"method": method, "lam": value}
            key = (method, value)
        if key not in seen:
            seen.add(key)
            normalized.append(config)
    return normalized


def _fit_candidate(
    tree: ToyTree,
    config: dict[str, Any],
    calibrations: dict[Any, Any],
    observation_mask: np.ndarray | None,
    fit_options: dict[str, Any],
) -> dict[str, Any]:
    """Fit one configured model, optionally excluding observations."""
    method = config["method"]
    options = dict(fit_options)
    if options.get("nstarts") is None:
        options["nstarts"] = 4 if method == "discrete" else 1
    common = dict(
        calibrations=calibrations,
        full=True,
        inplace=False,
        _observation_mask=observation_mask,
        **options,
    )
    if method == "clock":
        return edges_make_ultrametric_clock(tree, **common)
    if method == "discrete":
        return edges_make_ultrametric_discrete(
            tree, ncategories=config["ncategories"], **common
        )
    if method == "relaxed":
        return edges_make_ultrametric_relaxed(tree, lam=config["lam"], **common)
    if method == "uncorrelated_lognormal":
        return edges_make_ultrametric_uncorrelated_lognormal(
            tree, lam=config["lam"], **common
        )
    return edges_make_ultrametric_correlated(tree, lam=config["lam"], **common)


def _fit_cv_fold(payload: dict[str, Any]) -> dict[str, Any]:
    """Fit and score one terminal-edge holdout."""
    tree = payload["tree"]
    edge_index = int(payload["edge_index"])
    child_index = int(payload["child_index"])
    observed = float(payload["observed"])
    all_dists = np.asarray(payload["all_dists"], dtype=float)
    mask = np.ones(tree.nedges, dtype=bool)
    mask[edge_index] = False

    # The held observation is also removed from all initialization heuristics.
    training = all_dists[mask]
    positive = training[training > 0.0]
    replacement = float(np.median(positive)) if positive.size else 1.0
    fit_tree = tree.set_node_data("dist", {child_index: replacement}, inplace=False)
    try:
        fit = _fit_candidate(
            fit_tree,
            payload["config"],
            payload["calibrations"],
            mask,
            payload["fit_options"],
        )
        predicted = float(fit["expected_branch_lengths"][edge_index])
        converged = bool(fit["converged"]) and np.isfinite(predicted)
        score = (
            _prediction_score(observed, predicted, payload.get("score", "pearson"))
            if converged
            else float("inf")
        )
        return {
            "fold": int(payload["fold"]),
            "edge_index": edge_index,
            "child_index": child_index,
            "observed": observed,
            "predicted": predicted,
            "score": score,
            "pseudologlik": float(fit["pseudologlik"]),
            "penalized_pseudologlik": float(fit["penalized_pseudologlik"]),
            "penalty": (None if "penalty" not in fit else float(fit["penalty"])),
            "converged": converged,
            "optimizer_message": str(fit.get("optimizer_message", "")),
            "nparams": int(fit["nparams"]),
        }
    except Exception as exc:
        return {
            "fold": int(payload["fold"]),
            "edge_index": edge_index,
            "child_index": child_index,
            "observed": observed,
            "predicted": float("nan"),
            "score": float("inf"),
            "pseudologlik": None,
            "penalized_pseudologlik": None,
            "penalty": None,
            "converged": False,
            "optimizer_message": f"{type(exc).__name__}: {exc}",
            "nparams": int(1e9),
        }


def _select_candidate_summaries(
    summaries: list[dict[str, Any]],
    selection_rule: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Annotate candidate summaries and return selected and minimum candidates."""
    finite = [value for value in summaries if value["valid"]]
    if not finite:
        raise RuntimeError("all cross-validation candidates had a failed fold.")
    minimum = min(value["mean_score"] for value in finite)
    tied = [value for value in finite if abs(value["mean_score"] - minimum) <= CV_EPS]
    minimum_candidate = min(tied, key=_minimum_tie_key)
    minimum_scores = np.asarray(
        [value["score"] for value in minimum_candidate["folds"]], dtype=float
    )
    for candidate in summaries:
        if not candidate["valid"]:
            candidate["paired_excess"] = float("inf")
            candidate["paired_standard_error"] = float("inf")
            candidate["one_se_eligible"] = False
            continue
        candidate_scores = np.asarray(
            [value["score"] for value in candidate["folds"]], dtype=float
        )
        differences = candidate_scores - minimum_scores
        paired_excess = float(np.mean(differences))
        paired_se = (
            float(np.std(differences, ddof=1) / np.sqrt(differences.size))
            if differences.size > 1
            else 0.0
        )
        candidate["paired_excess"] = paired_excess
        candidate["paired_standard_error"] = paired_se
        candidate["one_se_eligible"] = bool(paired_excess <= paired_se + CV_EPS)

    if selection_rule == "one_se":
        eligible = [value for value in finite if value["one_se_eligible"]]
        winner = min(eligible, key=_simplicity_key)
    else:
        winner = minimum_candidate
    return winner, minimum_candidate


def _historical_cv_model_select(
    tree: ToyTree,
    calibrations: dict[Any, Any] | None = None,
    candidate_configs: Iterable[dict[str, Any]] | None = None,
    ncategories: Iterable[int] = DEFAULT_NCATEGORIES,
    lambdas: Iterable[float] = DEFAULT_LAMBDAS,
    max_iter: int = 100_000,
    max_fun: int = 100_000,
    max_refine: int = 20,
    nstarts: int | None = None,
    ncores: int = 1,
    seed: int | None = None,
    selection_rule: Literal["one_se", "minimum"] = "one_se",
    score: Literal["pearson", "poisson_deviance", "relative_squared"] = "pearson",
) -> dict[str, Any]:
    """Reproduce the rejected cross-family v2 validation selector.

    This is deliberately private. It remains only so the archived v1/v2
    validation studies can be reproduced and rescored from their caches.
    """
    if isinstance(ncores, bool) or not isinstance(ncores, (int, np.integer)):
        raise ToytreeError("ncores must be a positive integer.")
    if int(ncores) < 1:
        raise ToytreeError("ncores must be a positive integer.")
    if seed is not None and (
        isinstance(seed, bool) or not isinstance(seed, (int, np.integer))
    ):
        raise ToytreeError("seed must be an integer or None.")
    if selection_rule not in SELECTION_RULES:
        raise ToytreeError(f"selection_rule must be one of {list(SELECTION_RULES)}.")
    if score not in SCORE_NAMES:
        raise ToytreeError(f"score must be one of {list(SCORE_NAMES)}.")

    calibrations = {} if calibrations is None else dict(calibrations)
    configs = _normalize_candidates(tree, candidate_configs, ncategories, lambdas)
    dists = _validate_branch_lengths(tree)
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    terminal = [
        (eidx, int(child))
        for eidx, (child, _) in enumerate(edges)
        if int(child) < tree.ntips
    ]
    if len(terminal) < 2:
        raise ToytreeError("terminal-edge CV requires a tree with at least two tips.")

    fit_options_base = {
        "max_iter": int(max_iter),
        "max_fun": int(max_fun),
        "max_refine": int(max_refine),
        "nstarts": None if nstarts is None else int(nstarts),
        "ncores": 1,
    }
    payloads: list[dict[str, Any]] = []
    for cidx, config in enumerate(configs):
        for fold, (edge_index, child_index) in enumerate(terminal):
            fold_seed = (
                None if seed is None else int(seed) + cidx * len(terminal) + fold
            )
            payloads.append(
                {
                    "tree": tree,
                    "config": config,
                    "candidate_index": cidx,
                    "fold": fold,
                    "edge_index": edge_index,
                    "child_index": child_index,
                    "observed": float(dists[edge_index]),
                    "all_dists": dists,
                    "calibrations": calibrations,
                    "score": score,
                    "fit_options": {**fit_options_base, "seed": fold_seed},
                }
            )

    if int(ncores) == 1:
        fold_results = []
        for payload in payloads:
            result = _fit_cv_fold(payload)
            result["candidate_index"] = payload["candidate_index"]
            fold_results.append(result)
    else:
        workers = max(1, min(int(ncores), len(payloads)))
        fold_results = []
        try:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                future_map = {
                    pool.submit(_fit_cv_fold, payload): payload["candidate_index"]
                    for payload in payloads
                }
                for future in as_completed(future_map):
                    result = future.result()
                    result["candidate_index"] = future_map[future]
                    fold_results.append(result)
        except (PermissionError, OSError) as exc:
            logger.warning(f"ProcessPool unavailable; using serial CV: {exc}")
            fold_results = []
            for payload in payloads:
                result = _fit_cv_fold(payload)
                result["candidate_index"] = payload["candidate_index"]
                fold_results.append(result)
        fold_results.sort(key=lambda value: (value["candidate_index"], value["fold"]))

    summaries: list[dict[str, Any]] = []
    for cidx, config in enumerate(configs):
        folds = [value for value in fold_results if value["candidate_index"] == cidx]
        valid = len(folds) == len(terminal) and all(
            value["converged"] for value in folds
        )
        scores = np.asarray([value["score"] for value in folds], dtype=float)
        valid = bool(valid and np.all(np.isfinite(scores)))
        mean = float(np.mean(scores)) if valid else float("inf")
        se = (
            float(np.std(scores, ddof=1) / np.sqrt(scores.size))
            if valid and scores.size > 1
            else (0.0 if valid else float("inf"))
        )
        nparams_value = min((value["nparams"] for value in folds), default=int(1e9))
        summaries.append(
            {
                "config": dict(config),
                "label": _candidate_label(config),
                "valid": valid,
                "mean_score": mean,
                "standard_error": se,
                "nparams": int(nparams_value),
                "folds": folds,
            }
        )

    winner, minimum_candidate = _select_candidate_summaries(summaries, selection_rule)
    selected_config = dict(winner["config"])
    selected_fit = _fit_candidate(
        tree,
        selected_config,
        calibrations,
        None,
        {**fit_options_base, "ncores": int(ncores), "seed": seed},
    )
    if not selected_fit["converged"]:
        raise RuntimeError("the selected model failed to converge on the full dataset.")
    return {
        "selection_method": "leave_one_terminal_edge_out",
        "selection_rule": selection_rule,
        "score": score,
        "minimum_config": dict(minimum_candidate["config"]),
        "selected_config": selected_config,
        "selected_fit": selected_fit,
        "mean_score": float(winner["mean_score"]),
        "standard_error": float(winner["standard_error"]),
        "candidates": summaries,
        "nfolds": len(terminal),
        "seed": None if seed is None else int(seed),
        "ncores": int(ncores),
    }
