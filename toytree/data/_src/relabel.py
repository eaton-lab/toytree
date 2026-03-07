#!/usr/bin/env python

"""Method to relabel node name features on a ToyTree."""

from __future__ import annotations

from typing import Callable, Sequence, TypeVar, Union

from toytree import Node, ToyTree
from toytree.core.apis import add_toytree_method
from toytree.utils import ToytreeError

Query = TypeVar("Query", int, str, Node)


def _normalize_queries(queries):
    """Return queries as list-like for get_nodes unpacking."""
    if queries is None:
        return None
    if isinstance(queries, (str, int, Node)):
        return [queries]
    try:
        return list(queries)
    except TypeError:
        return [queries]


def _normalize_delim_idxs(delim_idxs):
    """Return delimiter index selector as a list of ints."""
    if delim_idxs is None:
        return None
    if isinstance(delim_idxs, int):
        return [delim_idxs]
    return [int(i) for i in delim_idxs]


@add_toytree_method(ToyTree)
def relabel(
    tree: ToyTree,
    queries: Union[Query, Sequence[Query], None] = None,
    fn: Callable[[str], str] | None = None,
    delim: str | None = None,
    delim_idxs: int | Sequence[int] | None = None,
    delim_join: str = "_",
    italic: bool = False,
    bold: bool = False,
    tips_only: bool = True,
    inplace: bool = False,
) -> ToyTree:
    """Relabel node ``name`` features for all or a subset of nodes.

    Parameters
    ----------
    queries: Query | Sequence[Query] | None
        Optional node selectors (idx, name, regex query, or Node). If
        None then all nodes are considered, and then optionally filtered
        by ``tips_only``.
    fn: Callable[[str], str] | None
        Optional callable transform applied to each selected name after
        delimiter processing.
    delim: str | None
        Optional delimiter used to split names before selecting parts.
    delim_idxs: int | Sequence[int] | None
        Optional index or indices to select from split parts. Missing
        indices are skipped.
    delim_join: str
        Join string used to combine selected split parts.
    italic: bool
        If True wrap each non-empty relabeled name in ``<i>...</i>``
        unless italic tags already exist in the name.
    bold: bool
        If True wrap each non-empty relabeled name in ``<b>...</b>``
        unless bold tags already exist in the name.
    tips_only: bool
        If True only tip node names are relabeled.
    inplace: bool
        If True mutate the input tree; otherwise return a modified copy.

    Notes
    -----
    Empty node names are skipped and left unchanged.
    """
    if fn is not None and not callable(fn):
        raise ToytreeError("fn must be callable or None.")

    tree = tree if inplace else tree.copy()

    norm_queries = _normalize_queries(queries)
    if norm_queries is None:
        nodes = list(tree[:tree.ntips] if tips_only else tree)
    else:
        nodes = tree.get_nodes(*norm_queries)
        if tips_only:
            nodes = [i for i in nodes if i.is_leaf()]

    idxs = _normalize_delim_idxs(delim_idxs)

    for node in nodes:
        if node.name == "":
            continue
        new_name = node.name

        if delim is not None:
            parts = new_name.split(delim)
            if idxs is None:
                selected = parts
            else:
                selected = []
                for idx in idxs:
                    if (-len(parts)) <= idx < len(parts):
                        selected.append(parts[idx])
            if selected:
                new_name = delim_join.join(selected)

        if fn is not None:
            new_name = fn(new_name)

        if new_name is not None:
            new_name = str(new_name)
            if new_name == "":
                continue
            if italic:
                has_italic = ("<i>" in new_name) and ("</i>" in new_name)
                if not has_italic:
                    new_name = f"<i>{new_name}</i>"
            if bold:
                has_bold = ("<b>" in new_name) and ("</b>" in new_name)
                if not has_bold:
                    new_name = f"<b>{new_name}</b>"
            node.name = new_name
    return tree
