"""Topology and fixed-shape tree generators."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

import numpy as np

from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

from ._utils import (
    RNGSeed,
    assign_tip_names,
    get_rng,
    normalize_names,
    validate_bool,
    validate_int,
)

TopologyModel = Literal["yule", "pda"]

__all__ = ["random_topology"]


def _yule_root(ntips: int, rng: np.random.Generator) -> Node:
    """Return a Yule--Harding topology with unit edge lengths."""
    root = Node()
    active = [root]
    for _ in range(ntips - 1):
        idx = int(rng.integers(len(active)))
        parent = active[idx]
        active[idx] = active[-1]
        active.pop()
        left = Node(dist=1.0)
        right = Node(dist=1.0)
        parent._add_child(left)
        parent._add_child(right)
        active.extend((left, right))
    return root


def _pda_root(ntips: int, rng: np.random.Generator) -> Node:
    """Return a uniform rooted cladogram before label assignment."""
    root = Node()
    left = Node(dist=1.0)
    right = Node(dist=1.0)
    root._add_child(left)
    root._add_child(right)
    edge_children = [left, right]
    for _ in range(2, ntips):
        edge_idx = int(rng.integers(len(edge_children) + 1))
        new_leaf = Node(dist=1.0)
        if edge_idx == len(edge_children):
            new_root = Node()
            root._dist = 1.0
            new_root._add_child(root)
            new_root._add_child(new_leaf)
            edge_children.extend((root, new_leaf))
            root = new_root
            continue
        child = edge_children[edge_idx]
        parent = child.up
        inserted = Node(dist=1.0)
        parent._remove_child(child)
        parent._add_child(inserted)
        child._dist = 1.0
        inserted._add_child(child)
        inserted._add_child(new_leaf)
        edge_children.extend((inserted, new_leaf))
    return root


def random_topology(
    ntips: int,
    model: TopologyModel = "yule",
    names: Iterable[object] | None = None,
    randomize_labels: bool = True,
    seed: RNGSeed = None,
) -> ToyTree:
    """Return a random rooted bifurcating topology.

    Parameters
    ----------
    ntips : int
        Number of uniquely labelled leaves. Values must be integers greater
        than or equal to two; booleans are rejected.
    model : {"yule", "pda"}, default="yule"
        Distribution on rooted labelled topologies. ``"yule"`` samples the
        Yule--Harding distribution by splitting a uniformly selected leaf.
        ``"pda"`` samples the uniform, or proportional-to-distinguishable-
        arrangements, distribution by inserting each new leaf on a uniformly
        selected edge, including the stem edge.
    names : Iterable[object] or None, optional
        Unique labels for the tips. The iterable must contain exactly
        ``ntips`` values and values must remain unique after string
        conversion. If omitted, labels are ``r0``, ``r1``, and so on.
    randomize_labels : bool, default=True
        Randomly permute label placement after sampling the shape. The default
        makes labels exchangeable under both stochastic topology models.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. Integer and SeedSequence inputs create a new
        generator. A supplied Generator is consumed in place.

    Returns
    -------
    ToyTree
        Rooted binary tree with the requested number of labelled tips. Every
        real edge has arbitrary length 1 and the root distance is 0.

    Raises
    ------
    ToytreeError
        If ``ntips``, ``model``, or ``seed`` is invalid.
    ValueError
        If ``names`` has the wrong length or contains duplicate labels.

    Examples
    --------
    >>> tree = toytree.rtree.random_topology(10, model="yule", seed=123)
    >>> pda = toytree.rtree.random_topology(10, model="pda", seed=123)

    Notes
    -----
    These are topology distributions, not time-tree processes. Edge lengths
    carry no temporal or substitutional interpretation.
    """
    ntips = validate_int(ntips, "ntips", 2)
    if model not in {"yule", "pda"}:
        raise ToytreeError("model must be either 'yule' or 'pda'.")
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    labels = normalize_names(names, ntips)
    rng = get_rng(seed)
    root = _yule_root(ntips, rng) if model == "yule" else _pda_root(ntips, rng)
    tree = ToyTree(root)
    assign_tip_names(tree, labels, randomize_labels, rng)
    return tree
