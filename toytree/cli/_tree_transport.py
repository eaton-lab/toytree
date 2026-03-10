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
BINARY_TREE_MAGIC = b"TOYTREE_BIN_V1\n"


def resolve_input_arg(input_arg: str | None) -> str:
    """Return explicit input arg or infer stdin marker for piped input.

    Raises
    ------
    ToytreeError
        If no explicit input is provided and stdin is not piped.
    """
    if input_arg is not None:
        return input_arg
    if sys.stdin.isatty():
        raise ToytreeError(
            "no input tree provided; use -i PATH or pipe tree data to stdin."
        )
    return "-"


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


def is_binary_tree_payload(data: bytes) -> bool:
    """Return True when bytes are in toytree CLI binary transport format."""
    return data.startswith(BINARY_TREE_MAGIC)


def serialize_tree_binary(tree: "ToyTree") -> bytes:
    """Return a versioned binary payload for CLI tree transport.

    Notes
    -----
    The payload stores only the root Node object, then reconstructs the
    ``ToyTree`` on read. This avoids expensive unpickling of the full
    ``ToyTree`` object graph in each CLI process.
    """
    payload = pickle.dumps(tree.treenode, protocol=pickle.HIGHEST_PROTOCOL)
    return BINARY_TREE_MAGIC + payload


def deserialize_tree_binary(data: bytes) -> "ToyTree":
    """Return a ``ToyTree`` from binary payload bytes."""
    from toytree.core.node import Node
    from toytree.core.tree import ToyTree

    if not is_binary_tree_payload(data):
        raise ToytreeError("binary payload is not in toytree transport format.")
    raw_payload = data[len(BINARY_TREE_MAGIC) :]
    if not raw_payload:
        raise ToytreeError("binary payload is empty.")
    try:
        node = pickle.loads(raw_payload)
    except Exception as exc:
        raise ToytreeError("could not decode binary tree payload.") from exc
    if not isinstance(node, Node):
        raise ToytreeError("binary payload does not contain a Node tree object.")
    return ToyTree(node)


def _parse_tree_from_bytes(
    data: bytes,
    internal_labels: str | None = None,
    feature_prefix: str = "&",
    feature_delim: str = ",",
    feature_assignment: str = "=",
    feature_unpack: str = "|",
    prefer_text: bool = False,
) -> "ToyTree":
    """Parse bytes as binary transport payload or text tree data."""
    from toytree.io.src.treeio import tree as parse_tree

    if prefer_text:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None:
            try:
                return parse_tree(
                    text,
                    internal_labels=internal_labels,
                    feature_prefix=feature_prefix,
                    feature_delim=feature_delim,
                    feature_assignment=feature_assignment,
                    feature_unpack=feature_unpack,
                )
            except Exception:
                # Fallback to binary handling when a text parse fails.
                pass

    if is_binary_tree_payload(data):
        return deserialize_tree_binary(data)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ToytreeError(
            "could not parse tree input as binary transport payload or UTF-8 text."
        ) from exc
    try:
        return parse_tree(
            text,
            internal_labels=internal_labels,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            feature_unpack=feature_unpack,
        )
    except Exception as exc:
        raise ToytreeError(
            "could not parse tree input as binary transport payload "
            "or text tree string."
        ) from exc


def read_tree_auto(
    input_arg: str,
    internal_labels: str | None = None,
    feature_prefix: str = "&",
    feature_delim: str = ",",
    feature_assignment: str = "=",
    feature_unpack: str = "|",
) -> "ToyTree":
    """Read tree from CLI input, auto-detecting binary or text for stdin/path."""
    from toytree.io.src.treeio import tree as parse_tree

    stripped = input_arg.strip()

    if input_arg == "-":
        data = sys.stdin.buffer.read()
        if not data:
            raise ToytreeError("no data received on stdin.")
        return _parse_tree_from_bytes(
            data,
            internal_labels=internal_labels,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            feature_unpack=feature_unpack,
            prefer_text=_bytes_look_like_text_tree(data),
        )

    if _looks_like_inline_tree_text(stripped):
        return parse_tree(
            input_arg,
            internal_labels=internal_labels,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            feature_unpack=feature_unpack,
        )

    if stripped.startswith(("http://", "https://")):
        return parse_tree(
            input_arg,
            internal_labels=internal_labels,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            feature_unpack=feature_unpack,
        )

    path = Path(input_arg)
    if path.exists():
        data = path.read_bytes()
        return _parse_tree_from_bytes(
            data,
            internal_labels=internal_labels,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            feature_unpack=feature_unpack,
            prefer_text=(
                _path_has_text_tree_suffix(path) or _bytes_look_like_text_tree(data)
            ),
        )

    return parse_tree(
        input_arg,
        internal_labels=internal_labels,
        feature_prefix=feature_prefix,
        feature_delim=feature_delim,
        feature_assignment=feature_assignment,
        feature_unpack=feature_unpack,
    )


def write_tree_output(
    tree: "ToyTree",
    output: Path | None,
    binary_out: bool,
    *,
    features: set[str] | None = None,
    newick_write_kwargs: dict[str, Any] | None = None,
) -> None:
    """Write tree as binary transport bytes or Newick text."""
    if binary_out:
        payload = serialize_tree_binary(tree)
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
