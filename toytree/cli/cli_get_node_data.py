#!/usr/bin/env python

"""Runtime implementation for the `get-node-data` CLI command."""

from __future__ import annotations

import math
import sys


def _jsonify_value(value):
    """Return value converted to JSON-serializable Python types."""
    if value is None:
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (list, tuple)):
        return [_jsonify_value(i) for i in value]
    if isinstance(value, dict):
        return {str(k): _jsonify_value(v) for k, v in value.items()}
    return value


def run_get_node_data(args):
    """Run the `get-node-data` CLI command."""
    import pandas as pd

    from toytree.cli._tree_transport import read_tree_auto, resolve_input_arg

    tre = read_tree_auto(
        resolve_input_arg(args.input), internal_labels=args.internal_labels
    )

    if args.tips_only:
        data = tre.get_tip_data(args.features, missing=args.missing)
    else:
        data = tre.get_node_data(args.features, missing=args.missing)

    # Normalize single-feature output to DataFrame with a stable feature column.
    if isinstance(data, pd.Series):
        if args.features and len(args.features) == 1:
            colname = str(args.features[0])
        elif data.name is not None:
            colname = str(data.name)
        else:
            colname = "value"
        data = data.to_frame(name=colname)

    if args.nodes:
        nodes = tre.get_nodes(*args.nodes)
        data = data.loc[[node.idx for node in nodes]]

    if args.index_by_name:
        labels = []
        for idx in data.index:
            node = tre[int(idx)]
            name = str(node.name) if node.name is not None else ""
            labels.append(name if name.strip() else idx)
        data = data.copy()
        data.index = labels

    if args.json:
        out = data.to_json(
            orient="index",
            force_ascii=False,
            indent=2,
            default_handler=_jsonify_value,
        )
        if args.output:
            args.output.write_text(f"{out}\n", encoding="utf-8")
        else:
            sys.stdout.write(f"{out}\n")
    elif args.human_readable:
        datastr = data.to_string(float_format=args.float_format)
        if args.output:
            args.output.write_text(f"{datastr}\n", encoding="utf-8")
        else:
            sys.stdout.write(f"{datastr}\n")
    else:
        out = sys.stdout if args.output is None else args.output
        data.to_csv(out, sep=args.separator, float_format=args.float_format)
