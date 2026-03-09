#!/usr/bin/env python

"""Top-level CLI entry point with lazy runtime command loading."""

from __future__ import annotations

import importlib
import os
import sys
import textwrap
from argparse import Action, ArgumentParser
from typing import Optional

from . import subparsers

DESCRIPTION = "toytree command line tool. Select a subcommand."
EPILOG = "EXAMPLE:\n$ toytree draw -i TREE -ts o -wi 400 -he 400 -v"


def _get_cli_version() -> str:
    """Return installed toytree version without eager metadata imports."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("toytree")
    except PackageNotFoundError:
        return "unknown"


class _LazyVersionAction(Action):
    """Argparse action that resolves package version only when requested."""

    def __init__(self, option_strings, dest, **kwargs):
        kwargs.setdefault("nargs", 0)
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.exit(0, f"toytree {_get_cli_version()}\n")


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
    parser.add_argument(
        "-v",
        "--version",
        action=_LazyVersionAction,
        help="show program's version number and exit",
    )
    parent = parser.add_subparsers(
        prog="%(prog)s",
        required=True,
        title="subcommands",
        dest="subcommand",
    )
    subparsers.register_subparsers(parent)
    return parser


def _get_subcommand_names(parser: ArgumentParser) -> tuple[str, ...]:
    """Return registered top-level subcommand names in parser order."""
    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if choices and getattr(action, "dest", None) == "subcommand":
            return tuple(choices.keys())
    return tuple()


def _expand_subcommand_prefix(parser: ArgumentParser, argv: list[str]) -> list[str]:
    """Expand a unique top-level subcommand prefix to its canonical name."""
    if not argv:
        return argv
    token = argv[0]
    if token.startswith("-"):
        return argv

    commands = _get_subcommand_names(parser)
    if token in commands:
        return argv

    matches = [name for name in commands if name.startswith(token)]
    if len(matches) == 1:
        out = list(argv)
        out[0] = matches[0]
        return out
    if len(matches) > 1:
        parser.error(
            f"ambiguous subcommand prefix {token!r}; matches: {', '.join(matches)}"
        )
    return argv


def _load_handler(handler_spec: str):
    """Import and return the runtime handler function for a command."""
    mod_name, fn_name = handler_spec.split(":", 1)
    module = importlib.import_module(mod_name)
    return getattr(module, fn_name)


def _format_cli_exception(exc: Exception) -> str:
    """Return a concise user-facing CLI error message from an exception."""
    message = str(exc).strip()
    return message if message else exc.__class__.__name__


def main(cmd: Optional[str] = None) -> int:
    """Run CLI command and return exit status."""
    parser = setup_parsers()
    argv = cmd.split() if cmd else sys.argv[1:]
    argv = _expand_subcommand_prefix(parser, argv)

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
    except Exception as exc:
        print(f"Error: {_format_cli_exception(exc)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted by user", file=sys.stderr)
        raise SystemExit(130)
