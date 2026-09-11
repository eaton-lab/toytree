"""Deterministic and unit-edge tree-shape generators."""

from __future__ import annotations

from collections.abc import Iterable

from toytree.core.node import Node
from toytree.core.tree import ToyTree

from ._utils import (
    RNGSeed,
    assign_tip_names,
    extend_tips_to_present,
    get_rng,
    normalize_names,
    scale_to_root_height,
    validate_bool,
    validate_int,
    validate_real,
)
from .topology import random_topology

__all__ = ["baltree", "imbtree", "unittree"]


def unittree(
    ntips: int,
    treeheight: float = 1.0,
    randomize_labels: bool = False,
    seed: RNGSeed = None,
    names: Iterable[object] | None = None,
) -> ToyTree:
    """Return an ultrametric Yule topology with unit internal edges.

    Parameters
    ----------
    ntips : int
        Number of tips. Must be an integer greater than or equal to two.
    treeheight : float, default=1.0
        Requested root height in arbitrary time units. It must be finite and
        strictly positive. All edge lengths are scaled proportionally after
        terminal branches have been extended to align the tips.
    randomize_labels : bool, default=False
        Randomly permute labels over tips. By default labels follow ToyTree tip
        index order, which is useful for constructing predictable test trees.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source for the Yule topology and optional label
        permutation. A supplied Generator is consumed in place.
    names : Iterable[object] or None, optional
        Unique labels for exactly ``ntips`` leaves. If omitted, labels are
        generated as ``r0``, ``r1``, and so on.

    Returns
    -------
    ToyTree
        An ultrametric rooted binary tree with root height ``treeheight``.

    Raises
    ------
    ToytreeError
        If a numeric argument or random-number source is invalid.
    ValueError
        If labels are duplicated or their count differs from ``ntips``.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10, treeheight=5.0, seed=123)

    Notes
    -----
    Before scaling, every internal edge, including both edges descending from
    the root, has length one. Terminal edges are extended to the present. The
    resulting durations are a construction, not draws from a diversification
    process.
    """
    ntips = validate_int(ntips, "ntips", 2)
    treeheight = validate_real(treeheight, "treeheight", minimum=0, strict_minimum=True)
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    labels = normalize_names(names, ntips)
    rng = get_rng(seed)
    tree = random_topology(
        ntips,
        model="yule",
        names=labels,
        randomize_labels=randomize_labels,
        seed=rng,
    )
    extend_tips_to_present(tree)
    scale_to_root_height(tree, treeheight)
    return tree


def imbtree(
    ntips: int,
    treeheight: float = 1.0,
    randomize_labels: bool = False,
    seed: RNGSeed = None,
    names: Iterable[object] | None = None,
) -> ToyTree:
    """Return a maximally imbalanced ultrametric bifurcating tree.

    Parameters
    ----------
    ntips : int
        Number of tips. Must be an integer greater than or equal to two.
    treeheight : float, default=1.0
        Requested root height in arbitrary time units. It must be finite and
        strictly positive.
    randomize_labels : bool, default=False
        Randomly permute labels over tips instead of assigning them in tip
        index order.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source used only for optional label permutation because
        the ladder topology itself is deterministic.
    names : Iterable[object] or None, optional
        Unique labels for exactly ``ntips`` leaves. Generated labels are used
        when omitted.

    Returns
    -------
    ToyTree
        An ultrametric rooted binary ladder tree at ``treeheight``.

    Raises
    ------
    ToytreeError
        If a numeric argument or random-number source is invalid.
    ValueError
        If labels are duplicated or their count differs from ``ntips``.

    Examples
    --------
    >>> tree = toytree.rtree.imbtree(9, treeheight=2.0)

    Notes
    -----
    This is a deterministic extreme of tree imbalance. Its branch lengths are
    construction values rather than samples from an evolutionary process.
    """
    ntips = validate_int(ntips, "ntips", 2)
    treeheight = validate_real(treeheight, "treeheight", minimum=0, strict_minimum=True)
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    labels = normalize_names(names, ntips)
    rng = get_rng(seed)
    root = Node()
    active = root
    for _ in range(ntips - 1):
        left = Node(dist=1.0)
        right = Node(dist=1.0)
        active._add_child(left)
        active._add_child(right)
        active = left
    tree = ToyTree(root)
    extend_tips_to_present(tree)
    scale_to_root_height(tree, treeheight)
    assign_tip_names(tree, labels, randomize_labels, rng)
    return tree


def _balanced_subtree(ntips: int, *, is_root: bool = False) -> Node:
    """Build a maximally balanced subtree for a positive leaf count."""
    node = Node(dist=0.0 if is_root else 1.0)
    if ntips == 1:
        return node
    left_size = ntips // 2
    node._add_child(_balanced_subtree(left_size))
    node._add_child(_balanced_subtree(ntips - left_size))
    return node


def baltree(
    ntips: int,
    treeheight: float = 1.0,
    randomize_labels: bool = False,
    seed: RNGSeed = None,
    names: Iterable[object] | None = None,
) -> ToyTree:
    """Return a maximally balanced ultrametric bifurcating tree.

    Parameters
    ----------
    ntips : int
        Number of tips. Both odd and even integers greater than or equal to
        two are accepted.
    treeheight : float, default=1.0
        Requested finite, strictly positive root height in arbitrary units.
    randomize_labels : bool, default=False
        Randomly permute labels over tips instead of assigning them in tip
        index order.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source used only for optional label permutation because
        the balanced topology itself is deterministic.
    names : Iterable[object] or None, optional
        Unique labels for exactly ``ntips`` leaves. Generated labels are used
        when omitted.

    Returns
    -------
    ToyTree
        An ultrametric rooted binary tree at ``treeheight``. At every split,
        descendant leaf counts differ by at most one.

    Raises
    ------
    ToytreeError
        If a numeric argument or random-number source is invalid.
    ValueError
        If labels are duplicated or their count differs from ``ntips``.

    Examples
    --------
    >>> even = toytree.rtree.baltree(8, treeheight=1.0)
    >>> odd = toytree.rtree.baltree(9, treeheight=1.0)

    Notes
    -----
    Subtree sizes are assigned recursively as floor(n/2) and ceil(n/2), so a
    maximally balanced bifurcating tree exists for every ``ntips >= 2``.
    """
    ntips = validate_int(ntips, "ntips", 2)
    treeheight = validate_real(treeheight, "treeheight", minimum=0, strict_minimum=True)
    randomize_labels = validate_bool(randomize_labels, "randomize_labels")
    labels = normalize_names(names, ntips)
    rng = get_rng(seed)
    tree = ToyTree(_balanced_subtree(ntips, is_root=True))
    extend_tips_to_present(tree)
    scale_to_root_height(tree, treeheight)
    assign_tip_names(tree, labels, randomize_labels, rng)
    return tree
