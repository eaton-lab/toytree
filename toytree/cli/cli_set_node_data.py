#!/usr/bin/env python

import ast
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
import pandas as pd


KWARGS = dict(
    prog="set-node-data",
    usage="set-node-data [options]",
    help="set node features on a tree and return updated newick",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=120, max_help_position=120
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------
        | set-node-data: assign feature values to nodes and return tree
        -------------------------------------------------------------------
        | Apply feature updates using key=value node assignments or a
        | tabular file, then emit updated Newick with feature data.
        -------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        # Mapping mode: set one feature from explicit node queries
        $ set-node-data -i TRE.nwk --feature color --set a='red' b='blue' --default 'gray'
        $ set-node-data -i TRE.nwk --feature support2 --set 10=0.95 11=0.80 --inherit
        $ set-node-data -i TRE.nwk -f group -s '~^cladeA'=1 '~^cladeB'=2 -d 0
        $ cat TRE.nwk | set-node-data -i - -f score -s a=1.2 b=2.3 --default 0

        # DataFrame mode: first column is index (node name or idx), other columns are features
        $ set-node-data -i TRE.nwk --table data.tsv --table-sep '\\t' > OUT.nwk
        $ set-node-data -i TRE.nwk --table data.csv --table-sep ',' -o OUT.nwk
        $ set-node-data -i TRE.nwk --table data.space.txt --table-sep ' '
        $ set-node-data -i TRE.nwk --table data.tsv --table-query-regex
        $ set-node-data -i TRE.nwk --table data.tsv --table-query-column id
        $ set-node-data -i TRE.nwk --table data.noheader.tsv --table-headers group
        $ set-node-data -i TRE.nwk --table data.tsv --table-query-regex --table-allow-unmatched

        # Rename tips from an IMAP formatted TSV <name>\\t<newname>
        $ set-node-data -i TRE.nwk --table IMAP.tsv --table-query-regex --table-allow-unmatched --table-headers 'name'

        # Edge features and NHX-like formatting
        $ set-node-data -i TRE.nwk -f rate -s 10=0.1 11=0.2 --edge
        $ set-node-data -i TRE.nwk -f state -s a=1 b=2 --features-prefix '&&NHX:' --features-delim ':' > OUT.nhx

        # Binary piping between commands
        $ set-node-data -i TRE.nwk -f X -s a=1 b=2 -b | draw -i - -nm false -ns 10 -nc 'X' -v
        """
    ),
)


def _parse_scalar(text: str):
    """Parse scalar CLI value using Python literals when possible."""
    try:
        return ast.literal_eval(text)
    except Exception:
        return text


def _parse_assignments(items: list[str]) -> dict:
    """Parse repeated query=value items into a mapping."""
    mapping = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--set entries must be query=value, got: '{item}'")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"--set has empty query in '{item}'")
        try:
            query = int(key)
        except ValueError:
            query = key
        mapping[query] = _parse_scalar(value)
    return mapping


def _normalize_sep(value: str) -> str:
    """Normalize table separator, including escaped values and whitespace."""
    if not value:
        return value
    sep = value.encode("utf-8").decode("unicode_escape")
    # Use pandas special-case whitespace regex to avoid parser warnings.
    if sep.isspace():
        return r"\s+"
    return sep


def _parse_int_or_str(value: str):
    """Parse token as int when possible, else return as str."""
    try:
        return int(value)
    except ValueError:
        return value


def get_parser_set_node_data(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for set-node-data command."""
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
        help="input tree file/path/url/newick string, or '-' for stdin",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="path",
        help="optional output file path; default writes to stdout",
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
        "--edge",
        action="store_true",
        help="mark feature as edge-polarized feature",
    )
    mode_group.add_argument(
        "--table",
        type=Path,
        metavar="path",
        help="tabular file for set_node_data_from_dataframe mode",
    )
    mode_group.add_argument(
        "--table-sep",
        type=str,
        default="\t",
        metavar="sep",
        help="separator for --table file [\\t]",
    )
    mode_group.add_argument(
        "--table-query-column",
        type=_parse_int_or_str,
        metavar="idx|name",
        help="table mode: query column selector (int position or column name)",
    )
    mode_group.add_argument(
        "--table-query-regex",
        action="store_true",
        help="table mode: treat string queries as regex (prepend '~' when absent)",
    )
    mode_group.add_argument(
        "--table-headers",
        type=str,
        nargs="+",
        metavar="str",
        help="table mode: feature names for parsed table columns after query column",
    )
    mode_group.add_argument(
        "--table-allow-unmatched",
        action="store_true",
        help="table mode: ignore unmatched node queries (logged at DEBUG)",
    )

    out_group = p.add_argument_group(title="Output Features")
    out_group.add_argument(
        "--features-prefix",
        type=str,
        metavar="str",
        default="&",
        help="prefix for features in extended newick [&, use '&&NHX:' for NHX style]",
    )
    out_group.add_argument(
        "--features-delim",
        type=str,
        metavar="str",
        default=",",
        help="delimiter between feature key/value pairs in output [,]",
    )
    out_group.add_argument(
        "--features-assignment",
        type=str,
        metavar="str",
        default="=",
        help="assignment token between feature key and value in output [=]",
    )
    out_group.add_argument(
        "--features-formatter",
        type=str,
        metavar="fmt",
        default="%.12g",
        help="float formatter for feature values in output [%%.12g]",
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


def run_set_node_data(args):
    """Run set-node-data command."""
    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.utils import ToytreeError
    from toytree.utils.src.logger_setup import set_log_level
    if args.log_level is not None:
        set_log_level(args.log_level)

    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

    use_table = args.table is not None
    use_mapping = args.feature is not None or bool(args.assignments)
    if use_table and use_mapping:
        raise ToytreeError("choose either table mode (--table) or mapping mode (--feature/--set), not both")
    if not use_table and not use_mapping:
        raise ToytreeError("must provide either --table or mapping mode args (--feature and optional --set)")

    # parse a tabular file to assign features
    if use_table:
        sep = _normalize_sep(args.table_sep)
        df = pd.read_csv(args.table, sep=sep, header=None if args.table_headers else 0)
        tre = tre.set_node_data_from_dataframe(
            df,
            query_column=args.table_query_column,
            query_is_regex=args.table_query_regex,
            table_headers=args.table_headers,
            allow_unmatched_queries=args.table_allow_unmatched,
            inplace=False,
        )

    # parse the user's --feature arg to assign features
    else:
        if not args.feature:
            raise ToytreeError("--feature is required in mapping mode")
        mapping = _parse_assignments(args.assignments or [])
        default = _parse_scalar(args.default) if args.default is not None else None
        tre = tre.set_node_data(
            feature=args.feature,
            data=mapping,
            default=default,
            inherit=args.inherit,
            edge=args.edge,
            inplace=False,
        )

    if args.exclude_features:
        features = None
    else:
        features = set(tre.features) - {"name", "height", "dist", "support"}
    write_tree_output(
        tre,
        output=args.output,
        binary_out=args.binary_out,
        features=features,
        newick_write_kwargs={
            "features_prefix": args.features_prefix,
            "features_delim": args.features_delim,
            "features_assignment": args.features_assignment,
            "features_formatter": args.features_formatter,
        },
    )


def main():
    parser = get_parser_set_node_data()
    args = parser.parse_args()
    run_set_node_data(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
