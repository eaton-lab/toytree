#!/usr/bin/env python

"""Runtime implementation for the `make-ultrametric` CLI command."""

from __future__ import annotations

import json
import math
import sys

from .subparsers import NEGATIVE_CAL_QUERY_PREFIX


def _jsonify_value(value):
    """Return value converted to JSON-serializable Python types."""
    if value is None:
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (list, tuple)):
        return [_jsonify_value(i) for i in value]
    if isinstance(value, dict):
        return {str(k): _jsonify_value(v) for k, v in value.items()}
    return value


def _parse_calibration_value(text: str):
    """Parse one calibration as float or (low, high) tuple."""
    import re

    text = text.strip()
    rng = re.match(
        r"^([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*-\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)$",
        text,
    )
    if rng:
        low = float(rng.group(1))
        high = float(rng.group(2))
        if low > high:
            raise ValueError(f"invalid calibration range '{text}' (min > max)")
        return (low, high)
    return float(text)


def _parse_calibrations(
    tree, items: list[str] | None
) -> dict[int, float | tuple[float, float]]:
    """Parse calibration args as query=value or query=min-max."""
    if not items:
        return {}
    calibrations = {}
    for item in items:
        if "=" not in item:
            raise ValueError(
                f"calibration must be query=value or query=min-max, got: '{item}'"
            )
        query, value = item.split("=", 1)
        query = query.strip()
        value = value.strip()
        if query.startswith(NEGATIVE_CAL_QUERY_PREFIX):
            query = "-" + query.removeprefix(NEGATIVE_CAL_QUERY_PREFIX)
        if not query or not value:
            raise ValueError(f"invalid calibration entry: '{item}'")

        try:
            selector = int(query)
        except ValueError:
            selector = query
        nodes = tree.get_nodes(selector)
        if len(nodes) != 1:
            raise ValueError(
                f"calibration query '{query}' matched {len(nodes)} nodes; "
                "must match exactly one node."
            )
        if nodes[0].is_leaf():
            raise ValueError(
                "tip calibrations are not supported; heterochronous tips are "
                "not implemented."
            )
        calibration = _parse_calibration_value(value)
        values = (calibration,) if isinstance(calibration, float) else calibration
        if any(i < 0.0 for i in values):
            raise ValueError("calibration ages must be non-negative.")
        calibrations[nodes[0].idx] = calibration
    return calibrations


def run_make_ultrametric(args):
    """Run the `make-ultrametric` CLI command."""
    from toytree.cli._tree_transport import (
        read_tree_auto,
        resolve_input_arg,
        write_tree_output,
    )
    from toytree.utils import ToytreeError

    tre = read_tree_auto(
        resolve_input_arg(args.input), internal_labels=args.internal_labels
    )
    calibrations = _parse_calibrations(tre, args.calibrations)
    report_full = bool((args.full or args.json) and args.method != "extend")
    if args.method == "discrete" and args.ncat is None:
        raise ToytreeError("--ncat is required when --method discrete is used.")

    if args.method == "extend":
        if calibrations or args.ncat is not None or args.lam is not None:
            raise ToytreeError(
                "calibrations, --ncat, and --lam are not valid with --method extend."
            )
        result = tre.mod.edges_extend_tips_to_align(inplace=False)
    else:
        result = tre.mod.edges_make_ultrametric(
            method=args.method,
            calibrations=calibrations,
            ncategories=args.ncat,
            lam=args.lam,
            full=report_full,
            inplace=False,
            max_iter=args.max_iter,
            max_fun=args.max_fun,
            max_refine=args.max_refine,
            nstarts=args.nstarts,
            ncores=args.ncores,
            seed=args.seed,
        )
    if report_full:
        if args.json:
            payload = {"method": args.method}
            for key, val in result.items():
                if key != "tree":
                    payload[str(key)] = _jsonify_value(val)
            print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            for key, val in result.items():
                if key != "tree":
                    print(f"{key}={val}", file=sys.stderr)
        tre = result["tree"]
    else:
        tre = result

    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {"name", "height", "dist", "support"}

    write_tree_output(
        tre,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
    )
