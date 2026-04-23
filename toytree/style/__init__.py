#!/usr/bin/env python

"""Deprecated compatibility shim for the old ``toytree.style`` namespace."""

from __future__ import annotations

import importlib
import sys

__all__ = [
    "TreeStyle",
    "SubStyle",
    "get_base_tree_style_by_name",
    "get_color_mapped_feature",
    "get_color_mapped_values",
    "get_range_mapped_feature",
    "get_range_mapped_values",
    "validate_style",
    "tree_style_to_css_dict",
    "substyle_dict_to_css_dict",
    "check_arr",
]

_DEPRECATED_ATTRS = {
    "TreeStyle": ("toytree.core", "TreeStyle", "toytree.core.TreeStyle"),
    "SubStyle": ("toytree.core", "SubStyle", "toytree.core.SubStyle"),
    "get_base_tree_style_by_name": (
        "toytree.core",
        "get_base_tree_style_by_name",
        "toytree.core.get_base_tree_style_by_name",
    ),
    "get_color_mapped_feature": (
        "toytree.data",
        "get_color_mapped_feature",
        "toytree.data.get_color_mapped_feature",
    ),
    "get_color_mapped_values": (
        "toytree.data",
        "get_color_mapped_values",
        "toytree.data.get_color_mapped_values",
    ),
    "get_range_mapped_feature": (
        "toytree.data",
        "get_range_mapped_feature",
        "toytree.data.get_range_mapped_feature",
    ),
    "get_range_mapped_values": (
        "toytree.data",
        "get_range_mapped_values",
        "toytree.data.get_range_mapped_values",
    ),
    "validate_style": (
        "toytree.drawing.src.validate_style",
        "validate_style",
        "toytree.drawing.src.validate_style.validate_style",
    ),
    "tree_style_to_css_dict": (
        "toytree.drawing.src.validate_utils",
        "tree_style_to_css_dict",
        "toytree.drawing.src.validate_utils.tree_style_to_css_dict",
    ),
    "substyle_dict_to_css_dict": (
        "toytree.drawing.src.validate_utils",
        "substyle_dict_to_css_dict",
        "toytree.drawing.src.validate_utils.substyle_dict_to_css_dict",
    ),
    "check_arr": (
        "toytree.drawing.src.validate_utils",
        "check_arr",
        "toytree.drawing.src.validate_utils.check_arr",
    ),
}

_WARNED = False


def _warn_once() -> None:
    """Emit one deprecation message for the old style namespace."""
    global _WARNED
    if _WARNED:
        return
    print(
        "`toytree.style` is deprecated and will be removed in a future release. "
        "Use `toytree.data`, `toytree.core`, or `toytree.drawing.src` instead.",
        file=sys.stderr,
    )
    _WARNED = True


def __getattr__(name: str):
    """Lazily redirect deprecated public names to their new homes."""
    if name not in _DEPRECATED_ATTRS:
        raise AttributeError(name)
    _warn_once()
    module_name, attr_name, _ = _DEPRECATED_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Return module attributes plus deprecated public compatibility names."""
    return sorted(set(globals()) | set(__all__) | set(_DEPRECATED_ATTRS))
