#!/usr/bin/env python

"""Command line interface for consensus tree inference."""

from __future__ import annotations

import io
import sys
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from toytree.core.multitree import MultiTree
from toytree.io.src.newick import parse_newick_string
from toytree.io.src.parse import parse_data_from_str, parse_generic_to_str, translate_node_names


KWARGS = dict(
    prog="consensus",
    usage="consensus [options]",
    help="infer a consensus tree from a multi-tree input",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=120, max_help_position=120
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------
        | consensus: infer consensus tree from a single multi-tree input
        -------------------------------------------------------------------
        | Input can be a multi-Newick/Nexus file path, a string, or stdin.
        | Optionally map selected node/edge features to the consensus tree.
        -------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        $ consensus -i TREES.nwk
        $ consensus -i TREES.nwk -m 0.5
        $ consensus -i TREES.nwk --edge-features dist support
        $ consensus -i TREES.nwk --features height --ultrametric
        $ cat TREES.nwk | consensus -i - -m 0.5 -o CONS.nwk
        $ consensus -i TREES.nwk -b | draw -i - -v
        """
    ),
)


def _read_multitree_text(input_arg: str) -> str:
    """Return multitree text from stdin/path/string input."""
    if input_arg == "-":
        data = io.TextIOWrapper(io.BytesIO(sys.stdin.buffer.read()), encoding="utf-8", errors="strict").read()
        return data
    path = Path(input_arg)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return input_arg


def _parse_multitree_text(text: str, internal_labels: str | None = None) -> MultiTree:
    """Parse multi-tree text into a MultiTree without relying on mtree parser state."""
    strdata = parse_generic_to_str(text)
    nwks, tdict = parse_data_from_str(strdata)
    treelist = []
    for nwk in nwks:
        tree = parse_newick_string(nwk, internal_labels=internal_labels)
        treelist.append(translate_node_names(tree, tdict))
    return MultiTree(treelist)


def get_parser_consensus(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for consensus command."""
    if parser:
        kwargs = dict(KWARGS)
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs = dict(KWARGS)
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        required=True,
        help="input multi-tree file/string, or '-' for stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output path; default writes to stdout",
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
        help="do not include node features in output newick",
    )

    consensus_group = p.add_argument_group(title="Consensus")
    consensus_group.add_argument(
        "-m",
        "--min-freq",
        type=float,
        default=0.0,
        metavar="float",
        help="minimum split frequency for consensus inclusion [0.0]",
    )

    map_group = p.add_argument_group(title="Feature Mapping")
    map_group.add_argument(
        "-f",
        "--features",
        type=str,
        nargs="+",
        metavar="str",
        help="node feature names to summarize onto consensus tree",
    )
    map_group.add_argument(
        "-F",
        "--edge-features",
        type=str,
        nargs="+",
        metavar="str",
        help="edge feature names to summarize onto consensus tree",
    )
    map_group.add_argument(
        "-u",
        "--ultrametric",
        action="store_true",
        help="require rooted ultrametric sources (for height feature summaries)",
    )
    map_group.add_argument(
        "-c",
        "--conditional",
        action="store_true",
        help="use conditional split-dependent mapping where supported",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-l",
        "--log-level",
        type=str,
        metavar="level",
        default=None,
        help="set toytree logger level (DEBUG, INFO, WARNING, ERROR)",
    )
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )
    return p


def run_consensus(args) -> None:
    """Run consensus command."""
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


def main():
    parser = get_parser_consensus()
    args = parser.parse_args()
    run_consensus(args)


if __name__ == "__main__":
    main()
