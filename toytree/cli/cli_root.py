#!/usr/bin/env python

"""
"""

import sys
from pathlib import Path
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from .make_wide import make_wide
# from loguru import logger
# logger = logger.bind(name="toytree")


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
        $ root -i TRE.nwk -n ~prefix -o RTRE.nwk
        $ root -i TRE.nwk -n A B C --mad > RTRE.nwk
        $ root -i TRE.nwk --mad > RTRE.nwk
        $ root -i TRE.nwk --mad -n ~[A-C] -x -I support > RTRE.nwk
    """)
)


def string_or_stdin_parse(intree: str) -> str:
    """If TREE is stdin then return the string from stdin."""
    if intree == "-":
        return sys.stdin.read().strip()
    return intree


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
    parser.add_argument("-i", "--input", type=string_or_stdin_parse, metavar="path", required=True, help="input tree file (nwk, nex or nhx)")
    parser.add_argument("-o", "--output", type=Path, metavar="path", help="optional outfile path name. If None prints to STDOUT")
    parser.add_argument("-n", "--nodes", type=str, metavar="str", nargs="*", help="one or more names or regular expressions to select outgroup mrca")
    # options
    parser.add_argument("-I", "--internal-labels", type=str, metavar="str", help="parse internal node feature (e.g., support) [auto]")
    parser.add_argument("-e", "--edge-features", type=str, metavar="str", nargs="*", help="one or more edge features on tree that should be re-polarized")
    parser.add_argument("-x", "--exclude-features", action="store_true", help="do not preserve node feature data")
    parser.add_argument("-m", "--mad", action="store_true", help="use minimal-ancestor-deviation to find rooting or place node on selected edge")
    parser.add_argument("-s", "--stats", action="store_true", help="return tree and mad stats")
    parser.add_argument("-d", "--min-dist", type=float, metavar="float", default=1e-12, help="set zero-length edges to [1e-12] during mad to prevent division error")
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
        tre = tree(args.input, internal_labels=args.internal_labels)

    # root
    args.nodes = [] if not args.nodes else args.nodes
    if args.mad:
        _, mdict = root_on_minimal_ancestor_deviation(tre, *args.nodes, inplace=True, return_stats=True, min_dist=args.min_dist, edge_features=args.edge_features)
        if args.stats:
            for key in mdict:
                print(f"{key}={mdict[key]}")
    else:
        root(tre, *args.nodes, inplace=True, edge_features=args.edge_features)

    # write tree with or wi/o feature data
    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {'name', 'height', 'dist', 'support'}
    if args.output:
        tre.write(args.output, features=features)
    else:
        sys.stdout.write(tre.write(None, features=features) + "\n")


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
        raise exc
        # logger.error(exc)
