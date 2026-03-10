#!/usr/bin/env python

"""Parse tree data from strings, files, and URLs."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Mapping

from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core.multitree import MultiTree
    from toytree.core.tree import ToyTree

ILLEGAL_NEWICK_CHARS = re.compile(r"[:;(),\[\]\t\n\r=]")
WHITE_SPACE = re.compile(r"[\n\r\t ]+")


def _read_tree_path(path: Path) -> str:
    """Return tree text read from a filesystem path."""
    path = path.expanduser()
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ToytreeError(f"Tree file does not exist: '{path}'") from exc
    except OSError as exc:
        raise ToytreeError(f"Could not read tree file: '{path}'") from exc


def _warn_multiple_trees(count: int) -> None:
    """Print a user-facing warning when only the first tree is loaded."""
    msg = (
        f"Data contains ({count}) trees.\n"
        "Loading only the first tree using `toytree.tree`. Use `toytree.mtree` "
        "to instead load a MultiTree."
    )
    print(msg, file=sys.stderr)


def _parse_trees(data: str | Path | bytes, **kwargs) -> list[ToyTree]:
    """Return parsed trees with any NEXUS tip translation applied."""
    from toytree.io.src.newick import parse_newick_string

    strdata = parse_generic_to_str(data)
    nwks, tdict = parse_data_from_str(strdata)
    trees = [parse_newick_string(nwk, **kwargs) for nwk in nwks]
    return [translate_node_names(tree, tdict) for tree in trees]


def replace_whitespace(nwk: str, sub: str = "") -> str:
    r"""Replace intra-tree whitespace while preserving tree boundaries.

    Parameters
    ----------
    nwk : str
        Serialized Newick text that may contain embedded whitespace.
    sub : str, default=""
        Replacement text inserted for matched whitespace.

    Returns
    -------
    str
        Tree text with whitespace removed except for separators between
        distinct serialized trees.

    Examples
    --------
    >>> replace_whitespace("((a, b), c);\\n((a,c),b);")
    '((a,b),c);\\n((a,c),b);'

    See Also
    --------
    parse_data_from_str
    """
    pattern = r"(?<!;)\s"
    return re.sub(pattern, sub, nwk).strip()


def parse_generic_to_str(data: str | Path | bytes) -> str:
    """Return serialized tree text from a path, URL, string, or bytes.

    Parameters
    ----------
    data : str, Path, or bytes
        Tree input provided as serialized text, a local file path, a
        public HTTP(S) URL, or UTF-8 encoded bytes.

    Returns
    -------
    str
        Serialized tree text ready for Newick or NEXUS parsing.

    Raises
    ------
    ToytreeError
        Raised if the input is empty, unreadable, cannot be decoded, or
        is not recognized as tree text, a path, or an HTTP(S) URL.

    Examples
    --------
    >>> parse_generic_to_str("((a,b),c);")
    '((a,b),c);'

    See Also
    --------
    parse_tree
    parse_multitree
    """
    if isinstance(data, Path):
        return _read_tree_path(data)

    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ToytreeError("Tree bytes input must be valid UTF-8.") from exc
        return parse_generic_to_str(data)

    if isinstance(data, str):
        data = data.strip()
        if not data:
            raise ToytreeError("Cannot parse empty input for toytree.tree().")

        if data.startswith(("http://", "https://")):
            try:
                import requests
            except ImportError as exc:
                raise ToytreeError(
                    "The `requests` package is required to load tree data from URLs."
                ) from exc

            try:
                response = requests.get(data, timeout=30)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise ToytreeError(
                    f"Could not read tree data from URL: '{data}'"
                ) from exc
            return response.text

        if data[0] in ("(", "#") or data.endswith(";"):
            return data

        path = Path(data).expanduser()
        if path.exists():
            return _read_tree_path(path)

        raise ToytreeError(
            "String tree input must be Newick/NEXUS text, an existing file path, "
            f"or an http(s) URL: '{data}'"
        )

    raise ToytreeError(f"Cannot parse unrecognized tree data input: {data!r}")


def parse_data_from_str(strdata: str) -> tuple[list[str], Mapping[str, str]]:
    """Return serialized Newick strings and any NEXUS translation table.

    Parameters
    ----------
    strdata : str
        Serialized tree text already loaded into memory.

    Returns
    -------
    tuple[list[str], Mapping[str, str]]
        A list of Newick strings and a translation mapping extracted
        from NEXUS input when present.

    Raises
    ------
    ToytreeError
        Raised if no trees are found in the serialized input.

    Examples
    --------
    >>> parse_data_from_str("((a,b),c);")[0]
    ['((a,b),c);']

    See Also
    --------
    parse_generic_to_str
    translate_node_names
    """
    if not strdata.strip():
        raise ToytreeError("No trees were found in the input data.")

    if strdata[:6].upper() == "#NEXUS":
        from toytree.io.src.nexus import get_newicks_and_translation_from_nexus

        nwks, tdict = get_newicks_and_translation_from_nexus(strdata)
    else:
        if not any(char in strdata for char in "\n\r\t "):
            nwks = [strdata]
        else:
            strdata = replace_whitespace(strdata)
            nwks = [item for item in strdata.split("\n") if item]
        tdict = {}

    if not nwks:
        raise ToytreeError("No trees were found in the input data.")
    return nwks, tdict


def translate_node_names(tree: ToyTree, tdict: Mapping[str, str]) -> ToyTree:
    """Translate NEXUS tip labels using a translation dictionary.

    Parameters
    ----------
    tree : ToyTree
        Parsed tree whose tip labels may require translation.
    tdict : Mapping[str, str]
        NEXUS translation mapping from serialized tip tokens to labels.

    Returns
    -------
    ToyTree
        The same tree object with translated tip labels applied.

    Raises
    ------
    ToytreeError
        Raised if a NEXUS translation table is present but a numeric tip
        token is missing from the table.

    Examples
    --------
    >>> tree = parse_tree("((a,b),c);")
    >>> translate_node_names(tree, {}).get_tip_labels()
    ['a', 'b', 'c']

    See Also
    --------
    parse_tree
    parse_data_from_str
    """
    if not tdict:
        return tree

    for idx in range(tree.ntips):
        node = tree[idx]
        if not node.name:
            continue
        label = str(node.name)
        if label in tdict:
            node.name = ILLEGAL_NEWICK_CHARS.sub("_", tdict[label])
        elif label.isdigit():
            raise ToytreeError(
                f"NEXUS translate block is missing a tip label for token '{label}'."
            )
    return tree


def parse_tree(data: str | Path | bytes, **kwargs) -> ToyTree:
    """Return one `ToyTree` parsed from flexible input types.

    Parameters
    ----------
    data : str, Path, or bytes
        Tree input provided as serialized Newick/NEXUS text, a local
        file path, a public HTTP(S) URL, or UTF-8 encoded bytes.
    **kwargs
        Additional keyword arguments forwarded to
        :func:`toytree.io.parse_newick_string`.

    Returns
    -------
    ToyTree
        The parsed tree. If multiple trees are present, only the first
        tree is returned and a warning is printed to stderr.

    Raises
    ------
    ToytreeError
        Raised if the input cannot be read or does not contain any
        trees.

    Examples
    --------
    >>> parse_tree("((a,b),c);").ntips
    3

    See Also
    --------
    parse_multitree
    parse_tree_object
    toytree.tree
    """
    trees = _parse_trees(data, **kwargs)
    if len(trees) > 1:
        _warn_multiple_trees(len(trees))
    return trees[0]


def parse_multitree(data: str | Path | bytes, **kwargs) -> MultiTree:
    r"""Return a `MultiTree` parsed from flexible input types.

    Parameters
    ----------
    data : str, Path, or bytes
        Tree input provided as serialized Newick/NEXUS text, a local
        file path, a public HTTP(S) URL, or UTF-8 encoded bytes.
    **kwargs
        Additional keyword arguments forwarded to
        :func:`toytree.io.parse_newick_string`.

    Returns
    -------
    MultiTree
        Parsed multitree object containing every tree found in the
        input data.

    Raises
    ------
    ToytreeError
        Raised if the input cannot be read or does not contain any
        trees.

    Examples
    --------
    >>> parse_multitree("((a,b),c);\\n((a,c),b);").ntrees
    2

    See Also
    --------
    parse_tree
    parse_tree_object
    toytree.mtree
    """
    from toytree.core.multitree import MultiTree

    return MultiTree(_parse_trees(data, **kwargs))


def parse_tree_object(data: str | Path | bytes, **kwargs) -> ToyTree | MultiTree:
    r"""Return a `ToyTree` or `MultiTree` parsed from flexible input.

    Parameters
    ----------
    data : str, Path, or bytes
        Tree input provided as serialized Newick/NEXUS text, a local
        file path, a public HTTP(S) URL, or UTF-8 encoded bytes.
    **kwargs
        Additional keyword arguments forwarded to
        :func:`toytree.io.parse_newick_string`.

    Returns
    -------
    ToyTree or MultiTree
        A `ToyTree` when the input contains one tree, otherwise a
        `MultiTree`.

    Raises
    ------
    ToytreeError
        Raised if the input cannot be read or does not contain any
        trees.

    Examples
    --------
    >>> type(parse_tree_object("((a,b),c);")).__name__
    'ToyTree'
    >>> type(parse_tree_object("((a,b),c);\\n((a,c),b);")).__name__
    'MultiTree'

    See Also
    --------
    parse_tree
    parse_multitree
    toytree.tree
    toytree.mtree
    """
    trees = _parse_trees(data, **kwargs)
    if len(trees) == 1:
        return trees[0]

    from toytree.core.multitree import MultiTree

    return MultiTree(trees)
