#!/usr/bin/env python

"""CLI subparser definitions.

This module defines only argparse setup for CLI subcommands. It intentionally
avoids importing non-CLI toytree runtime modules so top-level `-h` screens stay
fast. Command execution is delegated at runtime from `main.py`.
"""

from __future__ import annotations

import re
from argparse import (
    SUPPRESS,
    ArgumentParser,
    ArgumentTypeError,
    RawDescriptionHelpFormatter,
)
from pathlib import Path
from tempfile import gettempdir
from textwrap import dedent
from typing import Any

from ._subparser_helpers import parse_bool, parse_bool_or_feature, parse_node_mask

TMPDIR = gettempdir()
SINGLE_TREE_INPUT_HELP = "tree input: file/path/url/newick; '-' or piped stdin"
BINARY_OUTPUT_HELP = "write ToyTree in binary for faster piping with large trees"


class SingleMetavarHelpFormatter(RawDescriptionHelpFormatter):
    """Render optional args as '-x, --long VALUE' (single metavar copy)."""

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)
        if action.nargs == 0:
            return ", ".join(action.option_strings)
        default = self._get_default_metavar_for_optional(action)
        args = self._format_args(action, default)
        return f"{', '.join(action.option_strings)} {args}"


def _formatter(width: int, max_help_position: int):
    """Return formatter factory configured for consistent single-metavar help."""
    return lambda prog: SingleMetavarHelpFormatter(
        prog,
        width=width,
        max_help_position=max_help_position,
    )


NEGATIVE_CAL_QUERY_PREFIX = "__toytree_negidx__"


def normalize_calibration_argv(argv: list[str]) -> list[str]:
    """Protect calibration tokens like '-1=10' from argparse option parsing."""
    out: list[str] = []
    in_cal_block = False
    for tok in argv:
        if tok in {"-c", "--calibrations"}:
            in_cal_block = True
            out.append(tok)
            continue

        if tok.startswith("--calibrations="):
            value = tok.split("=", 1)[1]
            if re.match(r"^-\d+=", value):
                value = NEGATIVE_CAL_QUERY_PREFIX + value[1:]
                out.append(f"--calibrations={value}")
            else:
                out.append(tok)
            in_cal_block = False
            continue

        if in_cal_block:
            if tok.startswith("-") and (not re.match(r"^-\d+=", tok)):
                in_cal_block = False
                out.append(tok)
                continue
            if re.match(r"^-\d+=", tok):
                out.append(NEGATIVE_CAL_QUERY_PREFIX + tok[1:])
            else:
                out.append(tok)
            continue
        out.append(tok)
    return out


def _parse_int_or_str(value: str):
    """Parse token as int when possible, else return as str."""
    try:
        return int(value)
    except ValueError:
        return value


RTREE_METHODS = ("rtree", "unittree", "imbtree", "baltree", "bdtree", "coaltree")


def _parse_rtree_method(value: str) -> str:
    """Parse full or unambiguous-prefix rtree method names."""
    token = value.strip().lower()
    if token in RTREE_METHODS:
        return token
    matches = [method for method in RTREE_METHODS if method.startswith(token)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ArgumentTypeError(
            "invalid method: " f"{value!r}; choose from {'|'.join(RTREE_METHODS)}"
        )
    raise ArgumentTypeError(
        f"ambiguous method prefix {value!r}; matches: {'|'.join(matches)}"
    )


def string_or_stdin_parse(intree: str) -> str:
    """Return raw tree arg as entered (supports '-' stdin marker)."""
    return intree


def _set_handler(parser: ArgumentParser, handler: str) -> None:
    """Attach runtime handler import path to a command parser."""
    parser.set_defaults(_handler=handler)


def get_parser_get_node_data(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for get-node-data command."""
    kwargs = dict(
        prog="get-node-data",
        usage="get-node-data [options]",
        help="return table of node feature data from a tree",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | get-node-data: return tabular feature data from tree nodes
            -------------------------------------------------------------------
            | Returns data for all nodes or selected nodes, and all features
            | or selected features. Output can be written to stdout or file.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ get-node-data -i TRE.nwk
            $ get-node-data -i TRE.nwk -H
            $ get-node-data -i TRE.nwk -n A B C
            $ get-node-data -i TRE.nwk -n ~prefix -f name dist support
            $ get-node-data -i TRE.nwk -s ',' -o DATA.csv
            $ get-node-data -i TRE.nwk -f dist -N
            $ get-node-data -i TRE.nwk --float-format %.6f
            $ get-node-data -i TRE.nwk -f name dist --json
            $ cat TRE.nwk | get-node-data -i -
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output path; default writes to stdout",
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
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
        "-t", "--tips-only", action="store_true", help="only return tip node data"
    )

    format_group = p.add_argument_group(title="Formatting")
    format_group.add_argument(
        "-s",
        "--separator",
        type=str,
        metavar="str",
        default="\t",
        help=r"separator used for delimited output [\t]",
    )
    format_group.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="print pretty aligned table (overrides --separator)",
    )
    format_group.add_argument(
        "-m",
        "--missing",
        type=str,
        metavar="str",
        help="value for missing data (replaces NaN)",
    )
    format_group.add_argument(
        "-F",
        "--float-format",
        type=str,
        metavar="fmt",
        help="printf-style float format (e.g., %%.6f)",
    )
    format_group.add_argument(
        "-N",
        "--index-by-name",
        action="store_true",
        help="set output index to node names; fallback to idx when names are empty",
    )
    format_group.add_argument(
        "--json",
        action="store_true",
        help="write structured JSON output (overrides table text formatting)",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_get_node_data:run_get_node_data")
    return p


def get_parser_set_node_data(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for set-node-data command."""
    kwargs = dict(
        prog="set-node-data",
        usage="set-node-data [options]",
        help="set node features on a tree and return updated newick",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | set-node-data: assign feature values to nodes and return tree
            -------------------------------------------------------------------
            | Store or update feature data using key=value node assignments or
            | a tabular file, then emit updated Newick with feature data.
            | Pipe to `toytree io` to change metadata comment formatting.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            # From Mapping: set one feature from explicit node queries
            $ set-node-data -i TRE.nwk --feature color --set a='red' b='blue' --default 'gray'
            $ set-node-data -i TRE.nwk --feature support2 --set 10=0.95 11=0.80 --inherit
            $ set-node-data -i TRE.nwk -f group -s '~^cladeA'=1 '~^cladeB'=2 -d 0
            $ cat TRE.nwk | set-node-data -i - -f score -s a=1.2 b=2.3 --default 0

            # From Table: first column is query index (node name or idx), other columns are features
            $ set-node-data -i TRE.nwk --table data.tsv --table-sep '\\t' > OUT.nwk
            $ set-node-data -i TRE.nwk --table data.csv --table-sep ',' -o OUT.nwk
            $ set-node-data -i TRE.nwk --table data.space.txt --table-sep ' '
            $ set-node-data -i TRE.nwk --table data.tsv --table-query-regex
            $ set-node-data -i TRE.nwk --table data.tsv --table-query-column id
            $ set-node-data -i TRE.nwk --table data.noheader.tsv --table-headers group
            $ set-node-data -i TRE.nwk --table data.tsv --table-query-regex --table-allow-unmatched

            # From Table (IMAP): rename tips from TSV <name>\\t<newname>
            $ set-node-data -i TRE.nwk --table IMAP.tsv --table-query-regex --table-allow-unmatched --table-headers 'name'

            # Edge features
            $ set-node-data -i TRE.nwk -f rate -s 10=0.1 11=0.2 --edge

            # Convert output metadata to NHX-like formatting via `toytree io`
            $ set-node-data -i TRE.nwk -f state -s a=1 b=2 \\
                | toytree io -i - -fp '&&NHX:' -fd ':' -fa '=' > OUT.nhx

            # Binary piping between commands
            $ set-node-data -i TRE.nwk -f X -s a=1 b=2 -b | draw -i - -nm false -ns 10 -nc 'X' -v
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    mode_group = p.add_argument_group(title="Mode")
    mode_group.add_argument(
        "-f",
        "--feature",
        type=str,
        metavar="name",
        help="feature name to set in mapping mode",
    )
    mode_group.add_argument(
        "-s",
        "--set",
        dest="assignments",
        type=str,
        nargs="*",
        metavar="query=value",
        help="mapping assignments (query can be node idx, name, or regex)",
    )
    mode_group.add_argument(
        "-d",
        "--default",
        type=str,
        metavar="value",
        help="default value for nodes not present in mapping mode",
    )
    mode_group.add_argument(
        "--inherit",
        action="store_true",
        help="inherit mapping values from internal nodes to descendants",
    )
    mode_group.add_argument(
        "--edge", action="store_true", help="mark feature as edge-polarized feature"
    )

    table_group = p.add_argument_group(title="From Table")
    table_group.add_argument(
        "-t",
        "--table",
        type=Path,
        metavar="path",
        help="tabular file input for set_node_data_from_dataframe mode",
    )
    table_group.add_argument(
        "-ts",
        "--table-sep",
        type=str,
        default="\t",
        metavar="sep",
        help="separator for --table file [\\t]",
    )
    table_group.add_argument(
        "-tc",
        "--table-query-column",
        type=_parse_int_or_str,
        metavar="idx|name",
        help="table input: query column selector (int position or column name)",
    )
    table_group.add_argument(
        "-tr",
        "--table-query-regex",
        action="store_true",
        help="table input: treat string queries as regex (prepend '~' when absent)",
    )
    table_group.add_argument(
        "-th",
        "--table-headers",
        type=str,
        nargs="+",
        metavar="str",
        help="table input: feature names for parsed table columns after query column",
    )
    table_group.add_argument(
        "-tu",
        "--table-allow-unmatched",
        action="store_true",
        help="table input: ignore unmatched node queries (logged at DEBUG)",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_set_node_data:run_set_node_data")
    return p


def get_parser_io(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for io command."""
    kwargs = dict(
        prog="io",
        usage="io [options]",
        help="convert tree data between binary/Newick/Nexus with NHX metadata",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | io: convert tree input/output with extended NHX metadata
            -------------------------------------------------------------------
            | Read a single tree from binary or text input, then emit binary,
            | Newick, or Nexus output while controlling metadata parsing and
            | serialization settings.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            # pass-through Newick (stdout)
            $ io -i TRE.nwk

            # parse stdin and write binary for fast metadata-safe piping
            $ cat TRE.nwk | io -b > TRE.bin

            # convert binary back to Newick text
            $ io -i TRE.bin > TRE.nwk

            # write Nexus using flag or output suffix
            $ io -i TRE.bin --nexus -o TRE.nex
            $ io -i TRE.bin -o TRE.nexus

            # read non-default NHX metadata formatting
            $ io -i TRE.nhx --in-feature-prefix '&&NHX:' --in-feature-delim ':' --in-feature-assignment '='
            $ io -i TRE.nhx --in-feature-unpack ';'

            # suppress support labels and metadata comments in text output
            $ io -i TRE.bin -x

            # write a single node feature in name{value} format
            $ io -i TRE.bin --write-single-feature X

            # pack list-like metadata values with a custom separator
            $ io -i TRE.bin --features-pack ';'

            # to extract a TSV table, pipe to get-node-data
            $ io -i TRE.bin | get-node-data -i - -H
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    in_features_group = p.add_argument_group(title="Input Features")
    in_features_group.add_argument(
        "-ifp",
        "--in-feature-prefix",
        type=str,
        metavar="str",
        default="&",
        help="input metadata prefix in NHX-like comments [&]",
    )
    in_features_group.add_argument(
        "-ifd",
        "--in-feature-delim",
        type=str,
        metavar="str",
        default=",",
        help="input metadata delimiter between key/value pairs [,]",
    )
    in_features_group.add_argument(
        "-ifa",
        "--in-feature-assignment",
        type=str,
        metavar="str",
        default="=",
        help="input metadata assignment token between key and value [=]",
    )
    in_features_group.add_argument(
        "-ifu",
        "--in-feature-unpack",
        type=str,
        metavar="str",
        default="|",
        help="input list-value unpack token in metadata values [|]",
    )

    output_mode_group = p.add_argument_group(title="Output Mode")
    output_mode_group.add_argument(
        "--nexus",
        action="store_true",
        help="write Nexus text output (also auto-enabled for .nex/.nexus output paths)",
    )

    out_features_group = p.add_argument_group(title="Output Features")
    out_features_group.add_argument(
        "-fp",
        "--features-prefix",
        type=str,
        metavar="str",
        default="&",
        help="prefix for features in extended newick [&, use '&&NHX:' for NHX style]",
    )
    out_features_group.add_argument(
        "-fd",
        "--features-delim",
        type=str,
        metavar="str",
        default=",",
        help="delimiter between feature key/value pairs in output [,]",
    )
    out_features_group.add_argument(
        "-fa",
        "--features-assignment",
        type=str,
        metavar="str",
        default="=",
        help="assignment token between feature key and value in output [=]",
    )
    out_features_group.add_argument(
        "-fk",
        "--features-pack",
        type=str,
        metavar="str",
        default="|",
        help="pack list-like feature values using this token [|]",
    )
    out_features_group.add_argument(
        "-ff",
        "--features-formatter",
        type=str,
        metavar="fmt",
        default="%.12g",
        help="float formatter for feature values in output [%%.12g]",
    )
    out_features_group.add_argument(
        "--write-single-feature",
        type=str,
        metavar="str",
        default=None,
        help="write one feature on every node as name{value} labels in Newick text",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_io:run_io")
    return p


def get_parser_draw(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for draw command."""
    kwargs = dict(
        prog="draw",
        usage="draw [options]",
        help="render styled tree figures in graphic formats",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | draw: render styled tree figures
            -------------------------------------------------------------------
            | Create graphic tree figures for notebooks, reports, and files.
            | Render to html, svg, pdf, or png, save with --output, and
            | optionally open the result with --view. Control layout, built-in
            | tree styles, labels, and node/edge styling from the CLI.
            | For terminal text rendering, use `toytree view`.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ draw -i TRE.nwk --output tree.svg
            $ draw -i TRE.nwk -f png --view
            $ draw -i TRE.nwk -f html -v -ts c
            $ draw -i TRE.nwk -f pdf -o /tmp/DRAWING -ns 8 -nc teal -ta true
            $ draw -i TRE.nwk -v -ta
            $ draw -i TRE.nwk -v -ta false
            $ draw -i TRE.nwk -v -N fill=red -E stroke=pink -T font-size=10px fill=blue
            $ root -i TRE.nwk -n R | draw -i - -v
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional path to save drawing in format -f; ASCII defaults to stdout",
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )

    render_group = p.add_argument_group(title="Render Mode")
    render_group.add_argument(
        "-f",
        "--format",
        type=str.lower,
        choices=["html", "svg", "pdf", "png"],
        default=None,
        help="graphic output format [pdf]",
    )
    render_group.add_argument(
        "-v",
        "--view",
        type=str,
        metavar="app",
        const="auto",
        nargs="?",
        help="open rendered graphic in default viewer, or provided app name",
    )
    render_group.add_argument(
        "-a",
        "--ascii",
        action="store_true",
        help="deprecated text mode; prefer `toytree view --ascii`",
    )
    render_group.add_argument(
        "-e", "--ladderize", action="store_true", help="ladderize tree before drawing"
    )

    layout_group = p.add_argument_group(title="Layout")
    layout_group.add_argument(
        "-wi", "--width", type=int, metavar="int", help="width in pixels"
    )
    layout_group.add_argument(
        "-he", "--height", type=int, metavar="int", help="height in pixels"
    )
    layout_group.add_argument(
        "-la",
        "--layout",
        type=str,
        metavar="str",
        help="layout ['r', 'l', 'u', 'd', 'c', 'c0-180', 'un']",
    )
    layout_group.add_argument(
        "-ts",
        "--tree-style",
        type=str,
        metavar="str",
        help="base tree style ['n', 'r', 'c', 's', 'o', 'b']",
    )
    layout_group.add_argument(
        "-pa", "--padding", type=float, metavar="float", help="canvas padding in pixels"
    )
    layout_group.add_argument(
        "-sb",
        "--scale-bar",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="draw scale bar (true/false) [default: auto]",
    )
    layout_group.add_argument(
        "-ue",
        "--use-edge-lengths",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="use edge lengths (true/false) [default: auto]",
    )

    node_group = p.add_argument_group(title="Node Style")
    node_group.add_argument(
        "-nm",
        "--node-mask",
        type=parse_node_mask,
        metavar="bool|a,b,c",
        help="node mask: true/false or 3-value binary tuple for (tips,internal,root)",
    )
    node_group.add_argument(
        "-ns",
        "--node-sizes",
        type=float,
        metavar="float",
        nargs="+",
        help="node sizes (scalar or list)",
    )
    node_group.add_argument(
        "-nc",
        "--node-colors",
        type=str,
        metavar="str",
        nargs="+",
        help="node colors (scalar or list)",
    )
    node_group.add_argument(
        "-nl",
        "--node-labels",
        type=str,
        metavar="str",
        help="node labels feature or literal",
    )
    node_group.add_argument(
        "-N",
        "--node-style",
        type=str,
        metavar="str",
        nargs="+",
        help="node style key=value args",
    )

    edge_group = p.add_argument_group(title="Edge Style")
    edge_group.add_argument(
        "-et",
        "--edge-type",
        type=str,
        metavar="str",
        choices=["p", "c", "b"],
        help="edge type ([p]hylogram, [c]ladogram, [b]ezier)",
    )
    edge_group.add_argument(
        "-ew",
        "--edge-widths",
        type=float,
        metavar="float",
        nargs="+",
        help="edge widths (scalar or list)",
    )
    edge_group.add_argument(
        "-ec",
        "--edge-colors",
        type=str,
        metavar="str",
        nargs="+",
        help="edge colors (scalar or list)",
    )
    edge_group.add_argument(
        "-E",
        "--edge-style",
        type=str,
        metavar="str",
        nargs="+",
        help="edge style key=value args",
    )

    label_group = p.add_argument_group(title="Label Style")
    label_group.add_argument(
        "-tl",
        "--tip-labels",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="draw tip labels (true/false) [default: auto]",
    )
    label_group.add_argument(
        "-ta",
        "--tip-labels-align",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        help="align tip labels (true/false) [default: auto]",
    )
    label_group.add_argument(
        "-tc",
        "--tip-labels-colors",
        type=str,
        metavar="str",
        nargs="+",
        help="tip-label colors (scalar or list)",
    )
    label_group.add_argument(
        "-T",
        "--tip-labels-style",
        type=str,
        metavar="str",
        nargs="+",
        help="tip-label style key=value args",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_draw:run_draw")
    return p


def get_parser_view(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for view command."""
    kwargs = dict(
        prog="view",
        usage="view [options]",
        help="print tree as unicode or ASCII text",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | view: print a tree as unicode or ASCII text
            -------------------------------------------------------------------
            | Prints a text rendering to stdout using the lightweight
            | ASCII/Unicode viewer. Use shell redirection to save output.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ toytree view -i TRE.nwk
            $ toytree view -i TRE.nwk --ascii
            $ toytree view -i TRE.nwk --ladderize
            $ toytree view -i TRE.nwk --tip-labels idx --use-edge-lengths false
            $ toytree view -i TRE.nwk --heavy 'support>95'
            $ toytree view -i TRE.nwk --heavy 'support>95' --heavier
            $ toytree rtree -n 20 | toytree view
            $ toytree rt -n 20 | toytree set -f X -s ~r[0-5]=1 | toytree v --heavy 'X=1'
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )

    render_group = p.add_argument_group(title="Rendering")
    render_group.add_argument(
        "-w",
        "--width",
        type=int,
        metavar="int",
        help="target text width in columns",
    )
    render_group.add_argument(
        "-a",
        "--ascii",
        dest="charset",
        action="store_const",
        const="ascii",
        default="unicode",
        help="use ASCII instead of Unicode line drawing",
    )
    render_group.add_argument(
        "-e",
        "--ladderize",
        action="store_true",
        help="ladderize clades for display only",
    )
    render_group.add_argument(
        "-tl",
        "--tip-labels",
        type=parse_bool_or_feature,
        metavar="bool|feature",
        nargs="?",
        const=True,
        default=True,
        help="show tip labels (true/false) or use a tip feature [true]",
    )
    render_group.add_argument(
        "-ue",
        "--use-edge-lengths",
        type=parse_bool,
        metavar="bool",
        nargs="?",
        const=True,
        default=True,
        help="use edge lengths (true/false) [true]; false aligns tips",
    )
    render_group.add_argument(
        "-y",
        "--heavy",
        type=str,
        metavar="selector",
        help="show heavy branches where features match a query, e.g. 'support>95' or 'sex=M'",
    )
    render_group.add_argument(
        "-Y",
        "--heavier",
        action="store_true",
        help="use stronger heavy glyphs (# in ASCII, ▒ in Unicode)",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_view:run_view")
    return p


def get_parser_root(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Create argparse parser for the `root` CLI command."""
    kwargs = dict(
        prog="root",
        usage="root [options]",
        help="root a tree using outgroup, MAD, or DLC optimization",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | root: root trees using outgroup queries, MAD, or DLC optimization
            -------------------------------------------------------------------
            | outgroup mode: use -n/--nodes to set an outgroup edge by MRCA.
            | MAD mode     : choose the root minimizing ancestor-deviation of
            |                root-to-tip path distances across the tree.
            | DLC mode     : choose the root minimizing duplication/loss/
            |                coalescence reconciliation cost to a species tree.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
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
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    mode_group = p.add_argument_group(title="Rooting Mode")
    mode_group.add_argument(
        "-n",
        "--nodes",
        type=str,
        metavar="str",
        nargs="*",
        help="outgroup node queries; MRCA defines the outgroup edge",
    )
    mode_switch = mode_group.add_mutually_exclusive_group()
    mode_switch.add_argument(
        "--mad",
        action="store_true",
        help="infer root by MAD; with --nodes, optimize on selected outgroup edge",
    )
    mode_switch.add_argument(
        "--dlc",
        action="store_true",
        help="infer root by minimizing weighted DLC reconciliation score",
    )

    mad_group = p.add_argument_group(title="MAD Options")
    mad_group.add_argument(
        "--min-dist",
        type=float,
        metavar="float",
        default=1e-12,
        help="MAD only: minimum edge-length floor for zero-length edges [1e-12]",
    )

    dlc_group = p.add_argument_group(title="DLC Options")
    dlc_group.add_argument(
        "--species-tree",
        type=str,
        metavar="path",
        help="DLC only: rooted species tree path",
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

    feature_group = p.add_argument_group(title="Feature Handling")
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

    general_group = p.add_argument_group(title="Options")
    general_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_root:run_root")
    return p


def get_parser_prune(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for prune command."""
    kwargs = dict(
        prog="prune",
        usage="prune [options]",
        help="return tree connecting only the selected tip names",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | prune: return tree with only branches connecting a subset of tips
            -------------------------------------------------------------------
            | The prune method returns a tree with a subset of queried Nodes
            | along with the minimal spanning edges required to connect them.
            | Nodes can be queried as individual arguments or as a set of
            | indices, e.g. prune([0,1,2]). When called on a rooted tree, the
            | user can require the originial root to be retained in the pruned
            | tree using --require-root. By default, this is False and the
            | lowest MRCA connecting the queried Nodes is instead be kept as
            | the new root. When internal Nodes are discarded by prune their
            | distances will be merged into the distance of the queried Node
            | such that the original distance between the root and the queried
            | Node remains the same. If not --preserve-dists, then only the
            | original distances assigned to the queried Nodes are retained.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ prune -i TREE.nwk -n A B C D > PRUNED.nwk
            $ prune -i TREE.nwk -n A B C D --preserve-dists --require-root > PRUNED.nwk
            $ prune -i TREE.nwk -n A B C D -o PRUNED.nwk
            $ prune -i TREE.nwk -n '~prefixA' '~prefixB' > PRUNED.nwk
            $ prune -i TREE.nwk -n A B -b | set-node-data -i - -f score -s a=1 b=2 > OUT.nwk
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    edit_group = p.add_argument_group(title="Prune")
    edit_group.add_argument(
        "-n",
        "--nodes",
        type=str,
        metavar="str",
        nargs="*",
        help="One or more names or regular expressions to select nodes",
    )
    edit_group.add_argument(
        "-r",
        "--require-root",
        action="store_true",
        help="keep root node even if unary after pruning children",
    )
    edit_group.add_argument(
        "-p",
        "--not-preserve-dists",
        action="store_true",
        help="if not preserved then children do not inherit parent dists",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_prune:run_prune")
    return p


def get_parser_distance(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for distance command."""
    kwargs = dict(
        prog="distance",
        usage="distance [options]",
        help="compute a distance between two trees",
        formatter_class=_formatter(120, 34),
        description=dedent(
            """
            -------------------------------------------------------------------
            | distance: compute a tree distance metric between two trees
            -------------------------------------------------------------------
            | Supports Robinson-Foulds and generalized RF metrics, plus
            | quartet-based distances.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ distance -i TREE1.nwk -j TREE2.nwk -m rf
            $ distance -i TREE1.nwk -j TREE2.nwk -m rf --normalize
            $ distance -i TREE1.nwk -j TREE2.nwk -m rfg_mci --normalize
            $ distance -i TREE1.nwk -j TREE2.nwk -m quartet --quartet-metric symmetric_difference
            $ distance -i TREE1.nwk -j TREE2.nwk -m quartet-all
            $ distance -i TREE1.nwk -j TREE2.nwk -m rf --json
            $ cat TREE1.nwk | distance -i - -j TREE2.nwk -m rf
            """
        ),
    )
    metrics = (
        "rf",
        "rfi",
        "rfg_ms",
        "rfg_msi",
        "rfg_spi",
        "rfg_mci",
        "quartet",
        "quartet-all",
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--tree1",
        dest="tree1",
        type=string_or_stdin_parse,
        metavar="path",
        required=True,
        help="first tree (path/url/newick), or '-' for stdin",
    )
    io_group.add_argument(
        "-j",
        "--tree2",
        dest="tree2",
        type=string_or_stdin_parse,
        metavar="path",
        required=True,
        help="second tree (path/url/newick), or '-' for stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output path; default writes to stdout",
    )

    metric_group = p.add_argument_group(title="Metric Selection")
    metric_group.add_argument(
        "-m",
        "--metric",
        type=str,
        default="rf",
        choices=metrics,
        metavar="name",
        help="distance metric: rf, rfi, rfg_ms, rfg_msi, rfg_spi, rfg_mci, quartet, quartet-all [rf]",
    )
    metric_group.add_argument(
        "-q",
        "--quartet-metric",
        type=str,
        default="symmetric_difference",
        metavar="name",
        help="quartet metric name",
    )
    metric_group.add_argument(
        "-n",
        "--normalize",
        action="store_true",
        help="normalize distance when supported by metric",
    )
    metric_group.add_argument(
        "--similarity",
        action="store_true",
        help="for quartet metrics, return similarity instead of distance",
    )

    format_group = p.add_argument_group(title="Formatting")
    format_group.add_argument(
        "--float-format",
        type=str,
        default="%.6g",
        metavar="fmt",
        help="format string for scalar output [%%.6g]",
    )
    format_group.add_argument(
        "--json",
        action="store_true",
        help="write structured JSON output",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_distance:run_distance")
    return p


def get_parser_make_ultrametric(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for make-ultrametric command."""
    kwargs = dict(
        prog="make-ultrametric",
        usage="make-ultrametric [options]",
        help="make a tree ultrametric using fast or penalized-likelihood methods",
        formatter_class=_formatter(130, 36),
        description=dedent(
            """
            -------------------------------------------------------------------------
            | make-ultrametric: transform a tree to ultrametric branch lengths
            -------------------------------------------------------------------------
            | method=extend      : fast tip-extension alignment.
            | method=clock       : strict-clock penalized-likelihood fit.
            | method=discrete    : ncat rate classes penalized-likelihood fit.
            | method=relaxed     : uncorrelated relaxed-clock penalized-likelihood fit.
            | method=correlated  : correlated relaxed-clock penalized-likelihood fit.
            -------------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ make-ultrametric -i TREE.nwk -m extend > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m clock -c -1=1.0 > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m discrete --ncat 3 -c -1=1.0 > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m relaxed --lam 0.5 -c -1=1.0 > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m correlated --lam 0.5 -c -1=1.0 > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m correlated --lam 0.5 --nstarts 8 --ncores 4 --seed 123 > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m discrete --estimate 5 -c -1=1.0 > UTREE.nwk
            $ make-ultrametric -i TREE.nwk -m correlated --lam 0.5 --json > UTREE.nwk 2> fit.json
            $ make-ultrametric -i TREE.nwk -m clock -c AB=0.8-1.2 CD=0.4
            $ cat TREE.nwk | make-ultrametric -i - --method extend
            $ make-ultrametric -i TREE.nwk -m relaxed -b | root -i - --mad > UTREE.nwk
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    method_group = p.add_argument_group(title="Method")
    method_group.add_argument(
        "-m",
        "--method",
        type=str,
        default="extend",
        choices=("extend", "clock", "discrete", "relaxed", "correlated"),
        metavar="method",
        help="method: extend|clock|discrete|relaxed|correlated [extend]",
    )
    method_group.add_argument(
        "-c",
        "--calibrations",
        type=str,
        nargs="*",
        metavar="query=value",
        help="clock/discrete/relaxed/correlated: one or more query=value or query=min-max entries",
    )
    method_group.add_argument(
        "--ncat",
        type=int,
        default=None,
        metavar="int",
        help="discrete only: number of rate categories (required unless --estimate is set)",
    )
    method_group.add_argument(
        "--lam",
        type=float,
        default=None,
        metavar="float",
        help="relaxed/correlated only: penalty lambda; lower=weaker regularization [1.0]",
    )
    method_group.add_argument(
        "--estimate",
        type=int,
        default=None,
        metavar="int",
        help="estimate ncat/lam by PHIIC using this many candidate values",
    )

    opt_group = p.add_argument_group(title="Optimization")
    opt_group.add_argument(
        "--max-iter",
        type=int,
        default=100_000,
        metavar="int",
        help="PL only: max optimizer iterations [100000]",
    )
    opt_group.add_argument(
        "--max-fun",
        type=int,
        default=100_000,
        metavar="int",
        help="PL only: max optimizer function evaluations [100000]",
    )
    opt_group.add_argument(
        "--max-refine",
        type=int,
        default=20,
        metavar="int",
        help="PL only: max alternating refinement rounds [20]",
    )
    opt_group.add_argument(
        "--nstarts",
        type=int,
        default=1,
        metavar="int",
        help="PL only: number of starts; best fit retained [1]",
    )
    opt_group.add_argument(
        "--ncores",
        type=int,
        default=1,
        metavar="int",
        help="PL only: worker processes for multistart [1]",
    )
    opt_group.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="int",
        help="PL only: random seed for reproducible multistart",
    )
    opt_group.add_argument(
        "--full",
        action="store_true",
        help="PL only: print model-fit summary fields to stderr",
    )
    opt_group.add_argument(
        "--json",
        action="store_true",
        help="PL only: print model-fit summary as JSON to stderr",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_make_ultrametric:run_make_ultrametric")
    return p


def get_parser_anc_state_discrete(
    parser: ArgumentParser | None = None,
) -> ArgumentParser:
    """Return parser for anc-state-discrete command."""
    kwargs = dict(
        prog="anc-state-discrete",
        usage="anc-state-discrete [options]",
        help="fit CTMC model and write ancestral-state metadata to tree output",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | anc-state-discrete: fit CTMC and reconstruct ancestral states
            -------------------------------------------------------------------
            | Fits a discrete CTMC model (ER, SYM, ARD) to a feature that
            | is already stored on the input tree, then writes reconstructed MAP
            | states and packed posterior metadata to output Newick or binary
            | ToyTree using feature names {feature}_anc and
            | {feature}_anc_posterior. Additional NHX metadata formatting can
            | be applied by piping output to `toytree io`. To produce TSV
            | output, pipe this command into `toytree get`.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ anc-state-discrete -i TRE.nwk -f X -n 3 -m ER > TRE.anc.nwk

            $ anc-state-discrete -i TRE.nwk -f X -n 3 -m ARD \\
                | toytree get -f X_anc X_anc_posterior -s ',' -o anc.csv

            $ anc-state-discrete -i TRE.nwk -f X -n 3 -m ER \\
                | toytree io -fp '&&NHX:' -fd ':' -fa '=' > TRE.anc.nhx

            $ anc-state-discrete -i TRE.nwk -f X -n 3 -b | toytree get -f X_anc
            $ anc-state-discrete -i TRE.nwk -f X -n 3 --json > TRE.anc.nwk 2> fit.json
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    model_group = p.add_argument_group(title="Model")
    model_group.add_argument(
        "-f",
        "--feature",
        type=str,
        metavar="name",
        required=True,
        help="discrete feature already stored on tree nodes",
    )
    model_group.add_argument(
        "-n",
        "--nstates",
        type=int,
        metavar="int",
        required=True,
        help="total number of CTMC states",
    )
    model_group.add_argument(
        "-m",
        "--model",
        type=str.upper,
        choices=("ER", "SYM", "ARD"),
        default="ER",
        metavar="name",
        help="rate model parameterization: ER|SYM|ARD [ER]",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "--json",
        action="store_true",
        help="print fitted model summary as JSON to stderr",
    )
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_anc_state_discrete:run_anc_state_discrete")
    return p


def get_parser_consensus(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for consensus command."""
    kwargs = dict(
        prog="consensus",
        usage="consensus [options]",
        help="infer a consensus tree from a multi-tree input",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | consensus: infer consensus tree from a single multi-tree input
            -------------------------------------------------------------------
            | Input can be a multi-Newick/Nexus file path, a string, or stdin.
            | Optionally map selected node/edge features to the consensus tree.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
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
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
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
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_consensus:run_consensus")
    return p


def get_parser_rtree(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for rtree command."""
    kwargs = dict(
        prog="rtree",
        usage="rtree [options]",
        help="generate random trees from toytree.rtree methods",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | rtree: generate random trees using toytree.rtree generators
            -------------------------------------------------------------------
            | Supports random topology, balanced/imbalanced/unit trees,
            | birth-death simulations, and coalescent trees.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            # Default random bifurcating topology
            $ rtree -n 10 --seed 123 > TREE.nwk

            # Unit-height ultrametric random tree
            $ rtree --method unittree -n 20 --treeheight 5 --seed 123 > TREE.nwk

            # Balanced topology with randomized tip names
            $ rtree --method baltree -n 12 --random-names --seed 3 > TREE.nwk

            # Birth-death simulation with stats to stderr
            $ rtree --method bdtree -n 25 --b 1.0 --d 0.2 --stop taxa --stats > TREE.nwk

            # Coalescent simulation (uses -n as k)
            $ rtree --method coaltree -n 16 --N 500 --seed 7 > TREE.nwk

            # Binary output for large-tree or metadata-safe piping
            $ rtree -n 100 -b | draw -i - -a
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
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
        help=BINARY_OUTPUT_HELP,
    )

    method_group = p.add_argument_group(title="Generator")
    method_group.add_argument(
        "-m",
        "--method",
        type=_parse_rtree_method,
        metavar="method",
        default="rtree",
        choices=RTREE_METHODS,
        help="method: rtree|unittree|imbtree|baltree|bdtree|coaltree [rtree]",
    )

    common_group = p.add_argument_group(title="Common")
    common_group.add_argument(
        "-n",
        "--ntips",
        type=int,
        metavar="int",
        default=10,
        help="number of tips (or k for coaltree) [10]",
    )
    common_group.add_argument(
        "-s",
        "--seed",
        type=int,
        metavar="int",
        help="random seed",
    )
    common_group.add_argument(
        "--random-names", action="store_true", help="assign names in random order"
    )
    common_group.add_argument(
        "--names",
        type=str,
        nargs="+",
        metavar="str",
        help="optional explicit tip labels",
    )

    topo_group = p.add_argument_group(title="Topology Scaling")
    topo_group.add_argument(
        "--treeheight",
        type=float,
        metavar="float",
        help="tree height (valid for unittree, imbtree, baltree)",
    )

    bd_group = p.add_argument_group(title="Birth-Death (bdtree)")
    bd_group.add_argument("--b", type=float, metavar="float", help="birth rate")
    bd_group.add_argument("--d", type=float, metavar="float", help="death rate")
    bd_group.add_argument(
        "--stop",
        type=str,
        metavar="name",
        choices=["taxa", "time"],
        help="'taxa' stops at ntips; 'time' stops at elapsed time. [taxa]",
    )
    bd_group.add_argument(
        "--time",
        type=float,
        metavar="float",
        help="simulation time horizon (used with --stop time)",
    )
    bd_group.add_argument(
        "--retain-extinct",
        action="store_true",
        help="retain extinct lineages in reconstructed tree",
    )
    bd_group.add_argument(
        "--max-resets",
        type=int,
        metavar="int",
        help="max restarts after total extinction",
    )
    bd_group.add_argument(
        "--stats",
        action="store_true",
        help="print bdtree simulation statistics to stderr",
    )

    coal_group = p.add_argument_group(title="Coalescent (coaltree)")
    coal_group.add_argument(
        "--N",
        type=float,
        metavar="float",
        help="effective population size scalar [100]",
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_rtree:run_rtree")
    return p


def get_parser_relabel(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for relabel command."""
    kwargs = dict(
        prog="relabel",
        usage="relabel [options]",
        help="relabel node name features for all nodes or selected subsets",
        formatter_class=_formatter(120, 120),
        description=dedent(
            """
            -------------------------------------------------------------------
            | relabel: transform node name features using query and text rules
            -------------------------------------------------------------------
            | Apply delimiter parsing, built-in transforms, prepend/append, and
            | optional italic/bold wrappers to tip names or selected nodes.
            -------------------------------------------------------------------
            """
        ),
        epilog=dedent(
            """
            Examples
            --------
            $ relabel -i TRE.nwk --strip '_-'
            $ relabel -i TRE.nwk --delim '|' --delim-idxs 0 2 --delim-join '_'
            $ relabel -i TRE.nwk -n '~^DE' --append '_X'
            $ relabel -i TRE.nwk --prepend 'sp_' --stripleft '._'
            $ relabel -i TRE.nwk --italic --bold
            $ relabel -i TRE.nwk --strip '_-' -b | draw -i - -a
            """
        ),
    )
    if parser:
        kwargs["name"] = kwargs.pop("prog")
        kwargs["add_help"] = False
        p = parser.add_parser(**kwargs)
    else:
        kwargs.pop("help", None)
        kwargs["add_help"] = False
        p = ArgumentParser(**kwargs)

    io_group = p.add_argument_group(title="Input / Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="path",
        help=SINGLE_TREE_INPUT_HELP,
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
        help=BINARY_OUTPUT_HELP,
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="parse internal newick labels as this feature (overrides auto-detect)",
    )
    io_group.add_argument(
        "-x",
        "--exclude-features",
        action="store_true",
        help="omit non-default node features from output Newick",
    )

    relabel_group = p.add_argument_group(title="Relabeling")
    relabel_group.add_argument(
        "-n",
        "--nodes",
        type=str,
        nargs="*",
        metavar="query",
        help="optional node queries (idx/name/regex) to relabel",
    )
    relabel_group.add_argument(
        "--tips-only",
        type=parse_bool,
        nargs="?",
        const=True,
        default=True,
        metavar="bool",
        help="relabel only tips (true/false) [default: true]",
    )
    relabel_group.add_argument(
        "--delim", type=str, metavar="str", help="delimiter for splitting names"
    )
    relabel_group.add_argument(
        "--delim-idxs",
        type=int,
        nargs="+",
        metavar="int",
        help="split part indices to keep",
    )
    relabel_group.add_argument(
        "--delim-join",
        type=str,
        default="_",
        metavar="str",
        help="join string for selected split parts [_]",
    )
    relabel_group.add_argument(
        "--strip", type=str, metavar="str", help="strip chars from both ends"
    )
    relabel_group.add_argument(
        "--stripleft", type=str, metavar="str", help="strip chars from left side only"
    )
    relabel_group.add_argument(
        "--prepend", type=str, metavar="str", help="prepend constant string"
    )
    relabel_group.add_argument(
        "--append", type=str, metavar="str", help="append constant string"
    )
    relabel_group.add_argument(
        "--italic", action="store_true", help="wrap names in <i>...</i>"
    )
    relabel_group.add_argument(
        "--bold", action="store_true", help="wrap names in <b>...</b>"
    )

    options_group = p.add_argument_group(title="Options")
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="show this help message and exit",
    )

    _set_handler(p, "toytree.cli.cli_relabel:run_relabel")
    return p


def register_subparsers(parent: Any) -> None:
    """Register all command parsers on a subparser parent in display order."""
    get_parser_get_node_data(parent)
    get_parser_set_node_data(parent)
    get_parser_io(parent)
    get_parser_view(parent)
    get_parser_draw(parent)
    get_parser_rtree(parent)
    get_parser_root(parent)
    get_parser_prune(parent)
    get_parser_distance(parent)
    get_parser_make_ultrametric(parent)
    get_parser_anc_state_discrete(parent)
    get_parser_consensus(parent)
    get_parser_relabel(parent)
