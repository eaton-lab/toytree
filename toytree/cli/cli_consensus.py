#!/usr/bin/env python

"""Runtime implementation for the `consensus` CLI command."""

from __future__ import annotations

import io
import sys
from pathlib import Path


def _read_multitree_text(input_arg: str) -> str:
    """Return multitree text from stdin, path, or direct string input."""
    if input_arg == "-":
        data = io.TextIOWrapper(
            io.BytesIO(sys.stdin.buffer.read()),
            encoding="utf-8",
            errors="strict",
        ).read()
        return data
    path = Path(input_arg)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return input_arg


def _parse_multitree_text(text: str, internal_labels: str | None = None):
    """Parse raw multi-tree text into a `MultiTree` instance."""
    from toytree.core.multitree import MultiTree
    from toytree.io.src.newick import parse_newick_string
    from toytree.io.src.parse import (
        parse_data_from_str,
        parse_generic_to_str,
        translate_node_names,
    )

    strdata = parse_generic_to_str(text)
    nwks, tdict = parse_data_from_str(strdata)
    treelist = []
    for nwk in nwks:
        tree = parse_newick_string(nwk, internal_labels=internal_labels)
        treelist.append(translate_node_names(tree, tdict))
    return MultiTree(treelist)


def run_consensus(args) -> None:
    """Run the `consensus` CLI command."""
    from toytree.cli._tree_transport import write_tree_output
    from toytree.infer import consensus_features, consensus_tree
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    text = _read_multitree_text(args.input)
    mtree = _parse_multitree_text(text, internal_labels=args.internal_labels)

    ctree = consensus_tree(mtree.treelist, min_freq=args.min_freq)
    if args.features or args.edge_features:
        ctree = consensus_features(
            tree=ctree,
            trees=mtree.treelist,
            features=args.features,
            edge_features=args.edge_features,
            ultrametric=args.ultrametric,
            conditional=args.conditional,
        )

    if args.exclude_features:
        features = None
    else:
        features = set(ctree.features) - {"name", "height", "dist", "support"}
    write_tree_output(
        ctree,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
    )
