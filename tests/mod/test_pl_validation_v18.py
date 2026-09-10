"""Tests for the V18 matched per-tree lambda-identifiability study."""

# ruff: noqa: D103, E402 -- repository validation modules are not installed.
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
import toytree
from toytree.mod._src.penalized_pseudolikelihood import uncorrelated_lognormal as ucln
from validation.penalized_pseudolikelihood import (
    run_validation_v18_lambda_identifiability as study,
)


def test_v18_frozen_design_is_paired_and_has_expected_size():
    config = json.loads(study.CONFIG_PATH.read_text())
    specs = study._build_specs(config, "pilot")
    assert len(specs) == 128
    assert len({spec["pair_id"] for spec in specs}) == 64
    assert len(config["lambdas"]) == 17
    assert np.allclose(np.diff(np.log10(config["lambdas"])), 0.5)
    for pair_id in range(64):
        pair = [spec for spec in specs if spec["pair_id"] == pair_id]
        assert {spec["model"] for spec in pair} == set(study.MODELS)
        for key in ("topology_seed", "rate_seed", "observation_seed"):
            assert len({spec[key] for spec in pair}) == 1
        assert len({spec["fit_seed"] for spec in pair}) == 2


def test_v18_simulation_pairs_topology_calibrations_and_noise():
    config = json.loads(study.CONFIG_PATH.read_text())
    all_specs = study._build_specs(config, "pilot")
    pair_id = next(
        spec["pair_id"]
        for spec in all_specs
        if spec["observation_model"] == "continuous_gamma"
    )
    specs = [spec for spec in all_specs if spec["pair_id"] == pair_id]
    left = study._simulate(specs[0], config)
    right = study._simulate(specs[1], config)
    assert np.allclose(left["true_ages"], right["true_ages"])
    assert left["calibrations"] == right["calibrations"]
    assert np.allclose(
        left["observed"] / left["expected"],
        right["observed"] / right["expected"],
    )
    assert not np.allclose(left["true_rates"], right["true_rates"])


def test_v18_dense_calibrations_are_distinct_and_contain_truth():
    config = json.loads(study.CONFIG_PATH.read_text())
    spec = next(
        item
        for item in study._build_specs(config, "pilot")
        if item["calibration"] == "root_and_three_internal_intervals"
    )
    simulated = study._simulate(spec, config)
    calibrations = simulated["calibrations"]
    assert len(calibrations) == 4
    assert calibrations[-1] == 1.0
    for idx, value in calibrations.items():
        if idx != -1:
            lower, upper = value
            assert lower < simulated["true_ages"][idx] < upper


def test_v18_selection_favors_stronger_lambda_on_exact_tie():
    scores = np.asarray([[1.0, 1.0], [1.0, 1.0], [2.0, 2.0]])
    valid = np.asarray([True, True, True])
    lambdas = np.asarray([0.1, 1.0, 10.0])
    assert study._select_index(scores, valid, lambdas) == 1
    result = study._bootstrap_fold_selection(scores, valid, lambdas, 20, 123)
    assert result["selection_frequencies"] == {"1.0": 1.0}
    assert result["supported_lambdas"] == [1.0]


def test_v18_fold_bootstrap_is_deterministic_and_paired():
    scores = np.asarray([[0.0, 10.0, 0.0], [4.0, 0.0, 4.0]])
    valid = np.asarray([True, True])
    lambdas = np.asarray([0.1, 1.0])
    one = study._bootstrap_fold_selection(scores, valid, lambdas, 100, 45)
    two = study._bootstrap_fold_selection(scores, valid, lambdas, 100, 45)
    assert one == two
    assert sum(one["selection_frequencies"].values()) == 1.0


def test_v18_fit_and_scoring_fingerprints_are_separate():
    config = json.loads(study.CONFIG_PATH.read_text())
    fit_hash = study._fit_source_hash(config)
    spec = study._build_specs(config, "smoke")[0]
    before = study._dataset_fingerprint(spec, config, fit_hash)
    changed = json.loads(json.dumps(config))
    changed["decision_gates"]["maximum_boundary_selection_fraction"] = 0.2
    assert before == study._dataset_fingerprint(spec, changed, fit_hash)
    assert study._scoring_hash(config, 100) != study._scoring_hash(changed, 100)


def test_v18_summary_cannot_drop_failed_datasets():
    config = json.loads(study.CONFIG_PATH.read_text())
    rows = [
        {"model": "correlated", "status": "error"},
        {"model": "uncorrelated_lognormal", "status": "error"},
    ]
    summary = study._summarize(rows, config["decision_gates"])
    for model in study.MODELS:
        assert not summary["models"][model]["checks"]["all_datasets_scored"]
        assert not summary["models"][model]["gates_passed"]


def test_v18_task_graph_parallelizes_over_complete_tip_paths(tmp_path: Path):
    config = json.loads(study.CONFIG_PATH.read_text())
    source_hash = study._fit_source_hash(config)
    contexts = [
        study._context(spec, config, "smoke", tmp_path, source_hash)
        for spec in study._build_specs(config, "smoke")
    ]
    tasks = [
        task
        for context in contexts
        for task in study._tasks_for_context(context, config, True)
    ]
    assert len(tasks) == 2 * (6 + 1)
    assert sum(task["kind"] == "fold" for task in tasks) == 12
    assert all(len(task["lambdas"]) == 3 for task in tasks)
    assert all(task["fit_options"]["nstarts"] == 2 for task in tasks)


def test_ucln_private_continuation_is_available_without_public_selector():
    tree = toytree.rtree.unittree(6, treeheight=1.0, seed=18)
    first = ucln._edges_make_ultrametric_ucln(
        tree, lam=10.0, calibrations={-1: 1.0}, full=True, nstarts=2, seed=18
    )
    continued = ucln._edges_make_ultrametric_ucln(
        tree,
        lam=1.0,
        calibrations={-1: 1.0},
        full=True,
        nstarts=2,
        seed=19,
        _initial_rates=first["rates"],
        _initial_ages=first["tree"].get_node_data("height").to_numpy(dtype=float),
    )
    assert any(item["start_kind"] == "continuation" for item in continued["starts"])
    assert continued["converged"]
    assert not hasattr(
        toytree.mod, "edges_make_ultrametric_uncorrelated_lognormal_lambda_cv"
    )
