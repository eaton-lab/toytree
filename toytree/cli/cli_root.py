#!/usr/bin/env python

"""Runtime implementation for the `root` CLI command."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _apply_delim_map(
    labels: list[str],
    *,
    delim: str | None,
    delim_idxs: list[int] | None,
    delim_join: str,
) -> dict[str, str]:
    """Return gene->species mapping by delimiter parsing gene labels."""
    from toytree.utils import ToytreeError

    mapping: dict[str, str] = {}
    for name in labels:
        if not delim:
            mapping[name] = name
            continue
        parts = re.split(delim, name)
        if delim_idxs:
            try:
                parts = [parts[i] for i in delim_idxs]
            except IndexError as exc:
                raise ToytreeError(
                    f"--delim-idxs has out-of-range index for label '{name}'."
                ) from exc
        mapping[name] = delim_join.join(parts)
    return mapping


def _load_imap(path: Path, sep: str) -> dict[str, str]:
    """Load 2-column gene->species mapping table from file."""
    import pandas as pd

    from toytree.utils import ToytreeError

    data = pd.read_csv(path, sep=sep, header=None, comment="#", dtype=str)
    if data.shape[1] < 2:
        raise ToytreeError("--imap must have at least two columns: gene and species.")
    data = data.iloc[:, :2].dropna(axis=0, how="any")
    if data.empty:
        raise ToytreeError("--imap did not contain usable gene/species rows.")
    mapping = dict(zip(data.iloc[:, 0], data.iloc[:, 1], strict=False))
    if not mapping:
        raise ToytreeError("--imap could not be parsed into gene->species mapping.")
    return mapping


def run_root(args):
    """Run the `root` CLI command."""
    from toytree.cli._tree_transport import (
        read_tree_auto,
        resolve_input_arg,
        write_tree_output,
    )
    from toytree.mod._src.root_funcs import (
        root_on_minimal_ancestor_deviation,
        root_on_minimal_dlc,
    )
    from toytree.mod._src.root_unroot import root
    from toytree.utils import ToytreeError

    # parse the tree
    tre = read_tree_auto(
        resolve_input_arg(args.input), internal_labels=args.internal_labels
    )

    # Normalize optional list args from argparse (`nargs="*"` can be None).
    nodes = args.nodes or []
    edge_features = args.edge_features or []

    # Validate rooting mode.
    if args.mad and args.dlc:
        raise ToytreeError("Use only one rooting mode: --mad or --dlc.")
    if args.dlc and nodes:
        raise ToytreeError("--nodes cannot be used together with --dlc.")
    if args.min_dist != 1e-12 and (not args.mad):
        raise ToytreeError("--min-dist is only valid with --mad.")
    if not args.dlc and any(
        [
            args.species_tree,
            args.imap,
            args.delim,
            args.delim_idxs,
            args.imap_sep != "\t",
            args.delim_join != "_",
            args.wdup != 3.0,
            args.wloss != 1.0,
            args.wcoal != 0.0,
        ]
    ):
        raise ToytreeError("DLC options require --dlc.")
    if (not nodes) and (not args.mad) and (not args.dlc):
        raise ToytreeError("root requires -n/--nodes unless --mad or --dlc is used.")

    # Root by selected mode.
    if args.dlc:
        if not args.species_tree:
            raise ToytreeError("--species-tree is required with --dlc.")
        sptree = read_tree_auto(args.species_tree)

        # Build imap from file or by direct/delimited name matching.
        if args.imap:
            imap = _load_imap(args.imap, sep=args.imap_sep)
        else:
            imap = _apply_delim_map(
                tre.get_tip_labels(),
                delim=args.delim,
                delim_idxs=args.delim_idxs,
                delim_join=args.delim_join,
            )

        _, stats = root_on_minimal_dlc(
            tre,
            sptree,
            imap=imap,
            inplace=True,
            return_stats=True,
            store_scores=args.stats,
            weight_duplications=float(args.wdup),
            weight_losses=float(args.wloss),
            weight_coalescences=float(args.wcoal),
            edge_features=edge_features,
        )
        print(f"best_edge_idx={stats['best_edge_idx']}", file=sys.stderr)
        print(f"best_score={stats['best_score']}", file=sys.stderr)
        print(f"n_candidates={stats['n_candidates']}", file=sys.stderr)
        print(f"n_tied_best={stats['n_tied_best']}", file=sys.stderr)
    elif args.mad:
        _, mdict = root_on_minimal_ancestor_deviation(
            tre,
            *nodes,
            inplace=True,
            return_stats=True,
            min_dist=args.min_dist,
            edge_features=edge_features,
        )
        # Always report MAD summary statistics to stderr.
        for key, value in mdict.items():
            print(f"{key}={value}", file=sys.stderr)

        # By default do not keep MAD score edge-feature data in output.
        if not args.stats:
            tre.remove_features("MAD", "MAD_root_prob", inplace=True)
    else:
        root(tre, *nodes, inplace=True, edge_features=edge_features)

    # write tree with or wi/o feature data
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
