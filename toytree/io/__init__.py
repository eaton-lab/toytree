#!/usr/bin/env python

"""toytree I/O data parsing utilities."""

from __future__ import annotations

import importlib

__all__ = [
    "parse_newick_string",
    "parse_newick_string_custom",
    "tree",
    "mtree",
    "write",
]

_LAZY_ATTRS = {
    "parse_newick_string": ("toytree.io.src.newick", "parse_newick_string"),
    "parse_newick_string_custom": (
        "toytree.io.src.newick",
        "parse_newick_string_custom",
    ),
    "tree": ("toytree.io.src.treeio", "tree"),
    "mtree": ("toytree.io.src.mtreeio", "mtree"),
    "write": ("toytree.io.src.writer", "write"),
}


def __getattr__(name: str):
    """Lazily import I/O helpers on first access."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Return module attributes plus lazily available public names."""
    return sorted(set(globals()) | set(_LAZY_ATTRS))
