#!/usr/bin/env python

"""CLI for rooting trees by outgroup queries, MAD, or DLC reconciliation."""

import re
import sys
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

import pandas as pd

from toytree.utils import ToytreeError

KWARGS = dict(
    prog="root",
    usage="root [options]",
    help="root a tree using outgroup, MAD, or DLC optimization",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog,
        width=120,
        max_help_position=120,
    ),
    description=textwrap.dedent("""
        -------------------------------------------------------------------
        | root: root trees using outgroup queries, MAD, or DLC optimization
        -------------------------------------------------------------------
        | outgroup mode: use -n/--nodes to set an outgroup edge by MRCA.
        | MAD mode     : use -m/--mad (optionally with -n to constrain edge).
        | DLC mode     : use --dlc with --species-tree (and optional --imap).
        -------------------------------------------------------------------
    """),
    epilog=textwrap.dedent("""
        Examples
        --------
        # Root by outgroup query (single taxon)
        $ root -i TRE.nwk -n R > RTRE.nwk

        # Root by outgroup regex query
        $ root -i TRE.nwk -n ~prefix -o RTRE.nwk

        # Infer root with MAD (no outgroup required)
        $ root -i TRE.nwk --mad > RTRE.nwk

        # Constrain to a selected edge and optimize placement with MAD
        $ root -i TRE.nwk -n A B C --mad > RTRE.nwk

        # Keep MAD features and parse internal labels as support
        $ root -i TRE.nwk --mad --stats -I support > RTRE.nwk

        # Infer root with DLC reconciliation using explicit imap
        $ root -i GENE.nwk --dlc --species-tree SPECIES.nwk --imap IMAP.tsv > RTRE.nwk

        # Infer root with DLC reconciliation using exact tip-name matching
        $ root -i GENE.nwk --dlc --species-tree SPECIES.nwk > RTRE.nwk

        # Infer root with DLC and delimiter parsing for gene->species matching
        $ root -i GENE.nwk --dlc --species-tree SPECIES.nwk --delim '|' \\
            --delim-idxs 0 > RTRE.nwk

        # Emit binary ToyTree for fast piping to another command
        $ root -i TRE.nwk -n R -b | prune -i - -n A B > PRUNED.nwk
    """),
)


def _apply_delim_map(
    labels: list[str],
    *,
    delim: str | None,
    delim_idxs: list[int] | None,
    delim_join: str,
) -> dict[str, str]:
    """Return gene->species mapping by delimiter parsing gene labels."""
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


def get_parser_root(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Create argparse parser for the `root` CLI command."""
    # create parser or connect as subparser to cli parser
    if parser:
        kwargs = dict(KWARGS)
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        parser = parser.add_parser(**kwargs)
    else:
        kwargs = dict(KWARGS)
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        parser = ArgumentParser(**kwargs)

    # I/O
    io_group = parser.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        required=True,
        help="input tree path (newick/nexus/nhx), or '-' to read from stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output path; if omitted, writes rooted tree to stdout",
    )
    io_group.add_argument(
        "-b",
        "--binary-out",
        action="store_true",
        help="write output as binary pickled ToyTree for fast piping between commands",
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="Parse internal labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="write tree without extra node features (only default structural fields)",
    )

    # Rooting selection / method
    mode_group = parser.add_argument_group(title="Rooting Mode")
    mode_group.add_argument(
        "-n",
        "--nodes",
        type=str,
        metavar="str",
        nargs="*",
        help=(
            "one or more node queries (name, idx label, or regex with '~'). "
            "The MRCA of selected nodes is treated as the outgroup edge."
        ),
    )
    mode_group.add_argument(
        "-m",
        "--mad",
        action="store_true",
        help="infer root by MAD; with --nodes, optimize on selected outgroup edge",
    )
    mode_group.add_argument(
        "--dlc",
        action="store_true",
        help="infer root by minimizing weighted DLC reconciliation score",
    )

    mad_group = parser.add_argument_group(title="MAD Options")
    mad_group.add_argument(
        "-d",
        "--min-dist",
        type=float,
        metavar="float",
        default=1e-12,
        help="MAD only: minimum edge-length floor for zero-length edges [1e-12]",
    )

    dlc_group = parser.add_argument_group(title="DLC Options")
    dlc_group.add_argument(
        "--species-tree",
        type=str,
        metavar="path",
        help="DLC only: rooted species tree path",
    )
    dlc_group.add_argument(
        "--species-internal-labels",
        type=str,
        metavar="str",
        help="DLC only: parse species-tree internal labels as this feature",
    )
    dlc_group.add_argument(
        "--imap",
        type=Path,
        metavar="path",
        help="DLC only: 2-column gene-to-species mapping table",
    )
    dlc_group.add_argument(
        "--imap-sep",
        type=str,
        metavar="str",
        default="\t",
        help="DLC only: delimiter for --imap table [\\t]",
    )
    dlc_group.add_argument(
        "--delim",
        type=str,
        metavar="str",
        help="DLC only: regex delimiter for deriving species labels from gene labels",
    )
    dlc_group.add_argument(
        "--delim-idxs",
        type=int,
        metavar="int",
        nargs="+",
        help="DLC only: token indices to keep after --delim split",
    )
    dlc_group.add_argument(
        "--delim-join",
        type=str,
        metavar="str",
        default="_",
        help="DLC only: joiner for selected --delim-idxs tokens ['_']",
    )
    dlc_group.add_argument(
        "--wdup",
        type=float,
        metavar="float",
        default=3.0,
        help="DLC only: duplication weight [3.0]",
    )
    dlc_group.add_argument(
        "--wloss",
        type=float,
        metavar="float",
        default=1.0,
        help="DLC only: loss weight [1.0]",
    )
    dlc_group.add_argument(
        "--wcoal",
        type=float,
        metavar="float",
        default=0.0,
        help="DLC only: coalescence weight [0.0]",
    )

    feature_group = parser.add_argument_group(title="Feature Handling")
    feature_group.add_argument(
        "-e",
        "--edge-features",
        type=str,
        metavar="str",
        nargs="*",
        help="additional edge features to re-polarize during rooting",
    )
    feature_group.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="keep per-edge score features in output (MAD* or DLC*)",
    )

    general_group = parser.add_argument_group(title="Options")
    general_group.add_argument(
        "-l",
        "--log-level",
        type=str,
        metavar="level",
        default=None,
        help="set toytree logger level (DEBUG, INFO, WARNING, ERROR)",
    )
    general_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )
    # parser.add_argument(
    #     "-L",
    #     "--log-file",
    #     type=Path,
    #     metavar="path",
    #     help="append stderr log to a file",
    # )
    return parser


def run_root(args):
    """Run root command."""
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.mod._src.root_funcs import (
        root_on_minimal_ancestor_deviation,
        root_on_minimal_dlc,
    )
    from toytree.mod._src.root_unroot import root
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    # parse the tree
    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

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
            args.species_internal_labels,
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
        sptree = read_tree_auto(
            args.species_tree,
            internal_labels=args.species_internal_labels,
        )

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


def main():
    """Run root CLI as a standalone entrypoint."""
    parser = get_parser_root()
    args = parser.parse_args()
    run_root(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
