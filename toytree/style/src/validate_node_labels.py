#!/usr/bin/env python

"""...

"""

from typing import Union, Sequence, Mapping, Any, Dict, TypeVar
import numpy as np
import toyplot
# from toytree.utils import ToytreeError
from toytree.color import ToyColor
from toytree.style.src.style_base import NodeLabelStyle, TreeStyle
from toytree.style.src.validate_utils import check_arr


ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "validate_node_labels",
    "validate_node_labels_style",
]


def validate_node_labels(
    tree: ToyTree,
    style: TreeStyle,
    float_format: str = "{:.4g}",
    **kwargs,
) -> Union[None, np.ndarray]:
    """Sets node_labels to np.ndarray[str] or None.

    Also applies floating point string formatting on node_labels. If
    set to None then no labels are added during rendering.

    node_labels: Union[None, bool, str, Sequence[str]],

    Args
    ----
    None: None
    False: None
    True: 'idx' int labels
    str: extract feature
    Series[Any: custom collection of the proper size.
    """
    # get user value or style base value
    node_labels = kwargs.get("node_labels")
    if node_labels is None:
        if isinstance(style, TreeStyle):
            node_labels = getattr(style, "node_labels")

    # Don't use 'is in' to support pd.Series
    if node_labels is False:
        return None
    if node_labels is None:
        return None

    # True: use idxs as labels
    if node_labels is True:
        node_labels = range(tree.nnodes)

    # str: extract feature as labels as an np.array
    elif isinstance(node_labels, str):
        node_labels = tree.get_node_data(node_labels).values

    # or, user entered a list, tuple, Series, array, etc.
    # which is checked and handled below.

    # float format numeric values, and convert to strings
    flabels = []
    for label in node_labels:
        try:
            flabel = float_format.format(label)
            flabels.append(str(flabel))
        except (ValueError, TypeError):
            slabel = str(label)
            if slabel == "nan":
                flabels.append("")
            else:
                flabels.append(slabel)

    # validate len and type and convert to an array
    node_labels = check_arr(flabels, "node_labels", tree.nnodes, str)
    return node_labels


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
