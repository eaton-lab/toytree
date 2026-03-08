#!/usr/bin/env python

"""Runtime implementation for the `prune` CLI command."""

from __future__ import annotations


def run_prune(args):
    """Run the `prune` CLI command."""
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.mod._src.mod_topo import prune
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    # parse the tree
    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

    # operate
    tre = prune(
        tre,
        *(args.nodes or []),
        preserve_dists=(not args.not_preserve_dists),
        require_root=args.require_root,
    )

    # write tree with or without feature data
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
