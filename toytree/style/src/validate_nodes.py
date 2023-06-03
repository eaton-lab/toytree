#!/usr/bin/env python

"""Testing simple alternative validation

Problem
-------
[x] function calls from Tree
[x] default/object style from Tree
[x] Annotate module only has nnodes, etc.
[ ] communicate node_colors(single) -> node_style['fill']
[ ] all substyles as dicts w/ keys converted to css style: (fill-opacity, -toyplot-anchor-shift)
"""

from typing import Union, Dict, TypeVar
import numpy as np
from toytree.color import ToyColor

from toytree.style.src.style_base import NodeStyle

ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "validate_node_style",
]


def validate_node_style(
    tree: ToyTree,
    style: NodeStyle = None,
    **kwargs,
) -> Union[NodeStyle, Dict]:
    """Ensure tip labels are in px sizes and fill color as ToyColor.

    Parameters
    ----------
    style: NodeStyle or None
        A NodeStyle object if validating a ToyTree, else None to get a
        default NodeStyle for validating an annotation.
    **kwargs:
        Any arguments accepted by node_style.
    """
    if not isinstance(style, NodeStyle):
        style = NodeStyle()

    # ToyTree drawing validation modifies values in NodeStyle dict.
    # update default style with user style args
    for key, val in kwargs.items():
        style[key] = val

    # convert stroke to ToyColor
    style.stroke = ToyColor(style.stroke)

    # convert fill to ToyColor
    style.fill = ToyColor(style.fill)

    # require opacity settings even though they are None by default
    if style.stroke_opacity is None:
        style.stroke_opacity = 1.0
    if style.fill_opacity is None:
        style.fill_opacity = 1.0

    # return as a NodeStyle object
    return style


if __name__ == "__main__":

    import toytree

    tree = toytree.rtree.unittree(10, seed=123)
