#!/usr/bin/env python

"""Simple command line tool for viewing trees in browser.

Commands
>>> toytree draw [options] STDIN              # return ASCII (default)
>>> toytree root [options] STDIN              # root and return to nwk
>>> toytree get-node-data [options] STDIN     # tabular node feature data
>>> toytree set-node-data [options] STDIN     # assign node features, return nwk
>>> toytree distance [options] STDIN1 STDIN2  # compare two trees
>>> toytree make-ultrametric [options] STDIN  # transform tree edge lengths
>>> toytree consensus [options] STDIN         # infer consensus tree
>>> toytree relabel [options] STDIN           # relabel node names
>>> toytree io [options] STDIN                # read/write to nwk

Chain commands
>>> toytree root -o A B C $file | toytree draw -i - --output /tmp/tree.html
>>> toytree draw -o /tmp/test.html -ts p '((a,b),c)'
>>> toytree root \
>>>   https://eaton-lab.org/data/Cyathophora.tre -o "prz*" -r | \
>>>   toytree draw -v -ts o -
"""

import os
import sys
from typing import Optional
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from .cli_draw import get_parser_draw, run_draw
from .cli_root import get_parser_root, run_root
from .cli_get_node_data import get_parser_get_node_data, run_get_node_data
from .cli_set_node_data import get_parser_set_node_data, run_set_node_data
from .cli_prune import get_parser_prune, run_prune
from .cli_distance import get_parser_distance, run_distance
from .cli_relabel import get_parser_relabel, run_relabel
from .cli_consensus import get_parser_consensus, run_consensus
from .cli_make_ultrametric import (
    get_parser_make_ultrametric,
    normalize_calibration_argv,
    run_make_ultrametric,
)


DESCRIPTION = "toytree command line tool. Select a subcommand."
EPILOG = "EXAMPLE:\n$ toytree draw -i TREE -ts o -wi 400 -he 400 -v"
VERSION = "..."


def setup_parsers() -> ArgumentParser:
    """Setup and return an ArgumentParser w/ subcommands."""
    parser = ArgumentParser(
        "toytree",
        usage="toytree [subcommand] --help",
        formatter_class=lambda prog: RawDescriptionHelpFormatter(
            prog, width=110, max_help_position=28
        ),
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

    parser.add_argument("-v", "--version", action='version', version=f"toytree {VERSION}")
    subparsers = parser.add_subparsers(
        prog="%(prog)s",
        required=True,
        title="subcommands",
        dest="subcommand",
    )

    # this sets the order of subcommands
    get_parser_get_node_data(subparsers)
    get_parser_set_node_data(subparsers)
    get_parser_draw(subparsers)
    get_parser_root(subparsers)
    get_parser_prune(subparsers)
    get_parser_distance(subparsers)
    get_parser_make_ultrametric(subparsers)
    get_parser_consensus(subparsers)
    get_parser_relabel(subparsers)
    return parser


def main(cmd: Optional[str] = None) -> int:
    """Command line tool.

    """
    parser = setup_parsers()

    # special handling of -1:age calibration args in make-ultrametric
    argv = cmd.split() if cmd else sys.argv[1:]
    if argv and argv[0] == "make-ultrametric":
        argv = normalize_calibration_argv(argv)
    args = parser.parse_args(argv)

    dispatch = {
        "get-node-data": run_get_node_data,
        "set-node-data": run_set_node_data,
        "draw": run_draw,
        "root": run_root,
        "prune": run_prune,
        "distance": run_distance,
        "make-ultrametric": run_make_ultrametric,
        "consensus": run_consensus,
        "relabel": run_relabel,
    }
    if args.subcommand:
        run_func = dispatch[args.subcommand]
        try:
            run_func(args)
        except BrokenPipeError:
            # Typical in pipelines when downstream exits early (e.g. `... | toytree draw -h`).
            try:
                devnull = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull, sys.stdout.fileno())
            except Exception:
                pass
            return 141
        return 0

    # unreachable
    parser.print_help()
    return 1


if __name__ == "__main__":

    try:
        main()
    except BrokenPipeError:
        # Downstream command in a pipeline may exit early.
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except Exception:
            pass
        raise SystemExit(141)
    except KeyboardInterrupt:
        print("interrupted by user", file=sys.stderr)
    except Exception as exc:
        from toytree.utils import ToytreeError
        if exc == ToytreeError:
            print(exc, file=sys.stderr)
            raise SystemExit(1)
        raise exc
