#!/usr/bin/env python

"""Command line interface for tree distance metrics."""

from __future__ import annotations

import sys
import textwrap
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

KWARGS = dict(
    prog="distance",
    usage="distance [options]",
    help="compute a distance between two trees",
    formatter_class=lambda prog: RawDescriptionHelpFormatter(
        prog, width=120, max_help_position=34
    ),
    description=textwrap.dedent(
        """
        -------------------------------------------------------------------
        | distance: compute a tree distance metric between two trees
        -------------------------------------------------------------------
        | Supports Robinson-Foulds and generalized RF metrics, plus
        | quartet-based distances.
        -------------------------------------------------------------------
        """
    ),
    epilog=textwrap.dedent(
        """
        Examples
        --------
        $ distance -i TREE1.nwk -j TREE2.nwk -m rf
        $ distance -i TREE1.nwk -j TREE2.nwk -m rf --normalize
        $ distance -i TREE1.nwk -j TREE2.nwk -m rfg_mci --normalize
        $ distance -i TREE1.nwk -j TREE2.nwk -m quartet --quartet-metric symmetric_difference
        $ distance -i TREE1.nwk -j TREE2.nwk -m quartet-all
        $ cat TREE1.nwk | distance -i - -j TREE2.nwk -m rf
        """
    ),
)


METRICS = ("rf", "rfi", "rfg_ms", "rfg_msi", "rfg_spi", "rfg_mci", "quartet", "quartet-all")
QUARTET_METRICS = (
    "do_not_conflict",
    "explicitly_agree",
    "strict_joint_assertions",
    "semistrict_joint_assertions",
    "steel_and_penny",
    "symmetric_difference",
    "symmetric_divergence",
    "similarity_to_reference",
    "marczewski_steinhaus",
)


def string_or_stdin_parse(intree: str) -> str:
    """If TREE is stdin marker '-' then return stdin text."""
    if intree == "-":
        return sys.stdin.read().strip()
    return intree


def get_parser_distance(parser: ArgumentParser | None = None) -> ArgumentParser:
    """Return parser for `distance` command."""
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
        help="optional output file; default writes to stdout",
    )
    io_group.add_argument(
        "-I",
        "--internal-labels",
        type=str,
        metavar="str",
        help="Parse internal labels as this feature (overrides auto-detect)",
    )

    metric_group = p.add_argument_group(title="Metric Selection")
    metric_group.add_argument(
        "-m",
        "--metric",
        type=str,
        default="rf",
        choices=METRICS,
        metavar="name",
        help="distance metric: rf, rfi, rfg_ms, rfg_msi, rfg_spi, rfg_mci, quartet, quartet-all [rf]",
    )
    metric_group.add_argument(
        "-q",
        "--quartet-metric",
        type=str,
        default="symmetric_difference",
        metavar="name",
        help="quartet metric: do_not_conflict, explicitly_agree, strict_joint_assertions, semistrict_joint_assertions, "
        "steel_and_penny, symmetric_difference, symmetric_divergence, similarity_to_reference, marczewski_steinhaus",
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


def _write_result(args, text: str) -> None:
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")


def run_distance(args) -> None:
    """Run distance command."""
    from toytree.io.src.treeio import tree
    from toytree.distance import (
        get_treedist_rf,
        get_treedist_rfi,
        get_treedist_rfg_ms,
        get_treedist_rfg_msi,
        get_treedist_rfg_spi,
        get_treedist_rfg_mci,
        get_treedist_quartets,
    )
    from toytree.distance._src.quartet_dist import get_quartet_metric
    from toytree.utils import ToytreeError
    from toytree.utils.src.logger_setup import set_log_level

    if args.log_level is not None:
        set_log_level(args.log_level)

    if args.tree1 == "-" and args.tree2 == "-":
        raise ToytreeError("only one of --tree1/--tree2 can read from stdin ('-').")

    t1 = tree(args.tree1, internal_labels=args.internal_labels)
    t2 = tree(args.tree2, internal_labels=args.internal_labels)

    scalar_metric_funcs = {
        "rf": get_treedist_rf,
        "rfi": get_treedist_rfi,
        "rfg_ms": get_treedist_rfg_ms,
        "rfg_msi": get_treedist_rfg_msi,
        "rfg_spi": get_treedist_rfg_spi,
        "rfg_mci": get_treedist_rfg_mci,
    }

    if args.metric in scalar_metric_funcs:
        value = scalar_metric_funcs[args.metric](t1, t2, normalize=args.normalize)
        _write_result(args, args.float_format % float(value))
        return

    if args.metric == "quartet":
        value = get_quartet_metric(
            t1,
            t2,
            metric=args.quartet_metric,
            similarity=args.similarity,
        )
        _write_result(args, args.float_format % float(value))
        return

    # quartet-all: emit tabular metric-value lines.
    qseries = get_treedist_quartets(t1, t2, similarity=args.similarity)
    lines = [f"{name}\t{args.float_format % float(val)}" for name, val in qseries.items()]
    _write_result(args, "\n".join(lines))


def main():
    parser = get_parser_distance()
    args = parser.parse_args()
    run_distance(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise exc
