#!/usr/bin/env python

"""Parse flexible multitree inputs into a `MultiTree`."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any

from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core.multitree import MultiTree
    from toytree.core.tree import ToyTree


def _is_serialized_tree_input(data: object) -> bool:
    """Return True for one parseable serialized tree input."""
    return isinstance(data, (str, bytes, PathLike))


def _normalize_serialized_tree_input(
    data: str | bytes | PathLike[str],
) -> str | bytes | Path:
    """Return one serialized input normalized for parser helpers."""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data
    return Path(data)


def _iter_collection_items(data: Iterable[Any]) -> list[Any]:
    """Return one ordered collection of multitree input items."""
    if isinstance(data, Mapping):
        raise ToytreeError(
            "Cannot parse mapping input for toytree.mtree(); "
            "pass an ordered iterable of trees instead."
        )
    if isinstance(data, (set, frozenset)):
        raise ToytreeError(
            "Cannot parse unordered collections in toytree.mtree(); "
            "use a list or tuple to preserve tree order."
        )

    items = list(data)
    if not items:
        raise ToytreeError("Cannot parse an empty collection in toytree.mtree().")
    return items


def _parse_collection_input(items: list[Any], **kwargs) -> MultiTree:
    """Return a `MultiTree` parsed from an ordered collection input."""
    from toytree.core.multitree import MultiTree
    from toytree.core.tree import ToyTree
    from toytree.io.src.parse import parse_tree

    has_trees = False
    has_serialized = False
    for idx, item in enumerate(items):
        if isinstance(item, ToyTree):
            has_trees = True
        elif _is_serialized_tree_input(item):
            has_serialized = True
        else:
            raise ToytreeError(
                "Unsupported item in toytree.mtree() input collection at index "
                f"{idx}: {item!r}"
            )
        if has_trees and has_serialized:
            raise ToytreeError(
                "Input collection cannot mix ToyTree objects with serialized "
                "tree inputs."
            )

    if has_trees:
        return MultiTree([tree.copy() for tree in items])

    trees = [
        parse_tree(_normalize_serialized_tree_input(item), **kwargs) for item in items
    ]
    return MultiTree(trees)


def mtree(
    data: str | bytes | PathLike[str] | Iterable[ToyTree | str | bytes | PathLike[str]],
    **kwargs,
) -> MultiTree:
    r"""Return a `MultiTree` parsed from supported multitree input.

    Parameters
    ----------
    data : str, bytes, os.PathLike[str], or iterable
        Input provided as serialized multi-tree text, a local file path,
        an HTTP(S) URL string, UTF-8 encoded bytes, or an ordered iterable
        of `ToyTree` objects and/or serialized single-tree inputs.
        Ordered serialized collections may mix `str`, `bytes`, and path-like
        objects, but they cannot mix `ToyTree` objects with serialized inputs.
    **kwargs
        Additional keyword arguments forwarded to
        :func:`toytree.io.parse_newick_string` when serialized tree text is
        parsed.

    Returns
    -------
    MultiTree
        Parsed multitree object containing every accepted input tree in order.

    Raises
    ------
    ToytreeError
        Raised if the input is empty, unordered, a mapping, contains unsupported
        collection items, or cannot be parsed into tree data.

    Examples
    --------
    >>> toytree.mtree("((a,b),c);\\n((a,c),b);").ntrees
    2
    >>> toytree.mtree([toytree.tree("((a,b),c);")]).ntrees
    1
    >>> toytree.mtree([b"((a,b),c);", "((a,c),b);"]).ntrees
    2

    See Also
    --------
    toytree.tree
    toytree.io.src.parse.parse_multitree
    toytree.io.src.parse.parse_tree_object
    """
    from toytree.io.src.parse import parse_multitree

    if isinstance(data, str):
        if not data.strip():
            raise ToytreeError("Cannot parse empty input for toytree.mtree().")
        return parse_multitree(data, **kwargs)

    if isinstance(data, bytes):
        if not data.strip():
            raise ToytreeError("Cannot parse empty input for toytree.mtree().")
        return parse_multitree(data, **kwargs)

    if isinstance(data, PathLike):
        return parse_multitree(_normalize_serialized_tree_input(data), **kwargs)

    return _parse_collection_input(_iter_collection_items(data), **kwargs)
