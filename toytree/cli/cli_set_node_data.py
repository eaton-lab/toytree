#!/usr/bin/env python

"""Runtime implementation for the `set-node-data` CLI command."""

from __future__ import annotations

import ast


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


def run_set_node_data(args):
    """Run the `set-node-data` CLI command."""
    import pandas as pd

    from toytree.cli._tree_transport import read_tree_auto, write_tree_output
    from toytree.utils import ToytreeError
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    tre = read_tree_auto(args.input, internal_labels=args.internal_labels)

    use_table = args.table is not None
    use_mapping = args.feature is not None or bool(args.assignments)
    if use_table and use_mapping:
        raise ToytreeError(
            "choose either table mode (--table) or mapping mode (--feature/--set), not both"
        )
    if not use_table and not use_mapping:
        raise ToytreeError(
            "must provide either --table or mapping mode args (--feature and optional --set)"
        )

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
