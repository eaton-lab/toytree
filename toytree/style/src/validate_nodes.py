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
import toyplot
from toytree import ToyTree
from toytree.color import ToyColor
from toytree.style.src.color_mapper import get_color_mapped_feature
from toytree.style.src.validator import check_arr

Color = TypeVar("Color", str, tuple, np.ndarray)


def style_to_css_dict(style: Mapping[str, Any]) -> Dict[str, Any]:
    """Return dict with css style keys, e.g., 'font_size' -> 'font-size'."""
    return dict(
        (i, j) if "_" not in i else
        (i.replace("_", "-"), j)
        for (i, j) in style.items()
    )


def validate_node_mask(
    tree: ToyTree,
    node_mask: Union[None, bool, Sequence[str]],
) -> np.ndarray:
    """Sets node_mask to ndarray[bool] size=nnodes.

    Mask is a bool array in idx order where True hides node marker.

    Supported args
    --------------
    None: special arg to hide tips only
    True: mask all nodes
    False: show all nodes
    Iterable: custom boolean mask
    Tuple: (bool, bool, bool) for show (tips, internal, root).
    """
    # default None masks tip Nodes and shows internal + root
    if node_mask is None:
        node_mask = np.zeros(tree.nnodes, dtype=bool)
        node_mask[:tree.ntips] = True
    # True or False mask all or none.
    elif node_mask is True:
        node_mask = np.repeat(True, tree.nnodes)
    elif node_mask is False:
        node_mask = np.repeat(False, tree.nnodes)
    # special tuple arg
    elif isinstance(node_mask, tuple):
        node_mask = tree.get_node_mask(
            mask_tips=node_mask[0],
            mask_internal=node_mask[1],
            mask_root=node_mask[2],
        )
    # else it is a custom sequence.
    # Check size and type and return as an array.
    node_mask = check_arr(
        node_mask, "node_mask", tree.nnodes, np.bool_)
    return node_mask


def validate_node_labels(
    tree: ToyTree,
    node_labels: Union[None, bool, Sequence[str]],
) -> Union[None, np.ndarray]:
    """Sets node_labels to np.ndarray[str] or None.

    Also applies floating point string formatting on node_labels.

    Args
    ----
    None: None
    False: None
    True: 'idx' int labels
    other: custom collection of the proper size.
    """
    # get node_labels as either None or mixed type
    if node_labels is False:
        node_labels = None
    elif node_labels is None:
        node_labels = None
    elif node_labels is True:
        node_labels = range(tree.nnodes)

    # feature expansion w/ auto-float format to :.2g
    elif isinstance(node_labels, str):
        node_labels = tree.get_node_data(node_labels)

    # or, user entered a list, tuple, Series, array, etc.
    # which is checked and handled below.

    # double check size and cast to str
    if node_labels is not None:
        # try to float format but OK if fails b/c data may not be a
        # float, and could even be a complex type like a list.
        try:
            node_labels = [f"{i:.4g}" for i in node_labels]
        except (ValueError, TypeError):
            node_labels = [str(i) for i in node_labels]

        # set any missing (nan) labels to empty strings.
        node_labels = [
            "" if i == "nan" else i for i in node_labels
        ]
        # validate len and type and convert to an array
        node_labels = check_arr(
            node_labels, "node_labels", tree.nnodes, str,
        )
    return node_labels


def validate_node_labels_style(
    tree: ToyTree,
    style: Mapping[str, Any],
    serialize: bool = False,
) -> Dict[str, Any]:
    """Ensure tip labels are in px sizes and fill color as ToyColor.

    Parameters
    ----------
    serialize: bool
        Serialize color to str ("fill:(rgb),fill-o:a"). If not, ToyColor
        keeps opacity separate to possibly share color and/or opacity
        style among higher level objects for faster rendering.
    """
    _style = tree.style.node_labels_style.__dict__.copy()
    _style = style_to_css_dict(_style)
    if style:
        _style.update(style)
    style = _style

    size = toyplot.units.convert(value=style["font-size"], target="px", default="px")
    style["font-size"] = f"{size:.1f}px"
    if style['fill'] in (None, "none"):
        style['fill'] in (0, 0, 0, 0)
    style['fill'] = ToyColor(style['fill'])
    if serialize:
        style['fill'] = style['fill'].get_style_str(stroke=False, opacity=style['fill-opacity'])
        style.pop('fill-opacity')
    return style


def validate_node_sizes(
    tree: ToyTree,
    node_sizes: Union[float, Sequence[float]],
) -> np.ndarray:
    """Sets node_sizes to ndarray[float]."""
    if isinstance(node_sizes, (int, float)):
        node_sizes = np.repeat(node_sizes, tree.nnodes)
    node_sizes = check_arr(
        node_sizes, "node_sizes", tree.nnodes, (int, float, np.integer))
    return node_sizes


def validate_node_colors(
    tree: ToyTree,
    node_colors: Union[None, Color, Sequence[Color]],
    serialize: bool = False,
) -> Union[np.ndarray, None]:
    """Set .node_colors to type=ndarray size=nnodes or None.

    If only one color was entered then store as style.fill.
    Only expand .node_colors into an array of size nnodes if there
    is variation among nodes.

    Args
    ----
    None
    ToyColor, str (css)
    """
    # if no node_colors then nodes will be colored by style.fill
    if node_colors is None:
        return

    # special (feature, cmap) tuple. This must captures special
    # tuple colormappings but not colors entered as a tuple, e.g.,
    # (0, 1, 0, 1).
    if isinstance(node_colors, tuple) and len(node_colors) == 2:
        feat, cmap = node_colors
        values = tree.get_node_data(feat).values
        node_colors = get_color_mapped_feature(values, cmap)
        return node_colors

    # user entered ToyColor or List[ToyColor], pd.Series[ToyColor]
    # this converts to single ToyColor or List[ToyColor]
    colors = ToyColor.color_expander(node_colors)

    # will set: style.fill = color  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if isinstance(colors, ToyColor):
        return None

    # converts to a ndarray of type np.void
    node_colors = check_arr(
        values=colors,
        label="node_colors",
        size=tree.nnodes,
        ctype=np.void,
    )
    if serialize:
        return list(node_colors)
    return node_colors


def validate_node_markers(
    tree: ToyTree,
    node_markers: Union[str, Sequence[str], toyplot.marker.Marker],
) -> np.ndarray:
    """Sets node_markers to ndarray[str] or ndarray[Marker]."""
    if isinstance(node_markers, (str, toyplot.marker.Marker)):
        node_markers = np.repeat(node_markers, tree.nnodes)
    node_markers = check_arr(
        node_markers, "node_markers", tree.nnodes,
        (str, toyplot.marker.Marker)
    )
    return node_markers


def validate_node_style(
    tree: ToyTree,
    style: Mapping[str, Any],
    serialize: bool = False,
) -> Dict[str, Any]:
    """Sets style.fill and .stroke"""
    _style = tree.style.node_style.__dict__.copy()
    _style = style_to_css_dict(_style)
    if style:
        _style.update(style)
    style = _style

    if style["stroke"] in [None, "none"]:
        style["stroke"] = (0, 0, 0, 0)
    style["stroke"] = ToyColor(style["stroke"])

    if style["fill"] in [None, "none"]:
        style["fill"] = (0, 0, 0, 0)
    style["fill"] = ToyColor(style["fill"])

    if serialize:
        style['fill'] = style['fill'].css
        style['stroke'] = style['stroke'].css
        if not style.get("fill-opacity"):
            style['fill-opacity'] = 1.0
        if not style.get("stroke-opacity"):
            style['stroke-opacity'] = 1.0
    return style


if __name__ == "__main__":

    import toytree

    tree = toytree.rtree.unittree(10, seed=123)

    # node_labels = validate_node_labels(tree, "idx")
    # print(node_labels)

    # node_mask = validate_node_mask(tree, False)
    # print(node_mask)

    # node_sizes = validate_node_sizes(tree, False)
    # print(node_sizes)

    # node_labels_style = validate_node_labels_style(tree, style={"fill": "red", "fill-opacity": 0.1}, serialize=True, )
    # print(node_labels_style)

    # node_style = validate_node_style(tree, style={"fill": "red", "fill-opacity": 0.1}, serialize=True)
    # print(node_style)

    colors = validate_node_colors(tree, ['red'] * tree.nnodes)
    print(colors)

    colors = validate_node_colors(tree, ('idx', "Spectral"))
    print(colors)
