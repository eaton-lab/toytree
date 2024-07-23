#!/usr/bin/env python

"""...

"""

from typing import Tuple, Sequence, Mapping, Any, Union, TypeVar
import numpy as np

from toytree.core import ToyTree, Cartesian, Mark
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
from toytree.style.src.validate_nodes import (
    validate_node_style,
)
from toytree.style.src.validate_node_labels import (
    validate_node_labels_style,
)
from toytree.layout.src.get_edge_midpoints import get_edge_midpoints

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "add_edge_markers",
    "add_edge_labels",
    # "add_edge_pie_charts",  # see add_pie_markers.py
]


@add_subpackage_method(AnnotationAPI)
def add_edge_markers(
    tree: ToyTree,
    axes: Cartesian,
    marker: Union[str, Sequence[str]] = "o",
    size: Union[int, Sequence[int]] = 8,
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
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
        A boolean array of len nnodes or nnodes - 1 where True masks
        an edge from being shown and False shows the edge. None shows
        all edges. A tuple of 3 booleans can be entered as a shortcut
        to build an array of (mask_tips, mask_internal, mask_root).
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

    # only show read edges (not the root edge in unrooted trees)
    nedges = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1

    # get coordinates of all real edges
    # coords = _get_edge_midpoints(tree, mark.ntable, mark.layout, mark.edge_type)[:nedges]
    coords = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)[:nedges]

    # mask some edges
    mask = validate_mask(tree, style={"node_mask": mask})[:nedges]

    # set styles on top of defaults. Must run before node_colors.
    style = {} if style is None else style
    style = validate_node_style(tree, style=style, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # update node colors setting; sets to None if only one color.
    colors, fill_color = validate_colors(
        tree, key="color", size=tree.nnodes, style={"color": color})

    # if fill_color then set to node_style.fill since node_colors = None
    if colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        colors = colors[:nedges][mask]
        style.pop("fill")

    # ...
    markers = validate_markers(tree, key="edge_markers", size=tree.nnodes, style={"edge_markers": marker})[:nedges][mask]
    sizes = validate_numeric(tree, key="size", size=tree.nnodes, style={"size": size})[:nedges][mask]
    opacity = validate_numeric(tree, key="opacity", size=tree.nnodes, style={"opacity": opacity})[:nedges][mask]

    # logger.warning(coords)
    # logger.warning(mask)
    coords = coords[mask, :]

    # plot edge markers as scatterplot markers
    mark = AnnotationMarker(
        ntable=coords,
        xshift=xshift,
        yshift=yshift,
        sizes=sizes,
        colors=colors,
        opacity=opacity,
        shapes=markers,
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
        A sequence of labels as strings in Node idx traversal order.
        The length must be equal to nnodes or nnodes - 1. Use '' to
        not add a label to some edges. You can also enter a single str
        as the name of a feature on the tree to extract data as labels,
        e.g., "idx" will show int idx labels for edges.
    color: str, tuple, array or Sequence
        A single color or Sequence of colors for edge labels.
    opacity: float or Sequence[float]
        A single opacity or Sequence of opacities for edge labels.
    font_size: float
        Font size in px. Overrides 'font-size' setting in style dict.
    angle: int or Sequence[int]
        A single angle applied to all labels, or Sequence of angles.
    mask: np.array or None
        A boolean array of len nnodes or nnodes - 1 where True masks
        an edge from being shown and False shows the edge. None shows
        all edges. A tuple of 3 booleans can be entered as a shortcut
        to build an array of (mask_tips, mask_internal, mask_root).
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

    # get coordinates of all real edges
    nedges = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1
    # coords = _get_edge_midpoints(tree, mark.ntable, mark.layout, mark.edge_type)[:nedges]
    coords = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)[:nedges]

    # mask some edges
    mask = validate_mask(tree, style={"node_mask": mask})[:nedges]
    labels = validate_labels(
        tree, key="labels", size=tree.nnodes, style={"labels": labels})[:nedges][mask]

    # set styles on top of defaults
    style = {} if style is None else style
    style = validate_node_labels_style(tree, style=None, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # override font size
    if font_size:
        style["font-size"] = font_size

    # check colors
    label_colors, fill_color = validate_colors(
        tree, key="color", size=tree.nnodes, style={"color": color})
    if label_colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides ..._style.fill
        else:
            pass  # node_style.fill overrides
    else:
        label_colors = label_colors[:nedges][mask]
        style.pop("fill")

    # mask some nodes
    opacity = validate_numeric(
        tree, key="opacity", size=tree.nnodes, style={"opacity": opacity})[:nedges][mask]
    angle = validate_numeric(
        tree, key="angle", size=tree.nnodes, style={"angle": angle})[:nedges][mask]

    # expand xshift,yshift args as anchor_shift,baseline_shift
    style['-toyplot-anchor-shift'] += xshift
    style['baseline-shift'] -= yshift

    # add text at Node positions + half length of dists.
    coords = coords[mask, :]
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
