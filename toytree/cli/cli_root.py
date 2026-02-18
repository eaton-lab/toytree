#!/usr/bin/env python

"""

"""

import sys
from pathlib import Path
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter


KWARGS = dict(
    prog="root",
    usage="root [options]",
    help="root a tree on an outgroup edge or via MAD optimization",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(prog, width=120, max_help_position=120),
    description=textwrap.dedent("""
        -------------------------------------------------------------------
        | root: root trees using outgroup queries or MAD optimization
        -------------------------------------------------------------------
        | Use -n/--nodes to choose an outgroup (MRCA-based rooting), or
        | use -m/--mad to infer a root from branch-length information.
        | If both are provided, MAD optimizes root position on that edge.
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

        # Emit binary ToyTree for fast piping to another command
        $ root -i TRE.nwk -n R -b | prune -i - -n A B > PRUNED.nwk
    """)
)
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
    options_group = parser.add_argument_group(title="Options")
    options_group.add_argument(
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
    options_group.add_argument(
        "-m",
        "--mad",
        action="store_true",
        help="infer root by MAD; with --nodes, optimize on selected outgroup edge",
    )
    options_group.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="with --mad, keep MAD and MAD_root_prob edge features in output",
    )
    options_group.add_argument(
        "-d",
        "--min-dist",
        type=float,
        metavar="float",
        default=1e-12,
        help="MAD only: minimum edge-length floor for zero-length edges [1e-12]",
    )

    # Feature handling
    options_group.add_argument(
        "-e",
        "--edge-features",
        type=str,
        metavar="str",
        nargs="*",
        help="additional edge features to re-polarize during rooting",
    )
    general_group = parser.add_argument_group(title="General")
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
    # parser.add_argument("-L", "--log-file", type=Path, metavar="path", help="append stderr log to a file")
    return parser


def run_root(args):
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.mod._src.root_funcs import root_on_minimal_ancestor_deviation
    from toytree.mod._src.root_unroot import root
    from toytree.utils.src.logger_setup import set_log_level
    if args.log_level is not None:
        set_log_level(args.log_level)

    # parse the tree
    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

    # Normalize optional list args from argparse (`nargs="*"` can be None).
    nodes = args.nodes or []
    edge_features = args.edge_features or []

    # Require outgroup node queries unless MAD rooting is requested.
    if (not nodes) and (not args.mad):
        raise ValueError("root requires -n/--nodes unless --mad is used.")

    # root
    if args.mad:
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

        # By default do not keep MAD edge-feature data in output.
        if not args.stats:
            tre.remove_features("MAD", "MAD_root_prob", inplace=True)
    else:
        root(tre, *nodes, inplace=True, edge_features=edge_features)

    # write tree with or wi/o feature data
    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {'name', 'height', 'dist', 'support'}
    write_tree_output(
        tre,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
    )


def main():
    parser = get_parser_root()
    args = parser.parse_args()
    run_root(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
