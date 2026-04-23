#!/usr/bin/env python

"""Resolve cached fixed-order tip labels for multitree drawing."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import toytree

MultiTree = TypeVar("MultiTree")
ToyTree = TypeVar("ToyTree")


def get_fixed_order_cache_key(
    treelist: Sequence[ToyTree],
) -> tuple[tuple[object, tuple[str, ...]], ...]:
    """Return a stable cache key for inferred fixed-order tip labels."""
    return tuple(
        (
            tree.get_topology_id(include_root=True),
            tuple(tree.get_tip_labels()),
        )
        for tree in treelist
    )


def resolve_fixed_order(
    mtree: MultiTree,
    treelist: Sequence[ToyTree],
    fixed_order: bool | Sequence[str] | None,
    *,
    infer_when_missing: bool = False,
) -> Sequence[str] | None:
    """Return explicit or cached inferred fixed-order tip labels."""
    if not treelist:
        return None

    if fixed_order is True:
        should_infer = True
    elif fixed_order is False:
        should_infer = infer_when_missing
    elif fixed_order is None:
        should_infer = infer_when_missing
    else:
        return fixed_order

    if not should_infer:
        return None

    if len(treelist) == 1:
        return treelist[0].get_tip_labels()

    cache_key = get_fixed_order_cache_key(treelist)
    cache = mtree._draw_fixed_order_cache
    if cache_key not in cache:
        cache[cache_key] = list(
            toytree.MultiTree(list(treelist)).get_consensus_tree().get_tip_labels()
        )
    return cache[cache_key]
