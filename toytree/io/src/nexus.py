#!/usr/bin/env python

"""Extract serialized trees and translation tables from NEXUS text."""

from __future__ import annotations

import re
from collections.abc import Iterator

__all__ = ["get_newicks_and_translation_from_nexus"]

_TREES_BLOCK = re.compile(
    r"(?<=begin trees;).*?(?=end;)",
    flags=re.IGNORECASE | re.DOTALL,
)
_TRANSLATE_BLOCK = re.compile(r"translate\s*([\s\S]*?);", flags=re.IGNORECASE)
_TREE_RECORD = re.compile(r"\s*TREE\s", flags=re.IGNORECASE)


def _extract_trees_block(data: str) -> str:
    """Return the first `begin trees; ... end;` block from NEXUS text."""
    match = _TREES_BLOCK.search(data)
    if not match:
        raise IOError("NEXUS file must contain a 'begin trees' block.")
    return match.group(0).strip()


def _extract_translate_map(trees_block: str) -> dict[str, str]:
    """Return the optional translation table from a NEXUS trees block."""
    match = _TRANSLATE_BLOCK.search(trees_block)
    if not match:
        return {}

    translated: dict[str, str] = {}
    for raw_line in match.group(1).strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        label, value = line.split(None, 1)
        translated[label] = _unquote_nexus_label(value.rstrip(",").strip())
    return translated


def _iter_newick_strings(trees_block: str) -> Iterator[str]:
    """Yield serialized Newick strings from a NEXUS trees block."""
    iter_lines = iter(trees_block.splitlines())
    for line in iter_lines:
        if not _TREE_RECORD.match(line):
            continue

        tree_lines = [line.strip()]
        while not line.strip().endswith(";"):
            line = next(iter_lines)
            tree_lines.append(line.strip())

        tree_record = "".join(tree_lines)
        _, data_parts = tree_record.split("=", 1)
        start = data_parts.find("(")
        yield data_parts[start:]


def _unquote_nexus_label(value: str) -> str:
    """Return one NEXUS translate label with quotes unescaped."""
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def get_newicks_and_translation_from_nexus(
    data: str,
) -> tuple[list[str], dict[str, str]]:
    r"""Return serialized Newick strings and translation labels from NEXUS text.

    Parameters
    ----------
    data : str
        Serialized NEXUS text containing a `begin trees;` block.

    Returns
    -------
    tuple[list[str], dict[str, str]]
        A list of serialized Newick strings and a translation mapping
        from tip tokens to labels when a `translate` block is present.

    Raises
    ------
    IOError
        Raised if the NEXUS text does not contain a `begin trees;`
        block.

    Examples
    --------
    >>> text = "#NEXUS\\nbegin trees;\\n tree t0 = ((1,2),3);\\nend;"
    >>> get_newicks_and_translation_from_nexus(text)[0]
    ['((1,2),3);']

    See Also
    --------
    toytree.io.src.parse.parse_data_from_str
    toytree.tree
    """
    trees_block = _extract_trees_block(data)
    return list(_iter_newick_strings(trees_block)), _extract_translate_map(trees_block)
