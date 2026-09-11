"""Shared validation and random-number helpers for tree simulation."""

from __future__ import annotations

from collections.abc import Iterable
from numbers import Integral, Real
from typing import TypeAlias

import numpy as np

from toytree.core.tree import ToyTree
from toytree.utils import ToytreeError

RNGSeed: TypeAlias = (
    int | np.integer | np.random.Generator | np.random.SeedSequence | None
)


def get_rng(seed: RNGSeed) -> np.random.Generator:
    """Return a NumPy generator while preserving supplied generator state."""
    if isinstance(seed, np.random.Generator):
        return seed
    if isinstance(seed, np.random.SeedSequence) or seed is None:
        return np.random.default_rng(seed)
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise ToytreeError(
            "seed must be an integer, numpy.random.Generator, "
            "numpy.random.SeedSequence, or None."
        )
    try:
        return np.random.default_rng(int(seed))
    except ValueError as exc:
        raise ToytreeError("integer seeds must be nonnegative.") from exc


def validate_bool(value: object, name: str) -> bool:
    """Return a bool after rejecting truthy non-boolean values."""
    if not isinstance(value, (bool, np.bool_)):
        raise ToytreeError(f"{name} must be a boolean.")
    return bool(value)


def validate_int(value: object, name: str, minimum: int) -> int:
    """Return an integer after rejecting booleans and out-of-range values."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ToytreeError(f"{name} must be an integer >= {minimum}.")
    result = int(value)
    if result < minimum:
        raise ToytreeError(f"{name} must be an integer >= {minimum}.")
    return result


def validate_real(
    value: object,
    name: str,
    *,
    minimum: float | None = None,
    strict_minimum: bool = False,
) -> float:
    """Return a finite real number subject to an optional lower bound."""
    if isinstance(value, bool) or not isinstance(value, Real):
        qualifier = ">" if strict_minimum else ">="
        suffix = "" if minimum is None else f" {qualifier} {minimum}"
        raise ToytreeError(f"{name} must be a finite numeric value{suffix}.")
    result = float(value)
    if not np.isfinite(result):
        raise ToytreeError(f"{name} must be a finite numeric value.")
    if minimum is not None:
        invalid = result <= minimum if strict_minimum else result < minimum
        if invalid:
            qualifier = ">" if strict_minimum else ">="
            raise ToytreeError(
                f"{name} must be a finite numeric value {qualifier} {minimum}."
            )
    return result


def normalize_names(
    names: Iterable[object] | None,
    size: int,
    *,
    size_name: str = "ntips",
) -> list[str] | None:
    """Normalize explicit labels and require one unique label per tip."""
    if names is None:
        return None
    if isinstance(names, (str, bytes)):
        raise ValueError("names must be an iterable of labels, not one string.")
    try:
        labels = [str(item) for item in names]
    except TypeError as exc:
        raise ValueError("names must be an iterable of labels.") from exc
    if len(labels) != size:
        raise ValueError(f"len(names)={len(labels)} does not match {size_name}={size}.")
    if len(set(labels)) != len(labels):
        raise ValueError("names must contain unique labels after string conversion.")
    return labels


def assign_tip_names(
    tree: ToyTree,
    names: list[str] | None,
    randomize_labels: bool,
    rng: np.random.Generator,
) -> None:
    """Assign generated or explicit labels to tips in place."""
    labels = [f"r{idx}" for idx in range(tree.ntips)] if names is None else list(names)
    if randomize_labels:
        labels = [labels[int(idx)] for idx in rng.permutation(tree.ntips)]
    for node, label in zip(tree[: tree.ntips], labels):
        node.name = label


def scale_to_root_height(tree: ToyTree, treeheight: float) -> None:
    """Scale all non-root edges to a requested root height in place."""
    current = float(tree.treenode.height)
    if current <= 0:
        raise ToytreeError("cannot scale a tree with nonpositive root height.")
    ratio = treeheight / current
    for node in tree:
        if not node.is_root():
            node._dist *= ratio
    tree._update()


def extend_tips_to_present(tree: ToyTree) -> None:
    """Extend terminal edges until all tips are at height zero."""
    for node in tree[: tree.ntips]:
        node._dist += node._height
    tree._update()
