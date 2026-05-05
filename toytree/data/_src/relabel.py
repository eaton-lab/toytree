#!/usr/bin/env python

"""Method to relabel node name features on a ToyTree."""

from __future__ import annotations

import re
import sys
from collections.abc import Mapping as MappingABC
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, TypeVar, Union

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


def _load_imap_file(path: str | Path) -> dict[str, str]:
    """Load whitespace-delimited tip-name mappings from file."""
    path = Path(path).expanduser()
    mapping: dict[str, str] = {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            for lnum, line in enumerate(handle, start=1):
                stripped = line.strip()
                if (not stripped) or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 2:
                    raise ToytreeError(
                        "imap file must have at least two whitespace-delimited "
                        f"columns on line {lnum}."
                    )
                mapping[parts[0]] = parts[1]
    except OSError as exc:
        raise ToytreeError(f"could not read imap file '{path}': {exc}") from exc
    if not mapping:
        raise ToytreeError("imap file did not contain any usable selector/name rows.")
    return mapping


def _coerce_imap_mapping(
    imap: Mapping[str, Any] | str | Path | None,
) -> dict[str, Any]:
    """Return imap as a selector->replacement mapping."""
    if imap is None:
        return {}
    if isinstance(imap, MappingABC):
        raw = dict(imap)
    elif isinstance(imap, (str, Path)):
        raw = _load_imap_file(imap)
    else:
        raise ToytreeError("imap must be a mapping, file path string, Path, or None.")

    mapping: dict[str, Any] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise ToytreeError("imap selectors must be strings.")
        mapping[key] = value
    return mapping


def _match_tip_selector(tree: ToyTree, selector: str) -> list[Node]:
    """Return tip Nodes matched by one exact-name or regex selector."""
    nodes = list(tree[: tree.ntips])
    if selector.startswith("~"):
        try:
            regex = re.compile(selector[1:])
        except re.error as exc:
            msg = f"invalid regex query '{selector}' raised re.error:\n{exc}"
            raise ToytreeError(msg) from exc
        return [node for node in nodes if regex.search(node.name)]
    return [node for node in nodes if node.name == selector]


def _resolve_tip_imap(
    tree: ToyTree,
    imap: Mapping[str, Any] | str | Path | None,
) -> dict[Node, Any]:
    """Resolve imap selectors to uniquely matched tip Nodes."""
    mapping = _coerce_imap_mapping(imap)
    resolved: dict[Node, Any] = {}
    selectors: dict[Node, str] = {}
    for selector, value in mapping.items():
        matches = _match_tip_selector(tree, selector)
        if not matches:
            print(
                f"WARNING: imap selector '{selector}' did not match any tip names.",
                file=sys.stderr,
            )
            continue
        if len(matches) > 1:
            names = ", ".join(node.name for node in matches)
            raise ToytreeError(
                f"imap selector '{selector}' matched multiple tips: {names}."
            )
        node = matches[0]
        if node in resolved:
            raise ToytreeError(
                "imap selectors "
                f"'{selectors[node]}' and '{selector}' both matched tip '{node.name}'."
            )
        resolved[node] = value
        selectors[node] = selector
    return resolved


@add_toytree_method(ToyTree)
def relabel(
    tree: ToyTree,
    queries: Union[Query, Sequence[Query], None] = None,
    fn: Callable[[str], str] | None = None,
    imap: Mapping[str, Any] | str | Path | None = None,
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
    imap: Mapping[str, Any] | str | Path | None
        Optional tip-name remapping entered as a selector->replacement
        mapping or as a whitespace-delimited file path. Selectors target
        current tip names only, and strings prefixed with ``~`` are
        treated as regex queries that must still match exactly one tip.
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
    Empty node names are skipped and left unchanged. When ``imap`` is
    provided its replacements are resolved against current tip names
    before any transforms, then applied afterward as the final override
    on those matched tips.
    """
    if fn is not None and not callable(fn):
        raise ToytreeError("fn must be callable or None.")

    tree = tree if inplace else tree.copy()
    resolved_imap = _resolve_tip_imap(tree, imap)

    norm_queries = _normalize_queries(queries)
    if norm_queries is None:
        nodes = list(tree[: tree.ntips] if tips_only else tree)
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

    for node, new_name in resolved_imap.items():
        if new_name is None:
            continue
        new_name = str(new_name)
        if new_name == "":
            continue
        node.name = new_name
    return tree
