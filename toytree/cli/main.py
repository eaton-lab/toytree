#!/usr/bin/env python

"""Simple command line tool for viewing trees in browser.

Commands
>>> toytree draw [options] STDIN              # return as HTML
>>> toytree root [options] STDIN              # root and return to nwk
>>> toytree distance [options] STDIN1 STDIN2  # compare trees
>>> toytree io [options] STDIN                # read/write to nwk

Chain commands
>>> toytree root -o A B C $file | toytree draw - -o /tmp/tree.html
>>> toytree draw -o /tmp/test.html -ts p '((a,b),c)'
>>> toytree root \
>>>   https://eaton-lab.org/data/Cyathophora.tre -o "prz*" -r | \
>>>   toytree draw -v -ts o -
"""

import sys
from typing import Optional
import textwrap
import argparse
# from loguru import logger
# import toytree
from .make_wide import make_wide
from .cli_draw import get_parser_draw, run_draw
from .cli_root import get_parser_root, run_root
from .cli_get_node_data import get_parser_get_node_data, run_get_node_data
from .cli_prune import get_parser_prune, run_prune
# from cli_distance import get_parser_distance

# logger = logger.bind(name="toytree")
DESCRIPTION = "toytree command line tool. Select a subcommand."
EPILOG = "EXAMPLE:\n$ toytree draw TREE -ts o -d 400 400 -v"
VERSION = "..."


def setup_parsers() -> argparse.ArgumentParser:
    """Setup and return an ArgumentParser w/ subcommands."""
    parser = argparse.ArgumentParser(
        "toytree",
        # usage="%(prog)s",
        usage="toytree [subcommand] --help",
        #  description = '%(prog)s: testing help mods',
        # help="toytree...",
        formatter_class=make_wide(argparse.RawDescriptionHelpFormatter, 120, 120),
        # formatter_class=CustomHelpFormatter,
        description=textwrap.dedent("""
            ----------------------------------------------------------
            |  %(prog)s: phylogenetic tree toolkit                   |
            ----------------------------------------------------------
            """),
        epilog=textwrap.dedent(r"""
            Tutorials
            ---------
            https://eaton-lab.org/toytree/
        """)
    )


# def setup_parsers() -> argparse.ArgumentParser:
#     """Setup and return an ArgumentParser w/ subcommands."""
#     parser = argparse.ArgumentParser(
#         prog="toytree",
#         description=DESCRIPTION,
#         epilog=EPILOG,
#     )
    parser.add_argument("-v", "--version", action='version', version=f"toytree {VERSION}")
    subparsers = parser.add_subparsers(
        prog="%(prog)s", required=True,
        title="subcommands",
        dest="subcommand",
        metavar="--------------",
        help="-----------------------------------------------------",
    )

    # this sets the order of subcommands
    get_parser_get_node_data(subparsers)
    get_parser_draw(subparsers)
    get_parser_root(subparsers)
    get_parser_prune(subparsers)
    # get_parser_distance(subparsers)
    return parser


def main(cmd: Optional[str] = None) -> int:
    """Command line tool.

    """
    parser = setup_parsers()
    args = parser.parse_args(cmd.split() if cmd else None)

    dispatch = {
        "node-data": run_get_node_data,
        "draw": run_draw,
        "root": run_root,
        "prune": run_prune,
    }
    if args.subcommand:
        run_func = dispatch[args.subcommand]
        run_func(args)
        return 0

    # unreachable
    parser.print_help()
    return 1


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print("interrupted by user", file=sys.stderr)
        # logger.warning("interrupted by user")
    except Exception as exc:
        raise exc
        # logger.error(exc)
