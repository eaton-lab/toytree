#!/usr/bin/env python

"""...

"""

from typing import TypeVar
import numpy as np
import toyplot
# from toytree.utils import ToytreeError
from toytree.color import ToyColor
from toytree.style.src.style_base import NodeLabelStyle, TreeStyle


ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "validate_node_labels_style",
]


def validate_node_labels_style(
    tree: ToyTree,
    style: NodeLabelStyle = None,
    **kwargs,
) -> TreeStyle:
    """Ensure tip labels are in px sizes and fill color as ToyColor.

    Parameters
    ----------
    base: TreeStyle or None
        A base tree style to modify. If None then new NodeLabelStyle is used.
    style: Mapping
        A dict of style changes.
    copy: bool
        If False the base is copied and modified, else modified directly.
    """
    if not isinstance(style, NodeLabelStyle):
        style = NodeLabelStyle()

    # update default style with user style args
    for key, val in kwargs.items():
        style[key] = val

    # ensure font-size is in px units
    size = toyplot.units.convert(value=style.font_size, target="px", default="px")
    style.font_size = f"{size:.12g}px"

    # convert fill to a ToyColor
    style.fill = ToyColor(style.fill)
    if style.fill_opacity is None:
        style.fill_opacity = 1.0
    return style


if __name__ == "__main__":

    import toytree

    tree = toytree.rtree.unittree(5)
    style = tree.style.copy()

    print(style.node_labels_style)
    s = validate_node_labels_style(tree, style.node_labels_style, {"-toyplot-anchor-shift": 10}, copy=True)

    print(s)
