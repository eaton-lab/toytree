"""Forward simulation of complete constant-rate birth--death histories."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

import numpy as np

from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

from ._utils import (
    RNGSeed,
    get_rng,
    normalize_names,
    validate_bool,
    validate_int,
    validate_real,
)

__all__ = ["BirthDeathProcessResult", "birth_death_process"]


@dataclass(slots=True)
class BirthDeathProcessResult:
    """Result of a forward birth--death process simulation.

    Attributes
    ----------
    complete_tree : ToyTree
        Full history, including extinct lineages and any unary origin node.
    reconstructed_tree : ToyTree or None
        Tree induced by extant lineages after extinct leaves and resulting
        unary nodes are removed. It is None if the process ended extinct.
    elapsed_time : float
        Time from process origin to the observation or stopping event.
    births, deaths, events : int
        Event counts in the returned realization. ``events`` equals births
        plus deaths.
    attempted_events : int
        Events across the accepted realization and discarded extinct runs.
    restarts : int
        Number of extinct realizations discarded when conditioning on survival.
    extant_tips, extinct_tips : int
        Counts of extant and extinct leaves in ``complete_tree``.
    stop_reason : {"time", "taxa", "extinction"}
        Condition that ended the returned realization.
    start : {"stem", "crown"}
        Initial process convention.
    """

    complete_tree: ToyTree
    reconstructed_tree: ToyTree | None
    elapsed_time: float
    births: int
    deaths: int
    events: int
    attempted_events: int
    restarts: int
    extant_tips: int
    extinct_tips: int
    stop_reason: str
    start: str


def _new_process(start: str) -> tuple[Node, list[Node]]:
    """Return a fresh origin and active-lineage list."""
    root = Node()
    if start == "stem":
        lineage = Node()
        lineage._birth_time = 0.0
        root._add_child(lineage)
        return root, [lineage]
    left = Node()
    right = Node()
    left._birth_time = 0.0
    right._birth_time = 0.0
    root._add_child(left)
    root._add_child(right)
    return root, [left, right]


def _clone_reconstructed(node: Node) -> Node | None:
    """Clone the extant-induced subtree while collapsing unary nodes."""
    if node.is_leaf():
        if not getattr(node, "extant", False):
            return None
        clone = Node(name=node.name, dist=node.dist)
        clone.extant = True
        clone.extinct = False
        return clone

    children = [
        child
        for child in (_clone_reconstructed(item) for item in node.children)
        if child is not None
    ]
    if not children:
        return None
    if len(children) == 1:
        child = children[0]
        child._dist += node.dist
        return child
    clone = Node(name=node.name, dist=node.dist)
    for child in children:
        clone._add_child(child)
    return clone


def _label_process_tips(
    tree: ToyTree,
    names: list[str] | None,
    randomize_labels: bool,
    rng: np.random.Generator,
) -> tuple[int, int]:
    """Label and count extant and extinct leaves in a complete history."""
    extant = [node for node in tree[: tree.ntips] if getattr(node, "extant", False)]
    extinct = [
        node for node in tree[: tree.ntips] if not getattr(node, "extant", False)
    ]
    labels = [f"r{idx}" for idx in range(len(extant))] if names is None else list(names)
    if len(labels) != len(extant):
        raise ToytreeError(
            "the returned extant-tip count does not match the supplied names."
        )
    if randomize_labels:
        labels = [labels[int(idx)] for idx in rng.permutation(len(labels))]
    for node, label in zip(extant, labels):
        node.name = label
    for idx, node in enumerate(extinct):
        node.name = f"extinct{idx}"
        node.extant = False
        node.extinct = True
    return len(extant), len(extinct)


def birth_death_process(
    birth_rate: float = 1.0,
    death_rate: float = 0.0,
    *,
    stop_time: float | None = None,
    stop_ntips: int | None = None,
    start: Literal["stem", "crown"] = "stem",
    condition_on_survival: bool = True,
    max_restarts: int = 1000,
    max_events: int = 1_000_000,
    names: Iterable[object] | None = None,
    randomize_labels: bool = True,
    seed: RNGSeed = None,
) -> BirthDeathProcessResult:
    """Simulate a complete constant-rate birth--death process forward.

    Parameters
    ----------
    birth_rate : float, default=1.0
        Per-lineage birth rate per time unit. It must be finite and
        nonnegative.
    death_rate : float, default=0.0
        Per-lineage extinction rate per time unit. It must be finite and
        nonnegative. At least one of the two event rates must be positive.
    stop_time : float or None, optional
        Exact observation horizon measured from the process origin. Supply a
        finite positive value for time stopping and leave ``stop_ntips`` None.
        No event beyond this time is applied.
    stop_ntips : int or None, optional
        Stop immediately when this many extant lineages are first present.
        Supply an integer at least one and leave ``stop_time`` None. A final
        birth can therefore produce two valid zero-duration terminal edges.
    start : {"stem", "crown"}, default="stem"
        ``"stem"`` begins with one lineage descending from an explicit unary
        origin. ``"crown"`` begins with two lineages at an initial split.
    condition_on_survival : bool, default=True
        Restart after total extinction until the requested stopping condition
        is reached. If False, return the extinct history immediately with
        ``reconstructed_tree=None``.
    max_restarts : int, default=1000
        Maximum discarded extinct histories when conditioning on survival.
        This finite cap prevents high-extinction regimes from running forever.
    max_events : int, default=1000000
        Maximum total number of events across all attempts. Exceeding this
        computational safety cap raises ``ToytreeError``.
    names : Iterable[object] or None, optional
        Unique labels for extant tips. Explicit names are supported only with
        ``stop_ntips`` and must have exactly that length. Extinct tips receive
        generated ``extinct0``, ``extinct1``, ... labels.
    randomize_labels : bool, default=True
        Randomly permute labels over extant tips in the complete and
        reconstructed trees.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place,
        including across discarded extinct attempts.

    Returns
    -------
    BirthDeathProcessResult
        Typed result containing the complete history, reconstructed extant
        tree, stopping metadata, and event counts.

    Raises
    ------
    ToytreeError
        If arguments are invalid, a richness target is impossible, or a
        restart/event safety limit is exceeded.
    ValueError
        If explicit names are duplicated or have the wrong length.

    Examples
    --------
    >>> result = toytree.rtree.birth_death_process(
    ...     birth_rate=1.0, death_rate=0.2, stop_time=3.0, seed=123
    ... )
    >>> complete = result.complete_tree
    >>> reconstructed = result.reconstructed_tree

    Notes
    -----
    This is an event simulator, not a direct draw from a reconstructed process
    conditioned on a fixed number of extant taxa and age. Use
    ``birth_death_conditioned_tree`` for that distribution. Event histories
    retain extinct lineages and may contain unary nodes. The reconstructed
    tree removes them and collapses the corresponding paths.
    """
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    condition_on_survival = validate_bool(
        condition_on_survival, "condition_on_survival"
    )
    birth_rate = validate_real(birth_rate, "birth_rate", minimum=0)
    death_rate = validate_real(death_rate, "death_rate", minimum=0)
    if birth_rate + death_rate == 0:
        raise ToytreeError("birth_rate and death_rate cannot both be zero.")
    if (stop_time is None) == (stop_ntips is None):
        raise ToytreeError("supply exactly one of stop_time or stop_ntips.")
    if start not in {"stem", "crown"}:
        raise ToytreeError("start must be either 'stem' or 'crown'.")
    max_restarts = validate_int(max_restarts, "max_restarts", 0)
    max_events = validate_int(max_events, "max_events", 1)
    if stop_time is not None:
        stop_time = validate_real(
            stop_time, "stop_time", minimum=0, strict_minimum=True
        )
        if names is not None:
            raise ToytreeError("explicit names are supported only with stop_ntips.")
        labels = None
    else:
        stop_ntips = validate_int(stop_ntips, "stop_ntips", 1)
        initial = 1 if start == "stem" else 2
        if stop_ntips < initial:
            raise ToytreeError(f"stop_ntips must be >= {initial} when start={start!r}.")
        if birth_rate == 0 and stop_ntips > initial:
            raise ToytreeError(
                "a positive birth_rate is required to increase richness."
            )
        labels = normalize_names(names, stop_ntips)

    rng = get_rng(seed)
    p_birth = birth_rate / (birth_rate + death_rate)
    attempted_events = 0
    restarts = 0

    while True:
        root, active = _new_process(start)
        elapsed = 0.0
        births = 0
        deaths = 0
        stop_reason = ""

        if stop_ntips is not None and len(active) == stop_ntips:
            stop_reason = "taxa"

        while not stop_reason:
            rate = len(active) * (birth_rate + death_rate)
            wait = float(rng.exponential(1.0 / rate))
            if stop_time is not None and elapsed + wait >= stop_time:
                elapsed = stop_time
                stop_reason = "time"
                break
            elapsed += wait
            attempted_events += 1
            if attempted_events > max_events:
                raise ToytreeError(
                    f"birth_death_process exceeded max_events={max_events}."
                )

            idx = int(rng.integers(len(active)))
            lineage = active[idx]
            lineage._dist = elapsed - float(lineage._birth_time)
            if float(rng.random()) < p_birth:
                left = Node()
                right = Node()
                left._birth_time = elapsed
                right._birth_time = elapsed
                lineage._add_child(left)
                lineage._add_child(right)
                active[idx] = left
                active.append(right)
                births += 1
                if stop_ntips is not None and len(active) == stop_ntips:
                    stop_reason = "taxa"
            else:
                lineage.extant = False
                lineage.extinct = True
                active[idx] = active[-1]
                active.pop()
                deaths += 1
                if not active:
                    if condition_on_survival:
                        restarts += 1
                        if restarts > max_restarts:
                            raise ToytreeError(
                                "birth_death_process exceeded "
                                f"max_restarts={max_restarts}."
                            )
                        break
                    stop_reason = "extinction"

        if not active and condition_on_survival and not stop_reason:
            continue
        break

    for lineage in active:
        lineage._dist = elapsed - float(lineage._birth_time)
        lineage.extant = True
        lineage.extinct = False

    complete = ToyTree(root)
    extant_count, extinct_count = _label_process_tips(
        complete, labels, randomize_labels, rng
    )
    reconstructed_root = _clone_reconstructed(complete.treenode)
    if reconstructed_root is None:
        reconstructed = None
    else:
        reconstructed_root._up = None
        reconstructed = ToyTree(reconstructed_root)

    return BirthDeathProcessResult(
        complete_tree=complete,
        reconstructed_tree=reconstructed,
        elapsed_time=elapsed,
        births=births,
        deaths=deaths,
        events=births + deaths,
        attempted_events=attempted_events,
        restarts=restarts,
        extant_tips=extant_count,
        extinct_tips=extinct_count,
        stop_reason=stop_reason,
        start=start,
    )
