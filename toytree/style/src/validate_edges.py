#!/usr/bin/env python

"""Testing simple alternative validation

"""

from typing import Union, Sequence, Mapping, Any, Dict, TypeVar, Tuple
import numpy as np

from toytree.color import ToyColor
from toytree.utils import ToytreeError
from toytree.style import get_range_mapped_feature, get_color_mapped_feature
from toytree.style.src.validate_utils import check_arr
from toytree.style.src.style_base import TreeStyle, EdgeStyle, EdgeAlignStyle

ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "validate_edge_colors",
    "validate_edge_widths",
    "validate_edge_style",
    "validate_edge_align_style",
]


def validate_edge_colors(
    tree: ToyTree,
    style: TreeStyle,
    **kwargs,
    # serialize: bool = False,
) -> Tuple[Union[np.ndarray, None], Union[Color, None]]:
    """Set edge_colors to type=ndarray size=nnodes or None.

    If only one color was entered then store as style.fill.
    Only expand .edge_colors into an array of size nnodes if there
    is variation among nodes.

    colors: Union[None, Color, Sequence[Color], Tuple],

    Args
    ----
    None: None. will use edge_style.fill
    str: set all as ToyColor(str)
    ndarray dtype: set all as ToyColor(ndarray)
    tuple w/ len > 2:
    tuple w/ len == 2:
    colormap: not supported. Use (feature, colormap)
    """
    # get user value or style base value
    colors = kwargs.get("edge_colors")
    if colors is None:
        colors = getattr(style, "edge_colors")

    # if None then Nodes will be colored by style.fill during render
    if colors is None:
        return None, None

    # special (feature, cmap):
    if isinstance(colors, tuple) and isinstance(colors[0], str):
        feat, *args = colors
        return get_color_mapped_feature(tree, feat, *args), None

    # get user entered value as ToyColor or List[ndarray]
    # e.g., str, tuple, or ndarray[r,g,b,a] -> ToyColor
    # e.g., List[str], pd.Series[ToyColor], ndarray[void] -> List[ToyColor]
    colors = ToyColor.color_expander(colors)

    # if single color return None. The node_style validator will recognize
    # None and check orig node_color arg to override node_style.fill.
    if isinstance(colors, ToyColor):
        return None, colors

    # convert the List[ToyColor] to an ndarray of dtype np.void
    colors = check_arr(values=colors, label="edge_colors", size=tree.nnodes, ctype=np.void)

    # # serialize is optionally used...
    # if serialize:
    #     return list(colors)
    return colors, None


def validate_edge_widths(
    tree: ToyTree,
    style: TreeStyle,
    **kwargs,
) -> np.ndarray:
    """Sets node_sizes to ndarray[float].

    sizes: Union[float, Sequence[float], Tuple],

    None: return None. Uses stroke-width value of style.
    int: sizes all set to same.
    Sequence[int] = sizes in Node idx order.
    tuple[str, Tuple] = sizes mapped to range by feature value
    """
    sizes = kwargs.get("edge_widths")
    if sizes is None:
        sizes = getattr(style, "edge_widths")

    if sizes is None:
        return None
    if isinstance(sizes, (int, float)):
        sizes = np.repeat(sizes, tree.nnodes)
    elif isinstance(sizes, tuple) and isinstance(sizes[0], str):
        feature, *args = sizes
        # defaults selected for edge widths
        kwargs = dict(zip(("min_value", "max_value", "nan_value"), args))
        kwargs["min_value"] = kwargs.get("min_value", 1.5)
        kwargs["max_value"] = kwargs.get("max_value", 5.0)
        kwargs["nan_value"] = kwargs.get("nan_value", 1.)
        return get_range_mapped_feature(tree, feature, **kwargs)

    # validate and return as ndarray
    return check_arr(sizes, "edge_widths", tree.nnodes, (int, float, np.integer))


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
