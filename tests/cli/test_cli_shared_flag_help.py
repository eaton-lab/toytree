#!/usr/bin/env python

"""Regression tests for shared tree-flag help text."""

from __future__ import annotations

import pytest

from toytree.cli import subparsers

HELP_INPUT = (
    "input tree file/path/url/newick string, or '-' for stdin; "
    "defaults to stdin when piped"
)
HELP_OUTPUT = "optional output path; default writes to stdout"
HELP_OUTPUT_DRAW = (
    "optional path to save drawing in format -f; ASCII defaults to stdout"
)
HELP_BINARY = "write binary ToyTree output for efficient piping between commands"
HELP_INTERNAL = "parse internal newick labels as this feature (overrides auto-detect)"
HELP_EXCLUDE = "omit non-default node features from output Newick"


def _help_text(parser, option: str) -> str:
    """Return help text for one option string from an argparse parser."""
    for action in parser._actions:
        if option in action.option_strings:
            return action.help
    raise AssertionError(f"option {option} not found")


def _has_option(parser, option: str) -> bool:
    """Return True if parser defines option string."""
    return any(option in action.option_strings for action in parser._actions)


def _is_required(parser, option: str) -> bool:
    """Return argparse required flag for one option string."""
    for action in parser._actions:
        if option in action.option_strings:
            return bool(getattr(action, "required", False))
    raise AssertionError(f"option {option} not found")


@pytest.mark.parametrize(
    "parser_factory, expected",
    [
        (
            subparsers.get_parser_get_node_data,
            {"-i": HELP_INPUT, "-o": HELP_OUTPUT, "-I": HELP_INTERNAL},
        ),
        (
            subparsers.get_parser_set_node_data,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
        (
            subparsers.get_parser_io,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
        (
            subparsers.get_parser_draw,
            {"-i": HELP_INPUT, "-o": HELP_OUTPUT_DRAW, "-I": HELP_INTERNAL},
        ),
        (
            subparsers.get_parser_root,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
        (
            subparsers.get_parser_prune,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
        (
            subparsers.get_parser_make_ultrametric,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
        (
            subparsers.get_parser_anc_state_discrete,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
        (
            subparsers.get_parser_relabel,
            {
                "-i": HELP_INPUT,
                "-o": HELP_OUTPUT,
                "-b": HELP_BINARY,
                "-I": HELP_INTERNAL,
                "-x": HELP_EXCLUDE,
            },
        ),
    ],
)
def test_single_tree_parsers_use_shared_flag_help(parser_factory, expected):
    """Single-tree command parsers should use shared help text."""
    parser = parser_factory()
    for option, text in expected.items():
        assert _help_text(parser, option) == text


@pytest.mark.parametrize(
    "parser_factory",
    [
        subparsers.get_parser_get_node_data,
        subparsers.get_parser_set_node_data,
        subparsers.get_parser_io,
        subparsers.get_parser_draw,
        subparsers.get_parser_root,
        subparsers.get_parser_prune,
        subparsers.get_parser_make_ultrametric,
        subparsers.get_parser_anc_state_discrete,
        subparsers.get_parser_relabel,
    ],
)
def test_single_tree_parsers_make_input_optional(parser_factory):
    """Single-tree commands should allow implicit stdin when -i is omitted."""
    parser = parser_factory()
    assert not _is_required(parser, "-i")


def test_get_node_data_internal_labels_in_input_output_group():
    """get-node-data should list -I in Input / Output section."""
    help_text = subparsers.get_parser_get_node_data().format_help()
    io_idx = help_text.index("Input / Output:")
    i_idx = help_text.index("-I, --internal-labels", io_idx)
    options_idx = help_text.index("Options:")
    assert io_idx < i_idx < options_idx


def test_get_node_data_separator_and_human_readable_in_formatting_group():
    """get-node-data should list -s/-H under Formatting section."""
    help_text = subparsers.get_parser_get_node_data().format_help()
    fmt_idx = help_text.index("Formatting:")
    opt_idx = help_text.index("Options:")
    s_idx = help_text.index("-s, --separator", fmt_idx)
    h_idx = help_text.index("-H, --human-readable", fmt_idx)
    n_idx = help_text.index("-N, --index-by-name", fmt_idx)
    assert fmt_idx < s_idx < opt_idx
    assert fmt_idx < h_idx < opt_idx
    assert fmt_idx < n_idx < opt_idx


def test_distance_parser_does_not_define_internal_labels_option():
    """Distance should not expose --internal-labels."""
    parser = subparsers.get_parser_distance()
    assert not _has_option(parser, "--internal-labels")


def test_draw_format_and_view_in_render_mode_group():
    """Draw should list -f/-v options under Render Mode."""
    help_text = subparsers.get_parser_draw().format_help()
    io_idx = help_text.index("Input / Output:")
    render_idx = help_text.index("Render Mode:")
    layout_idx = help_text.index("Layout:")
    f_idx = help_text.index("-f, --format", render_idx)
    v_idx = help_text.index("-v, --view", render_idx)
    assert io_idx < render_idx < layout_idx
    assert render_idx < f_idx < layout_idx
    assert render_idx < v_idx < layout_idx


def test_set_node_data_table_flags_grouped_under_from_table():
    """set-node-data should list table args under a dedicated From Table section."""
    help_text = subparsers.get_parser_set_node_data().format_help()
    io_idx = help_text.index("Input / Output:")
    mode_idx = help_text.index("Mode:")
    table_idx = help_text.index("From Table:")
    option_idx = help_text.index("Options:")
    assert io_idx < mode_idx < table_idx < option_idx
    assert "--table " in help_text[table_idx:option_idx]
    assert "--table-sep " in help_text[table_idx:option_idx]
    assert "--table-query-column " in help_text[table_idx:option_idx]
    assert "--table-query-regex" in help_text[table_idx:option_idx]
    assert "--table-headers " in help_text[table_idx:option_idx]
    assert "--table-allow-unmatched" in help_text[table_idx:option_idx]


def test_set_node_data_examples_use_from_table_term():
    """set-node-data examples should use From Table terminology."""
    help_text = subparsers.get_parser_set_node_data().format_help()
    assert "From Table:" in help_text
    assert "DataFrame mode" not in help_text


def test_rtree_method_help_lists_all_options():
    """Rtree method help should list canonical method options."""
    parser = subparsers.get_parser_rtree()
    assert (
        _help_text(parser, "--method")
        == "method: rtree|unittree|imbtree|baltree|bdtree|coaltree [rtree]"
    )


def test_rtree_bdtree_help_order_and_stop_description():
    """Rtree bdtree args should appear in requested order with expanded stop help."""
    help_text = subparsers.get_parser_rtree().format_help()
    bd_idx = help_text.index("Birth-Death (bdtree):")
    coal_idx = help_text.index("Coalescent (coaltree):")
    bd_text = help_text[bd_idx:coal_idx]
    b_idx = bd_text.index("--b ")
    d_idx = bd_text.index("--d ")
    stop_idx = bd_text.index("--stop ")
    time_idx = bd_text.index("--time ")
    assert b_idx < d_idx < stop_idx < time_idx
    assert "'taxa' stops at ntips" in bd_text
    assert "'time' stops at elapsed time" in bd_text


def test_json_output_flags_present_for_reporting_commands():
    """Reporting/model-summary parsers should expose --json."""
    for parser_factory in (
        subparsers.get_parser_get_node_data,
        subparsers.get_parser_distance,
        subparsers.get_parser_anc_state_discrete,
        subparsers.get_parser_make_ultrametric,
    ):
        parser = parser_factory()
        assert _has_option(parser, "--json")
