#!/usr/bin/env python

"""Annotation methods for adding tip markers to tree drawings.

Examples
--------
...
"""

from typing import Tuple, Sequence, Mapping, Any, Union, TypeVar
import numpy as np
from toyplot.mark import Mark
from toyplot.coordinates import Cartesian

from toytree import ToyTree
from toytree.color import ToyColor
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.annotate.src.checks import get_last_toytree_mark, assert_tree_matches_mark

# WORK IN PROGRESS...
from toytree.drawing.src.mark_annotation import AnnotationMarker
from toytree.style.src.validate_data import (
    validate_colors,
    validate_markers,
    validate_numeric,
    validate_mask,
    validate_labels,
)
from toytree.style.src.validate_node_labels import validate_node_labels_style
from toytree.style.src.validate_nodes import (
    validate_node_style,
)

Color = TypeVar("Color", str, tuple, np.ndarray)

__all__ = [
    # "add_tip_labels",
    "add_tip_markers",
    # "add_tip_pie_charts", #to go in add_pie_markers?
    # "add_node_bars",
    # "add_node_histograms",
    # "add_node_densigrams",
]


@add_subpackage_method(AnnotationAPI)
def add_tip_markers(
    tree: ToyTree,
    axes: Cartesian,
    align: bool = None,  # default=None and use T/F to override ts?
    marker: Union[str, Sequence[str]] = "o",
    size: Union[int, Sequence[int]] = 8,
    color: Union[Color, Sequence[Color]] = None,
    opacity: Union[float, Sequence[float]] = 1.0,
    mask: Union[np.ndarray, Tuple[int, int, int], bool, None] = None,
    style: Mapping[str, Any] = None,
    xshift: int = 0,
    yshift: int = 0,
    # label: Optional[str] = None,
    # label_angle: int = 45,
) -> Mark:
    """Return toyplot Mark of markers aligned with tips of tree plot.

    This adds node markers to the last tree drawn on the Cartesian
    axes using the coordinates of plotted Nodes. The shape, size,
    color, and style of markers can be modified.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    align: bool
        If True markers align at the farthest tip position; if False
        markers align at each tip's position; if None markers align
        according to the tip_labels_align arg used during tree drawing.
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
    style: dict
        Marker style dict. See `tree.style.node_style` for options.
    xshift: int
        Shift position of markers by x canvas (px) units on x axis.
    yshift: int
        Shift position of markers by x canvas (px) units on y axis.

    Example
    -------
    >>> tree = toytree.rtree.unittree(6, seed=123)
    >>> canvas, axes, m0 = tree.draw()
    >>> # add markers to all Nodes
    >>> m1 = tree.annotate.add_tip_markers(
    >>>     axes,
    >>>     marker='s',
    >>>     size=9,
    >>>     color='red',
    >>>     style={'stroke': 'white', 'stroke-width': 2.5}
    >>> )
    >>>
    >>> # add markers to only a few Nodes
    >>> m2 = tree.annotate.add_tip_markers(
    >>>     axes, marker=">", size=20, mask=tree.get_node_mask(9)
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # get coordinates of the tip Nodes
    coords = mark.ttable.copy()

    # align tips: if mark.tip_labels_align == True this is already done
    align = align if align is not None else mark.tip_labels_align
    if align:
        if mark.layout == "r":
            coords[:, 0] = coords[:, 0].max()
        elif mark.layout == "l":
            coords[:, 0] = coords[:, 0].min()
        elif mark.layout == "u":
            coords[:, 1] = coords[:, 1].max()
        elif mark.layout == "d":
            coords[:, 1] = coords[:, 1].min()
        else:
            raise NotImplementedError("TODO")

    # get mask and apply to all other styles below. Allow user to enter
    # either a node mask or tip mask.
    if mask is None:
        mask = tree.get_node_mask(show_tips=True)[:tree.ntips]
    else:
        if mask.size == tree.ntips:
            mask = np.concatenate(mask, np.full(tree.nnodes - tree.ntips), False)
            mask = validate_mask(tree, style={"node_mask": mask})[:tree.ntips]
        elif mask.size == tree.nnodes:
            mask = validate_mask(tree, style={"node_mask": mask})[:tree.ntips]
        else:
            raise ValueError(f"mask should be of size ntips ({tree.ntips}).")

    # update node_style setting
    style = {} if style is None else style
    style = validate_node_style(tree, style=None, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # update node colors setting; sets to None if only one color.
    colors, fill_color = validate_colors(
        tree, key="colors", size=tree.ntips, style={"colors": color},
    )

    # if fill_color then set to node_style.fill since node_colors = None
    if colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        colors = colors
        style.pop("fill")

    # validate others and trim to mask
    markers = validate_markers(
        tree, key="node_markers", size=tree.ntips, style={"node_markers": marker})[mask]
    sizes = validate_numeric(
        tree, key="size", size=tree.ntips, style={"size": size})[mask]
    opacity = validate_numeric(
        tree, key="opacity", size=tree.ntips, style={"opacity": opacity})[mask]

    # create custom Mark that allows for [xy]shift
    mark = AnnotationMarker(
        ntable=coords[mask],
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

    # add label for the data column
    # if label:
    #     label = axes.text(
    #         coords[0, 0] + xoffset,
    #         tree.ntips,
    #         label,
    #         angle=label_angle,
    #         style={'text-anchor': 'start', 'fill': "#252525"},
    #     )


# TODO: auto-angles for different layouts...
# @add_subpackage_method(AnnotationAPI)
# def add_tip_labels(
#     tree: ToyTree,
#     axes: Cartesian,
#     labels: Union[str, Sequence[str]] = "idx",
#     color: Union[Color, Sequence[Color]] = None,
#     opacity: Union[float, Sequence[float]] = 1.0,
#     font_size: Union[int, None] = 12,
#     angle: Union[int, Sequence[int]] = 0,
#     offset: int = 15,
#     style: Mapping[str, Any] = None,
# ) -> Mark:
#     """Return a toyplot Mark of node labels added to a tree drawing.

#     This adds node labels to the last tree drawn on the Cartesian axes.

#     Parameters
#     ----------
#     axes: Cartesian
#         A toyplot Cartesian axes object containing a tree drawing.
#     labels: str or Sequence[str] or None
#         A sequence of labels as strings in Node idx traversal order.
#         The length must be equal to nnodes or nnodes - 1. Use '' to
#         not add a label to some edges. You can also enter a single str
#         as the name of a feature on the tree to extract data as labels,
#         e.g., "idx" will show int idx labels for nodes.
#     color: str, tuple, array or Sequence
#         A single color or Sequence of colors for node labels.
#     opacity: float or Sequence[float]
#         A single opacity or Sequence of opacities for node labels.
#     font_size: float
#         Font size in px. Overrides 'font-size' setting in style dict.
#     angle: int or Sequence[int]
#         A single angle applied to all labels, or Sequence of angles.
#     mask: np.array or None
#         A boolean array of len nnodes or nnodes - 1 where True masks
#         an node from being shown and False shows the node. None or False
#         shows all nodes. A tuple of 3 booleans can be entered as a
#         shortcut to (show_tips, show_internal, show_root).
#     style: dict
#         Style dict. See `tree.style.node_labels_style` for options.

#     Example
#     -------
#     >>> tree = toytree.rtree.unittree(6, seed=123)
#     >>> canvas, axes, m0 = tree.draw()
#     >>> m1 = tree.annotate.add_node_labels(
#     >>>     axes,
#     >>>     labels=tree.get_node_data("idx"),
#     >>>     color='blue',
#     >>>     style={'font-size': 16, 'baseline-shift': 8}
#     >>> )
#     """
#     # get mark for coordinates on plotted tree.
#     mark = get_last_toytree_mark_from_cartesian(axes)
#     assert_tree_matches_mark(tree, mark)
#     coords = mark.ttable

#     # check length and type of labels
#     labels = validate_tip_labels(tree, style=None, tip_labels=labels)

#     # set styles on top of defaults
#     style = {"-toyplot-anchor-shift": 0} if style is None else style
#     style = validate_tip_labels_style(tree, style=None, **style)
#     style = substyle_dict_to_css_dict(style.__dict__)

#     # override font size
#     if font_size:
#         style["font-size"] = font_size

#     # update node colors setting; sets to None if only one color.
#     node_colors, fill_color = validate_tip_labels_colors(
#         tree, style=None, tip_labels_colors=color)

#     # if fill_color then set to node_style.fill since node_colors = None
#     if node_colors is None:
#         if fill_color:
#             style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
#         else:
#             pass  # node_style.fill overrides
#     else:
#         node_colors = node_colors
#         style.pop("fill")

#     # opacity = validate_node_numeric(tree, style=None, key="opacity", opacity=opacity)
#     # angle = validate_node_numeric(tree, style=None, key="angle", angle=angle)
#     style['fill-opacity'] = 1.0

#     # add text at Node positions + half length of dists.
#     mark = axes.text(
#         coords[:, 0],
#         coords[:, 1],
#         labels,
#         color=node_colors,
#         opacity=opacity,
#         angle=angle,
#         style=style,
#         annotation=True,
#     )
#     return mark


# @add_subpackage_method(AnnotationAPI)
# def add_node_pie_charts(
#     tree: ToyTree,
#     axes: Cartesian,
#     data: np.ndarray,
#     size: Union[int, Sequence[int]] = 10,
#     colors: Union[Sequence[Color], Color] = None,
#     ostroke: Color = "#262626",
#     ostroke_width: float = 1.5,
#     istroke: Color = "#262626",
#     istroke_width: float = 0.,
#     rotate: int = -45,
#     mask: Union[bool, np.ndarray, tuple] = False,
#     xshift: int = 0,
#     yshift: int = 0,
# ) -> Mark:
#     """Return a toyplot Mark of node markers added to a tree plot.

#     This adds node markers to the last tree drawn on the Cartesian
#     axes. The shape, size, color, and style of markers can be modified.

#     Parameters
#     ----------
#     axes: Cartesian
#         A toyplot Cartesian axes object containing a tree drawing.
#     data: numpy.ndarray
#         Array of shape(ncategories, nnodes) with rows summing to 1.
#     size: int or Sequence[int]
#         Size of markers as single int or Sequence of ints, in px units.
#     colors: None, str, tuple, or array, or Sequence
#         Color for each category/trait or the name of a colormap.
#     ostroke: Color
#         Color of the stroke on the outside of the Mark.
#     ostroke_width: float
#         Width of the stroke on the outside of the Mark
#     istroke: Color
#         Color of the stroke on the inside of the Mark between wedges.
#     istroke_width: float
#         Width of the stroke on the inside of the Mark between wedges.
#     rotate: int
#         Rotate the starting point of the wedges.
#     mask: bool, np.ndarray, or tuple
#         Node mask to hide/show some or all Nodes.
#     xshift: int
#         Shift marker horizontally by px units (+=right, -=left).
#     yshift: int
#         Shift marker vertically by px units (+=down, -=up).

#     Example
#     -------
#     >>> tree = toytree.rtree.unittree(6, seed=123)
#     >>> canvas, axes, m0 = tree.draw()

#     >>> # generate random pie-like (proportion) data array
#     >>> import numpy as np
#     >>> ncategories = 3
#     >>> arr = np.random.random(size=(tree.nnodes, ncategories))
#     >>> arr = (arr.T / arr.sum(axis=1)).T

#     >>> # add pie charts to all internal Nodes
#     >>> tree.annotate.add_node_pie_charts(
#     >>>     axes=axes, data=arr, size=20, mask=(0, 1, 1),
#     >>>     istroke_width=0.75, istroke="black", rotate=-45,
#     >>> )
#     """
#     # get mark for coordinates on plotted tree.
#     mark = get_last_toytree_mark_from_cartesian(axes)
#     assert_tree_matches_mark(tree, mark)

#     # get mask
#     mask = validate_node_mask(tree, style=None, node_mask=mask)

#     # check and cleanup data input.
#     # TODO: option to collapse categories below a minimum percentage
#     data = validate_pie_data(tree, data)

#     # expand colormap to an array of colors
#     if colors is None:
#         colors = "Set2"
#     if isinstance(colors, (tuple, list, np.ndarray)):
#         pass
#     else:
#         colors = get_color_mapped_values(range(data.shape[1]), colors)

#     # ensure conversion of colors to array type and size=ncategories
#     colors = check_arr(
#         values=colors,
#         label="colors (pie chart category colors)",
#         size=data.shape[1],
#         ctype=np.void,
#     )
#     sizes = validate_node_sizes(tree, style=None, node_sizes=size)[mask]

#     # mask some Nodes
#     data = data[mask, :]
#     coords = mark.ntable[mask, :]
#     if xshift or yshift:
#         # Note: if later annotations change the projection this will be off
#         axes._finalize()
#         if xshift:
#             origin, xshifted = axes._x_projection.inverse([0, xshift])
#             x_shift_projected = xshifted - origin
#             coords[:, 0] += x_shift_projected
#         if yshift:
#             origin, yshifted = axes._y_projection.inverse([0, yshift])
#             y_shift_projected = yshifted - origin
#             coords[:, 1] += y_shift_projected
#         axes._finalized = None

#     # plot edge markers as scatterplot markers
#     mark = PieChartMark(
#         coordinates=coords,
#         data=data,
#         sizes=sizes,
#         colors=colors,
#         ostroke=ostroke,
#         ostroke_width=ostroke_width,
#         istroke=istroke,
#         istroke_width=istroke_width,
#         rotate=rotate,
#     )
#     axes.add_mark(mark)
#     return mark


# def add_node_bars(
#     tree: ToyTree,
#     axes: Cartesian,
#     # bars: Mapping[Query, Tuple[float, float]],
#     color: Union[Color, Sequence[Color]],
#     opacity: Union[float, Sequence[float]],
# ):
#     """

#     Example
#     -------
#     >>> tree = toytree.rtree.unittree(10, treeheight=1e5)
#     >>> ages_ci = {
#     >>>     nidx: (node.dist - 1000, node.dist + 1000)
#     >>>     for nidx, node in enumerate(tree)
#     >>> }
#     >>> canvas, axes, mark0 = tree.draw()
#     >>> tree.annotate.node_height_confidence_intervals(axes, ages_ci)
#     >>>
#     >>> mark = toytree.annotate.node_height_confidence_intervals(
#     >>>     tree=tree, axes=axes, mapping=ages_ci)
#     """
#     pass


# def add_clade_box(
#     tree: ToyTree,
#     axes: Cartesian,
# ):
#     pass


if __name__ == "__main__":

    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(6)
    c, a, m = tree.draw(layout='d')

    # annotate with edge labels
    # add_edge_labels(tree, axes=a, labels=tree.get_node_data("idx"))
    # add_node_markers(
    #     tree, axes=a, size=10, marker='s', color=("idx", "BlueRed"))
    # add_node_labels(tree, axes=a, labels='idx')
    data = np.array([[0.5, 0.3, 0.2]] * tree.nnodes)
    m = tree.annotate.add_tip_markers(
        a, 
        mask=tree.get_node_mask(1, 2, 3),
        color=("name", "Spectral"),
        opacity=1.0, size=10,
        # xshift=0, yshift=10,
    )
    # print(m.extents(['x', 'y']))
    toytree.utils.show(c, tmpdir="~")
