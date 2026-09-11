#!/usr/bin/env python

"""Paired, task-parallel ToyTree versus ape::chronos benchmark."""

# ruff: noqa: E402 -- thread limits must precede NumPy/SciPy imports.

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

for _name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_name] = "1"

import numpy as np
import scipy
from scipy.stats import spearmanr

import toytree
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
from validation.penalized_pseudolikelihood.simulation_helpers import (
    _scale_true_tree,
    _simulate_rates,
)

toytree.set_log_level("WARNING")

CONFIG_PATH = HERE / "config-v17.json"
R_RUNNER = HERE / "run_chronos_v17.R"
DEFAULT_OUTPUT = HERE / "v17"
DATASET_SCHEMA = 1
FIT_CACHE_SCHEMA = 1
ROOT_CLADE = "__root__"


def _atomic_json(path: Path, value: Any) -> None:
    """Write JSON atomically so interrupted jobs leave no valid cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _json_hash(value: Any) -> str:
    """Return a stable SHA256 digest for JSON-compatible content."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _function_hash(*functions: Callable[..., Any]) -> str:
    """Hash selected functions that affect generated or fitted results."""
    digest = hashlib.sha256()
    for function in functions:
        digest.update(function.__name__.encode())
        digest.update(inspect.getsource(function).encode())
    return digest.hexdigest()


def _clade(node: Any) -> str:
    """Return a stable, engine-independent node identifier."""
    if node.is_root():
        return ROOT_CLADE
    return "|".join(sorted(leaf.name for leaf in node.iter_leaves()))


def _age_map(tree: Any) -> dict[str, float]:
    """Return internal-node ages indexed by descendant-tip clade."""
    return {
        _clade(node): float(node.height)
        for node in tree.treenode.traverse("preorder")
        if not node.is_leaf()
    }


def _rate_map(tree: Any, rates: np.ndarray) -> dict[str, float]:
    """Return edge rates indexed by the descendant node's clade."""
    return {
        _clade(tree[int(child)]): float(rates[idx])
        for idx, (child, _) in enumerate(tree.get_edges("idx"))
    }


def _calibrations(tree: Any, regime: str) -> list[dict[str, Any]]:
    """Return engine-independent truth-containing calibration records."""
    records = [{"clade": ROOT_CLADE, "lower": 1.0, "upper": 1.0}]
    if regime == "root":
        return records
    if regime != "root_and_internal_interval":
        raise ValueError(f"unknown calibration regime: {regime}")
    candidates = [
        node
        for node in tree.treenode.traverse("preorder")
        if not node.is_root() and not node.is_leaf()
    ]
    node = max(candidates, key=lambda item: (item.height, item.idx))
    records.append(
        {
            "clade": _clade(node),
            "lower": 0.9 * float(node.height),
            "upper": 1.1 * float(node.height),
        }
    )
    return records


def _resolve_calibrations(tree: Any, records: list[dict[str, Any]]) -> dict[int, Any]:
    """Resolve clade records to ToyTree node indices."""
    result = {}
    for record in records:
        if record["clade"] == ROOT_CLADE:
            idx = -1
        else:
            idx = int(tree.get_mrca_node(*record["clade"].split("|")).idx)
        lower = float(record["lower"])
        upper = float(record["upper"])
        result[idx] = lower if lower == upper else (lower, upper)
    return result


def _scenario_rates(
    tree: Any,
    scenario: dict[str, Any],
    rng: np.random.Generator,
    baseline: float,
) -> np.ndarray:
    """Simulate branch rates under one frozen scenario."""
    generator = scenario["generator"]
    if generator == "clock":
        return np.full(tree.nedges, baseline)
    if generator == "discrete":
        multipliers = np.asarray(scenario["rate_multipliers"], dtype=float)
        categories = np.resize(np.arange(multipliers.size), tree.nedges)
        rng.shuffle(categories)
        return baseline * multipliers[categories]
    if generator in {"correlated", "uncorrelated_lognormal"}:
        simulation = {
            "baseline_rate": baseline,
            "correlated_log_sigma": float(scenario.get("sigma_log", 0.3)),
            "uncorrelated_log_sigma": float(scenario.get("sigma_log", 0.3)),
        }
        return _simulate_rates(tree, generator, rng, simulation)
    if generator == "independent_gamma":
        shape = float(scenario["rate_gamma_shape"])
        rates = rng.gamma(shape, baseline / shape, size=tree.nedges)
        return rates * (baseline / rates.mean())
    raise ValueError(f"unknown rate generator: {generator}")


def _simulate_dataset(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate one shared manifest for both fitting engines."""
    rng = np.random.default_rng(int(payload["seed"]))
    tree = _scale_true_tree(int(payload["ntips"]), int(payload["seed"]))
    scenario = payload["scenario_config"]
    rates = _scenario_rates(
        tree, scenario, rng, float(payload["simulation"]["baseline_rate"])
    )
    edges = np.asarray(tree.get_edges("idx"), dtype=int)
    ages = tree.get_node_data("height").to_numpy(dtype=float)
    times = ages[edges[:, 1]] - ages[edges[:, 0]]
    expected = times * rates
    observation_model = payload["observation_model"]
    if observation_model == "expected_branch":
        observed = expected.copy()
    elif observation_model == "fractional_poisson":
        observed = rng.poisson(expected).astype(float)
    elif observation_model == "continuous_gamma":
        shape = float(payload["simulation"]["observation_gamma_shape"])
        observed = expected * rng.gamma(shape, 1.0 / shape, size=expected.size)
    else:
        raise ValueError(f"unknown observation model: {observation_model}")
    observed_tree = tree.set_node_data(
        "dist",
        {int(child): float(observed[idx]) for idx, (child, _) in enumerate(edges)},
        inplace=False,
    )
    return {
        "dataset_schema": DATASET_SCHEMA,
        "dataset_id": payload["dataset_id"],
        "mode": payload["mode"],
        "scenario": payload["scenario"],
        "fit_model": scenario["fit_model"],
        "ape_model": scenario.get("ape_model"),
        "ncategories": scenario.get("ncategories"),
        "lambda": scenario.get("lambda"),
        "ntips": int(payload["ntips"]),
        "calibration": payload["calibration"],
        "observation_model": observation_model,
        "replicate": int(payload["replicate"]),
        "seed": int(payload["seed"]),
        "true_tree_newick": tree.write(dist_formatter="%.17g", internal_labels=None),
        "observed_tree_newick": observed_tree.write(
            dist_formatter="%.17g", internal_labels=None
        ),
        "true_ages": _age_map(tree),
        "true_rates": _rate_map(tree, rates),
        "calibrations": _calibrations(tree, payload["calibration"]),
        "zero_branch_count": int(np.count_nonzero(observed == 0.0)),
        "expected_branch_mean": float(expected.mean()),
    }


def _generation_source_hash(config: dict[str, Any]) -> str:
    """Hash simulation code and configuration inputs."""
    return _json_hash(
        {
            "functions": _function_hash(
                _scale_true_tree,
                _simulate_rates,
                _clade,
                _age_map,
                _rate_map,
                _calibrations,
                _scenario_rates,
                _simulate_dataset,
            ),
            "simulation": config["simulation"],
            "scenarios": config["scenarios"],
            "schema": DATASET_SCHEMA,
        }
    )


def _dataset_id(
    scenario: str,
    ntips: int,
    calibration: str,
    observation_model: str,
    replicate: int,
) -> str:
    """Return a deterministic filesystem-safe dataset identifier."""
    return f"{scenario}-n{ntips}-{calibration}-{observation_model}-" f"r{replicate:04d}"


def _dataset_payloads(config: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    """Enumerate the frozen paired dataset stream."""
    spec = config["modes"][mode]
    seed_base = int(
        config["confirmation_seed"]
        if mode == "confirmation"
        else config["development_seed"]
    )
    payloads = []
    index = 0
    for scenario in config["scenarios"]:
        for ntips in spec["ntips"]:
            for calibration in spec["calibrations"]:
                for observation_model in spec["observation_models"]:
                    for replicate in range(int(spec["replicates"])):
                        dataset_id = _dataset_id(
                            scenario["id"],
                            int(ntips),
                            calibration,
                            observation_model,
                            replicate,
                        )
                        payloads.append(
                            {
                                "dataset_id": dataset_id,
                                "mode": mode,
                                "scenario": scenario["id"],
                                "scenario_config": scenario,
                                "ntips": int(ntips),
                                "calibration": calibration,
                                "observation_model": observation_model,
                                "replicate": replicate,
                                "seed": seed_base + index * 100_003,
                                "simulation": config["simulation"],
                            }
                        )
                        index += 1
    return payloads


def _manifest_path(output_dir: Path, mode: str, dataset_id: str) -> Path:
    """Return the path for one shared dataset manifest."""
    return output_dir / "cache-v17" / mode / "datasets" / f"{dataset_id}.json"


def _generate_manifests(
    config: dict[str, Any], mode: str, output_dir: Path
) -> list[Path]:
    """Generate or verify all shared paired-input manifests."""
    source_hash = _generation_source_hash(config)
    paths = []
    for payload in _dataset_payloads(config, mode):
        path = _manifest_path(output_dir, mode, payload["dataset_id"])
        fingerprint = _json_hash(
            {
                "payload": payload,
                "source_hash": source_hash,
                "schema": DATASET_SCHEMA,
            }
        )
        if path.exists():
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") != fingerprint:
                raise RuntimeError(f"stale dataset manifest: {path}")
        else:
            record = _simulate_dataset(payload)
            record["generation_source_hash"] = source_hash
            record["fingerprint"] = fingerprint
            _atomic_json(path, record)
        paths.append(path)
    return paths


def _solver_hash(model: str) -> str:
    """Hash ToyTree implementation files relevant to one model."""
    root = REPO / "toytree" / "mod" / "_src" / "penalized_pseudolikelihood"
    dependencies = {
        "clock": ("clock.py",),
        "discrete": ("discrete.py", "clock.py"),
        "correlated": ("correlated.py", "clock.py"),
        "uncorrelated_lognormal": (
            "uncorrelated_lognormal.py",
            "clock.py",
        ),
        "relaxed": (
            "relaxed.py",
            "uncorrelated_lognormal.py",
            "clock.py",
        ),
    }
    digest = hashlib.sha256()
    for name in (*dependencies[model], "optimization.py", "utils.py"):
        path = root / name
        digest.update(name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _fit_source_hash(engine: str, model: str) -> str:
    """Hash engine code affecting fitted values, excluding scoring code."""
    if engine == "ape":
        return hashlib.sha256(R_RUNNER.read_bytes()).hexdigest()
    return _json_hash(
        {
            "solver": _solver_hash(model),
            "fit_functions": _function_hash(
                _resolve_calibrations,
                _fit_toytree,
                _slim_toytree_fit,
            ),
        }
    )


def _task_path(output_dir: Path, mode: str, dataset_id: str, engine: str) -> Path:
    """Return one independently resumable fit-cache path."""
    return output_dir / "cache-v17" / mode / f"{dataset_id}-{engine}.json"


def _task_payloads(
    manifests: list[Path], config: dict[str, Any], output_dir: Path
) -> list[dict[str, Any]]:
    """Expand datasets into one global engine-task pool."""
    tasks = []
    for manifest in manifests:
        dataset = json.loads(manifest.read_text())
        engines = ["toytree"] + (["ape"] if dataset["ape_model"] else [])
        for engine in engines:
            model = (
                dataset["fit_model"] if engine == "toytree" else dataset["ape_model"]
            )
            source_hash = _fit_source_hash(engine, model)
            engine_options = (
                {
                    "max_iter": config["fit"]["max_iter"],
                    "max_fun": config["fit"]["max_fun"],
                    "max_refine": config["fit"]["max_refine"],
                    "nstarts": config["fit"]["toytree_nstarts"][model],
                }
                if engine == "toytree"
                else {"chronos_control": "ape::chronos.control defaults"}
            )
            fingerprint = _json_hash(
                {
                    "dataset_fingerprint": dataset["fingerprint"],
                    "engine": engine,
                    "model": model,
                    "engine_options": engine_options,
                    "expected_ape_version": (
                        config["expected_ape_version"] if engine == "ape" else None
                    ),
                    "source_hash": source_hash,
                    "schema": FIT_CACHE_SCHEMA,
                }
            )
            tasks.append(
                {
                    "manifest_path": str(manifest),
                    "cache_path": str(
                        _task_path(
                            output_dir,
                            dataset["mode"],
                            dataset["dataset_id"],
                            engine,
                        )
                    ),
                    "engine": engine,
                    "model": model,
                    "fit_options": config["fit"],
                    "expected_ape_version": config["expected_ape_version"],
                    "source_hash": source_hash,
                    "fingerprint": fingerprint,
                }
            )
    return tasks


def _timing_tasks(
    tasks: list[dict[str, Any]],
    config: dict[str, Any],
    mode: str,
    output_dir: Path,
) -> list[dict[str, Any]]:
    """Select a paired subset for serial, low-contention timing."""
    spec = config["modes"][mode]
    timing_replicates = int(spec["timing_replicates"])
    calibration = (
        "root_and_internal_interval"
        if "root_and_internal_interval" in spec["calibrations"]
        else spec["calibrations"][0]
    )
    observation = (
        "continuous_gamma"
        if "continuous_gamma" in spec["observation_models"]
        else spec["observation_models"][0]
    )
    grouped = defaultdict(list)
    for task in tasks:
        dataset = json.loads(Path(task["manifest_path"]).read_text())
        if (
            dataset["replicate"] < timing_replicates
            and dataset["calibration"] == calibration
            and dataset["observation_model"] == observation
        ):
            grouped[dataset["dataset_id"]].append((dataset, task))
    selected = []
    for dataset_id in sorted(grouped):
        group = sorted(grouped[dataset_id], key=lambda item: item[1]["engine"])
        if group[0][0]["replicate"] % 2:
            group.reverse()
        for dataset, task in group:
            timing = dict(task)
            timing["cache_path"] = str(
                output_dir
                / "cache-v17"
                / mode
                / "timing"
                / f"{dataset_id}-{task['engine']}.json"
            )
            timing["fingerprint"] = _json_hash(
                {
                    "fit_fingerprint": task["fingerprint"],
                    "protocol": "serial-alternating-v1",
                }
            )
            selected.append(timing)
    return selected


def _optional_float(value: Any) -> float | None:
    """Return a finite float or None."""
    if value in (None, ""):
        return None
    value = float(value)
    return value if np.isfinite(value) else None


def _optional_int(value: Any) -> int | None:
    """Return an integer or None."""
    return None if value is None else int(value)


def _slim_toytree_fit(fit: dict[str, Any], elapsed: float) -> dict[str, Any]:
    """Return JSON-native ToyTree values needed for scoring."""
    rates = np.asarray(fit.get("rates", [fit.get("rate", np.nan)]), dtype=float)
    rate_clades = []
    if rates.size == fit["tree"].nedges:
        rate_clades = [
            _clade(fit["tree"][int(child)]) for child, _ in fit["tree"].get_edges("idx")
        ]
    return {
        "status": "ok",
        "converged": bool(fit.get("converged", True)),
        "elapsed_seconds": float(elapsed),
        "tree_newick": fit["tree"].write(dist_formatter="%.17g", internal_labels=None),
        "rates": rates.tolist(),
        "rate_clades": rate_clades,
        "frequencies": [float(value) for value in fit.get("weights", [])],
        "pseudologlik": _optional_float(fit.get("pseudologlik")),
        "penalized_pseudologlik": _optional_float(fit.get("penalized_pseudologlik")),
        "optimizer_message": str(fit.get("optimizer_message", "")),
        "nfev": _optional_int(fit.get("nfev")),
        "nit": _optional_int(fit.get("nit")),
        "direct_age_fallback_used": fit.get("direct_age_fallback_used"),
        "direct_age_fallback_converged": fit.get("direct_age_fallback_converged"),
        "direct_age_fallback_accepted": fit.get("direct_age_fallback_accepted"),
        "solution_stable": fit.get("solution_stable"),
        "near_optimal_starts": _optional_int(fit.get("near_optimal_starts")),
    }


def _fit_toytree(dataset: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    """Fit one ToyTree model, timing only the estimator call."""
    tree = toytree.tree(dataset["observed_tree_newick"])
    calibrations = _resolve_calibrations(tree, dataset["calibrations"])
    model = dataset["fit_model"]
    common = {
        "tree": tree,
        "calibrations": calibrations,
        "full": True,
        "inplace": False,
        "max_iter": int(options["max_iter"]),
        "max_fun": int(options["max_fun"]),
        "max_refine": int(options["max_refine"]),
        "nstarts": int(options["toytree_nstarts"][model]),
        "ncores": 1,
        "seed": int(dataset["seed"]) + 7_919,
    }
    started = time.perf_counter()
    if model == "clock":
        fit = edges_make_ultrametric_clock(**common)
    elif model == "discrete":
        fit = edges_make_ultrametric_discrete(
            ncategories=int(dataset["ncategories"]), **common
        )
    elif model == "correlated":
        fit = edges_make_ultrametric_correlated(lam=float(dataset["lambda"]), **common)
    elif model == "relaxed":
        fit = edges_make_ultrametric_relaxed(lam=float(dataset["lambda"]), **common)
    elif model == "uncorrelated_lognormal":
        fit = edges_make_ultrametric_uncorrelated_lognormal(
            lam=float(dataset["lambda"]), **common
        )
    else:
        raise ValueError(f"unknown ToyTree model: {model}")
    return _slim_toytree_fit(fit, time.perf_counter() - started)


def _parse_protocol(stdout: str) -> dict[str, str]:
    """Parse the R adapter's two-column key/value protocol."""
    values = {}
    for line in stdout.splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
            values[key] = value
    if values.get("protocol") != "toytree-chronos-v17":
        raise RuntimeError(f"invalid chronos adapter output: {stdout[-1000:]}")
    return values


def _parse_float_list(value: str) -> list[float]:
    """Parse a comma-separated numeric vector from R."""
    if not value.strip():
        return []
    return [float(item.strip()) for item in value.split(",")]


def _fit_ape(dataset: dict[str, Any], expected_version: str) -> dict[str, Any]:
    """Fit one ape::chronos model through the standalone R adapter."""
    with tempfile.TemporaryDirectory(prefix="toytree-v17-") as directory:
        directory = Path(directory)
        tree_path = directory / "tree.nwk"
        calibration_path = directory / "calibrations.tsv"
        tree_path.write_text(dataset["observed_tree_newick"] + "\n")
        with calibration_path.open("w", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=("clade", "lower", "upper"),
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(dataset["calibrations"])
        command = [
            "Rscript",
            str(R_RUNNER),
            str(tree_path),
            str(calibration_path),
            str(dataset["ape_model"]),
            str(dataset.get("lambda") or 1.0),
            str(dataset.get("ncategories") or 1),
            expected_version,
        ]
        process = subprocess.run(command, capture_output=True, text=True, check=False)
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())
    values = _parse_protocol(process.stdout)
    if values.get("status") != "ok":
        return {
            "status": "error",
            "converged": False,
            "elapsed_seconds": _optional_float(values.get("elapsed_seconds")),
            "ape_version": values.get("ape_version"),
            "error": values.get("error", "unknown chronos error"),
            "warnings": values.get("warnings", ""),
        }
    convergence = values.get("convergence", "")
    return {
        "status": "ok",
        "converged": values.get("converged", "").lower() == "true",
        "elapsed_seconds": float(values["elapsed_seconds"]),
        "ape_version": values["ape_version"],
        "tree_newick": values["tree_newick"],
        "rates": _parse_float_list(values.get("rates", "")),
        "rate_clades": [
            item for item in values.get("rate_clades", "").split(",") if item
        ],
        "frequencies": _parse_float_list(values.get("frequencies", "")),
        "pseudologlik": _optional_float(values.get("loglik")),
        "penalized_pseudologlik": _optional_float(values.get("penalized_loglik")),
        "optimizer_message": values.get("message", ""),
        "convergence_code": convergence or None,
        "warnings": values.get("warnings", ""),
    }


def _fit_worker(payload: dict[str, Any]) -> str:
    """Run and atomically cache one independent engine fit."""
    path = Path(payload["cache_path"])
    if payload["resume"] and path.exists():
        try:
            cached = json.loads(path.read_text())
            if cached.get("fingerprint") == payload["fingerprint"]:
                return str(path)
        except (OSError, json.JSONDecodeError):
            pass
    dataset = json.loads(Path(payload["manifest_path"]).read_text())
    try:
        if payload["engine"] == "toytree":
            fit = _fit_toytree(dataset, payload["fit_options"])
        else:
            fit = _fit_ape(dataset, payload["expected_ape_version"])
    except Exception as error:
        fit = {
            "status": "error",
            "converged": False,
            "elapsed_seconds": None,
            "error": f"{type(error).__name__}: {error}",
        }
    _atomic_json(
        path,
        {
            "cache_schema": FIT_CACHE_SCHEMA,
            "fingerprint": payload["fingerprint"],
            "source_hash": payload["source_hash"],
            "dataset_id": dataset["dataset_id"],
            "engine": payload["engine"],
            "fit": fit,
        },
    )
    return str(path)


def _run_tasks(tasks: list[dict[str, Any]], ncores: int, resume: bool) -> None:
    """Execute one global task pool and report resumable progress."""
    for task in tasks:
        task["resume"] = resume
    started = time.perf_counter()
    workers = (os.cpu_count() or 1) if ncores == 0 else ncores
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_fit_worker, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), 1):
            future.result()
            if completed == len(tasks) or completed % max(1, len(tasks) // 100) == 0:
                print(
                    json.dumps(
                        {
                            "event": "fit_progress",
                            "completed": completed,
                            "total": len(tasks),
                            "elapsed_seconds": time.perf_counter() - started,
                        }
                    ),
                    flush=True,
                )


def _read_fit(task: dict[str, Any]) -> dict[str, Any]:
    """Read one required fit cache and enforce its fingerprint."""
    path = Path(task["cache_path"])
    if not path.exists():
        raise FileNotFoundError(f"missing fit cache: {path}")
    cached = json.loads(path.read_text())
    if cached.get("fingerprint") != task["fingerprint"]:
        raise RuntimeError(f"stale fit cache: {path}")
    return cached


def _fit_age_map(fit: dict[str, Any]) -> dict[str, float]:
    """Return fitted internal ages, or an empty map on failure."""
    if fit.get("status") != "ok" or not fit.get("tree_newick"):
        return {}
    return _age_map(toytree.tree(fit["tree_newick"]))


def _calibrations_valid(
    ages: dict[str, float],
    calibrations: list[dict[str, Any]],
    tolerance: float = 1e-6,
) -> bool:
    """Return whether a fitted chronogram satisfies every calibration."""
    if not ages:
        return False
    for record in calibrations:
        value = ages.get(record["clade"])
        if value is None:
            return False
        scale = max(1.0, abs(float(record["upper"])))
        if value < float(record["lower"]) - tolerance * scale:
            return False
        if value > float(record["upper"]) + tolerance * scale:
            return False
    return True


def _safe_spearman(x: list[float], y: list[float]) -> float | None:
    """Return a finite Spearman correlation or None."""
    if len(x) < 2 or np.ptp(x) == 0.0 or np.ptp(y) == 0.0:
        return None
    value = float(spearmanr(x, y).statistic)
    return value if np.isfinite(value) else None


def _score_fit(dataset: dict[str, Any], cached: dict[str, Any]) -> dict[str, Any]:
    """Score one engine fit against the shared simulated truth."""
    fit = cached["fit"]
    ages = _fit_age_map(fit)
    true_ages = dataset["true_ages"]
    clades = sorted(set(true_ages) - {ROOT_CLADE})
    root_age = float(true_ages[ROOT_CLADE])
    if ages and all(clade in ages for clade in clades):
        errors = np.asarray([ages[clade] - true_ages[clade] for clade in clades])
        age_mae = float(np.mean(np.abs(errors)) / root_age)
        age_rmse = float(np.sqrt(np.mean(errors**2)) / root_age)
        age_bias = float(np.mean(errors) / root_age)
    else:
        age_mae = age_rmse = age_bias = None
    rate_spearman = None
    rate_clades = fit.get("rate_clades", [])
    rates = fit.get("rates", [])
    if rate_clades and len(rate_clades) == len(rates):
        pairs = [
            (float(dataset["true_rates"][clade]), float(rate))
            for clade, rate in zip(rate_clades, rates)
            if clade in dataset["true_rates"]
        ]
        if pairs:
            rate_spearman = _safe_spearman(
                [value[0] for value in pairs],
                [value[1] for value in pairs],
            )
    calibrations_valid = _calibrations_valid(ages, dataset["calibrations"])
    converged = bool(fit.get("converged", False))
    status = fit.get("status", "error")
    accuracy_eligible = bool(
        status == "ok"
        and converged
        and calibrations_valid
        and age_mae is not None
        and age_rmse is not None
    )
    return {
        "dataset_id": dataset["dataset_id"],
        "scenario": dataset["scenario"],
        "model": dataset["fit_model"],
        "engine": cached["engine"],
        "ntips": dataset["ntips"],
        "calibration": dataset["calibration"],
        "observation_model": dataset["observation_model"],
        "replicate": dataset["replicate"],
        "seed": dataset["seed"],
        "zero_branch_count": dataset["zero_branch_count"],
        "status": status,
        "converged": converged,
        "calibrations_valid": calibrations_valid,
        "accuracy_eligible": accuracy_eligible,
        "elapsed_seconds": fit.get("elapsed_seconds"),
        "normalized_age_mae": age_mae,
        "normalized_age_rmse": age_rmse,
        "normalized_age_bias": age_bias,
        "rate_spearman": rate_spearman,
        "pseudologlik": fit.get("pseudologlik"),
        "penalized_pseudologlik": fit.get("penalized_pseudologlik"),
        "error": fit.get("error"),
        "optimizer_message": fit.get("optimizer_message", fit.get("message", "")),
        "warnings": fit.get("warnings", ""),
    }


def _pair_score(
    dataset: dict[str, Any], caches: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    """Return paired ToyTree/ape contrasts for one shared dataset."""
    if set(caches) != {"toytree", "ape"}:
        return None
    toy = caches["toytree"]["fit"]
    ape = caches["ape"]["fit"]
    toy_ages = _fit_age_map(toy)
    ape_ages = _fit_age_map(ape)
    common = sorted((set(toy_ages) & set(ape_ages)) - {ROOT_CLADE})
    root_age = float(dataset["true_ages"][ROOT_CLADE])
    maximum_age_difference = None
    if common:
        maximum_age_difference = float(
            max(abs(toy_ages[key] - ape_ages[key]) for key in common) / root_age
        )
    objective_kind = None
    if dataset["fit_model"] in {"clock", "discrete"}:
        objective_kind = "pseudologlik"
    elif dataset["fit_model"] == "relaxed":
        objective_kind = "penalized_pseudologlik"
    objective_difference = None
    if objective_kind:
        left = toy.get(objective_kind)
        right = ape.get(objective_kind)
        if left is not None and right is not None:
            objective_difference = float(left - right)
    toy_time = toy.get("elapsed_seconds")
    ape_time = ape.get("elapsed_seconds")
    runtime_ratio = None
    if toy_time is not None and ape_time is not None and float(ape_time) > 0.0:
        runtime_ratio = float(toy_time) / float(ape_time)
    both_succeeded = bool(toy.get("status") == "ok" and ape.get("status") == "ok")
    both_converged = bool(
        both_succeeded and toy.get("converged") and ape.get("converged")
    )
    both_calibrations_valid = bool(
        _calibrations_valid(toy_ages, dataset["calibrations"])
        and _calibrations_valid(ape_ages, dataset["calibrations"])
    )
    comparison_eligible = bool(
        both_converged
        and both_calibrations_valid
        and maximum_age_difference is not None
    )
    return {
        "dataset_id": dataset["dataset_id"],
        "scenario": dataset["scenario"],
        "model": dataset["fit_model"],
        "ntips": dataset["ntips"],
        "calibration": dataset["calibration"],
        "observation_model": dataset["observation_model"],
        "replicate": dataset["replicate"],
        "both_succeeded": both_succeeded,
        "both_converged": both_converged,
        "both_calibrations_valid": both_calibrations_valid,
        "comparison_eligible": comparison_eligible,
        "maximum_normalized_chronogram_difference": maximum_age_difference,
        "objective_kind": objective_kind,
        "toytree_minus_ape_objective": objective_difference,
        "toytree_over_ape_runtime": runtime_ratio,
    }


def _finite(values: list[Any]) -> np.ndarray:
    """Return finite values as a one-dimensional float array."""
    array = np.asarray(
        [np.nan if value is None else value for value in values], dtype=float
    )
    return array[np.isfinite(array)]


def _summary_stats(values: list[Any]) -> dict[str, Any]:
    """Return compact distribution summaries for finite values."""
    array = _finite(values)
    if not array.size:
        return {"n": 0, "median": None, "mean": None, "p90": None}
    return {
        "n": int(array.size),
        "median": float(np.median(array)),
        "mean": float(np.mean(array)),
        "p90": float(np.quantile(array, 0.9)),
    }


def _bootstrap_interval(
    rows: list[dict[str, Any]],
    statistic: Callable[[list[dict[str, Any]]], float],
    replicates: int,
    seed: int,
) -> dict[str, float | int | None]:
    """Return a deterministic percentile bootstrap interval."""
    if not rows:
        return {
            "replicates": replicates,
            "estimate": None,
            "lower": None,
            "upper": None,
        }
    estimate = float(statistic(rows))
    rng = np.random.default_rng(seed)
    values = np.empty(replicates)
    for idx in range(replicates):
        sample = [rows[item] for item in rng.integers(0, len(rows), len(rows))]
        values[idx] = statistic(sample)
    values = values[np.isfinite(values)]
    return {
        "replicates": replicates,
        "estimate": estimate,
        "lower": float(np.quantile(values, 0.025)) if values.size else None,
        "upper": float(np.quantile(values, 0.975)) if values.size else None,
    }


def _summarize(
    rows: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Summarize performance and paired contrasts by scenario."""
    engine_groups = defaultdict(list)
    for row in rows:
        engine_groups[(row["scenario"], row["engine"])].append(row)

    def summarize_engine_group(group: list[dict[str, Any]]) -> dict[str, Any]:
        eligible = [row for row in group if row["accuracy_eligible"]]
        return {
            "datasets": len(group),
            "fit_success_fraction": float(
                np.mean([row["status"] == "ok" for row in group])
            ),
            "convergence_fraction": float(np.mean([row["converged"] for row in group])),
            "calibration_validity_fraction": float(
                np.mean([row["calibrations_valid"] for row in group])
            ),
            "accuracy_eligible_fraction": float(len(eligible) / len(group)),
            "elapsed_seconds": _summary_stats(
                [row["elapsed_seconds"] for row in group]
            ),
            "normalized_age_mae": _summary_stats(
                [row["normalized_age_mae"] for row in eligible]
            ),
            "normalized_age_rmse": _summary_stats(
                [row["normalized_age_rmse"] for row in eligible]
            ),
            "normalized_age_mae_all_returned": _summary_stats(
                [row["normalized_age_mae"] for row in group]
            ),
            "normalized_age_rmse_all_returned": _summary_stats(
                [row["normalized_age_rmse"] for row in group]
            ),
            "rate_spearman": _summary_stats([row["rate_spearman"] for row in eligible]),
        }

    engines = {}
    for (scenario, engine), group in sorted(engine_groups.items()):
        engines[f"{scenario}:{engine}"] = summarize_engine_group(group)

    cell_groups = defaultdict(list)
    for row in rows:
        key = (
            row["scenario"],
            row["engine"],
            row["ntips"],
            row["calibration"],
            row["observation_model"],
        )
        cell_groups[key].append(row)
    cells = {}
    for key, group in sorted(cell_groups.items()):
        scenario, engine, ntips, calibration, observation = key
        label = f"{scenario}:{engine}:n{ntips}:{calibration}:{observation}"
        cells[label] = summarize_engine_group(group)
    pair_groups = defaultdict(list)
    for row in pairs:
        pair_groups[row["scenario"]].append(row)
    row_by_key = {(row["dataset_id"], row["engine"]): row for row in rows}
    paired = {}
    for offset, (scenario, group) in enumerate(sorted(pair_groups.items())):
        eligible_pairs = [row for row in group if row["comparison_eligible"]]
        valid_accuracy = []
        for pair in eligible_pairs:
            toy = row_by_key[(pair["dataset_id"], "toytree")]
            ape = row_by_key[(pair["dataset_id"], "ape")]
            if (
                toy["normalized_age_mae"] is not None
                and ape["normalized_age_mae"] is not None
            ):
                valid_accuracy.append(
                    {
                        "difference": toy["normalized_age_mae"]
                        - ape["normalized_age_mae"]
                    }
                )
        valid_runtime = [
            row
            for row in group
            if row["toytree_over_ape_runtime"] is not None
            and row["toytree_over_ape_runtime"] > 0.0
        ]
        paired[scenario] = {
            "datasets": len(group),
            "both_converged_fraction": float(
                np.mean([row["both_converged"] for row in group])
            ),
            "comparison_eligible_fraction": float(len(eligible_pairs) / len(group)),
            "maximum_normalized_chronogram_difference": _summary_stats(
                [
                    row["maximum_normalized_chronogram_difference"]
                    for row in eligible_pairs
                ]
            ),
            "objective_difference": _summary_stats(
                [row["toytree_minus_ape_objective"] for row in eligible_pairs]
            ),
            "maximum_normalized_chronogram_difference_all_returned": _summary_stats(
                [row["maximum_normalized_chronogram_difference"] for row in group]
            ),
            "objective_difference_all_returned": _summary_stats(
                [row["toytree_minus_ape_objective"] for row in group]
            ),
            "runtime_ratio": _summary_stats(
                [row["toytree_over_ape_runtime"] for row in group]
            ),
            "age_mae_difference_bootstrap": _bootstrap_interval(
                valid_accuracy,
                lambda sample: float(np.mean([row["difference"] for row in sample])),
                bootstrap_replicates,
                bootstrap_seed + offset * 2,
            ),
            "geometric_runtime_ratio_bootstrap": _bootstrap_interval(
                valid_runtime,
                lambda sample: float(
                    np.exp(
                        np.mean(
                            np.log([row["toytree_over_ape_runtime"] for row in sample])
                        )
                    )
                ),
                bootstrap_replicates,
                bootstrap_seed + offset * 2 + 1,
            ),
        }
    return {"engines": engines, "cells": cells, "paired": paired}


def _write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write flat per-engine scores for downstream publication scripts."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if fields:
            writer.writeheader()
            writer.writerows(rows)
    temporary.replace(path)


def _score_timing(
    tasks: list[dict[str, Any]], mode: str, output_dir: Path
) -> dict[str, Any]:
    """Score only controlled serial timing tasks."""
    rows = []
    grouped = defaultdict(dict)
    for task in tasks:
        cached = _read_fit(task)
        dataset = json.loads(Path(task["manifest_path"]).read_text())
        fit = cached["fit"]
        row = {
            "dataset_id": dataset["dataset_id"],
            "scenario": dataset["scenario"],
            "model": dataset["fit_model"],
            "engine": task["engine"],
            "ntips": dataset["ntips"],
            "replicate": dataset["replicate"],
            "status": fit.get("status", "error"),
            "converged": bool(fit.get("converged", False)),
            "elapsed_seconds": fit.get("elapsed_seconds"),
        }
        rows.append(row)
        grouped[dataset["dataset_id"]][task["engine"]] = row
    pairs = []
    for dataset_id, engines in sorted(grouped.items()):
        if set(engines) != {"toytree", "ape"}:
            continue
        toy = engines["toytree"]["elapsed_seconds"]
        ape = engines["ape"]["elapsed_seconds"]
        ratio = None
        if toy is not None and ape is not None and float(ape) > 0:
            ratio = float(toy) / float(ape)
        pairs.append(
            {
                "dataset_id": dataset_id,
                "scenario": engines["toytree"]["scenario"],
                "ntips": engines["toytree"]["ntips"],
                "toytree_over_ape_runtime": ratio,
                "both_converged": bool(
                    engines["toytree"]["status"] == "ok"
                    and engines["ape"]["status"] == "ok"
                    and engines["toytree"]["converged"]
                    and engines["ape"]["converged"]
                ),
            }
        )
    summaries = {}
    by_cell = defaultdict(list)
    for pair in pairs:
        by_cell[(pair["scenario"], pair["ntips"])].append(pair)
    for (scenario, ntips), group in sorted(by_cell.items()):
        eligible = [row for row in group if row["both_converged"]]
        summaries[f"{scenario}:n{ntips}"] = {
            "pairs": len(group),
            "jointly_converged_pairs": len(eligible),
            "toytree_over_ape_runtime": _summary_stats(
                [row["toytree_over_ape_runtime"] for row in eligible]
            ),
            "toytree_over_ape_runtime_all_returned": _summary_stats(
                [row["toytree_over_ape_runtime"] for row in group]
            ),
        }
    result = {
        "study_version": 17,
        "mode": mode,
        "timing_protocol": "serial-alternating-v1",
        "fit_tasks": len(tasks),
        "fit_source_hashes": _fit_source_hashes(tasks),
        "rows": rows,
        "pairs": pairs,
        "summary": summaries,
    }
    _atomic_json(output_dir / f"timings-v17-{mode}.json", result)
    return result


def _score(
    manifests: list[Path],
    tasks: list[dict[str, Any]],
    config: dict[str, Any],
    mode: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Assemble cache-only raw scores, contrasts, and summaries."""
    task_by_dataset = defaultdict(list)
    for task in tasks:
        dataset_id = Path(task["manifest_path"]).stem
        task_by_dataset[dataset_id].append(task)
    rows = []
    pairs = []
    for manifest in manifests:
        dataset = json.loads(manifest.read_text())
        caches = {
            task["engine"]: _read_fit(task)
            for task in task_by_dataset[dataset["dataset_id"]]
        }
        rows.extend(_score_fit(dataset, cache) for cache in caches.values())
        pair = _pair_score(dataset, caches)
        if pair is not None:
            pairs.append(pair)
    spec = config["modes"][mode]
    result = {
        "study_version": 17,
        "mode": mode,
        "diagnostic_only": mode != "confirmation",
        "datasets": len(manifests),
        "fit_tasks": len(tasks),
        "config_hash": _json_hash(config),
        "generation_source_hash": _generation_source_hash(config),
        "fit_source_hashes": _fit_source_hashes(tasks),
        "rows": rows,
        "pairs": pairs,
        "summary": _summarize(
            rows,
            pairs,
            int(spec["bootstrap_replicates"]),
            int(config["confirmation_seed"]) + 17,
        ),
    }
    _atomic_json(output_dir / f"results-v17-{mode}.json", result)
    _write_rows_csv(output_dir / f"results-v17-{mode}.csv", rows)
    return result


def _fit_source_hashes(tasks: list[dict[str, Any]]) -> dict[str, str]:
    """Return compact engine/model source provenance from task payloads."""
    return {
        f"{task['engine']}:{task['model']}": task["source_hash"]
        for task in sorted(tasks, key=lambda item: (item["engine"], item["model"]))
    }


def _command_output(command: list[str]) -> str | None:
    """Return compact command output without failing environment capture."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return (result.stdout or result.stderr).strip()


def _require_ape_version(expected: str) -> None:
    """Fail before launching workers if R or the pinned ape is unavailable."""
    observed = _command_output(
        [
            "Rscript",
            "-e",
            'cat(as.character(utils::packageVersion("ape")))',
        ]
    )
    if observed is None:
        raise RuntimeError("Rscript and the R package 'ape' are required")
    if observed != expected:
        raise RuntimeError(
            f"ape version {observed!r} does not match required {expected!r}"
        )


def _environment() -> dict[str, Any]:
    """Return Python, R, ape, and platform provenance."""
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "numerical_thread_limits": {
            name: os.environ.get(name)
            for name in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
            )
        },
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "toytree": getattr(toytree, "__version__", "unknown"),
        "rscript": _command_output(["Rscript", "--version"]),
        "ape": _command_output(
            [
                "Rscript",
                "-e",
                'cat(as.character(utils::packageVersion("ape")))',
            ]
        ),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
    }


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("smoke", "pilot", "confirmation"),
        required=True,
    )
    parser.add_argument(
        "--stage",
        choices=("generate", "fit", "score", "timing", "all"),
        default="all",
    )
    parser.add_argument(
        "--ncores",
        type=int,
        default=0,
        help="global fit workers; 0 uses all logical CPUs",
    )
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    if args.ncores < 0:
        parser.error("--ncores must be non-negative")
    return args


def main() -> None:
    """Run generation, globally parallel fits, or cache-only scoring."""
    args = _parse_args()
    config = json.loads(args.config.read_text())
    output_dir = args.output_dir.resolve()
    manifests = _generate_manifests(config, args.mode, output_dir)
    seeds = {
        "study_version": 17,
        "mode": args.mode,
        "datasets": [
            {"dataset_id": payload["dataset_id"], "seed": payload["seed"]}
            for payload in _dataset_payloads(config, args.mode)
        ],
    }
    _atomic_json(output_dir / f"seeds-v17-{args.mode}.json", seeds)
    if args.stage == "generate":
        print(json.dumps({"mode": args.mode, "datasets": len(manifests)}))
        return
    tasks = _task_payloads(manifests, config, output_dir)
    if args.stage in {"fit", "timing", "all"}:
        _require_ape_version(config["expected_ape_version"])
    if args.stage == "timing":
        timing_tasks = _timing_tasks(tasks, config, args.mode, output_dir)
        _run_tasks(timing_tasks, ncores=1, resume=not args.no_resume)
        timing = _score_timing(timing_tasks, args.mode, output_dir)
        _atomic_json(
            output_dir / f"environment-v17-{args.mode}.json",
            _environment(),
        )
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "timing_tasks": timing["fit_tasks"],
                    "output": str(output_dir / f"timings-v17-{args.mode}.json"),
                }
            )
        )
        return
    if args.stage in {"fit", "all"}:
        _run_tasks(tasks, args.ncores, resume=not args.no_resume)
    if args.stage in {"score", "all"}:
        result = _score(manifests, tasks, config, args.mode, output_dir)
        _atomic_json(
            output_dir / f"environment-v17-{args.mode}.json",
            _environment(),
        )
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": result["datasets"],
                    "fit_tasks": result["fit_tasks"],
                    "output": str(output_dir / f"results-v17-{args.mode}.json"),
                    "diagnostic_only": result["diagnostic_only"],
                }
            )
        )
    elif args.stage == "fit":
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "datasets": len(manifests),
                    "fit_tasks": len(tasks),
                }
            )
        )


if __name__ == "__main__":
    main()
