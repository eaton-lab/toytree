#!/usr/bin/env python
"""Run fixed-seed statistical and scaling validation for ``toytree.rtree``."""

from __future__ import annotations

import argparse
import gc
import json
import math
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np

import toytree
from toytree.rtree._src.birth_death_conditioned import _conditional_time_cdf


def _balanced_four(tree: toytree.ToyTree) -> bool:
    """Return whether a four-tip tree has two root clades of size two."""
    return sorted(len(child.get_leaves()) for child in tree.treenode.children) == [2, 2]


def _topology_check(nreps: int, tolerance: float) -> dict:
    """Validate exact four-tip Yule and PDA shape probabilities."""
    observed = {}
    for model, seed, expected in (("yule", 20260911, 1 / 3), ("pda", 20260912, 1 / 5)):
        rng = np.random.default_rng(seed)
        fraction = (
            sum(
                _balanced_four(toytree.rtree.random_topology(4, model=model, seed=rng))
                for _ in range(nreps)
            )
            / nreps
        )
        observed[model] = {
            "balanced_fraction": fraction,
            "expected": expected,
            "absolute_error": abs(fraction - expected),
            "passed": abs(fraction - expected) < tolerance,
        }
    return {
        "nreps": nreps,
        "tolerance": tolerance,
        "models": observed,
        "passed": all(item["passed"] for item in observed.values()),
    }


def _conditioned_time_check(nreps: int) -> dict:
    """Validate inverse-CDF branching-time draws using a DKW bound."""
    birth_rate, death_rate, origin_age = 1.0, 0.3, 4.0
    rng = np.random.default_rng(20260913)
    values = np.sort(
        np.asarray(
            [
                toytree.rtree.birth_death_conditioned_tree(
                    2,
                    birth_rate=birth_rate,
                    death_rate=death_rate,
                    origin_age=origin_age,
                    seed=rng,
                ).treenode.height
                for _ in range(nreps)
            ]
        )
    )
    expected = _conditional_time_cdf(values, origin_age, birth_rate, death_rate)
    upper = np.arange(1, nreps + 1) / nreps
    lower = np.arange(0, nreps) / nreps
    distance = max(float(np.max(upper - expected)), float(np.max(expected - lower)))
    alpha = 1e-6
    bound = float(np.sqrt(np.log(2 / alpha) / (2 * nreps)))
    return {
        "nreps": nreps,
        "ks_distance": distance,
        "dkw_alpha": alpha,
        "dkw_bound": bound,
        "passed": distance < bound,
    }


def _pure_birth_mean_check(nreps: int, tolerance: float) -> dict:
    """Validate a pure-birth conditional mean independently of the CDF code."""
    birth_rate, origin_age = 0.7, 3.0
    rng = np.random.default_rng(20260918)
    values = np.asarray(
        [
            toytree.rtree.birth_death_conditioned_tree(
                2,
                birth_rate=birth_rate,
                death_rate=0.0,
                origin_age=origin_age,
                seed=rng,
            ).treenode.height
            for _ in range(nreps)
        ]
    )
    expected = float(1.0 / birth_rate - origin_age / np.expm1(birth_rate * origin_age))
    observed = float(values.mean())
    error = float(abs(observed / expected - 1.0))
    return {
        "nreps": nreps,
        "observed_mean": observed,
        "expected_mean": expected,
        "relative_error": error,
        "tolerance": tolerance,
        "passed": bool(error < tolerance),
    }


def _coalescent_check(nreps: int, tolerance: float) -> dict:
    """Validate Kingman interval and finite-sample TMRCA expectations."""
    nsample, Ne, ploidy = 8, 100.0, 2.0
    rng = np.random.default_rng(20260914)
    first = np.empty(nreps)
    tmrca = np.empty(nreps)
    for idx in range(nreps):
        tree = toytree.rtree.coalescent_tree(nsample, Ne=Ne, ploidy=ploidy, seed=rng)
        first[idx] = min(node.height for node in tree[tree.ntips :])
        tmrca[idx] = tree.treenode.height
    expected_first = 2 * ploidy * Ne / (nsample * (nsample - 1))
    expected_tmrca = 2 * ploidy * Ne * (1 - 1 / nsample)
    first_error = abs(float(first.mean()) / expected_first - 1)
    tmrca_error = abs(float(tmrca.mean()) / expected_tmrca - 1)
    return {
        "nreps": nreps,
        "first_interval_mean": float(first.mean()),
        "first_interval_expected": expected_first,
        "first_interval_relative_error": first_error,
        "tmrca_mean": float(tmrca.mean()),
        "tmrca_expected": expected_tmrca,
        "tmrca_relative_error": tmrca_error,
        "tolerance": tolerance,
        "passed": max(first_error, tmrca_error) < tolerance,
    }


def _process_check(nreps: int, tolerance: float) -> dict:
    """Validate event-type probabilities and stopping invariants."""
    rng = np.random.default_rng(20260915)
    births = deaths = 0
    stop_valid = True
    for _ in range(nreps):
        result = toytree.rtree.birth_death_process(
            birth_rate=3.0,
            death_rate=2.0,
            stop_time=0.5,
            start="crown",
            condition_on_survival=False,
            seed=rng,
        )
        births += result.births
        deaths += result.deaths
        stop_valid &= result.elapsed_time == 0.5 or result.stop_reason == "extinction"
    fraction = births / (births + deaths)
    error = abs(fraction - 0.6)
    richness = [
        toytree.rtree.birth_death_process(
            birth_rate=1.0, death_rate=0.3, stop_ntips=32, seed=9000 + idx
        )
        for idx in range(20)
    ]
    richness_valid = all(
        item.extant_tips == 32 and item.stop_reason == "taxa" for item in richness
    )
    return {
        "nreps": nreps,
        "births": births,
        "deaths": deaths,
        "birth_fraction": fraction,
        "expected_birth_fraction": 0.6,
        "absolute_error": error,
        "tolerance": tolerance,
        "time_stop_valid": bool(stop_valid),
        "richness_stop_valid": richness_valid,
        "passed": error < tolerance and stop_valid and richness_valid,
    }


def _rate_check(ntips: int, tolerances: dict[str, float]) -> dict:
    """Validate UCLN moments and ACLN standardized increments."""
    topology = toytree.rtree.random_topology(ntips, seed=1)
    ucln = toytree.rtree.simulate_branch_rates(
        topology,
        "uncorrelated_lognormal",
        mean_rate=2.0,
        sigma=0.5,
        seed=20260916,
    )
    rates = np.asarray([node.rate for node in ucln[:-1]])
    mean_error = abs(float(rates.mean()) / 2.0 - 1)
    log_sd_error = abs(float(np.std(np.log(rates), ddof=1)) - 0.5)
    adjacent_correlation = abs(float(np.corrcoef(rates[:-1], rates[1:])[0, 1]))

    timetree = toytree.rtree.unittree(ntips, treeheight=10.0, seed=2)
    sigma = 0.35
    acln = toytree.rtree.simulate_branch_rates(
        timetree,
        "autocorrelated_lognormal",
        mean_rate=1.0,
        sigma=sigma,
        seed=20260917,
    )
    standardized = []
    for node in acln[:-1]:
        if node.time:
            increment = math.log(node.end_rate) - math.log(node.start_rate)
            standardized.append(
                (increment + 0.5 * sigma**2 * node.time)
                / (sigma * math.sqrt(node.time))
            )
    standardized = np.asarray(standardized)
    acln_mean_error = abs(float(standardized.mean()))
    acln_sd_error = abs(float(standardized.std(ddof=1)) - 1)
    passed = (
        mean_error < tolerances["ucln_mean"]
        and log_sd_error < tolerances["ucln_log_sd"]
        and adjacent_correlation < tolerances["ucln_correlation"]
        and acln_mean_error < tolerances["acln_standardized"]
        and acln_sd_error < tolerances["acln_standardized"]
    )
    return {
        "ntips": ntips,
        "ucln": {
            "mean_relative_error": mean_error,
            "log_sd_absolute_error": log_sd_error,
            "adjacent_rate_absolute_correlation": adjacent_correlation,
        },
        "acln": {
            "standardized_increment_mean_absolute_error": acln_mean_error,
            "standardized_increment_sd_absolute_error": acln_sd_error,
        },
        "tolerances": tolerances,
        "passed": passed,
    }


def _scaling_check(sizes: list[int], repeats: int, maximum_ratio: float) -> dict:
    """Record doubling-time ratios for the linear-bookkeeping implementations."""
    methods = {
        "yule": lambda n, seed: toytree.rtree.random_topology(
            n, model="yule", seed=seed
        ),
        "pda": lambda n, seed: toytree.rtree.random_topology(n, model="pda", seed=seed),
        "coalescent": lambda n, seed: toytree.rtree.coalescent_tree(n, seed=seed),
        "pure_birth_process": lambda n, seed: toytree.rtree.birth_death_process(
            birth_rate=1.0, death_rate=0.0, stop_ntips=n, seed=seed
        ),
    }
    results = {}
    passed = True
    for label, function in methods.items():
        medians = []
        for size in sizes:
            elapsed = []
            for rep in range(repeats):
                gc.collect()
                start = perf_counter()
                function(size, 7000 + rep)
                elapsed.append(perf_counter() - start)
            medians.append(float(statistics.median(elapsed)))
        ratios = [medians[idx + 1] / medians[idx] for idx in range(len(medians) - 1)]
        method_passed = max(ratios) < maximum_ratio
        passed &= method_passed
        results[label] = {
            "median_seconds": dict(zip(map(str, sizes), medians)),
            "doubling_ratios": ratios,
            "passed": method_passed,
        }
    return {
        "sizes": sizes,
        "repeats": repeats,
        "maximum_doubling_ratio": maximum_ratio,
        "methods": results,
        "passed": passed,
    }


def run(mode: str) -> dict:
    """Run the selected fixed-seed validation workload and return its record."""
    quick = mode == "quick"
    topology = _topology_check(2_000 if quick else 20_000, 0.05 if quick else 0.012)
    conditioned = _conditioned_time_check(1_000 if quick else 10_000)
    pure_birth_mean = _pure_birth_mean_check(
        1_000 if quick else 10_000, 0.08 if quick else 0.025
    )
    coalescent = _coalescent_check(1_000 if quick else 10_000, 0.12 if quick else 0.035)
    process = _process_check(500 if quick else 5_000, 0.07 if quick else 0.025)
    rate_tolerances = {
        "ucln_mean": 0.08 if quick else 0.02,
        "ucln_log_sd": 0.06 if quick else 0.02,
        "ucln_correlation": 0.10 if quick else 0.035,
        "acln_standardized": 0.10 if quick else 0.035,
    }
    rates = _rate_check(2_000 if quick else 20_000, rate_tolerances)
    scaling = _scaling_check(
        [1_000, 2_000, 4_000] if quick else [4_000, 8_000, 16_000],
        2 if quick else 5,
        4.5 if quick else 3.75,
    )
    checks = {
        "topology_distributions": topology["passed"],
        "conditioned_birth_death_times": conditioned["passed"],
        "conditioned_pure_birth_mean": pure_birth_mean["passed"],
        "coalescent_expectations": coalescent["passed"],
        "birth_death_process": process["passed"],
        "branch_rate_processes": rates["passed"],
        "scaling": scaling["passed"],
    }
    return {
        "schema": "toytree-rtree-validation-v1",
        "mode": mode,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "results": {
            "topology_distributions": topology,
            "conditioned_birth_death_times": conditioned,
            "conditioned_pure_birth_mean": pure_birth_mean,
            "coalescent_expectations": coalescent,
            "birth_death_process": process,
            "branch_rate_processes": rates,
            "scaling": scaling,
        },
    }


def main() -> None:
    """Parse arguments, run validation, write JSON, and set exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("quick", "confirmation"), default="confirmation"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(__file__).with_name(f"results-{args.mode}.json")
    result = run(args.mode)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "mode": args.mode,
                "output": str(output),
                "all_checks_passed": result["all_checks_passed"],
            }
        )
    )
    if not result["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
