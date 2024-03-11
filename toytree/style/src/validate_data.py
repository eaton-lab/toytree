#!/usr/bin/env python

"""Testing simple alternative validation

"""

from typing import Union, Sequence, Mapping, Any, Dict, TypeVar, Tuple, Optional, List
import numpy as np
import toyplot
from loguru import logger

from toytree.color import ToyColor
from toytree.utils import ToytreeError, ToyColorError
from toytree.style.src.validate_utils import check_arr
from toytree.style.src.style_base import NodeStyle, NodeLabelStyle, TreeStyle
from toytree.style import get_range_mapped_feature, get_color_mapped_feature

ToyTree = TypeVar("ToyTree")
Color = TypeVar("Color", str, tuple, np.ndarray)
logger = logger.bind(name="toytree")

__all__ = [
    "validate_mask",
    "validate_numeric",
    "validate_markers",
    "validate_colors",
    "validate_hover",
    "validate_labels",
    # "validate_style",
    # "validate_node_markers",
    # "validate_node_hover",
    # "validate_node_style",
]


def validate_mask(
    tree: ToyTree,
    tree_style: Optional[TreeStyle] = None,
    style: Optional[Mapping[str, Any]] = None
) -> np.ndarray:
    """Sets node_mask to ndarray[bool] size=nnodes.

    Mask is a bool array in idx order where False hides node markers.

    Supported args
    --------------
    None: Use default
    True: mask all nodes (return False array)
    False: show all nodes (return True array)
    Sequence: custom boolean mask
    Tuple: (bool, bool, bool) for show (tips, internal, root).
    """
    # get user value or, if None, use style base value
    mask = style.get("node_mask")
    if mask is None:
        if isinstance(tree_style, TreeStyle):
            mask = getattr(tree_style, "node_mask")

    # default None masks tip Nodes and shows internal + root
    if mask is None:
        mask = (0, 1, 1)

    # mask=True means mask all Nodes, so return all False.
    if mask is True:
        mask = np.repeat(False, tree.nnodes)

    # mask=False means show all Nodes, so return all True
    elif mask is False:
        mask = np.repeat(True, tree.nnodes)

    # special tuple arg (show_tips, show_internal, show_root)
    elif isinstance(mask, tuple):
        mask = tree.get_node_mask(
            show_tips=mask[0],
            show_internal=mask[1],
            show_root=mask[2],
        )

    # else custom. Check size and type and return as an array.
    mask = check_arr(mask, "node_mask", tree.nnodes, np.bool_)
    return mask


def validate_numeric(
    tree: ToyTree,
    key: str,
    size: int,
    tree_style: Optional[TreeStyle] = None,
    style: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Sets node_sizes to ndarray[float].

    Union[float, Sequence[float]],

    None: sizes all set to 0 (at rendering they are not drawn)
    int: sizes all set to same.
    Sequence[int] = sizes in Node idx order.
    tuple[str, Tuple] = sizes mapped to range by feature value
    """
    # get values from user values
    values = style.get(key)

    # or, get values from TreeStyle
    if values is None:
        if isinstance(tree_style, TreeStyle):
            values = getattr(tree_style, key)

    # expand value to a Series of sizes
    if values is None:
        # some return None to allow style args to override, others set
        # to zero so that zero is expanded as the value.
        if key in ["edge_widths", "tip_labels_angles"]:  # 'edge_opacity'
            return None
        values = 0
    if isinstance(values, (int, float)):
        values = np.repeat(values, size)

    # expand str feature name to a tuple of (feature, min, max) so that nan is handled below
    elif isinstance(values, str):
        if size == tree.ntips:
            data = tree.get_tip_data(values)
            values = (values, data.min(), data.max())
        else:
            data = tree.get_node_data(values)
            values = (values, data.min(), data.max())
        # if values == "node_sizes":
        #     values = (values, 5., 20.)
        # elif values == "edge_widths":
        #     values = (values, 2., 5.)
        # else:
        #     values = (values, )

    # expand as value mapped
    if isinstance(values, tuple) and isinstance(values[0], str):  # len(values) <= 4:
        feature, *args = values
        # defaults selected for marker sizes
        min_default = 2 if feature == "edge_widths" else 5
        max_default = 5 if feature == "edge_widths" else 20
        kwargs = dict(zip(("min_value", "max_value", "nan_value"), args))
        kwargs["min_value"] = kwargs.get("min_value", min_default)
        kwargs["max_value"] = kwargs.get("max_value", max_default)
        kwargs["nan_value"] = kwargs.get("nan_value", 0.0)
        kwargs["tips_only"] = True if size == tree.ntips else False
        return get_range_mapped_feature(tree, feature, **kwargs)

    # validate and return as ndarray
    return check_arr(values, key, size, (int, float, np.integer))


def validate_markers(
    tree: ToyTree,
    key: str,
    size: int,
    tree_style: Optional[TreeStyle] = None,
    style: Optional[Mapping[str, Union[int, Sequence[int]]]] = None,
) -> np.ndarray:
    """Sets node_markers to ndarray[str] or ndarray[Marker].

    node_markers: Union[str, Sequence[str], toyplot.marker.Marker],
    """
    # get user value or style base value
    markers = style.get(key)

    # or tree_style
    if markers is None:
        if isinstance(tree_style, TreeStyle):
            markers = getattr(tree_style, key)

    if markers is None:
        markers = "o"
    if isinstance(markers, (str, toyplot.marker.Marker)):
        markers = np.repeat(markers, size)
    markers = check_arr(markers, key, size, (str, toyplot.marker.Marker))
    return markers


def validate_colors(
    tree: ToyTree,
    key: str,
    size: int,
    tree_style: Optional[TreeStyle] = None,
    style: Optional[Mapping[str, Any]] = None,
) -> Tuple[Union[np.ndarray, None], Union[None, Color]]:
    """Set .node_colors to type=ndarray size=nnodes or None.

    If only one color was entered then store as style.fill.
    Only expand .node_colors into an array of size nnodes if there
    is variation among nodes.

    node_colors: Union[None, Color, Sequence[Color], tuple[str, str]],

    Args
    ----
    None: None. Node color will use node_style.fill
    str: set all as ToyColor(str) unless str is a feature name
    ndarray dtype: set all as ToyColor(ndarray)
    tuple w/ len > 2:
    tuple w/ len == 2:
    colormap: not supported. Use (feature, colormap)
    """
    # get node_colors value, else get from TreeStyle, else None.
    colors = style.get(key)

    # if None then try to get from TreeSTyle
    if colors is None:
        if isinstance(style, TreeStyle):
            colors = getattr(style, key, None)
        elif tree_style is not None:
            colors = getattr(tree_style, key, None)

    # if None then Nodes will be colored by style.fill during render
    if colors is None:
        return None, None

    # do colormapping if colors is a str feature name
    if isinstance(colors, str) and colors in tree.features:
        # do not colormap feature if feature is already a valid list of colors
        try:
            colors = ToyColor.color_expander(tree.get_node_data(colors))
        # else colormap it
        except ToyColorError:
            colors = (colors, )

    # special (feature, cmap), but not single color as tuple (0, 0, 1, 1).
    if isinstance(colors, tuple) and isinstance(colors[0], str):
        feat = colors[0]
        kw = dict(cmap=None if len(colors) < 2 else colors[1])
        kw["domain_min"] = None if len(colors) < 3 else colors[2]
        kw["domain_max"] = None if len(colors) < 4 else colors[3]
        kw["nan_value"] = None if len(colors) < 5 else colors[4]
        kw["tips_only"] = size == tree.ntips
        return get_color_mapped_feature(tree, feat, **kw), None

    # get user entered value as ToyColor or List[ndarray]
    # e.g., str, tuple, or ndarray[r,g,b,a] -> ToyColor
    # e.g., List[str], pd.Series[ToyColor], ndarray[void] -> List[ToyColor]
    colors = ToyColor.color_expander(colors)

    # if single color return None. The node_style validator will recognize
    # None and check orig node_color arg to override node_style.fill.
    if isinstance(colors, ToyColor):
        return None, colors

    # convert the List[ToyColor] to an ndarray of dtype np.void
    colors = check_arr(colors, key, size=size, ctype=np.void)
    return colors, None


def validate_hover(
    tree: ToyTree,
    key: str,
    size: int,
    float_format: str = "{:.12g}",
    tree_style: Optional[TreeStyle] = None,
    style: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Return node_hover as an ndarray of dtype str w/ float formatted vals.

    node_hover: Union[None, bool, str, Sequence[str]],

    None: no hover
    False: no hover
    True: hover with all features
    str: hover w/ just this feature
    Series[str]: hover w/ just these features
    """
    # get user value or style base value
    node_hover = style.get(key)

    # or from treestyle
    if node_hover is None:
        if isinstance(tree_style, TreeStyle):
            node_hover = getattr(tree_style, key)

    # None will not add hover (title) during rendering
    if node_hover is None:
        return None
    if node_hover is False:
        return None

    # True expands to a list of all features on hover.
    if node_hover is True:
        # get all features with default ones listed first
        default_features = ["idx", "dist", "support", "height"]
        non_default = list(set(tree.features) - set(default_features))
        features = default_features + non_default

    # str selects just one feature
    elif isinstance(node_hover, str):
        assert node_hover in tree.features, f"feature {node_hover} not in tree."
        features = [node_hover]

    # Series of features
    else:
        features = []
        for feature in node_hover:
            assert feature in tree.features, f"feature {feature} not in tree."
            features.append(feature)

    # build a multi-line string with feature {key: value} formatted.
    node_hover = {i: [] for i in tree}  # range(size)}
    for node in tree:
        for feature in features:
            val = getattr(node, feature, np.nan)
            if isinstance(val, float):
                val = str(float_format.format(val))
            else:
                val = str(val)
            node_hover[node].append(f"{feature}: {val}")
    # convert to idx ordered List[str]
    node_hover = ["\n".join(node_hover[i]) for i in tree]

    # validate and return as an array
    return check_arr(node_hover, key, size, str)


def validate_labels(
    tree: ToyTree,
    key: str,
    size: int,
    float_format: str = "{:.4g}",
    tree_style: Optional[TreeStyle] = None,
    style: Optional[Mapping[str, Any]] = None,
) -> Union[None, np.ndarray]:
    """Sets labels to np.ndarray[str] or None.

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
    labels = style.get(key)

    # or get from treestyle
    if labels is None:
        if isinstance(tree_style, TreeStyle):
            labels = getattr(tree_style, key)

    # Note: don't use 'is in' otherwise error w/ pd.Series type
    if labels is False:
        return None

    # Default None is OK for Node labels, but is "name" for tip labels
    if labels is None:
        return None

    # True: use idxs as labels
    if labels is True:
        if key == "tip_labels":
            labels = "name"
        else:
            labels = "idx"

    # str: extract feature as labels as an np.array
    if isinstance(labels, str):
        labels = tree.get_node_data(labels).values[:size]

    # tuple (feature, str or Callable)
    if isinstance(labels, tuple) and isinstance(labels[0], str):

        # get feature data
        feature, *formatter = labels
        labels = tree.get_node_data(feature).values[:size]

        # optionally apply func or str formatting to it
        if formatter:
            formatter, *args = formatter
            if isinstance(formatter, str):
                float_format = formatter
            elif callable(formatter):
                # TODO: allow for nan without causing formatter exception
                labels = np.array([formatter(i, *args) for i in labels])
            else:
                raise ToytreeError(
                    "Tuple type label arg must be (feature, Callable, *args) or (feature, formatter).\n"
                    "Examples with Callable:\n"
                    ">>> node_labels=('dist', lambda x: round(x, 2)) \n"
                    ">>> node_labels=('dist', round, 2)\n"
                    ">>> tip_labels=('name', lambda x: f'<i>{x}</i>')"
                    "Examples with format string:\n"
                    ">>> node_labels=('dist', '{:.4g}')"
                )

    # or, user entered a list, tuple, Series, array, etc.
    # which is checked and handled below.

    # float format numeric values, and convert to strings
    flabels = []
    for label in labels:
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
    labels = check_arr(flabels, key, size, str)
    return labels


def validate_labels_style(
    tree: ToyTree,
    style: NodeLabelStyle = None,
    **kwargs,
) -> TreeStyle:
    """Ensure tip labels are in px sizes and fill color as ToyColor.

    Parameters
    ----------
    tree:
        A ToyTree.
    style: Mapping
        A dict or SubStyle for Node label style.
    kwargs:
        user style changes.
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


def validate_admixture_edges(tree: ToyTree, **kwargs) -> List[Tuple]:
    """Return the aedges list with src,dest expanded to Nodes.
    """
    admixture_edges = kwargs['style'].get("admixture_edges")
    if admixture_edges is None:
        return []

    if not admixture_edges:
        return []

    # ((2,3),(2,4)) or (2,3)
    if isinstance(admixture_edges, tuple):
        if isinstance(admixture_edges[0], tuple):
            admixture_edges = list(admixture_edges)
        else:
            admixture_edges = [admixture_edges]

    # [(2,3),]
    # [((2,3), 4, ...), (...)]
    aedges = []
    for aedge in admixture_edges:
        # user can enter multiple Nodes to get mrca or a single node
        if isinstance(aedge[0], (tuple, list)):
            src = tree.get_mrca_node(*aedge[0]).idx
        else:
            src = tree.get_nodes(aedge[0])[0].idx
        if isinstance(aedge[1], (tuple, list)):
            dst = tree.get_mrca_node(*aedge[1]).idx
        else:
            dst = tree.get_nodes(aedge[1])[0].idx
        aedges.append((src, dst) + tuple(aedge[2:]))
    return aedges


if __name__ == "__main__":

    import toytree

    tree = toytree.rtree.unittree(10, seed=123)

    # node_labels = validate_node_labels(tree, "idx")
    # print(node_labels)

    node_mask = validate_mask(tree, tree.style, {"node_mask": False})
    print(node_mask)

    # node_sizes = validate_node_sizes(tree, False)
    # print(node_sizes)

    # node_labels_style = validate_node_labels_style(tree, style={"fill": "red", "fill-opacity": 0.1}, serialize=True, )
    # print(node_labels_style)

    # node_style = validate_node_style(tree, style={"fill": "red", "fill-opacity": 0.1}, serialize=True)
    # print(node_style)

    # colors = validate_node_colors(tree, ['red'] * tree.nnodes)
    # print(colors)

    # colors = validate_node_colors(tree, ('idx', "Spectral"))
    # print(colors)


