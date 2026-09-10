"""Regression tests for the paired ToyTree--ape benchmark harness."""

# ruff: noqa: E402 -- repository validation package is not installed.

import json
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from validation.penalized_pseudolikelihood import (
    diagnose_relaxed_v17 as relaxed_diagnostics,
)
from validation.penalized_pseudolikelihood import (
    diagnose_relaxed_warmstart_v17 as warmstart_diagnostics,
)
from validation.penalized_pseudolikelihood import (
    diagnose_validation_v17 as diagnostics,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v17_benchmark as study,
)
from validation.penalized_pseudolikelihood import (
    run_validation_v17_relaxed_initialization as relaxed_initialization,
)

CONFIG = json.loads(study.CONFIG_PATH.read_text())


def test_v17_pilot_and_confirmation_sizes_are_frozen():
    """Pin the publication workload and untouched confirmation stream."""
    pilot = study._dataset_payloads(CONFIG, "pilot")
    confirmation = study._dataset_payloads(CONFIG, "confirmation")
    assert len(pilot) == 216
    assert len(confirmation) == 2_880
    assert pilot[0]["seed"] == CONFIG["development_seed"]
    assert confirmation[0]["seed"] == CONFIG["confirmation_seed"]
    assert CONFIG["development_seed"] != CONFIG["confirmation_seed"]
    assert sum(row["scenario"].startswith("ucln_") for row in pilot) == 36
    assert sum(row["scenario"].startswith("ucln_") for row in confirmation) == 480


def test_v17_smoke_matrix_uses_one_manifest_for_both_engines(tmp_path):
    """The smoke design expands to six datasets and eleven engine tasks."""
    manifests = study._generate_manifests(CONFIG, "smoke", tmp_path)
    tasks = study._task_payloads(manifests, CONFIG, tmp_path)

    assert len(manifests) == 6
    assert len(tasks) == 11
    assert len({json.loads(path.read_text())["fingerprint"] for path in manifests}) == 6

    by_dataset = {}
    for task in tasks:
        by_dataset.setdefault(Path(task["manifest_path"]).stem, set()).add(
            task["engine"]
        )
    assert by_dataset["ucln_sigma0p3-n6-root-expected_branch-r0000"] == {"toytree"}
    assert all(
        engines == {"toytree", "ape"}
        for dataset, engines in by_dataset.items()
        if not dataset.startswith("ucln_")
    )


def test_v17_manifests_resolve_calibrations_and_preserve_truth(tmp_path):
    """Serialized datasets retain clade-indexed ages, rates, and constraints."""
    payload = study._dataset_payloads(CONFIG, "smoke")[0]
    payload["calibration"] = "root_and_internal_interval"
    record = study._simulate_dataset(payload)
    observed = study.toytree.tree(record["observed_tree_newick"])
    resolved = study._resolve_calibrations(observed, record["calibrations"])

    assert len(resolved) == 2
    assert resolved[-1] == 1.0
    assert len(record["true_ages"]) == observed.ntips - 1
    assert len(record["true_rates"]) == observed.nedges
    assert set(record["true_ages"]) >= {study.ROOT_CLADE}


def test_v17_objective_parity_is_limited_to_compatible_models():
    """Correlated fits are compared for recovery, not unlike penalties."""
    tree = study.toytree.rtree.unittree(4, seed=1)
    newick = tree.write(dist_formatter="%.17g", internal_labels=None)
    true_ages = study._age_map(tree)
    dataset = {
        "dataset_id": "example",
        "scenario": "example",
        "fit_model": "clock",
        "ntips": 4,
        "calibration": "root",
        "observation_model": "expected_branch",
        "replicate": 0,
        "true_ages": true_ages,
        "calibrations": [{"clade": study.ROOT_CLADE, "lower": 1.0, "upper": 1.0}],
    }
    caches = {
        "toytree": {
            "fit": {
                "status": "ok",
                "converged": True,
                "tree_newick": newick,
                "pseudologlik": -10.0,
                "elapsed_seconds": 2.0,
            }
        },
        "ape": {
            "fit": {
                "status": "ok",
                "converged": True,
                "tree_newick": newick,
                "pseudologlik": -11.0,
                "elapsed_seconds": 1.0,
            }
        },
    }
    clock = study._pair_score(dataset, caches)
    assert clock["objective_kind"] == "pseudologlik"
    assert clock["toytree_minus_ape_objective"] == 1.0
    assert clock["toytree_over_ape_runtime"] == 2.0
    assert clock["comparison_eligible"]

    dataset["fit_model"] = "correlated"
    correlated = study._pair_score(dataset, caches)
    assert correlated["objective_kind"] is None
    assert correlated["toytree_minus_ape_objective"] is None


def test_v17_serial_timing_subset_is_separate_and_paired(tmp_path):
    """Controlled timings use separate caches and exclude no-ape UCLN pairs."""
    manifests = study._generate_manifests(CONFIG, "smoke", tmp_path)
    tasks = study._task_payloads(manifests, CONFIG, tmp_path)
    timing = study._timing_tasks(tasks, CONFIG, "smoke", tmp_path)

    assert len(timing) == 11
    assert all("/timing/" in task["cache_path"] for task in timing)
    assert all(
        task["fingerprint"] != original["fingerprint"]
        for task, original in zip(timing, tasks)
    )


def test_v17_engine_fingerprints_are_isolated(tmp_path):
    """ToyTree optimizer changes do not invalidate independent ape fits."""
    manifests = study._generate_manifests(CONFIG, "smoke", tmp_path)
    baseline = study._task_payloads(manifests, CONFIG, tmp_path)
    changed = deepcopy(CONFIG)
    changed["fit"]["toytree_nstarts"]["clock"] += 1
    altered = study._task_payloads(manifests, changed, tmp_path)
    original = {
        (Path(task["manifest_path"]).stem, task["engine"]): task["fingerprint"]
        for task in baseline
    }
    updated = {
        (Path(task["manifest_path"]).stem, task["engine"]): task["fingerprint"]
        for task in altered
    }
    ape_keys = [key for key in original if key[1] == "ape"]
    clock_key = ("clock-n6-root-expected_branch-r0000", "toytree")
    other_toy_keys = [
        key for key in original if key[1] == "toytree" and key != clock_key
    ]
    assert all(original[key] == updated[key] for key in ape_keys)
    assert original[clock_key] != updated[clock_key]
    assert all(original[key] == updated[key] for key in other_toy_keys)

    score_only = deepcopy(CONFIG)
    score_only["modes"]["smoke"]["bootstrap_replicates"] += 1
    rescored = study._task_payloads(manifests, score_only, tmp_path)
    rescored_hashes = {
        (Path(task["manifest_path"]).stem, task["engine"]): task["fingerprint"]
        for task in rescored
    }
    assert original == rescored_hashes


def test_v17_summary_helpers_are_deterministic():
    """Summary quantiles and bootstrap intervals have stable field names."""
    summary = study._summary_stats([1.0, 2.0, None, np.nan, 3.0])
    assert summary == {"n": 3, "median": 2.0, "mean": 2.0, "p90": 2.8}
    rows = [{"value": 1.0}, {"value": 3.0}]
    first = study._bootstrap_interval(
        rows,
        lambda sample: float(np.mean([row["value"] for row in sample])),
        100,
        123,
    )
    second = study._bootstrap_interval(
        rows,
        lambda sample: float(np.mean([row["value"] for row in sample])),
        100,
        123,
    )
    assert first == second
    assert first["estimate"] == 2.0


def test_v17_primary_summaries_exclude_nonconverged_outputs():
    """Sentinel objectives and ages remain diagnostic, not inferential."""
    rows = []
    pairs = []
    for dataset_id, ape_converged, ape_age, objective in (
        ("good", True, 0.2, 0.5),
        ("failed", False, 0.9, 1e100),
    ):
        for engine, age in (("toytree", 0.1), ("ape", ape_age)):
            converged = engine == "toytree" or ape_converged
            rows.append(
                {
                    "dataset_id": dataset_id,
                    "scenario": "clock",
                    "engine": engine,
                    "status": "ok",
                    "converged": converged,
                    "calibrations_valid": True,
                    "accuracy_eligible": converged,
                    "ntips": 8,
                    "calibration": "root",
                    "observation_model": "fractional_poisson",
                    "elapsed_seconds": 1.0,
                    "normalized_age_mae": age,
                    "normalized_age_rmse": age,
                    "rate_spearman": None,
                }
            )
        pairs.append(
            {
                "dataset_id": dataset_id,
                "scenario": "clock",
                "ntips": 8,
                "calibration": "root",
                "observation_model": "fractional_poisson",
                "both_converged": ape_converged,
                "comparison_eligible": ape_converged,
                "maximum_normalized_chronogram_difference": ape_age,
                "toytree_minus_ape_objective": objective,
                "toytree_over_ape_runtime": 1.0,
            }
        )

    summary = study._summarize(rows, pairs, 100, 123)

    assert summary["engines"]["clock:ape"]["normalized_age_mae"]["n"] == 1
    assert summary["engines"]["clock:ape"]["normalized_age_mae_all_returned"]["n"] == 2
    paired = summary["paired"]["clock"]
    assert paired["objective_difference"]["n"] == 1
    assert paired["objective_difference"]["median"] == 0.5
    assert paired["objective_difference_all_returned"]["p90"] > 1e99
    assert paired["age_mae_difference_bootstrap"]["estimate"] == -0.1


def test_v17_diagnostic_supports_existing_pilot_schema():
    """The diagnostic can analyze results written before scoring was refined."""
    result = {
        "mode": "pilot",
        "config_hash": "config",
        "fit_source_hashes": {"ape:clock": "ape", "toytree:clock": "toy"},
        "rows": [
            {
                "dataset_id": "failed",
                "scenario": "clock",
                "engine": "ape",
                "status": "ok",
                "converged": False,
                "calibrations_valid": True,
                "ntips": 8,
                "calibration": "root",
                "observation_model": "fractional_poisson",
                "zero_branch_count": 2,
                "normalized_age_mae": 0.9,
                "normalized_age_rmse": 1.0,
            }
        ],
        "pairs": [],
    }

    observed = diagnostics.diagnose(result)

    failure = observed["failure_patterns"]["clock:ape:fractional_poisson"]
    assert failure["datasets"] == 1
    assert failure["zero_containing"] == 1
    assert observed["diagnostic_only"]


def test_v17_relaxed_diagnostic_selects_failures_and_controls():
    """Target the strongest objective gaps in both directions."""
    pairs = []
    for idx, difference in enumerate((-4.0, -3.0, -2.0, 1.0, 2.0)):
        pairs.append(
            {
                "dataset_id": f"d{idx}",
                "scenario": "relaxed_gamma_shape4",
                "comparison_eligible": True,
                "toytree_minus_ape_objective": difference,
            }
        )
    observed = relaxed_diagnostics._select_dataset_ids(
        {"pairs": pairs}, ape_better=2, toytree_better=1
    )
    assert observed == ["d0", "d1", "d4"]


def test_v17_relaxed_diagnostic_reproduces_reported_objective():
    """Clade-mapped cache values reproduce the fitted relaxed objective."""
    payload = next(
        item
        for item in study._dataset_payloads(CONFIG, "smoke")
        if item["scenario"] == "relaxed_gamma_shape4"
    )
    manifest = study._simulate_dataset(payload)
    fit = study._fit_toytree(manifest, CONFIG["fit"])

    observed = relaxed_diagnostics._evaluate_fit(manifest, fit)

    assert np.isclose(observed["reported_objective_error"], 0.0, atol=1e-10)
    assert np.isclose(
        observed["penalized_pseudologlik"],
        fit["penalized_pseudologlik"],
        atol=1e-10,
    )

    problem = warmstart_diagnostics._problem(manifest, fit)
    function = warmstart_diagnostics._objective(problem)
    assert np.isclose(
        -function(problem["params"]),
        fit["penalized_pseudologlik"],
        atol=1e-10,
    )
    gradient = warmstart_diagnostics._projected_gradient(
        problem["params"], function, problem["bounds"]
    )
    assert np.isfinite(gradient["projected_gradient_max_abs"])


def test_v17_relaxed_warmstart_targets_only_ape_better_cases():
    """Warm starts focus on the strongest negative objective gaps."""
    result = {
        "pairs": [
            {
                "dataset_id": f"d{idx}",
                "scenario": "relaxed_gamma_shape4",
                "comparison_eligible": True,
                "toytree_minus_ape_objective": difference,
            }
            for idx, difference in enumerate((-1.0, -4.0, 2.0, -3.0))
        ]
    }
    assert warmstart_diagnostics._target_ids(result, 2) == ["d1", "d3"]


def test_v17_relaxed_initialization_replay_targets_all_relaxed_pairs():
    """The replay includes every relaxed pair once, regardless of convergence."""
    result = {
        "pairs": [
            {"dataset_id": "r1", "scenario": "relaxed_gamma_shape4"},
            {"dataset_id": "clock", "scenario": "clock"},
            {"dataset_id": "r1", "scenario": "relaxed_gamma_shape4"},
            {"dataset_id": "r2", "scenario": "relaxed_gamma_shape4"},
        ]
    }
    assert relaxed_initialization._target_ids(result) == ["r1", "r2"]


def test_v17_r_adapter_has_no_jsonlite_dependency():
    """The standalone R protocol remains deployable with ape alone."""
    source = study.R_RUNNER.read_text()
    assert 'requireNamespace("jsonlite"' not in source
    assert "library(jsonlite" not in source
    assert "toytree-chronos-v17" in source
    assert "descendant_tips" in source
