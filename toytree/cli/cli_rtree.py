#!/usr/bin/env python

"""Runtime implementation for the `rtree` CLI command."""

from __future__ import annotations

import sys


def _validate_method_args(args) -> None:
    """Validate method-specific options and reject incompatible combinations."""
    from toytree.utils import ToytreeError

    if args.method != "coaltree" and args.N is not None:
        raise ToytreeError("--N is only valid with --method coaltree.")

    if (
        args.method not in {"unittree", "imbtree", "baltree"}
        and args.treeheight is not None
    ):
        raise ToytreeError(
            "--treeheight is only valid with unittree, imbtree, or baltree."
        )

    if args.method != "bdtree":
        if any(
            [
                args.time is not None,
                args.b is not None,
                args.d is not None,
                args.stop is not None,
                args.retain_extinct,
                args.max_resets is not None,
                args.stats,
            ]
        ):
            raise ToytreeError(
                "--time/--b/--d/--stop/--retain-extinct/--max-resets/--stats "
                "are only valid with --method bdtree."
            )


def run_rtree(args) -> None:
    """Run the `rtree` CLI command."""
    from toytree.cli._tree_transport import write_tree_output
    from toytree.rtree import baltree, bdtree, coaltree, imbtree, rtree, unittree

    if args.log_level is not None:
        from toytree.utils.src.logger_setup import set_log_level

        set_log_level(args.log_level)

    _validate_method_args(args)

    names = args.names
    tree = None
    if args.method == "rtree":
        tree = rtree(
            ntips=args.ntips,
            random_names=args.random_names,
            seed=args.seed,
            names=names,
        )
    elif args.method == "unittree":
        tree = unittree(
            ntips=args.ntips,
            treeheight=(1.0 if args.treeheight is None else args.treeheight),
            random_names=args.random_names,
            seed=args.seed,
            names=names,
        )
    elif args.method == "imbtree":
        tree = imbtree(
            ntips=args.ntips,
            treeheight=(1.0 if args.treeheight is None else args.treeheight),
            random_names=args.random_names,
            seed=args.seed,
            names=names,
        )
    elif args.method == "baltree":
        tree = baltree(
            ntips=args.ntips,
            treeheight=(1.0 if args.treeheight is None else args.treeheight),
            random_names=args.random_names,
            seed=args.seed,
            names=names,
        )
    elif args.method == "coaltree":
        tree = coaltree(
            k=args.ntips,
            N=(100 if args.N is None else args.N),
            seed=args.seed,
            random_names=args.random_names,
            names=names,
        )
    else:  # bdtree
        result = bdtree(
            ntips=args.ntips,
            time=(4.0 if args.time is None else args.time),
            b=(1.0 if args.b is None else args.b),
            d=(0.0 if args.d is None else args.d),
            stop=("taxa" if args.stop is None else args.stop),
            seed=args.seed,
            retain_extinct=args.retain_extinct,
            max_resets=args.max_resets,
            return_stats=args.stats,
            random_names=args.random_names,
            names=names,
        )
        if args.stats:
            for key, value in result.items():
                if key != "tree":
                    print(f"{key}={value}", file=sys.stderr)
            tree = result["tree"]
        else:
            tree = result

    write_tree_output(
        tree,
        output=args.output,
        binary_out=args.binary_out,
    )
