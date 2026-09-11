#!/usr/bin/env python

"""Shared validation and output helpers for PCM simulation methods."""

from __future__ import annotations

from numbers import Integral, Real
from typing import TYPE_CHECKING, Any, Sequence, TypeAlias

import numpy as np
import pandas as pd

from toytree.core import ToyTree
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


RNGSeed: TypeAlias = (
    int | np.integer | np.random.Generator | np.random.SeedSequence | None
)


def get_rng(seed: RNGSeed) -> np.random.Generator:
    """Return a validated NumPy random-number generator.

    A supplied ``Generator`` is returned without resetting its state. Integer
    and ``SeedSequence`` inputs create a new generator. Boolean and negative
    integer seeds are rejected explicitly so all PCM simulators expose the
    same behavior.
    """
    if isinstance(seed, np.random.Generator):
        return seed
    if isinstance(seed, np.random.SeedSequence) or seed is None:
        return np.random.default_rng(seed)
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, Integral):
        raise ToytreeError(
            "seed must be an integer, numpy.random.Generator, "
            "numpy.random.SeedSequence, or None."
        )
    if int(seed) < 0:
        raise ToytreeError("integer seed must be non-negative.")
    return np.random.default_rng(int(seed))


def validate_tree_for_simulation(tree: ToyTree) -> ToyTree:
    """Return a tree whose non-root branch lengths are finite and nonnegative."""
    if not isinstance(tree, ToyTree):
        raise ToytreeError("tree must be a ToyTree instance.")
    if tree.nnodes < 1:
        raise ToytreeError("tree must contain at least one node.")
    lengths = np.asarray([node.dist for node in tree[:-1]], dtype=float)
    if np.any(~np.isfinite(lengths)):
        raise ToytreeError("tree branch lengths must be finite.")
    if np.any(lengths < 0.0):
        raise ToytreeError("tree branch lengths must be non-negative.")
    return tree


def validate_bool(value: object, name: str) -> bool:
    """Return a strict Boolean value."""
    if not isinstance(value, (bool, np.bool_)):
        raise ToytreeError(f"{name} must be a bool.")
    return bool(value)


def validate_positive_int(value: object, name: str) -> int:
    """Return a strictly positive, non-Boolean integer."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
        raise ToytreeError(f"{name} must be a positive integer.")
    out = int(value)
    if out <= 0:
        raise ToytreeError(f"{name} must be a positive integer.")
    return out


def validate_nonnegative_float(value: object, name: str) -> float:
    """Return a finite, nonnegative real scalar."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ToytreeError(f"{name} must be a finite float >= 0.")
    out = float(value)
    if not np.isfinite(out) or out < 0.0:
        raise ToytreeError(f"{name} must be a finite float >= 0.")
    return out


def validate_finite_float(value: object, name: str) -> float:
    """Return a finite real scalar."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ToytreeError(f"{name} must be a finite float.")
    out = float(value)
    if not np.isfinite(out):
        raise ToytreeError(f"{name} must be a finite float.")
    return out


def validate_feature_name(name: object, *, parameter: str = "name") -> str:
    """Return a nonempty string suitable for a tree feature name."""
    if not isinstance(name, str) or not name.strip():
        raise ToytreeError(f"{parameter} must be a non-empty string.")
    return name


def validate_state_labels(
    labels: Sequence[Any],
    nstates: int,
) -> list[str] | list[int]:
    """Return unique homogeneous string or integer discrete-state labels."""
    out = list(labels)
    if len(out) != nstates:
        raise ToytreeError("state_names length must match nstates.")
    if any(pd.isna(value) for value in out):
        raise ToytreeError("state_names cannot contain missing values.")
    if any(isinstance(value, (bool, np.bool_)) for value in out):
        raise ToytreeError("state_names cannot contain Boolean values.")
    if all(isinstance(value, str) for value in out):
        typed: list[str] | list[int] = [str(value) for value in out]
    elif all(isinstance(value, Integral) for value in out):
        typed = [int(value) for value in out]
    else:
        raise ToytreeError("state_names must be all strings or all integers.")
    if len(set(typed)) != len(typed):
        raise ToytreeError("state_names must be unique.")
    return typed


def make_node_series(
    tree: ToyTree,
    values: ArrayLike,
    *,
    name: str,
    tips_only: bool,
    inplace: bool,
    dtype: object | None = None,
) -> pd.Series:
    """Return one node-valued realization and optionally store it on a tree."""
    arr = np.asarray(values)
    if arr.shape != (tree.nnodes,):
        raise ToytreeError("internal simulation output must have tree.nnodes values.")
    full = pd.Series(arr, index=range(tree.nnodes), name=name, dtype=dtype)
    out = full.iloc[: tree.ntips].copy() if tips_only else full
    if inplace:
        tree.set_node_data(name, out, default=np.nan, inplace=True)
    return out


def make_node_dataframe(
    tree: ToyTree,
    values: ArrayLike,
    *,
    names: Sequence[str],
    tips_only: bool,
    inplace: bool,
) -> pd.DataFrame:
    """Return node-valued traits and optionally store their columns on a tree."""
    arr = np.asarray(values, dtype=float)
    if arr.shape != (tree.nnodes, len(names)):
        raise ToytreeError(
            "internal simulation output must have shape (tree.nnodes, ntraits)."
        )
    full = pd.DataFrame(arr, index=range(tree.nnodes), columns=list(names))
    out = full.iloc[: tree.ntips].copy() if tips_only else full
    if inplace:
        for feature in out.columns:
            tree.set_node_data(feature, out[feature], default=np.nan, inplace=True)
    return out
