#!/usr/bin/env python

"""Runtime implementation for the `get-node-data` CLI command."""

from __future__ import annotations

import sys


def run_get_node_data(args):
    """Run the `get-node-data` CLI command."""
    import pandas as pd

    from toytree.cli._tree_transport import read_tree_auto

    if args.log_level is not None:
        from toytree.utils.src.logger_setup import set_log_level

        set_log_level(args.log_level)

    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

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

    if args.human_readable:
        datastr = data.to_string(float_format=args.float_format)
        if args.output:
            args.output.write_text(f"{datastr}\n", encoding="utf-8")
        else:
            sys.stdout.write(f"{datastr}\n")
    else:
        out = sys.stdout if args.output is None else args.output
        data.to_csv(out, sep=args.separator, float_format=args.float_format)
