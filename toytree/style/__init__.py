#!/usr/bin/env python

"""..."""

from toytree.style.src.tree_style_base import TreeStyle
from toytree.style.src.sub_styles import SubStyle
from toytree.style.src.tree_styles import get_base_tree_style_by_name
from toytree.style.src.validator import validate_style

if __name__ == "__main__":

    import toytree
    tre = toytree.rtree.unittree(5)
    sty = tre.style

    sty.node_colors = ["red"] * tre.nnodes
    sty.tip_labels_colors = toytree.color.COLORS1[0]
    sty.node_markers = "o"

    validate_style(tre, sty)    
    print(sty)
