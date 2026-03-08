#!/usr/bin/env python

"""Regression tests for CLI help formatter consistency."""

from __future__ import annotations

from toytree.cli.main import setup_parsers
from toytree.cli import subparsers


def test_main_parser_uses_single_metavar_formatter():
    """Top-level parser should use the shared single-metavar formatter."""
    parser = setup_parsers()
    assert isinstance(parser._get_formatter(), subparsers.SingleMetavarHelpFormatter)


def test_all_subcommand_parsers_use_single_metavar_formatter():
    """Every parser factory in subparsers should use the shared formatter."""
    parser_fns = [
        getattr(subparsers, name)
        for name in dir(subparsers)
        if name.startswith("get_parser_")
    ]
    assert parser_fns
    for parser_fn in parser_fns:
        parser = parser_fn()
        assert isinstance(parser._get_formatter(), subparsers.SingleMetavarHelpFormatter)
