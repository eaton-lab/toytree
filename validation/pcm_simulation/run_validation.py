#!/usr/bin/env python

"""Run reproducible recovery validation for PCM trait simulators.

The quick mode is suitable for development and CI-like checks. Confirmation
mode increases both tree size and independent replicate count. Each replicate
is an independent task so ``--ncores`` scales across available processes.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import toytree

HERE = Path(__file__).resolve().parent
BASE_SEED = 20260911
MODES = {
    "quick": {"nreplicates": 16, "ntips": 64},
    "confirmation": {"nreplicates": 100, "ntips": 128},
}


def _finite(values: list[float]) -> np.ndarray:
    """Return finite values as a one-dimensional array."""
    array = np.asarray(values, dtype=float)
    return array[np.isfinite(array)]


def _stats(values: list[float]) -> dict[str, float | int | None]:
    """Return stable descriptive statistics for one metric."""
    array = _finite(values)
    if not array.size:
        return {"n": 0, "mean": None, "median": None, "p90": None}
    return {
        "n": int(array.size),
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.9)),
    }


def _run_replicate(task: tuple[int, int, int]) -> dict[str, Any]:
    """Simulate and fit all validation models for one independent replicate."""
    replicate, ntips, seed = task
    rng = np.random.default_rng(seed)
    tree = toytree.rtree.unittree(ntips=ntips, treeheight=2.0, seed=rng)
    result: dict[str, Any] = {"replicate": replicate, "seed": seed}

    continuous_specs = {
        "bm": {"params": 0.8, "root_state": 0.4},
        "ou": {"params": (0.8, 1.0), "root_state": 0.4},
        "eb": {"params": (0.8, -0.7), "root_state": 0.4},
    }
    for model, spec in continuous_specs.items():
        data = tree.pcm.simulate_continuous_trait(
            model,
            params=spec["params"],
            root_state=spec["root_state"],
            tips_only=True,
            seed=rng,
        )
        fit = tree.pcm.fit_continuous_ml(data, model=model.upper())
        record = {
            "converged": bool(fit.converged),
            "mu": float(fit.mu),
            "sigma2": float(fit.sigma2),
            "alpha": None if fit.alpha is None else float(fit.alpha),
            "r": None if fit.r is None else float(fit.r),
        }
        if model == "bm":
            pics = tree.pcm.get_phylogenetic_independent_contrasts(data)
            contrasts = pics["contrast"].to_numpy(dtype=float)
            signal = tree.pcm.phylogenetic_signal_k(data, nsims=0)
            record.update(
                {
                    "pic_mean": float(np.mean(contrasts)),
                    "pic_variance": float(np.var(contrasts, ddof=1)),
                    "blomberg_k": float(signal["K"]),
                }
            )
        result[model] = record

    labels = ["later", "earlier"]
    er = tree.pcm.simulate_discrete_trait(
        2,
        model="ER",
        relative_rates=1.0,
        rate_scalar=0.8,
        root_prior=[0.5, 0.5],
        state_names=labels,
        tips_only=True,
        seed=rng,
    )
    er_fit = tree.pcm.fit_discrete_ctmc(
        er,
        nstates=2,
        model="ER",
        root_prior=[0.5, 0.5],
    )
    result["er"] = {
        "rate": float(er_fit.relative_rates[0, 1]),
        "state_order": list(er_fit.state_labels),
    }

    ard_rates = np.array([[0.0, 0.7], [1.4, 0.0]])
    ard_prior = np.array([2.0 / 3.0, 1.0 / 3.0])
    ard = tree.pcm.simulate_discrete_trait(
        2,
        model="ARD",
        relative_rates=ard_rates,
        root_prior=ard_prior,
        state_names=labels,
        tips_only=True,
        seed=rng,
    )
    ard_fit = tree.pcm.fit_discrete_ctmc(
        ard,
        nstates=2,
        model="ARD",
        root_prior=ard_prior,
    )
    result["ard"] = {
        "rate_01": float(ard_fit.relative_rates[0, 1]),
        "rate_10": float(ard_fit.relative_rates[1, 0]),
        "state_order": list(ard_fit.state_labels),
    }

    tip_labels = tree.get_tip_labels()
    predictors = pd.DataFrame(
        {"x": rng.normal(size=ntips)},
        index=tip_labels,
    )
    y = tree.pcm.simulate_pgls_trait(
        "y ~ x",
        {"Intercept": 0.5, "x": 1.2},
        lambda_=0.6,
        sigma2=0.7,
        data=predictors,
        seed=rng,
    )
    pgls_data = predictors.assign(y=y)
    fixed_pgls = tree.pcm.pgls("y ~ x", data=pgls_data, lambda_=0.6)
    optimized_pgls = tree.pcm.pgls("y ~ x", data=pgls_data, lambda_=None)
    result["pgls"] = {
        "converged": bool(fixed_pgls.converged and optimized_pgls.converged),
        "intercept": float(fixed_pgls.params["Intercept"]),
        "slope": float(fixed_pgls.params["x"]),
        "sigma2": float(fixed_pgls.sigma2),
        "lambda": float(optimized_pgls.lambda_),
    }

    pglm_y = tree.pcm.simulate_pglm_trait(
        "binary ~ x",
        {"Intercept": -0.4, "x": 1.0},
        family="binomial",
        link="logit",
        lambda_=0.5,
        sigma2=0.3,
        data=predictors,
        seed=rng,
    )
    pglm_data = predictors.assign(binary=pglm_y)
    try:
        pglm_fit = tree.pcm.pglm(
            "binary ~ x",
            data=pglm_data,
            lambda_=0.5,
            family="binomial",
            link="logit",
        )
        result["pglm"] = {
            "fit_succeeded": True,
            "converged": bool(pglm_fit.converged),
            "intercept": float(pglm_fit.params["Intercept"]),
            "slope": float(pglm_fit.params["x"]),
        }
    except Exception as exc:  # diagnostic: retain approximate-fitter failures
        result["pglm"] = {
            "fit_succeeded": False,
            "converged": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return result


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate recovery metrics and evaluate predeclared release gates."""
    summary: dict[str, Any] = {"replicates": len(records)}
    for model in ("bm", "ou", "eb"):
        summary[model] = {
            "convergence_fraction": float(
                np.mean([record[model]["converged"] for record in records])
            ),
            "mu_error": _stats([record[model]["mu"] - 0.4 for record in records]),
            "sigma2_ratio": _stats(
                [record[model]["sigma2"] / 0.8 for record in records]
            ),
        }
    summary["ou"]["alpha_error"] = _stats(
        [record["ou"]["alpha"] - 1.0 for record in records]
    )
    summary["eb"]["r_error"] = _stats([record["eb"]["r"] + 0.7 for record in records])
    summary["bm"].update(
        {
            "pic_mean": _stats([record["bm"]["pic_mean"] for record in records]),
            "pic_variance_ratio": _stats(
                [record["bm"]["pic_variance"] / 0.8 for record in records]
            ),
            "blomberg_k": _stats([record["bm"]["blomberg_k"] for record in records]),
        }
    )
    summary["er"] = {
        "rate_ratio": _stats([record["er"]["rate"] / 0.8 for record in records]),
        "state_order_preserved": all(
            record["er"]["state_order"] == ["later", "earlier"] for record in records
        ),
    }
    summary["ard"] = {
        "rate_01_ratio": _stats([record["ard"]["rate_01"] / 0.7 for record in records]),
        "rate_10_ratio": _stats([record["ard"]["rate_10"] / 1.4 for record in records]),
        "state_order_preserved": all(
            record["ard"]["state_order"] == ["later", "earlier"] for record in records
        ),
    }
    summary["pgls"] = {
        "convergence_fraction": float(
            np.mean([record["pgls"]["converged"] for record in records])
        ),
        "intercept_error": _stats(
            [record["pgls"]["intercept"] - 0.5 for record in records]
        ),
        "slope_error": _stats([record["pgls"]["slope"] - 1.2 for record in records]),
        "sigma2_ratio": _stats([record["pgls"]["sigma2"] / 0.7 for record in records]),
        "lambda_error": _stats([record["pgls"]["lambda"] - 0.6 for record in records]),
    }
    successful_pglm = [r["pglm"] for r in records if r["pglm"]["fit_succeeded"]]
    summary["pglm_diagnostic_only"] = {
        "fit_success_fraction": len(successful_pglm) / len(records),
        "convergence_fraction": (
            float(np.mean([record["converged"] for record in successful_pglm]))
            if successful_pglm
            else 0.0
        ),
        "intercept_error": _stats(
            [record["intercept"] + 0.4 for record in successful_pglm]
        ),
        "slope_error": _stats([record["slope"] - 1.0 for record in successful_pglm]),
        "release_gate": False,
        "reason": "pglm is an approximate IRLS fit to the exact latent generator",
    }

    checks = {
        "continuous_convergence": min(
            summary[model]["convergence_fraction"] for model in ("bm", "ou", "eb")
        )
        >= 0.95,
        "continuous_diffusion_recovery": all(
            0.65 <= summary[model]["sigma2_ratio"]["median"] <= 1.35
            for model in ("bm", "ou", "eb")
        ),
        "ou_alpha_recovery": abs(summary["ou"]["alpha_error"]["median"]) <= 0.5,
        "eb_r_recovery": abs(summary["eb"]["r_error"]["median"]) <= 0.5,
        "pic_calibration": (
            abs(summary["bm"]["pic_mean"]["mean"]) <= 0.15
            and 0.7 <= summary["bm"]["pic_variance_ratio"]["median"] <= 1.3
        ),
        "blomberg_k_calibration": 0.7 <= summary["bm"]["blomberg_k"]["median"] <= 1.3,
        "discrete_state_order": bool(
            summary["er"]["state_order_preserved"]
            and summary["ard"]["state_order_preserved"]
        ),
        "er_rate_recovery": 0.6 <= summary["er"]["rate_ratio"]["median"] <= 1.6,
        "ard_rate_recovery": all(
            0.5 <= summary["ard"][key]["median"] <= 1.8
            for key in ("rate_01_ratio", "rate_10_ratio")
        ),
        "pgls_convergence": summary["pgls"]["convergence_fraction"] >= 0.95,
        "pgls_coefficient_recovery": (
            abs(summary["pgls"]["intercept_error"]["mean"]) <= 0.2
            and abs(summary["pgls"]["slope_error"]["mean"]) <= 0.15
        ),
        "pgls_covariance_recovery": (
            0.7 <= summary["pgls"]["sigma2_ratio"]["median"] <= 1.3
            and abs(summary["pgls"]["lambda_error"]["median"]) <= 0.25
        ),
    }
    summary["checks"] = checks
    summary["all_release_gates_passed"] = all(checks.values())
    return summary


def main() -> None:
    """Parse CLI arguments, execute independent tasks, and write JSON evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=tuple(MODES), default="quick")
    parser.add_argument("--ncores", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.ncores < 1:
        parser.error("--ncores must be >= 1")

    config = MODES[args.mode]
    children = np.random.SeedSequence(BASE_SEED).spawn(config["nreplicates"])
    tasks = [
        (idx, config["ntips"], int(child.generate_state(1, dtype=np.uint32)[0]))
        for idx, child in enumerate(children)
    ]
    records: list[dict[str, Any]] = []
    if args.ncores == 1:
        for task in tasks:
            records.append(_run_replicate(task))
    else:
        with ProcessPoolExecutor(max_workers=args.ncores) as pool:
            futures = {pool.submit(_run_replicate, task): task[0] for task in tasks}
            for future in as_completed(futures):
                records.append(future.result())
    records.sort(key=lambda record: record["replicate"])

    payload = {
        "mode": args.mode,
        "config": config,
        "base_seed": BASE_SEED,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "toytree": toytree.__version__,
        },
        "records": records,
        "summary": _summarize(records),
    }
    output = args.output or HERE / f"results-{args.mode}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "mode": args.mode,
                "replicates": len(records),
                "output": str(output),
                "all_release_gates_passed": payload["summary"][
                    "all_release_gates_passed"
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
