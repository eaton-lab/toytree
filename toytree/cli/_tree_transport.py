#!/usr/bin/env python

"""Shared tree transport helpers for CLI commands."""

from __future__ import annotations

import pickle
import sys
from pathlib import Path
from typing import Any

from toytree.core.tree import ToyTree
from toytree.io.src.treeio import tree as parse_tree
from toytree.utils import ToytreeError


def _try_unpickle_tree(data: bytes) -> ToyTree | None:
    """Return ToyTree from pickle bytes, or None if bytes are not pickle."""
    try:
        obj = pickle.loads(data)
    except Exception:
        return None
    if not isinstance(obj, ToyTree):
        raise ToytreeError("binary input is not a ToyTree object.")
    return obj


def _parse_tree_from_bytes(data: bytes, internal_labels: str | None = None) -> ToyTree:
    """Parse bytes as binary ToyTree or text tree data."""
    ptree = _try_unpickle_tree(data)
    if ptree is not None:
        return ptree
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ToytreeError("could not parse tree input as binary ToyTree or UTF-8 text.") from exc
    try:
        return parse_tree(text, internal_labels=internal_labels)
    except Exception as exc:
        raise ToytreeError("could not parse tree input as binary ToyTree or text tree string.") from exc


def read_tree_auto(input_arg: str, internal_labels: str | None = None) -> ToyTree:
    """Read tree from CLI input, auto-detecting binary or text for stdin/path."""
    if input_arg == "-":
        return _parse_tree_from_bytes(sys.stdin.buffer.read(), internal_labels=internal_labels)

    path = Path(input_arg)
    if path.exists():
        return _parse_tree_from_bytes(path.read_bytes(), internal_labels=internal_labels)

    return parse_tree(input_arg, internal_labels=internal_labels)


def write_tree_output(
    tree: ToyTree,
    output: Path | None,
    binary_out: bool,
    *,
    features: set[str] | None = None,
    newick_write_kwargs: dict[str, Any] | None = None,
) -> None:
    """Write tree as pickled bytes or Newick text."""
    if binary_out:
        payload = pickle.dumps(tree, protocol=pickle.HIGHEST_PROTOCOL)
        if output:
            output.write_bytes(payload)
        else:
            sys.stdout.buffer.write(payload)
            sys.stdout.buffer.flush()
        return

    kwargs = dict(newick_write_kwargs or {})
    newick = tree.write(None, features=features, **kwargs)
    if output:
        output.write_text(newick + "\n", encoding="utf-8")
    else:
        sys.stdout.write(newick + "\n")
        sys.stdout.flush()
