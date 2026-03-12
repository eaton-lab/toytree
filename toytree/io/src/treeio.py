#!/usr/bin/env python

"""Parse one tree from a `Node`, string, path, or URL."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from toytree.core.node import Node
from toytree.core.tree import ToyTree
from toytree.utils.src.exceptions import ToytreeError


def tree(
    data: Node | str | Path,
    feature_prefix: str = "&",
    feature_delim: str = ",",
    feature_assignment: str = "=",
    feature_unpack: str = "|",
    internal_labels: Optional[str] = None,
) -> ToyTree:
    """Return a `ToyTree` parsed from one supported tree input.

    Parameters
    ----------
    data : Node, str, or Path
        Tree input provided as a `Node` root, serialized Newick/NEXUS
        text, a local file path, or a public HTTP(S) URL.
    feature_prefix : str, default="&"
        Prefix expected at the start of metadata comments, such as
        ``"&"`` or ``"&&NHX:"``.
    feature_delim : str, default=","
        Separator between metadata items inside a comment block.
    feature_assignment : str, default="="
        Separator between metadata keys and values.
    feature_unpack : str, default="|"
        Optional token used to unpack compact list-like metadata
        values. Built-in scalar features such as ``name`` are never
        unpacked.
    internal_labels : str or None, default=None
        Controls how internal labels are interpreted after parsing.
        Use ``"name"``, ``"support"``, or another feature name to
        force the assignment.

    Returns
    -------
    ToyTree
        Parsed tree object.

    Raises
    ------
    ToytreeError
        Raised if the input type is unsupported or if string/path/URL
        input cannot be parsed into a tree.

    Examples
    --------
    >>> tree("((a,b),c);").ntips
    3
    >>> root = Node(name="root")
    >>> tree(root).ntips
    1

    See Also
    --------
    toytree.mtree
    toytree.io.parse_newick_string
    toytree.io.parse_newick_string_custom
    toytree.io.src.parse.parse_tree
    """
    if isinstance(data, Node):
        return ToyTree(data.copy(detach=True))

    if isinstance(data, (str, Path)):
        from toytree.io.src.parse import parse_tree

        return parse_tree(
            data,
            feature_prefix=feature_prefix,
            feature_delim=feature_delim,
            feature_assignment=feature_assignment,
            feature_unpack=feature_unpack,
            internal_labels=internal_labels,
        )

    raise ToytreeError(f"Cannot parse input tree data: {data!r}")
