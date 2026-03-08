#!/usr/bin/env python

"""Runtime implementation for the `get-node-data` CLI command."""

from __future__ import annotations

import sys


def run_get_node_data(args):
    """Run the `get-node-data` CLI command."""
    from toytree.io.src.treeio import tree
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    intree = sys.stdin.read() if args.input == "-" else args.input
    tre = tree(intree, internal_labels=args.internal_labels)

    if args.tips_only:
        data = tre.get_tip_data(args.features, missing=args.missing)
    else:
        data = tre.get_node_data(args.features, missing=args.missing)

    if args.nodes:
        nodes = tre.get_nodes(*args.nodes)
        data = data.loc[[node.idx for node in nodes], :]

    if args.human_readable:
        datastr = data.to_string(float_format=args.float_format)
        if args.output:
            args.output.write_text(f"{datastr}\n", encoding="utf-8")
        else:
            sys.stdout.write(f"{datastr}\n")
    else:
        out = sys.stdout if args.output is None else args.output
        data.to_csv(out, sep=args.separator, float_format=args.float_format)
