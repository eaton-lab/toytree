#!/usr/bin/env python

"""Data sets and data conversion functions."""

from __future__ import annotations

import importlib

__all__ = [
    "get_node_data",
    "get_tip_data",
    "get_color_mapped_feature",
    "get_color_mapped_values",
    "get_range_mapped_feature",
    "get_range_mapped_values",
    "set_node_data",
    "set_node_data_from_dataframe",
    "relabel",
]

_LAZY_ATTRS = {
    "get_node_data": ("toytree.data._src.get_node_data", "get_node_data"),
    "get_tip_data": ("toytree.data._src.get_node_data", "get_tip_data"),
    "get_color_mapped_feature": (
        "toytree.data._src.map_colors",
        "get_color_mapped_feature",
    ),
    "get_color_mapped_values": (
        "toytree.data._src.map_colors",
        "get_color_mapped_values",
    ),
    "get_range_mapped_feature": (
        "toytree.data._src.map_values",
        "get_range_mapped_feature",
    ),
    "get_range_mapped_values": (
        "toytree.data._src.map_values",
        "get_range_mapped_values",
    ),
    "set_node_data": ("toytree.data._src.set_node_data", "set_node_data"),
    "set_node_data_from_dataframe": (
        "toytree.data._src.set_node_data",
        "set_node_data_from_dataframe",
    ),
    "relabel": ("toytree.data._src.relabel", "relabel"),
}


def __getattr__(name: str):
    """Lazily import non-essential data methods on first access."""
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
