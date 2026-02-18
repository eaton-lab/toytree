#!/usr/bin/env python

import sys
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path


KWARGS = dict(
    prog="get-node-data",
    usage="get-node-data [options]",
    help="return table of node feature data from a tree",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=120, max_help_position=120
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------
        | get-node-data: return tabular feature data from tree nodes
        -------------------------------------------------------------------
        | Returns data for all nodes or selected nodes, and all features
        | or selected features. Output can be written to stdout or file.
        -------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        $ get-node-data -i TRE.nwk
        $ get-node-data -i TRE.nwk -H
        $ get-node-data -i TRE.nwk -n A B C
        $ get-node-data -i TRE.nwk -n ~prefix -f name dist support
        $ get-node-data -i TRE.nwk -s ',' -o DATA.csv
        $ get-node-data -i TRE.nwk --float-format %.6f
        $ cat TRE.nwk | get-node-data -i -
        """
    ),
)


def get_parser_get_node_data(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for get-node-data command."""
    if parser:
        kwargs = dict(KWARGS)
        name = kwargs.pop("prog")
        kwargs["name"] = name
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
        help="input tree file/path/url/newick string, or '-' for stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output path; default writes to stdout",
    )
    io_group.add_argument(
        "-s",
        "--separator",
        type=str,
        metavar="str",
        default="\t",
        help=r"separator used for delimited output [\t]",
    )
    io_group.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="print pretty aligned table (overrides --separator)",
    )

    select_group = p.add_argument_group(title="Selection")
    select_group.add_argument(
        "-n",
        "--nodes",
        type=str,
        metavar="str",
        nargs="*",
        help="node queries (name, idx, regex) to subset rows",
    )
    select_group.add_argument(
        "-f",
        "--features",
        type=str,
        metavar="str",
        nargs="*",
        help="subset one or more feature columns",
    )
    select_group.add_argument(
        "-t",
        "--tips-only",
        action="store_true",
        help="only return tip node data",
    )

    format_group = p.add_argument_group(title="Formatting")
    format_group.add_argument(
        "-m",
        "--missing",
        type=str,
        metavar="str",
        help="value for missing data (replaces NaN)",
    )
    format_group.add_argument(
        "--float-format",
        type=str,
        metavar="fmt",
        help="printf-style float format (e.g., %%.6f)",
    )

    advanced_group = p.add_argument_group(title="Advanced")
    advanced_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="Parse internal labels as this feature (overrides auto-detect)",
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


def run_get_node_data(args):
    """Run get-node-data command."""
    from toytree.io.src.treeio import tree
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    intree = sys.stdin.read() if args.input == "-" else args.input
    tre = tree(intree, internal_labels=args.internal_labels)

    if args.tips_only:
        data = tre.get_tip_data(args.features, missing=args.missing)
    else:
        data = tre.get_node_data(args.features, missing=args.missing)

    if args.nodes:
        nodes = tre.get_nodes(*args.nodes)
        data = data.loc[[node.idx for node in nodes], :]

    if args.human_readable:
        datastr = data.to_string(float_format=args.float_format)
        if args.output:
            Path(args.output).write_text(f"{datastr}\n")
        else:
            sys.stdout.write(f"{datastr}\n")
    else:
        out = sys.stdout if args.output is None else args.output
        data.to_csv(out, sep=args.separator, float_format=args.float_format)


def main():
    parser = get_parser_get_node_data()
    args = parser.parse_args()
    run_get_node_data(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
