#!/usr/bin/env python

"""
"""

import sys
from pathlib import Path
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from .make_wide import make_wide
from loguru import logger


KWARGS = dict(
    prog="root",
    usage="root [options]",
    help="return ...",
    formatter_class=make_wide(RawDescriptionHelpFormatter, 120, 140),
    description=textwrap.dedent("""
        -------------------------------------------------------------------
        | root: return tree with only branches connecting a subset of tips
        -------------------------------------------------------------------
        | The root method ...
        -------------------------------------------------------------------
    """),
    epilog=textwrap.dedent("""
        Examples
        --------
        $ root -i TRE.nwk -n R > RTRE.nwk
        $ root -i TRE.nwk -n '~prefix' -o RTRE.nwk
        $ root -i TRE.nwk -n A B C --mad > RTRE.nwk
        $ root -i TRE.nwk --mad > RTRE.nwk
    """)
)


def get_parser_root(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return a parser tool for this method.
    """
    # create parser or connect as subparser to cli parser
    if parser:
        KWARGS['name'] = KWARGS.pop("prog")
        parser = parser.add_parser(**KWARGS)
    else:
        KWARGS.pop("help")
        parser = ArgumentParser(**KWARGS)

    # path args
    parser.add_argument("-i", "--input", type=Path, metavar="path", required=True, help="input tree file (nwk, nex or nhx)")
    parser.add_argument("-o", "--output", type=Path, metavar="path", help="optional outfile path name. If None prints to STDOUT")
    parser.add_argument("-n", "--nodes", type=str, metavar="str", nargs="*", help="one or more names or regular expressions to select outgroup mrca")
    # options
    parser.add_argument("-I", "--internal-labels", type=str, metavar="str", help="parse internal node feature (e.g., support) [auto]")
    parser.add_argument("-m", "--mad", action="store_true", help="use minimal-ancestor-deviation rooting")
    parser.add_argument("-e", "--edge-features", type=str, metavar="str", nargs="*", help="one or more edge features on tree that should be re-polarized")
    parser.add_argument("-s", "--stats", action="store_true", help="return tree and mad stats")
    parser.add_argument("-d", "--min-dist", type=float, default=1e-12, help="zero-length edges set to min_dist [1e-12] during mad to prevent division.")
    parser.add_argument("-l", "--log-level", type=str, metavar="level", default="INFO", help="stderr logging level (DEBUG, [INFO], WARNING, ERROR)")
    # parser.add_argument("-L", "--log-file", type=Path, metavar="path", help="append stderr log to a file")
    return parser


def run_root(args):
    from toytree.io.src.treeio import tree
    from toytree.mod._src.root_funcs import root_on_minimal_ancestor_deviation
    from toytree.mod._src.root_unroot import root
    # from toytree.utils.src.logger_setup import set_log_level
    # set_log_level(args.log_level)

    # parse the tree
    if args.input == Path("-"):
        data = sys.stdin.read()
        tre = tree(data, internal_labels=args.internal_labels)
    else:
        data = args.input.expanduser().absolute()
        tre = tree(data, internal_labels=args.internal_labels)

    # root
    args.nodes = [] if not args.nodes else args.nodes
    if args.mad:
        root_on_minimal_ancestor_deviation(tre, *args.nodes, inplace=True, return_stats=args.stats, min_dist=args.min_dist, edge_features=args.edge_features)
    else:
        root(tre, *args.nodes, inplace=True, edge_features=args.edge_features)
    if args.output:
        tre.write(args.output)
    else:
        sys.stdout.write(tre.write(None) + "\n")



def main():
    parser = get_parser_root()
    args = parser.parse_args()
    run_root(args)


if __name__ == "__main__":
    try:
        main()
    # except ToytreeError as exc:
    #     logger.bind(name="toytree").error(exc)
    except Exception as exc:
        logger.bind(name="toytree").error(exc)
