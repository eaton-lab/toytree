#!/usr/bin/env python

"""Shared tree transport helpers for CLI commands."""

from __future__ import annotations

import pickle
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from toytree.utils import ToytreeError

if TYPE_CHECKING:
    from toytree.core.tree import ToyTree


TEXT_TREE_SUFFIXES = frozenset({".nwk", ".newick", ".tre", ".tree", ".nex", ".nexus"})


def _looks_like_inline_tree_text(value: str) -> bool:
    """Return True when input string appears to be inline Newick/Nexus text."""
    text = value.strip()
    return bool(text) and text[0] in ("(", "[", "#")


def _path_has_text_tree_suffix(path: Path) -> bool:
    """Return True when a path suffix strongly suggests text tree content."""
    return path.suffix.lower() in TEXT_TREE_SUFFIXES


def _bytes_look_like_text_tree(data: bytes) -> bool:
    """Heuristically detect text tree payloads without expensive parsing."""
    if not data:
        return False
    sample = data[:512]
    if b"\x00" in sample:
        return False
    stripped = sample.lstrip()
    return bool(stripped) and stripped[0:1] in (b"(", b"[", b"#")


def _try_unpickle_tree(data: bytes) -> "ToyTree | None":
    """Return ToyTree from pickle bytes, or None if bytes are not pickle."""
    from toytree.core.tree import ToyTree

    try:
        obj = pickle.loads(data)
    except Exception:
        return None
    if not isinstance(obj, ToyTree):
        raise ToytreeError("binary input is not a ToyTree object.")
    return obj


def _parse_tree_from_bytes(
    data: bytes,
    internal_labels: str | None = None,
    prefer_text: bool = False,
) -> "ToyTree":
    """Parse bytes as binary ToyTree or text tree data."""
    from toytree.io.src.treeio import tree as parse_tree

    if prefer_text:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None:
            try:
                return parse_tree(text, internal_labels=internal_labels)
            except Exception:
                # Fallback to binary handling when a text parse fails.
                pass

    ptree = _try_unpickle_tree(data)
    if ptree is not None:
        return ptree
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ToytreeError(
            "could not parse tree input as binary ToyTree or UTF-8 text."
        ) from exc
    try:
        return parse_tree(text, internal_labels=internal_labels)
    except Exception as exc:
        raise ToytreeError(
            "could not parse tree input as binary ToyTree or text tree string."
        ) from exc


def read_tree_auto(input_arg: str, internal_labels: str | None = None) -> "ToyTree":
    """Read tree from CLI input, auto-detecting binary or text for stdin/path."""
    from toytree.io.src.treeio import tree as parse_tree

    stripped = input_arg.strip()

    if input_arg == "-":
        data = sys.stdin.buffer.read()
        return _parse_tree_from_bytes(
            data,
            internal_labels=internal_labels,
            prefer_text=_bytes_look_like_text_tree(data),
        )

    if _looks_like_inline_tree_text(stripped):
        return parse_tree(input_arg, internal_labels=internal_labels)

    if stripped.startswith(("http://", "https://")):
        return parse_tree(input_arg, internal_labels=internal_labels)

    path = Path(input_arg)
    if path.exists():
        data = path.read_bytes()
        return _parse_tree_from_bytes(
            data,
            internal_labels=internal_labels,
            prefer_text=(
                _path_has_text_tree_suffix(path) or _bytes_look_like_text_tree(data)
            ),
        )

    return parse_tree(input_arg, internal_labels=internal_labels)


def write_tree_output(
    tree: "ToyTree",
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
    from toytree.io.src.writer import write as write_newick

    newick = write_newick(tree, None, features=features, **kwargs)
    if output:
        output.write_text(newick + "\n", encoding="utf-8")
    else:
        sys.stdout.write(newick + "\n")
        sys.stdout.flush()
