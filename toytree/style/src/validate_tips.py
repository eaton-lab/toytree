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

from typing import Union, Sequence, Mapping, Any, Dict, TypeVar
import numpy as np
from loguru import logger
import toyplot
from toytree.color import ToyColor
from toytree.utils import ToytreeError
from toytree.style.src.validate_utils import check_arr
from toytree.style.src.style_base import TipLabelStyle, TreeStyle
from toytree.style.src.map_colors import get_color_mapped_values

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "validate_tip_labels",
    "validate_tip_labels_colors",
    "validate_tip_labels_angles",
    "validate_tip_labels_style",
]


def validate_tip_labels(
    tree: ToyTree,
    style: TreeStyle,
    **kwargs,
) -> Union[None, np.ndarray]:
    """Sets tip_labels to np.ndarray[str] or None.

    Also applies floating point string formatting on tip_labels. If
    set to None then no labels are added during rendering.

    tip_labels: Union[None, bool, str, Sequence[str]],

    Args
    ----
    None: None
    False: None
    True: 'idx' int labels
    str: extract feature
    Series[Any: custom collection of the proper size.
    """
    # get user value or style base value
    tip_labels = kwargs.get("tip_labels")
    if tip_labels is None:
        tip_labels = getattr(style, "tip_labels")

    # Don't use 'is in' to support pd.Series
    if tip_labels is False:
        return None
    if tip_labels is None:
        return None
    if tip_labels is True:
        return tree.get_tip_labels()

    # str: extract feature as labels as an np.array
    if isinstance(tip_labels, str):
        tip_labels = tree.get_tip_data(tip_labels).values

    # or, user entered a list, tuple, Series, array, etc.
    # which is checked and handled below.

    # float format numeric values, and convert to strings
    tip_labels = [str(i) for i in tip_labels]
    return check_arr(tip_labels, "tip_labels", tree.ntips, str)


def validate_tip_labels_colors(
    tree: ToyTree,
    style: TreeStyle,
    **kwargs,
) -> Union[np.ndarray, None]:
    """Return ndarray of tip_colors or None.

    If only one color was entered then return None and the
    tip_labels_style dict will instead set the color as 'fill'.

    colors: Union[None, Color, Sequence[Color], tuple[str, str]],

    Args
    ----
    None: None. Node color will use node_style.fill
    str: set all as ToyColor(str)
    ndarray dtype: set all as ToyColor(ndarray)
    tuple
    colormap: not supported. Use (feature, colormap)
    """
    # get user value or style base value
    colors = kwargs.get("tip_labels_colors")
    if colors is None:
        if isinstance(style, TreeStyle):
            colors = getattr(style, "tip_labels_colors")

    # if None then Nodes will be colored by style.fill during render
    if colors is None:
        return None, None

    # if None then Nodes will be colored by style.fill during render
    if colors is None:
        return None, None

    # special (feature, cmap), but not single color as tuple (0, 0, 1, 1).
    if isinstance(colors, tuple) and isinstance(colors[0], str):
        feat, *args = colors
        values = tree.get_tip_data(feat).values
        return get_color_mapped_values(values, *args), None

    # get user entered value as ToyColor or List[ndarray]
    # e.g., str, tuple, or ndarray[r,g,b,a] -> ToyColor
    # e.g., List[str], pd.Series[ToyColor], ndarray[void] -> List[ToyColor]
    colors = ToyColor.color_expander(colors)

    # if single color return None. The node_style validator will recognize
    # None and check orig node_color arg to override node_style.fill.
    if isinstance(colors, ToyColor):
        return None, colors

    # convert the List[ToyColor] to an ndarray of dtype np.void
    colors = check_arr(
        values=colors,
        label="tip_labels_colors",
        size=tree.ntips,
        ctype=np.void,
    )

    # serialize is optionally used...
    # if serialize:
    #     return list(tip_labels_colors)
    return colors, None


# def validate_tip_labels_font_sizes(
#     tree: ToyTree,
#     sizes: Union[float, Sequence[float]],
# ) -> np.ndarray:
#     """Sets node_sizes to ndarray[float]."""
#     if sizes is None:
#         sizes = 0
#     if isinstance(sizes, (int, float)):
#         sizes = np.repeat(sizes, tree.ntips)
#     sizes = check_arr(
#         sizes, "tip_labels_font_sizes", tree.ntips, (int, float, np.integer))
#     return sizes


def validate_tip_labels_angles(
    tree: ToyTree,
    style: TreeStyle,
    **kwargs,
) -> np.ndarray:
    """Return array with tip label angles given the layout, or user setting.
    """
    # get user value or style base value
    angles = kwargs.get("tip_labels_angles")
    if angles is None:
        angles = getattr(style, "tip_labels_angles")

    # get user value or style base value
    layout = kwargs.get("layout")
    if not layout:
        layout = getattr(style, "layout")

    # calculate propor angles from the layout
    if angles is None:
        if layout in ("u", "d"):  ################## also support kwargs layout
            angles = np.repeat(-90, tree.ntips)
        else:
            angles = np.zeros(tree.ntips)
    elif isinstance(angles, (float, int, np.integer)):
        angles = np.repeat(angles, tree.ntips)

    angles = check_arr(angles, "tip_labels_angles", tree.ntips, (int, float, np.integer))
    return angles


def validate_tip_labels_style(
    tree: ToyTree,
    style: TreeStyle = None,
    **kwargs,
) -> Dict[str, Any]:
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
    # annotation funcs use builtin base
    if style is None:
        style = TipLabelStyle()

    # update default style with user style args
    for key, val in kwargs.items():
        style[key] = val

    # ensure font-size is in px units
    size = toyplot.units.convert(value=style.font_size, target="px", default="px")
    style.font_size = f"{size:.12g}px"

    # convert fill to a ToyColor
    style.fill = ToyColor(style.fill)
    return style


if __name__ == "__main__":

    pass
