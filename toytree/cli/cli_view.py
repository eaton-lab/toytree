#!/usr/bin/env python

"""Runtime handler for the text-tree view CLI."""

from __future__ import annotations


def run_view(args):
    """Run the text tree viewer command."""
    from toytree.cli._tree_transport import read_tree_auto, resolve_input_arg

    tree = read_tree_auto(
        resolve_input_arg(args.input),
        internal_labels=args.internal_labels,
    )
    tree.view(
        width=args.width,
        tip_labels=args.tip_labels,
        charset=args.charset,
        use_edge_lengths=args.use_edge_lengths,
        heavy=args.heavy,
        heavier=args.heavier,
        ladderize=args.ladderize,
    )
    return 0
