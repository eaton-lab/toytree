#!/usr/bin/env python

"""Testing simple alternative validation

"""

from typing import Any, Dict, TypeVar
import numpy as np

from toytree.color import ToyColor
from toytree.style.src.style_base import TreeStyle, EdgeStyle, EdgeAlignStyle

ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "validate_edge_style",
    "validate_edge_align_style",
]


# STILL USED!
def validate_edge_style(
    tree: ToyTree,
    style: TreeStyle = None,
    **kwargs,
) -> Dict[str, Any]:
    """Return Dict with css style keys and ensure fill and stroke values.

    Parameters
    ----------
    base: TreeStyle or None
        A base tree style to modify. If None then new NodeLabelStyle is used.
    style: Mapping
        A dict of style changes.
    """
    # get user value or style base value
    if style is None:
        style = EdgeStyle()

    # update default style with user style args
    for key, val in kwargs.items():
        style[key] = val

    # convert stroke to ToyColor
    style.stroke = ToyColor(style.stroke)

    # optionally convert fill and stroke to css string: ??
    # "fill:{rgb};fill-opacity:{o};stroke:{rgb};stroke-opacity:{o}"
    # if serialize:
    #     style['stroke'] = style['stroke'].css
    #     if not style.get("stroke-opacity"):
    #         style['stroke-opacity'] = 1.0
    return style


# STILL USED!
def validate_edge_align_style(
    tree: ToyTree,
    style: TreeStyle = None,
    **kwargs,
) -> Dict[str, Any]:
    """Return Dict with css style keys and ensure fill and stroke values.

    Parameters
    ----------
    base: TreeStyle or None
        A base tree style to modify. If None then new NodeLabelStyle is used.
    style: Mapping
        A dict of style changes.
    """
    # get user value or style base value
    if style is None:
        style = EdgeAlignStyle()

    # update default style with user style args
    for key, val in kwargs.items():
        style[key] = val

    # convert stroke to ToyColor
    style.stroke = ToyColor(style.stroke)

    # check dasharray type
    assert isinstance(style.stroke_dasharray, str), (
        "edge_align_style 'stroke-dasharray' value must be a str "
        "e.g., '2,2'")

    # optionally convert fill and stroke to css string: ??
    # "fill:{rgb};fill-opacity:{o};stroke:{rgb};stroke-opacity:{o}"
    # if serialize:
    #     style['stroke'] = style['stroke'].css
    #     if not style.get("stroke-opacity"):
    #         style['stroke-opacity'] = 1.0
    return style


if __name__ == "__main__":

    pass
