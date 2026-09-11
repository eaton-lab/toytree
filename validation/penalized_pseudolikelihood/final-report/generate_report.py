#!/usr/bin/env python
# ruff: noqa: D103, E501
"""Generate the final penalized-pseudolikelihood evidence report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INPUTS = {
    "v17": ROOT / "v17" / "results-v17-confirmation.json",
    "replay": ROOT / "v17" / "failure-replay-v17-confirmation.json",
    "v18": ROOT / "v18" / "summary-v18-pilot.json",
    "ledger": ROOT / "release-status.json",
}
ORDER = [
    ("clock", "Strict clock"),
    ("discrete_k2", "Discrete K=2"),
    ("discrete_k3", "Discrete K=3"),
    ("correlated_sigma0p3", "Correlated"),
    ("relaxed_gamma_shape4", "Relaxed (chronos)"),
    ("ucln_sigma0p3", "UCLN"),
]
RELATIONS = {
    "clock": "Shared strict-clock fractional-Poisson objective",
    "discrete_k2": "Shared chronos branchwise mixture objective",
    "discrete_k3": "Shared chronos branchwise mixture objective",
    "correlated_sigma0p3": "Analogous model; ToyTree uses complete-tree log-rate smoothing",
    "relaxed_gamma_shape4": "Shared chronos Gamma-CDF convention",
    "ucln_sigma0p3": "ToyTree-only centered-log-rate model",
}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt(value):
    return "" if value is None else f"{float(value):.3f}"


def rows(v17):
    engines = v17["summary"]["engines"]
    paired = v17["summary"]["paired"]
    result = []
    for key, label in ORDER:
        tt = engines[f"{key}:toytree"]
        ape = engines.get(f"{key}:ape")
        pair = paired.get(key)
        ci = None if pair is None else pair["age_mae_difference_bootstrap"]
        result.append(
            {
                "model": key,
                "label": label,
                "objective_relationship": RELATIONS[key],
                "datasets_per_engine": tt["datasets"],
                "toytree_convergence_fraction": tt["convergence_fraction"],
                "ape_convergence_fraction": None
                if ape is None
                else ape["convergence_fraction"],
                "both_converged_fraction": None
                if pair is None
                else pair["both_converged_fraction"],
                "toytree_median_normalized_age_mae": tt["normalized_age_mae"]["median"],
                "ape_median_normalized_age_mae": None
                if ape is None
                else ape["normalized_age_mae"]["median"],
                "paired_age_mae_difference": None if ci is None else ci["estimate"],
                "paired_age_mae_difference_lower": None if ci is None else ci["lower"],
                "paired_age_mae_difference_upper": None if ci is None else ci["upper"],
            }
        )
    return result


def write_csv(path, data):
    with path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def reliability_svg(data):
    w, h, left, right, top, bottom = 900, 430, 210, 35, 55, 55
    pw = w - left - right
    rh = (h - top - bottom) / len(data)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        "<style>text{font-family:Helvetica,Arial,sans-serif;fill:#263238}.title{font-size:19px;font-weight:700}.label{font-size:14px}.tick,.legend{font-size:12px}</style>",
        '<text class="title" x="20" y="28">Convergence in the V17 confirmation benchmark</text>',
    ]
    for tick in range(0, 11, 2):
        x = left + pw * tick / 10
        out += [
            f'<line x1="{x:.1f}" y1="{top-5}" x2="{x:.1f}" y2="{h-bottom}" stroke="#e0e0e0"/>',
            f'<text class="tick" x="{x:.1f}" y="{h-bottom+22}" text-anchor="middle">{tick*10}%</text>',
        ]
    for i, row in enumerate(data):
        y = top + (i + 0.5) * rh
        t = row["toytree_convergence_fraction"]
        a = row["ape_convergence_fraction"]
        out += [
            f'<text class="label" x="{left-12}" y="{y+5:.1f}" text-anchor="end">{html.escape(row["label"])}</text>',
            f'<rect x="{left}" y="{y-15:.1f}" width="{pw*t:.1f}" height="12" rx="2" fill="#1565c0"/>',
        ]
        if a is not None:
            out.append(
                f'<rect x="{left}" y="{y+3:.1f}" width="{pw*a:.1f}" height="12" rx="2" fill="#ef6c00"/>'
            )
    out += [
        f'<rect x="{left}" y="{h-20}" width="14" height="10" fill="#1565c0"/><text class="legend" x="{left+20}" y="{h-11}">ToyTree</text>',
        f'<rect x="{left+100}" y="{h-20}" width="14" height="10" fill="#ef6c00"/><text class="legend" x="{left+120}" y="{h-11}">ape::chronos</text>',
        "</svg>",
    ]
    return "\n".join(out) + "\n"


def accuracy_svg(data):
    data = [r for r in data if r["paired_age_mae_difference"] is not None]
    w, h, left, right, top, bottom = 900, 390, 210, 45, 60, 60
    lo, hi = -0.075, 0.01
    pw = w - left - right
    rh = (h - top - bottom) / len(data)

    def xpos(value):
        return left + pw * (value - lo) / (hi - lo)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        "<style>text{font-family:Helvetica,Arial,sans-serif;fill:#263238}.title{font-size:19px;font-weight:700}.label{font-size:14px}.tick,.note{font-size:12px}</style>",
        '<text class="title" x="20" y="28">Paired normalized age-MAE difference (ToyTree minus ape)</text>',
        f'<line x1="{xpos(0):.1f}" y1="{top-8}" x2="{xpos(0):.1f}" y2="{h-bottom}" stroke="#c62828" stroke-width="1.5"/>',
    ]
    for tick in (-0.07, -0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0, 0.01):
        x = xpos(tick)
        out += [
            f'<line x1="{x:.1f}" y1="{top-5}" x2="{x:.1f}" y2="{h-bottom}" stroke="#eeeeee"/>',
            f'<text class="tick" x="{x:.1f}" y="{h-bottom+22}" text-anchor="middle">{tick:.2f}</text>',
        ]
    for i, row in enumerate(data):
        y = top + (i + 0.5) * rh
        low = xpos(row["paired_age_mae_difference_lower"])
        high = xpos(row["paired_age_mae_difference_upper"])
        point = xpos(row["paired_age_mae_difference"])
        out += [
            f'<text class="label" x="{left-12}" y="{y+5:.1f}" text-anchor="end">{html.escape(row["label"])}</text>',
            f'<line x1="{low:.1f}" y1="{y:.1f}" x2="{high:.1f}" y2="{y:.1f}" stroke="#1565c0" stroke-width="3"/>',
            f'<circle cx="{point:.1f}" cy="{y:.1f}" r="5" fill="#1565c0"/>',
        ]
    out += [
        f'<text class="note" x="{left}" y="{h-12}">Negative values favor ToyTree; paired bootstrap 95% intervals among eligible fits.</text>',
        "</svg>",
    ]
    return "\n".join(out) + "\n"


def report(data, v17, replay, v18):
    table = []
    for row in data:
        ape = (
            "—"
            if row["ape_convergence_fraction"] is None
            else fmt(row["ape_convergence_fraction"])
        )
        delta = (
            "—"
            if row["paired_age_mae_difference"] is None
            else f"{row['paired_age_mae_difference']:.4f} [{row['paired_age_mae_difference_lower']:.4f}, {row['paired_age_mae_difference_upper']:.4f}]"
        )
        table.append(
            f"| {row['label']} | {fmt(row['toytree_convergence_fraction'])} | {ape} | {delta} |"
        )
    c = v18["summary"]["models"]["correlated"]["metrics"]
    u = v18["summary"]["models"]["uncorrelated_lognormal"]["metrics"]
    remaining = replay["summary"]["remaining_failures"]
    return f"""# Final penalized-pseudolikelihood validation report

## Conclusion

Within the prespecified V17 simulation design, ToyTree was more reliable than `ape::chronos` for every shared workflow and was at least as accurate on comparison-eligible paired fits. This is a scoped simulation result, not a claim of universal superiority. It supports release of ToyTree's strict clock, explicit-category discrete model, and fixed-lambda correlated model; `relaxed` is retained for chronos compatibility. ToyTree additionally offers the validated fixed-lambda UCLN model, recommended for new continuous uncorrelated-rate analyses.

No speed claim is made. Accuracy jobs ran concurrently, and the timing pilot was neither large enough nor a controlled confirmation benchmark.

![Convergence comparison](figure-reliability.svg)

| Model | ToyTree converged | ape converged | Paired age-MAE difference (95% interval) |
|---|---:|---:|---:|
{chr(10).join(table)}

![Paired accuracy comparison](figure-accuracy.svg)

Negative paired differences favor ToyTree. Accuracy summaries exclude nonconverged or calibration-invalid fits; convergence is therefore reported alongside accuracy. Full values are in [table-model-comparison.csv](table-model-comparison.csv).

## What is comparable

Strict clock, discrete K=2/K=3, and relaxed implement the corresponding chronos objectives. Correlated expresses the same biological idea but is not objective-identical: ToyTree smooths adjacent log rates and connects basal branches through a profiled root log rate. UCLN has no chronos counterpart here. The [scope table](table-release-scope.csv) records these distinctions.

The confirmation contained {v17['datasets']} dataset-engine scenarios and {v17['fit_tasks']} fit tasks. ToyTree convergence was 0.998 for clock, 1.000 for correlated and both discrete settings, 0.935 for relaxed, and 1.000 for UCLN. Corresponding ape convergence was 0.571, 0.350, 0.540, 0.525, and 0.713. A production-budget replay resolved 31 relaxed failures but left {remaining} strict-clock fit nonconverged; the common-budget confirmation is the primary fair comparison.

## Accuracy interpretation

Among comparison-eligible pairs, ToyTree had lower normalized age MAE for clock, discrete K=2, correlated, and relaxed. Discrete K=3 was statistically indistinguishable because its interval crossed zero. The largest gain was for relaxed, although the engines can occupy different basins under its unusual Gamma-CDF convention. These simulations do not address topology error, calibration misspecification, heterochronous tips, or propagation of branch-length estimation uncertainty.

## Lambda decision

Automatic lambda estimation is not in the final API. In V18, correlated per-tree CV selected a grid boundary in {c['boundary_selection_fraction']:.1%} of datasets; median supported chronogram spread was {c['supported_chronogram_spread_median']:.3f} and its 90th percentile was {c['supported_chronogram_spread_p90']:.3f}. UCLN recovery was better, but boundary selection still occurred in {u['boundary_selection_fraction']:.1%} and its spread 90th percentile was {u['supported_chronogram_spread_p90']:.3f}. This does not justify a general point estimator from one tree. Users must supply lambda and report sensitivity across scientifically plausible values.

## Reproducibility

This report is generated deterministically by [generate_report.py](generate_report.py); [manifest.json](manifest.json) hashes all inputs and outputs. Historical runners and rejected algorithms are recoverable from the pinned [archive manifest](../archive/README.md). The oversized V18 result lives only in Git history, with exact recovery metadata in its compact summary.
"""


def generate(out):
    out.mkdir(parents=True, exist_ok=True)
    source = {k: read(v) for k, v in INPUTS.items()}
    data = rows(source["v17"])
    write_csv(out / "table-model-comparison.csv", data)
    workflow = source["ledger"]["workflows"]
    selected = (
        "clock",
        "discrete",
        "correlated",
        "uncorrelated_lognormal",
        "relaxed",
        "automatic_lambda_selection",
        "discrete_gamma",
        "phiic",
    )
    scope = [
        {
            "workflow": k,
            "status": workflow[k]["status"],
            "public_api": workflow[k].get("public_api") or "",
            "scope": workflow[k].get("scope", ""),
        }
        for k in selected
    ]
    write_csv(out / "table-release-scope.csv", scope)
    (out / "figure-reliability.svg").write_text(reliability_svg(data))
    (out / "figure-accuracy.svg").write_text(accuracy_svg(data))
    (out / "REPORT.md").write_text(
        report(data, source["v17"], source["replay"], source["v18"])
    )
    names = (
        "REPORT.md",
        "table-model-comparison.csv",
        "table-release-scope.csv",
        "figure-reliability.svg",
        "figure-accuracy.svg",
    )
    manifest = {
        "schema_version": 1,
        "generator": "validation/penalized_pseudolikelihood/final-report/generate_report.py",
        "inputs": {
            str(p.relative_to(ROOT.parents[1])): sha(p) for p in INPUTS.values()
        },
        "outputs": {n: sha(out / n) for n in names},
        "speed_claims": False,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        generate(HERE)
        return
    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp)
        generate(candidate)
        names = (
            "REPORT.md",
            "table-model-comparison.csv",
            "table-release-scope.csv",
            "figure-reliability.svg",
            "figure-accuracy.svg",
            "manifest.json",
        )
        stale = [
            n
            for n in names
            if not (HERE / n).is_file()
            or (HERE / n).read_bytes() != (candidate / n).read_bytes()
        ]
        if stale:
            raise SystemExit("stale generated report files: " + ", ".join(stale))


if __name__ == "__main__":
    main()
