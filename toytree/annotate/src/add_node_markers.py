#!/usr/bin/env python

"""...

"""

from typing import Tuple, Sequence, Mapping, Any, Union, TypeVar
import numpy as np
from numpy.typing import ArrayLike
# import toyplot
from toyplot.mark import Mark
from toyplot.coordinates import Cartesian

from toytree import ToyTree
from toytree.style.src.validator import check_arr
from toytree.color import get_color_mapped_feature
from toytree.annotate.src.node_pie_charts import (
    PieChartMark,
    validate_pie_data,
)
from toytree.annotate.src.annotation_mark import (
    get_last_toytree_mark_from_cartesian,
    assert_tree_matches_mark,
)
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.style.src.validate_nodes import (
    validate_node_labels,
    validate_node_labels_style,
    validate_node_colors,
    validate_node_sizes,
    validate_node_style,
    validate_node_markers,
    validate_node_mask,
)

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    "add_node_labels",
    "add_node_markers",
    # "add_node_pie_charts",
    # "add_node_bars",
    # "add_node_histograms",
    # "add_node_densigrams",
]


@add_subpackage_method(AnnotationAPI)
def add_node_markers(
    tree: ToyTree,
    axes: Cartesian,
    marker: Union[str, Sequence[str]] = "o",
    size: Union[int, Sequence[int]] = 8,
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], bool, None] = None,
    style: Mapping[str, Any] = None,
) -> Mark:
    """Return a toyplot Mark of node markers added to a tree plot.

    This adds node markers to the last tree drawn on the Cartesian
    axes using the coordinates of plotted Nodes. The shape, size,
    color, and style of markers can be modified.

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
        Opacity of markers (fill & stroke) as a float or Sequence
        of floats. Note: fill and stroke opacities can be set
        separately using the style dict, but only as single values.
    mask: np.array or None
        A boolean array of len nnodes or nnodes - 1 where True masks
        an node from being shown and False shows the edge. None shows
        all nodes. A tuple of 3 booleans can be entered as a shortcut
        to (show_tips, show_internal, show_root).
    style: dict
        Marker style dict. See `tree.style.node_style` for options.

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> # add markers to all Nodes
    >>> m1 = tree.annotate.add_node_markers(
    >>>     axes,
    >>>     marker='s',
    >>>     size=9,
    >>>     color='red',
    >>>     style={'stroke': 'white', 'stroke-width': 2.5}
    >>> )
    >>>
    >>> # add markers to only a few Nodes
    >>> m2 = tree.annotate.add_node_markers(
    >>>     axes, marker=">", size=20, mask=tree.get_node_mask(9)
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark_from_cartesian(axes)
    assert_tree_matches_mark(tree, mark)
    coords = mark.ntable

    # set styles on top of defaults. Must run before node_colors.
    style = validate_node_style(tree, style, serialize=True)

    # check length of colors
    node_colors = validate_node_colors(tree, color)
    if node_colors is None:
        if color:
            style["fill"] = color
    else:
        style.pop("fill")

    # mask some edges
    mask = validate_node_mask(tree, mask, default=False)
    coords = coords[mask, :]
    markers = validate_node_markers(tree, marker)[mask]
    sizes = validate_node_sizes(tree, size)[mask]
    opacity = validate_node_sizes(tree, opacity)[mask]

    # plot edge markers as scatterplot markers
    mark = axes.scatterplot(
        coords[:, 0],
        coords[:, 1],
        color=node_colors,
        size=sizes,
        marker=markers,
        mstyle=style,
        opacity=opacity,
        # annotation=True,
    )
    return mark


@add_subpackage_method(AnnotationAPI)
def add_node_labels(
    tree: ToyTree,
    axes: Cartesian,
    labels: Union[str, Sequence[str]] = "idx",
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    font_size: Union[int, None] = 12,
    angle: Union[int, Sequence[int]] = 0,
    mask: Union[np.ndarray, Tuple[int, int, int], None] = None,
    style: Mapping[str, Any] = None,
) -> Mark:
    """Return a toyplot Mark of node labels added to a tree drawing.

    This adds node labels to the last tree drawn on the Cartesian axes.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    labels: str or Sequence[str]
        A sequence of labels as strings in Node idx traversal order.
        The length must be equal to nnodes or nnodes - 1. Use '' to
        not add a label to some edges. You can also enter a single str
        as the name of a feature on the tree to extract data as labels,
        e.g., "idx" will show int idx labels for nodes.
    color: str, tuple, array or Sequence
        A single color or Sequence of colors for node labels.
    opacity: float or Sequence[float]
        A single opacity or Sequence of opacities for node labels.
    font_size: float
        Font size in px. Overrides 'font-size' setting in style dict.
    angle: int or Sequence[int]
        A single angle applied to all labels, or Sequence of angles.
    mask: np.array or None
        A boolean array of len nnodes or nnodes - 1 where True masks
        an node from being shown and False shows the node. None or False
        shows all nodes. A tuple of 3 booleans can be entered as a
        shortcut to (show_tips, show_internal, show_root).
    style: dict
        Style dict. See `tree.style.node_labels_style` for options.

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> m1 = tree.annotate.add_node_labels(
    >>>     axes,
    >>>     labels=tree.get_node_data("idx"),
    >>>     color='blue',
    >>>     style={'font-size': 16, 'baseline-shift': 8}
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark_from_cartesian(axes)
    assert_tree_matches_mark(tree, mark)
    coords = mark.ntable

    # check length and type of labels
    labels = validate_node_labels(tree, labels)

    # set styles on top of defaults
    style = validate_node_labels_style(tree, style)

    # override font size
    if font_size:
        style["font-size"] = font_size

    # check length of colors
    label_colors = validate_node_colors(tree, color, serialize=True)
    if label_colors is None:
        if color:
            style["fill"] = color
    else:
        style.pop("fill")

    # mask some edges
    mask = validate_node_mask(tree, mask, default=False)
    coords = coords[mask, :]
    labels = labels[mask]
    if label_colors is not None:
        label_colors = label_colors[mask]
    opacity = validate_node_sizes(tree, opacity)[mask]
    angle = validate_node_sizes(tree, angle)[mask]

    # add text at Node positions + half length of dists.
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


@add_subpackage_method(AnnotationAPI)
def add_node_pie_charts(
    tree: ToyTree,
    axes: Cartesian,
    data: ArrayLike,
    size: Union[int, Sequence[int]] = 10,
    colors: Union[Sequence[Color], Color] = None,
    ostroke: Color = "#262626",
    ostroke_width: float = 1.5,
    istroke: Color = "#262626",
    istroke_width: float = 0.,
    rotate: int = -45,
    mask: Union[bool, np.ndarray, tuple] = False,
) -> Mark:
    """Return a toyplot Mark of node markers added to a tree plot.

    This adds node markers to the last tree drawn on the Cartesian
    axes. The shape, size, color, and style of markers can be modified.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    data: numpy.ndarray
        Array of shape(ncategories, nnodes) with rows summing to 1. 
    size: int or Sequence[int]
        Size of markers as single int or Sequence of ints, in px units.
    color: str, tuple, or array, or Sequence
        Color of markers as single color or Sequence of colors.
    opacity: float or Sequence[float]
        Opacity of markers (fill & stroke) as a single float or Sequence
        of floats. Note that fill and stroke opacity can be set
        separately using the style dict, but only as single values.
    ...

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()

    >>> # generate random pie-like (proportion) data array
    >>> import numpy as np
    >>> ncategories = 3
    >>> arr = np.random.random(size=(tree.nnodes, ncategories))
    >>> arr = (arr.T / arr.sum(axis=1)).T

    >>> # add pie charts to all internal Nodes
    >>> tree.annotate.add_node_pie_charts(
    >>>     axes=axes, data=arr, size=20, mask=(0, 1, 1),
    >>>     istroke_width=0.75, istroke="black", rotate=-45,
    >>> )

    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark_from_cartesian(axes)
    assert_tree_matches_mark(tree, mark)
    coords = mark.ntable

    # check and cleanup data input.
    # TODO: option to collapse categories below a minimum percentage
    data = validate_pie_data(tree, data)

    # expand colormap to an array of colors
    if colors is None:
        colors = "Set2"
    if isinstance(colors, (tuple, list, np.ndarray)):
        pass
    else:
        colors = get_color_mapped_feature(range(data.shape[1]), colors)

    # ensure conversion of colors to array type and size=ncategories
    colors = check_arr(
        values=colors,
        label="colors (pie chart category colors)",
        size=data.shape[1],
        ctype=np.void,
    )

    # mask some Nodes
    mask = validate_node_mask(tree, mask, default=False)
    coords = coords[mask, :]
    data = data[mask, :]
    sizes = validate_node_sizes(tree, size)[mask]

    # plot edge markers as scatterplot markers
    mark = PieChartMark(
        coordinates=coords,
        data=data,
        sizes=sizes,
        colors=colors,
        ostroke=ostroke,
        ostroke_width=ostroke_width,
        istroke=istroke,
        istroke_width=istroke_width,
        rotate=rotate,
    )
    axes.add_mark(mark)
    return mark


if __name__ == "__main__":

    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(6)
    c, a, m = tree.draw(layout='d')

    # annotate with edge labels
    # add_edge_labels(tree, axes=a, labels=tree.get_node_data("idx"))
    # add_node_markers(
        # tree, axes=a, size=10, marker='s', color=("idx", "BlueRed"))
    # add_node_labels(tree, axes=a, labels='idx')
    data = np.array([[0.5, 0.3, 0.2]] * tree.nnodes)
    tree.annotate.add_node_pie_charts(
        a, data, size=18, istroke="white", istroke_width=0, rotate=90,
        colors="Greys",
        )
    toytree.utils.show(c)
