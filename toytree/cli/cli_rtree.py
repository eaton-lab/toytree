"""Runtime implementation for the ``rtree`` CLI command."""

from __future__ import annotations

import sys


def _provided(args, *names: str) -> bool:
    """Return True when any named optional argument is not None/False."""
    return any(getattr(args, name, None) not in (None, False) for name in names)


def _validate_method_args(args) -> None:
    """Reject options that do not apply to the selected generator."""
    from toytree.utils import ToytreeError

    method = args.method
    if method != "random-topology" and args.topology_model != "yule":
        raise ToytreeError("--topology-model is only valid with random-topology.")
    if method not in {"unittree", "imbtree", "baltree"} and args.treeheight is not None:
        raise ToytreeError("--treeheight is only valid with fixed-shape methods.")
    if method != "birth-death-process" and _provided(
        args,
        "stop_time",
        "stop_ntips",
        "start",
        "max_restarts",
        "max_events",
        "complete",
        "stats",
    ):
        raise ToytreeError(
            "process stopping and output options require birth-death-process."
        )
    if method != "birth-death-conditioned" and _provided(
        args, "crown_age", "origin_age"
    ):
        raise ToytreeError("--crown-age/--origin-age require birth-death-conditioned.")
    if method not in {"birth-death-process", "birth-death-conditioned"} and _provided(
        args, "birth_rate", "death_rate"
    ):
        raise ToytreeError("--birth-rate/--death-rate require a birth-death method.")
    if method != "coalescent-tree" and _provided(args, "Ne", "ploidy"):
        raise ToytreeError("--Ne/--ploidy require coalescent-tree.")


def run_rtree(args) -> None:
    """Generate a tree from parsed CLI arguments and write it."""
    from toytree.cli._tree_transport import write_tree_output
    from toytree.rtree import (
        baltree,
        birth_death_conditioned_tree,
        birth_death_process,
        coalescent_tree,
        imbtree,
        random_topology,
        unittree,
    )
    from toytree.utils import ToytreeError

    _validate_method_args(args)
    common = {
        "names": args.names,
        "randomize_labels": args.randomize_labels,
        "seed": args.seed,
    }

    if args.method == "random-topology":
        tree = random_topology(ntips=args.ntips, model=args.topology_model, **common)
    elif args.method == "unittree":
        tree = unittree(
            args.ntips,
            treeheight=1.0 if args.treeheight is None else args.treeheight,
            **common,
        )
    elif args.method == "imbtree":
        tree = imbtree(
            args.ntips,
            treeheight=1.0 if args.treeheight is None else args.treeheight,
            **common,
        )
    elif args.method == "baltree":
        tree = baltree(
            args.ntips,
            treeheight=1.0 if args.treeheight is None else args.treeheight,
            **common,
        )
    elif args.method == "coalescent-tree":
        tree = coalescent_tree(
            args.ntips,
            Ne=100.0 if args.Ne is None else args.Ne,
            ploidy=2.0 if args.ploidy is None else args.ploidy,
            **common,
        )
    elif args.method == "birth-death-conditioned":
        tree = birth_death_conditioned_tree(
            args.ntips,
            birth_rate=1.0 if args.birth_rate is None else args.birth_rate,
            death_rate=0.0 if args.death_rate is None else args.death_rate,
            crown_age=args.crown_age,
            origin_age=args.origin_age,
            **common,
        )
    else:
        result = birth_death_process(
            birth_rate=1.0 if args.birth_rate is None else args.birth_rate,
            death_rate=0.0 if args.death_rate is None else args.death_rate,
            stop_time=args.stop_time,
            stop_ntips=(
                None
                if args.stop_time is not None
                else (args.ntips if args.stop_ntips is None else args.stop_ntips)
            ),
            start="stem" if args.start is None else args.start,
            max_restarts=1000 if args.max_restarts is None else args.max_restarts,
            max_events=1_000_000 if args.max_events is None else args.max_events,
            **common,
        )
        if args.stats:
            for key in (
                "elapsed_time",
                "births",
                "deaths",
                "events",
                "attempted_events",
                "restarts",
                "extant_tips",
                "extinct_tips",
                "stop_reason",
                "start",
            ):
                print(f"{key}={getattr(result, key)}", file=sys.stderr)
        tree = result.complete_tree if args.complete else result.reconstructed_tree
        if tree is None:
            raise ToytreeError("the process ended with no reconstructed extant tree.")

    write_tree_output(tree, output=args.output, binary_out=args.binary_out)
