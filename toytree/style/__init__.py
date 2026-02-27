#!/usr/bin/env python

"""..."""

from __future__ import annotations

import importlib

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

_LAZY_ATTRS = {
    "TreeStyle": ("toytree.style.src.style_base", "TreeStyle"),
    "SubStyle": ("toytree.style.src.style_base", "SubStyle"),
    "get_base_tree_style_by_name": (
        "toytree.style.src.style_types",
        "get_base_tree_style_by_name",
    ),
    "get_color_mapped_feature": (
        "toytree.style.src.map_colors",
        "get_color_mapped_feature",
    ),
    "get_color_mapped_values": (
        "toytree.style.src.map_colors",
        "get_color_mapped_values",
    ),
    "get_range_mapped_feature": (
        "toytree.style.src.map_values",
        "get_range_mapped_feature",
    ),
    "get_range_mapped_values": (
        "toytree.style.src.map_values",
        "get_range_mapped_values",
    ),
    "validate_style": ("toytree.style.src.validate_style", "validate_style"),
    "tree_style_to_css_dict": (
        "toytree.style.src.validate_utils",
        "tree_style_to_css_dict",
    ),
    "substyle_dict_to_css_dict": (
        "toytree.style.src.validate_utils",
        "substyle_dict_to_css_dict",
    ),
    "check_arr": ("toytree.style.src.validate_utils", "check_arr"),
}


def __getattr__(name: str):
    """Lazily import style helpers to avoid importing toyplot at startup."""
    if name not in _LAZY_ATTRS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_ATTRS[name]
    module = importlib.import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


if __name__ == "__main__":
    import toytree

    tre = toytree.rtree.unittree(5)
    sty = tre.style

    sty.node_colors = ["red"] * tre.nnodes
    sty.tip_labels_colors = toytree.color.COLORS1[0]
    sty.node_markers = "o"

    # validate_style(tre, sty)
    print(sty)
