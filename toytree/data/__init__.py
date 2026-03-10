#!/usr/bin/env python

"""Example datasets for testing and demonstration.

toytree.data.newick
toytree.data.newick_multitree
toytree.data.nexus
toytree.data.nexus_multitree
toytree.data.nhx
toytree.data.nhx_mb
toytree.data.nhx_beast
toytree.data.distance_matrix
toytree.data.sequence_alignment
"""

from __future__ import annotations

import importlib

__all__ = [
    "get_node_data",
    "set_node_data",
    "relabel",
    "expand_node_mapping",
]

_LAZY_ATTRS = {
    "get_node_data": ("toytree.data._src.get_node_data", "get_node_data"),
    "set_node_data": ("toytree.data._src.set_node_data", "set_node_data"),
    "relabel": ("toytree.data._src.relabel", "relabel"),
    "expand_node_mapping": (
        "toytree.data._src.expand_node_mapping",
        "expand_node_mapping",
    ),
}


def __getattr__(name: str):
    """Lazily import data helpers on first access."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Return module attributes plus lazily available public names."""
    return sorted(set(globals()) | set(__all__) | set(_LAZY_ATTRS))
