#!/usr/bin/env python

"""Top-level CLI entry point with lazy runtime command loading."""

from __future__ import annotations

import importlib
import os
import sys
import textwrap
from argparse import ArgumentParser
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

from . import subparsers

DESCRIPTION = "toytree command line tool. Select a subcommand."
EPILOG = "EXAMPLE:\n$ toytree draw -i TREE -ts o -wi 400 -he 400 -v"
try:
    VERSION = version("toytree")
except PackageNotFoundError:
    VERSION = "unknown"


def setup_parsers() -> ArgumentParser:
    """Return initialized ArgumentParser with all subcommands."""
    parser = ArgumentParser(
        "toytree",
        usage="toytree [subcommand] --help",
        formatter_class=lambda prog: subparsers.SingleMetavarHelpFormatter(
            prog, width=110, max_help_position=28
        ),
        description=textwrap.dedent(
            """
            ----------------------------------------------------------
            |  %(prog)s: phylogenetic tree toolkit                   |
            ----------------------------------------------------------
            """
        ),
        epilog=textwrap.dedent(
            """
            Tutorials
            ---------
            https://eaton-lab.org/toytree/
            """
        ),
    )
    parser.add_argument("-v", "--version", action="version", version=f"toytree {VERSION}")
    parent = parser.add_subparsers(
        prog="%(prog)s",
        required=True,
        title="subcommands",
        dest="subcommand",
    )
    subparsers.register_subparsers(parent)
    return parser


def _load_handler(handler_spec: str):
    """Import and return the runtime handler function for a command."""
    mod_name, fn_name = handler_spec.split(":", 1)
    module = importlib.import_module(mod_name)
    return getattr(module, fn_name)


def main(cmd: Optional[str] = None) -> int:
    """Run CLI command and return exit status."""
    parser = setup_parsers()
    argv = cmd.split() if cmd else sys.argv[1:]

    # protect calibration tokens like '-1=10' before argparse sees them
    if argv and argv[0] == "make-ultrametric":
        argv = subparsers.normalize_calibration_argv(argv)

    args = parser.parse_args(argv)
    handler_spec = getattr(args, "_handler", None)
    if not handler_spec:
        parser.print_help()
        return 1

    run_func = _load_handler(handler_spec)
    try:
        run_func(args)
    except BrokenPipeError:
        # Typical in pipelines when downstream exits early.
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except Exception:
            pass
        return 141
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted by user", file=sys.stderr)
        raise SystemExit(130)
