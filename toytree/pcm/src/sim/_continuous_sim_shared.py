#!/usr/bin/env python

"""Shared helpers for continuous trait simulation methods."""

from __future__ import annotations

import numpy as np
import pandas as pd

from toytree.utils.src.exceptions import ToytreeError


def _get_time_from_root(tree) -> np.ndarray:
    """Return absolute time from root to each node."""
    times = np.zeros(tree.nnodes, dtype=float)
    root = tree.treenode
    times[root.idx] = 0.0
    for node in tree[::-1][1:]:
        pidx = node.up.idx
        times[node.idx] = times[pidx] + float(node.dist)
    return times


def _validate_feature_name(name: str) -> str:
    """Return a validated feature name used for simulated outputs."""
    name = str(name)
    if not name.strip():
        raise ToytreeError("name must be a non-empty string.")
    return name


def _get_unique_node_name_map(tree) -> dict[str, int]:
    """Return a mapping from unique non-empty node names to node idx labels."""
    mapping: dict[str, int] = {}
    dups: set[str] = set()
    for node in tree:
        if not node.name:
            continue
        if node.name in mapping:
            dups.add(node.name)
        else:
            mapping[node.name] = node.idx
    if dups:
        raise ToytreeError(
            "regime Series indexed by node names requires unique non-empty names. "
            f"Duplicates include: {sorted(dups)[:5]}"
        )
    return mapping


def _coerce_regime_labels(
    tree,
    regime: str | pd.Series | None,
) -> np.ndarray:
    """Return per-node regime labels (root label ignored by edge callers)."""
    labels = np.full(tree.nnodes, np.nan, dtype=object)
    if regime is None:
        return labels
    if isinstance(regime, str):
        ser = tree.get_node_data(regime, missing=np.nan)
        ser.index = range(tree.nnodes)
        return ser.to_numpy(dtype=object)
    if not isinstance(regime, pd.Series):
        raise ToytreeError(
            "regime must be a tree feature name (str), pandas Series, or None."
        )

    out = labels.copy()
    idx = regime.index
    is_int_index = isinstance(idx, pd.RangeIndex) or (
        hasattr(idx, "dtype") and np.issubdtype(idx.dtype, np.integer)
    )
    if is_int_index:
        for key, value in regime.items():
            ikey = int(key)
            if 0 <= ikey < tree.nnodes:
                out[ikey] = value
            else:
                raise ToytreeError(
                    f"regime Series index contains invalid node idx: {key}"
                )
        return out

    name_map = _get_unique_node_name_map(tree)
    for key, value in regime.items():
        skey = str(key)
        if skey not in name_map:
            raise ToytreeError(
                "regime Series index label "
                f"{skey!r} does not match a node name on the tree."
            )
        out[name_map[skey]] = value
    return out
