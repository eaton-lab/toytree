#!/usr/bin/env python

"""
"""

# from typing import List
import sys
import textwrap
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter
# from loguru import logger
from .make_wide import make_wide
# from ortholab.utils.parallel import run_pipeline  # , run_with_pool
# from ortholab.utils.logger_setup import set_log_level


KWARGS = dict(
    prog="node-data",
    usage="node-data [options]",
    help="return table of feature data stored in a tree file",
    formatter_class=make_wide(RawDescriptionHelpFormatter, 120, 140),
    description=textwrap.dedent("""
        -------------------------------------------------------------------
        | node-data: return...
        -------------------------------------------------------------------
        | The node-data method ...
        -------------------------------------------------------------------
    """),
    epilog=textwrap.dedent("""
        Examples
        --------
        $ node-data -i TRE.nwk -H
        $ node-data -i TRE.nwk -n A B C
        $ node-data -i TRE.nwk -n ~prefix -f name dist
        $ node-data -i TRE.nwk -s ',' > DATA.csv
        $ cat TRE.nwk | get-node-data -i -
    """)
)


def string_or_stdin_parse(intree: str) -> str:
    """If TREE is stdin then return the string from stdin."""
    if intree == "-":
        return sys.stdin.read().strip()
    return intree


def get_parser_get_node_data(parser: ArgumentParser | None = None) -> ArgumentParser:
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
    parser.add_argument("-i", "--input", type=string_or_stdin_parse, metavar="path", required=True, help="input CDS sequence (aligned or unaligned)")
    parser.add_argument("-o", "--output", type=Path, metavar="path", help="optional outfile path name. If None prints to STDOUT")
    parser.add_argument("-n", "--nodes", type=str, metavar="str", nargs="*", help="one or more names or regular expressions to select nodes")
    parser.add_argument("-f", "--features", type=str, metavar="str", nargs="*", help="subselect one or more features to return")
    parser.add_argument("-t", "--tips-only", action="store_true", help="only return tip (leaf) node data")
    # options
    parser.add_argument("-s", "--separator", type=str, metavar="str", default="\t", help=r"separator character [\t]")
    parser.add_argument("-m", "--missing", type=str, metavar="str", help=r"a value to set for missing data to replace NaN")
    parser.add_argument("-H", "--human-readable", action="store_true", help="use easy to read variable column spacing. Overrides -s")
    parser.add_argument("-I", "--internal-labels", type=str, metavar="str", help="internal node features (e.g., support) [auto]")
    parser.add_argument("-l", "--log-level", type=str, metavar="level", default="INFO", help="stderr logging level (DEBUG, [INFO], WARNING, ERROR)")
    # parser.add_argument("-f", "--force", action="store_true", help="overwrite existing result files in outdir")
    # parser.add_argument("-L", "--log-file", type=Path, metavar="path", help="append stderr log to a file")
    return parser


def run_get_node_data(args):
    from toytree.io.src.treeio import tree

    # parse the tree
    if args.input == Path("-"):
        data = sys.stdin.read()
        tre = tree(data, internal_labels=args.internal_labels)
    else:
        tre = tree(args.input, internal_labels=args.internal_labels)

    # get data
    if args.tips_only:
        data = tre.get_tip_data(args.features)
    else:
        data = tre.get_node_data(args.features)

    # subset nodes
    # TODO: support casting str back to int for node selections?
    if args.nodes:
        nodes = tre.get_nodes(*args.nodes)
        data = data.loc[[i.idx for i in nodes], :]

    # print
    out = sys.stdout if args.output is None else args.output
    if args.human_readable:
        datastr = data.to_string()
        sys.stdout.write(f"{datastr}\n")
    else:
        data.to_csv(out, sep=args.separator)


def main():
    parser = get_parser_get_node_data()
    args = parser.parse_args()
    run_get_node_data(args)


if __name__ == "__main__":

    try:
        main()
    except Exception as exc:
        raise exc
        # logger.bind(name="toytree").error(exc)

