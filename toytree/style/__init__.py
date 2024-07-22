#!/usr/bin/env python

"""..."""

from toytree.style.src.style_base import TreeStyle, SubStyle
from toytree.style.src.style_types import get_base_tree_style_by_name
from toytree.style.src.map_colors import (
    get_color_mapped_feature, get_color_mapped_values)
from toytree.style.src.map_values import (
    get_range_mapped_feature, get_range_mapped_values)
from toytree.style.src.validate_style import validate_style
from toytree.style.src.validate_utils import (
    tree_style_to_css_dict, substyle_dict_to_css_dict, check_arr)

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

if __name__ == "__main__":

    import toytree
    tre = toytree.rtree.unittree(5)
    sty = tre.style

    sty.node_colors = ["red"] * tre.nnodes
    sty.tip_labels_colors = toytree.color.COLORS1[0]
    sty.node_markers = "o"

    # validate_style(tre, sty)
    print(sty)
