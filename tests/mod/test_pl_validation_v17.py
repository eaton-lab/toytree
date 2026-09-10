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
    run_validation_v17_benchmark as study,
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


def test_v17_r_adapter_has_no_jsonlite_dependency():
    """The standalone R protocol remains deployable with ape alone."""
    source = study.R_RUNNER.read_text()
    assert 'requireNamespace("jsonlite"' not in source
    assert "library(jsonlite" not in source
    assert "toytree-chronos-v17" in source
    assert "descendant_tips" in source
