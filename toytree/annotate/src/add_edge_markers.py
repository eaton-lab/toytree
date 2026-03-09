#!/usr/bin/env python

"""...

"""

from typing import Tuple, Sequence, Mapping, Any, Union, TypeVar, Callable
import numpy as np

from toytree.core import ToyTree
from toytree.drawing import Cartesian, Mark
from toytree.color import ToyColor
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.annotate.src.checks import get_last_toytree_mark, assert_tree_matches_mark
from toytree.drawing.src.mark_annotation import AnnotationMarker
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.style.src.validate_data import (
    validate_colors,
    validate_numeric,
    validate_markers,
    validate_mask,
    validate_labels,
)
from toytree.style.src.validate_nodes import validate_node_style
from toytree.style.src.validate_node_labels import validate_node_labels_style
from toytree.layout.src.get_edge_midpoints import get_edge_midpoints
from toytree.utils import ToytreeError

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "add_edge_markers",
    "add_edge_labels",
    # "add_edge_pie_markers",  # see add_pie_markers.py
]


def _get_root_child_idxs(tree: ToyTree, nedges: int) -> np.ndarray:
    """Return child-node indices attached directly to the root."""
    if not tree.is_rooted():
        return np.array([], dtype=int)
    root = tree[-1]
    return np.array([i.idx for i in root.children if i.idx < nedges], dtype=int)


def _coerce_edge_mask(
    tree: ToyTree,
    mask: Union[np.ndarray, Tuple[int, int, int], None, bool],
    nedges: int,
    wrap_root_edge: bool,
) -> np.ndarray:
    """Return a bool show-mask for plotted edges in child-index order."""
    # explicit edge-level mask of len(nedges) bypasses node-mask semantics.
    if (mask is not None) and (not isinstance(mask, bool)):
        if not (isinstance(mask, tuple) and len(mask) == 3):
            arr = np.asarray(mask)
            if arr.size == nedges:
                if not np.issubdtype(arr.dtype, np.bool_):
                    raise ToytreeError(
                        "'mask' edge sequence must contain boolean values."
                    )
                return arr.astype(bool, copy=False)

    node_mask = validate_mask(tree, style={"node_mask": mask})
    edge_mask = node_mask[:nedges].copy()
    if wrap_root_edge and tree.is_rooted():
        root_show = bool(node_mask[tree.nnodes - 1])
        root_child_idxs = _get_root_child_idxs(tree, nedges)
        edge_mask[root_child_idxs] = root_show
    return edge_mask


def _coerce_edge_values(
    tree: ToyTree,
    key: str,
    value: Any,
    validator: Callable[..., np.ndarray],
    nedges: int,
    wrap_root_edge: bool,
) -> np.ndarray | None:
    """Validate input on nodes first, then fallback to explicit edge arrays."""
    style = {key: value}
    try:
        arr = validator(tree, key=key, size=tree.nnodes, style=style)
        from_nodes = True
    except ToytreeError:
        arr = validator(tree, key=key, size=nedges, style=style)
        from_nodes = False

    if arr is None:
        return None
    arr = np.array(arr, copy=True)
    if not from_nodes:
        return arr

    edge_arr = arr[:nedges].copy()
    if wrap_root_edge and tree.is_rooted():
        root_child_idxs = _get_root_child_idxs(tree, nedges)
        edge_arr[root_child_idxs] = arr[tree.nnodes - 1]
    return edge_arr


def _coerce_edge_colors(
    tree: ToyTree,
    color: Union[Color, Sequence[Color], None],
    nedges: int,
    wrap_root_edge: bool,
) -> tuple[np.ndarray | None, ToyColor | None]:
    """Validate colors on nodes first, then fallback to explicit edge arrays."""
    style = {"color": color}
    try:
        colors, fill_color = validate_colors(
            tree,
            key="color",
            size=tree.nnodes,
            style=style,
        )
        from_nodes = True
    except ToytreeError:
        colors, fill_color = validate_colors(
            tree,
            key="color",
            size=nedges,
            style=style,
        )
        from_nodes = False

    if colors is None:
        return None, fill_color
    colors = np.array(colors, copy=True)
    if not from_nodes:
        return colors, None

    edge_colors = colors[:nedges].copy()
    if wrap_root_edge and tree.is_rooted():
        root_child_idxs = _get_root_child_idxs(tree, nedges)
        edge_colors[root_child_idxs] = colors[tree.nnodes - 1]
    return edge_colors, None


@add_subpackage_method(AnnotationAPI)
def add_edge_markers(
    tree: ToyTree,
    axes: Cartesian,
    marker: Union[str, Sequence[str]] = "o",
    size: Union[int, Sequence[int]] = 8,
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    wrap_root_edge: bool = True,
    xshift: float = 0.0,
    yshift: float = 0.0,
    style: Mapping[str, Any] = None,
) -> Mark:
    """Return a toyplot Mark of edge markers added to a tree plot.

    This adds edge markers to the last tree drawn on the Cartesian
    axes. The shape, size, color, and style of markers can be modified.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    marker: str or toyplot.marker.Marker or Sequence
        Marker shape, e.g., "o", "s", "^", "r2x1". See toyplot Markers.
    size: int or Sequence[int]
        Size of markers as single int or Sequence of ints, in px units.
    color: str, tuple, or array, or Sequence
        Color of markers as single color or Sequence of colors.
    opacity: float or Sequence[float]
        Opacity of markers (fill & stroke) as a single float or Sequence
        of floats. Note that fill and stroke opacity can be set
        separately using the style dict, but only as single values.
    mask: np.array or None
        A boolean show-mask. Accepted forms are: bool, tuple
        (show_tips, show_internal, show_root), a node-sized boolean
        array (len=nnodes), or an edge-sized boolean array
        (len=nnodes-1). ``None`` uses the default node-mask behavior
        (show internal + root, hide tips). Use ``False`` to show all
        edges explicitly.
    wrap_root_edge: bool
        If True on rooted trees, a root-node feature value is wrapped
        onto all root-adjacent plotted edges. If False, each root-adjacent
        edge uses its own child-edge value.
    style: dict
        Marker style dict. See `tree.style.node_style` for options.
    xshift: int
        Shift marker horizontally by px units (+=right, -=left).
    yshift: int
        Shift marker vertically by px units (+=down, -=up).

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> m1 = tree.annotate.add_edge_markers(
    >>>     axes,
    >>>     marker='s',
    >>>     size=9,
    >>>     color='red',
    >>>     style={'stroke': 'white', 'stroke-width': 2.5}
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # plotted edges correspond to non-root child indices (0..nnodes-2).
    nedges = tree.nnodes - 1

    # get coordinates of all real edges
    coords = get_edge_midpoints(
        mark.etable,
        mark.ntable,
        mark.layout,
        mark.edge_type,
    )[:nedges]

    # mask some edges
    edge_mask = _coerce_edge_mask(
        tree=tree,
        mask=mask,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )

    # set styles on top of defaults. Must run before node_colors.
    style = {} if style is None else style
    style = validate_node_style(tree, style=style, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # update node colors setting; sets to None if only one color.
    colors, fill_color = _coerce_edge_colors(
        tree=tree,
        color=color,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )

    # if fill_color then set to node_style.fill since node_colors = None
    if colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        colors = colors[edge_mask]
        style.pop("fill", None)

    markers = _coerce_edge_values(
        tree=tree,
        key="edge_markers",
        value=marker,
        validator=validate_markers,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )[edge_mask]
    sizes = _coerce_edge_values(
        tree=tree,
        key="size",
        value=size,
        validator=validate_numeric,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )[edge_mask]
    opacity = _coerce_edge_values(
        tree=tree,
        key="opacity",
        value=opacity,
        validator=validate_numeric,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )[edge_mask]

    # logger.warning(coords)
    # logger.warning(mask)
    coords = coords[edge_mask, :]

    # plot edge markers as scatterplot markers
    mark = AnnotationMarker(
        ntable=coords,
        xshift=xshift,
        yshift=yshift,
        sizes=sizes,
        colors=colors,
        opacity=opacity,
        shapes=markers,
        local_span=None,
        local_depth=None,
        root_xy=None,
        style=style,
    )
    axes.add_mark(mark)
    return mark


@add_subpackage_method(AnnotationAPI)
def add_edge_labels(
    tree: ToyTree,
    axes: Cartesian,
    labels: Union[str, Sequence[str]] = "idx",
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    font_size: Union[int, None] = 12,
    angle: Union[int, Sequence[int]] = 0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    wrap_root_edge: bool = True,
    xshift: int = 0,
    yshift: int = 0,
    style: Mapping[str, Any] = None,
) -> Mark:
    """Return a toyplot Mark of edge labels added to a tree drawing.

    This adds edge labels to the last tree drawn on the Cartesian axes.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    labels: str or Sequence[str]
        A sequence of labels in node-idx or edge-idx traversal order.
        Length can be ``nnodes`` (node values) or ``nnodes-1``
        (explicit plotted-edge values). Use '' to skip a label on an
        edge. You can also enter a single feature name as a str.
    color: str, tuple, array or Sequence
        A single color or Sequence of colors for edge labels.
    opacity: float or Sequence[float]
        A single opacity or Sequence of opacities for edge labels.
    font_size: float
        Font size in px. Overrides 'font-size' setting in style dict.
    angle: int or Sequence[int]
        A single angle applied to all labels, or Sequence of angles.
    mask: np.array or None
        A boolean show-mask. Accepted forms are: bool, tuple
        (show_tips, show_internal, show_root), a node-sized boolean
        array (len=nnodes), or an edge-sized boolean array
        (len=nnodes-1). ``None`` uses the default node-mask behavior
        (show internal + root, hide tips). Use ``False`` to show all
        edges explicitly.
    wrap_root_edge: bool
        If True on rooted trees, a root-node feature value is wrapped
        onto all root-adjacent plotted edges. If False, each root-adjacent
        edge uses its own child-edge value.
    xshift: int
        Shift label horizontally by px units (+=right, -=left).
    yshift: int
        Shift label vertically by px units (+=down, -=up).
    style: dict
        Style dict. See `tree.style.node_labels_style` for options.

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> m1 = tree.annotate.add_edge_labels(
    >>>     axes,
    >>>     labels=tree.get_node_data("idx"),
    >>>     color='blue',
    >>>     style={'font-size': 16, 'baseline-shift': 8}
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # plotted edges correspond to non-root child indices (0..nnodes-2).
    nedges = tree.nnodes - 1
    coords = get_edge_midpoints(
        mark.etable,
        mark.ntable,
        mark.layout,
        mark.edge_type,
    )[:nedges]

    # mask some edges
    edge_mask = _coerce_edge_mask(
        tree=tree,
        mask=mask,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )
    labels = _coerce_edge_values(
        tree=tree,
        key="labels",
        value=labels,
        validator=validate_labels,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )[edge_mask]

    # set styles on top of defaults
    style = {} if style is None else style
    style = validate_node_labels_style(tree, style=None, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # override font size
    if font_size:
        style["font-size"] = font_size

    # check colors
    label_colors, fill_color = _coerce_edge_colors(
        tree=tree,
        color=color,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )
    if label_colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides ..._style.fill
        else:
            pass  # node_style.fill overrides
    else:
        label_colors = label_colors[edge_mask]
        style.pop("fill", None)

    opacity = _coerce_edge_values(
        tree=tree,
        key="opacity",
        value=opacity,
        validator=validate_numeric,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )[edge_mask]
    angle = _coerce_edge_values(
        tree=tree,
        key="angle",
        value=angle,
        validator=validate_numeric,
        nedges=nedges,
        wrap_root_edge=wrap_root_edge,
    )[edge_mask]

    # expand xshift,yshift args as anchor_shift,baseline_shift
    style['-toyplot-anchor-shift'] += xshift
    style['baseline-shift'] -= yshift

    # add text at Node positions + half length of dists.
    coords = coords[edge_mask, :]
    mark = axes.text(
        coords[:, 0],
        coords[:, 1],
        labels,
        color=label_colors,
        opacity=opacity,
        angle=angle,
        style=style,
        annotation=True,
    )
    return mark


if __name__ == "__main__":

    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(6)  # .unroot()
    tree[0].name = "amdodfl"
    tree[1]._name = "HI"
    c, a, m = tree.draw(layout='d')  # r')

    # annotate with edge labels
    add_edge_markers(tree, axes=a, size=10, marker='r1x2', color="height")
    add_edge_labels(tree, axes=a, labels="idx", font_size=15)

    data = np.array([[0.5, 0.3, 0.2]] * tree.nnodes)
    toytree.utils.show(c, tmpdir="~")
