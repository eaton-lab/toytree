#!/usr/bin/env python

"""Runtime implementation for the `distance` CLI command."""

from __future__ import annotations

import json
import sys


def _write_result(args, text: str) -> None:
    """Write command output to file or stdout."""
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


def _write_json_result(args, payload: dict) -> None:
    """Write JSON payload to file or stdout."""
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    _write_result(args, text)


def run_distance(args) -> None:
    """Run the `distance` CLI command."""
    from toytree.distance import (
        get_treedist_quartets,
        get_treedist_rf,
        get_treedist_rfg_mci,
        get_treedist_rfg_ms,
        get_treedist_rfg_msi,
        get_treedist_rfg_spi,
        get_treedist_rfi,
    )
    from toytree.distance._src.quartet_dist import get_quartet_metric
    from toytree.io.src.treeio import tree
    from toytree.utils import ToytreeError

    if args.tree1 == "-" and args.tree2 == "-":
        raise ToytreeError("only one of --tree1/--tree2 can read from stdin ('-').")

    t1 = tree(args.tree1)
    t2 = tree(args.tree2)

    scalar_metric_funcs = {
        "rf": get_treedist_rf,
        "rfi": get_treedist_rfi,
        "rfg_ms": get_treedist_rfg_ms,
        "rfg_msi": get_treedist_rfg_msi,
        "rfg_spi": get_treedist_rfg_spi,
        "rfg_mci": get_treedist_rfg_mci,
    }

    if args.metric in scalar_metric_funcs:
        value = scalar_metric_funcs[args.metric](t1, t2, normalize=args.normalize)
        if args.json:
            _write_json_result(
                args,
                {
                    "metric": args.metric,
                    "value": float(value),
                    "normalize": bool(args.normalize),
                },
            )
            return
        _write_result(args, args.float_format % float(value))
        return

    if args.metric == "quartet":
        value = get_quartet_metric(
            t1,
            t2,
            metric=args.quartet_metric,
            similarity=args.similarity,
        )
        if args.json:
            _write_json_result(
                args,
                {
                    "metric": "quartet",
                    "quartet_metric": args.quartet_metric,
                    "similarity": bool(args.similarity),
                    "value": float(value),
                },
            )
            return
        _write_result(args, args.float_format % float(value))
        return

    # quartet-all: emit tabular metric-value lines.
    qseries = get_treedist_quartets(t1, t2, similarity=args.similarity)
    if args.json:
        _write_json_result(
            args,
            {
                "metric": "quartet-all",
                "similarity": bool(args.similarity),
                "values": {str(name): float(val) for name, val in qseries.items()},
            },
        )
        return
    lines = [
        f"{name}\t{args.float_format % float(val)}" for name, val in qseries.items()
    ]
    _write_result(args, "\n".join(lines))
