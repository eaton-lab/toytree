#!/usr/bin/env python

"""Run an identifiable fixed-age rate-recovery control for validation v4."""

# ruff: noqa: E402 -- repository path setup must precede local imports.

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import numpy as np
from scipy.stats import spearmanr

from validation.penalized_pseudolikelihood import run_validation_v4 as study

CONFIG_PATH = HERE / "config-v4-rate-control.json"
MAIN_CONFIG_PATH = HERE / "config-v4.json"
SELECTED_PATH = HERE / "v4" / "selected-lambdas-v4-pilot.json"


def _source_hash() -> str:
    """Return a hash covering the estimators and both validation runners."""
    digest = hashlib.sha256(study._source_hash().encode())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


def _payloads(output_dir: Path, resume: bool) -> list[dict]:
    """Return deterministic lognormal, continuous-noise control payloads."""
    config = json.loads(CONFIG_PATH.read_text())
    main_config = json.loads(MAIN_CONFIG_PATH.read_text())
    selected = json.loads(SELECTED_PATH.read_text())["selected_lambdas"]
    payloads = []
    for replicate in range(int(config["replicates"])):
        payload = {
            "mode": "rate-control",
            "rate_process": "lognormal",
            "track": str(config["track"]),
            "ntips": int(config["ntips"]),
            "calibration": "fixed_internal_ages",
            "fixed_ages": True,
            "replicate": replicate,
            "seed": int(config["seed"]) + replicate,
            "simulation": main_config["simulation"],
            "fit": main_config["fit"],
            "lambdas": {
                method: [float(selected["lognormal"][method])]
                for method in study.METHODS
            },
            "resume": resume,
        }
        payload["fingerprint"] = study._json_hash(
            {
                "schema": study.CACHE_SCHEMA_VERSION,
                "source": _source_hash(),
                "config": config,
                "payload": {
                    key: value
                    for key, value in payload.items()
                    if key != "resume"
                },
            }
        )
        payload["cache_path"] = str(study._cache_path(output_dir, payload))
        payloads.append(payload)
    return payloads


def _score(payloads: list[dict]) -> dict:
    """Score estimator recovery and the information ceiling of observations."""
    config = json.loads(CONFIG_PATH.read_text())
    selected = json.loads(SELECTED_PATH.read_text())["selected_lambdas"]
    rows = []
    oracle = []
    for payload in payloads:
        record = json.loads(Path(payload["cache_path"]).read_text())
        if record.get("fingerprint") != payload["fingerprint"]:
            raise RuntimeError(f"stale cache record: {payload['cache_path']}")
        if record.get("status") != "ok":
            raise RuntimeError(
                f"failed cache {payload['cache_path']}: {record.get('message')}"
            )
        rows.append(
            study._metrics(
                record,
                "uncorrelated_lognormal",
                selected["lognormal"]["uncorrelated_lognormal"],
            )
        )
        true_rates = np.asarray(record["true_rates"], dtype=float)
        times = np.asarray(record["true_means"], dtype=float) / true_rates
        observed_rates = np.asarray(record["observed"], dtype=float) / times
        oracle.append(
            float(spearmanr(np.log(true_rates), np.log(observed_rates)).statistic)
        )
    good = [row for row in rows if row["converged"]]
    convergence = len(good) / len(rows)
    median_rho = float(
        np.median(
            [
                row["log_rate_spearman"]
                for row in good
                if row["log_rate_spearman"] is not None
            ]
        )
    )
    gates = {
        "convergence": convergence >= config["minimum_convergence_rate"],
        "rate_recovery": median_rho
        >= config["minimum_median_log_rate_spearman"],
    }
    return {
        "study_version": "4-rate-control",
        "design": {
            "rate_process": "iid_lognormal",
            "observation_track": config["track"],
            "internal_ages": "fixed_at_truth",
            "ntips": config["ntips"],
            "replicates": config["replicates"],
        },
        "convergence_rate": convergence,
        "median_log_rate_spearman": median_rho,
        "median_observed_rate_spearman": float(np.median(oracle)),
        "gate_checks": gates,
        "passed": all(gates.values()),
        "source_hash": _source_hash(),
    }


def main(argv=None) -> int:
    """Run and score the supplemental rate-recovery control."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=HERE / "v4")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(argv)
    payloads = _payloads(args.output_dir, not args.no_resume)
    study._run(payloads, max(1, int(args.ncores)))
    result = _score(payloads)
    study._atomic_json(args.output_dir / "results-v4-rate-control.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
