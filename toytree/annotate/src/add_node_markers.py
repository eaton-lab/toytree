#!/usr/bin/env python

"""Annotation methods for adding node markers to tree drawings.

Examples
--------
...
"""

from typing import Tuple, Sequence, Mapping, Any, Union, TypeVar
import numpy as np
from loguru import logger

from toytree.core import ToyTree, Cartesian, Mark
from toytree.color import ToyColor
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
from toytree.annotate.src.checks import get_last_toytree_mark, assert_tree_matches_mark
from toytree.drawing.src.mark_annotation import AnnotationRect, AnnotationMarker

from toytree.style.src.validate_data import (
    validate_colors,
    validate_numeric,
    validate_markers,
    validate_mask,
    validate_labels,
)
from toytree.style.src.validate_node_labels import validate_node_labels_style
from toytree.style.src.validate_nodes import validate_node_style


logger = logger.bind(name="toytree")
Color = TypeVar("Color", str, tuple, np.ndarray)
__all__ = [
    "add_node_markers",
    "add_node_labels",
    "add_node_bars",
    # "add_node_histograms",
    # "add_node_densigrams",
    # "add_node_pie_charts",  # see add_pie_markers.py
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
    xshift: int = 0,
    yshift: int = 0,
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
    xshift: int
        Shift marker horizontally by px units (+=right, -=left).
    yshift: int
        Shift marker vertically by px units (+=down, -=up).

    Examples
    --------
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
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)
    coords = mark.ntable

    # get mask and apply to all other styles below
    mask = validate_mask(tree, style={"node_mask": mask})

    # update node_style setting
    style = {} if style is None else style
    style = validate_node_style(tree, style=None, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # update node colors setting; sets to None if only one color.
    colors, fill_color = validate_colors(
        tree, key="color", size=tree.nnodes, style={"color": color})

    # if fill_color then set to node_style.fill since colors = None
    if colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        colors = colors[mask]
        style.pop("fill")

    # validate others and trim to mask
    markers = validate_markers(
        tree, key="marker", size=tree.nnodes, style={"marker": marker})[mask]
    sizes = validate_numeric(
        tree, key="size", size=tree.nnodes, style={"size": size})[mask]
    opacity = validate_numeric(
        tree, key="opacity", size=tree.nnodes, style={"opacity": opacity})[mask]

    # if all marker opacities are the same then set to 1 and use style.
    # this simplifies the CSS and makes things faster, but is otherwise
    # not necessary. EDIT: commented out for now until `concat_style_fix_color`
    # used in render_annotations.py can handle fill-opacity w/o fill.
    # if len(set(opacity)) == 1:
    #     style["fill-opacity"] = opacity[0]
    #     opacity = None
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

    # # apply mask to Node coordinates
    # # TODO: alternative strategy here
    # coords = coords[mask, :]
    # if xshift or yshift:
    #     # Note: if later annotations change the projection this will be off
    #     axes._finalize()
    #     if xshift:
    #         origin, xshifted = axes._x_projection.inverse([0, xshift])
    #         x_shift_projected = xshifted - origin
    #         coords[:, 0] += x_shift_projected
    #     if yshift:
    #         origin, yshifted = axes._y_projection.inverse([0, yshift])
    #         y_shift_projected = yshifted - origin
    #         coords[:, 1] += y_shift_projected
    #     axes._finalized = None

    # # plot edge markers as scatterplot markers
    # mark = axes.scatterplot(
    #     coords[:, 0],
    #     coords[:, 1],
    #     color=node_colors,
    #     size=sizes,
    #     marker=markers,
    #     mstyle=style,
    #     opacity=opacity,
    # )
    # return mark


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
    xshift: int = 0,
    yshift: int = 0,
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
    xshift: int
        Shift label horizontally by px units (+=right, -=left).
    yshift: int
        Shift label vertically by px units (+=down, -=up).
    style: dict
        Style dict. See `tree.style.node_labels_style` for options.

    Examples
    --------
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
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # mask some edges
    mask = validate_mask(tree, style={"node_mask": mask})
    coords = mark.ntable[mask]

    # check length and type of labels
    labels = validate_labels(
        tree, key="labels", size=tree.nnodes, style={"labels": labels})[mask]

    # set styles on top of defaults
    style = {} if style is None else style
    style = validate_node_labels_style(tree, style=style, **style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # override font size
    if font_size:
        style["font-size"] = font_size

    # update node colors setting; sets to None if only one color.
    node_colors, fill_color = validate_colors(
        tree, key="color", size=tree.nnodes, style={"color": color})

    # if fill_color then set to node_style.fill since node_colors = None
    if node_colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        node_colors = node_colors[mask]
        style.pop("fill")

    # ...
    opacity = validate_numeric(
        tree, key="opacity", size=tree.nnodes, style={"opacity": opacity})[mask]
    angle = validate_numeric(
        tree, key="angle", size=tree.nnodes, style={"angle": angle})[mask]

    # expand xshift,yshift args as anchor_shift,baseline_shift
    style['-toyplot-anchor-shift'] += xshift
    style['baseline-shift'] -= yshift

    # add text at Node positions + half length of dists.
    mark = axes.text(
        coords[:, 0],
        coords[:, 1],
        labels,
        color=node_colors,
        opacity=opacity,
        angle=angle,
        style=style,
        annotation=True,
    )
    return mark


@add_subpackage_method(AnnotationAPI)
def add_node_bars(
    tree: ToyTree,
    axes: Cartesian,
    bar_min: Union[int, Sequence[int], str],
    bar_max: Union[int, Sequence[int], str],
    # Note: what about CI(5-95) features? suggest parsing... enter only as min?
    color: Union[Color, Sequence[Color]] = None,
    mask: Union[np.ndarray, bool, Tuple, None] = (0, 1, 1),
    size: Union[float, Sequence[float]] = 0.5,
    opacity: Union[float, Sequence[float]] = 0.7,
    xshift: int = 0,
    yshift: int = 0,
    style: Mapping[str, Any] = None,
    z_index: int = 0,
) -> Mark:
    """Returns a toyplot marker to add bars at Nodes.

    This is commonly used to display confidence intervals on node ages.
    Bars are rectangles on which styles can be set.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    bar_min: float, Series of float, or str
        Minimum height of the bar.
    bar_max: float, Series of float, or str
        Maximum height of the bar.
    color: str, tuple, array or Sequence
        A single color or Sequence of colors for node labels.
    mask: np.array or None
        A boolean array of len nnodes or nnodes - 1 where True masks
        an node from being shown and False shows the node. None or False
        shows all nodes. A tuple of 3 booleans can be entered as a
        shortcut to (show_tips, show_internal, show_root).
    xshift: int
        Shift label horizontally by px units (+=right, -=left).
    yshift: int
        Shift label vertically by px units (+=down, -=up).
    style: dict
        Style dict. See `tree.style.node_labels_style` for options.
    z_index: int
        Index of annotation (default=0). Lower index makes the bars
        appears behind other marks (e.g., tree or other annotations).

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10, treeheight=1e5)
    >>> c, a, m = tree.draw()
    >>> node_height = tree.get_node_data("height").values
    >>> tree.annotate.add_node_bars(
    >>>     axes=a,
    >>>     bar_min=node_height * 0.5,
    >>>     bar_max=node_height * 1.5,
    >>>     size=0.33, z_index=-1, color='purple', opacity=0.4,
    >>> )
    """
    # get mark for coordinates of Nodes on plotted tree.
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # mask some edges
    mask = validate_mask(tree, style={"node_mask": mask})

    # get Node coordinates
    coords = mark.ntable.copy()[mask]

    # update node_style setting
    base_style = {"stroke": None, "fill-opacity": 0.5}
    if style is not None:
        base_style.update(style)
    style = validate_node_style(tree, style=None, **base_style)
    style = substyle_dict_to_css_dict(style.__dict__)

    # update node colors setting; sets to None if only one color.
    opacity = validate_numeric(
        tree, key="opacity", size=tree.nnodes, style={"opacity": opacity})[mask]
    colors, fill_color = validate_colors(
        tree, key="color", size=tree.nnodes, style={"color": color})

    # if fill_color then set to node_style.fill since node_colors = None
    if colors is None:
        if fill_color:
            style["fill"] = ToyColor(fill_color)  # overrides node_style.fill
        else:
            pass  # node_style.fill overrides
    else:
        colors = colors[mask]
        style.pop("fill")

    # check values for positions
    bar_min = validate_numeric(
        tree, key="bar_min", size=tree.nnodes, style={"bar_min": bar_min})[mask]
    bar_max = validate_numeric(
        tree, key="bar_max", size=tree.nnodes, style={"bar_max": bar_max})[mask]
    sizes = validate_numeric(
        tree, key="size", size=tree.nnodes, style={"size": size})[mask]

    # orient rectangles for the tree layout
    if mark.layout == "r":
        xtable = np.column_stack([-bar_max, -bar_min])
        ytable = np.column_stack([coords[:, 1] - sizes / 2., coords[:, 1] + sizes / 2.])
    elif mark.layout == "l":
        xtable = np.column_stack([bar_min, bar_max])
        ytable = np.column_stack([coords[:, 1] - sizes / 2., coords[:, 1] + sizes / 2.])
    elif mark.layout == "d":
        xtable = np.column_stack([coords[:, 0] - sizes / 2., coords[:, 0] + sizes / 2.])
        ytable = np.column_stack([bar_min, bar_max])
    elif mark.layout == "u":
        xtable = np.column_stack([coords[:, 0] - sizes / 2., coords[:, 0] + sizes / 2.])
        ytable = np.column_stack([-bar_max, -bar_min])
    else:
        raise NotImplementedError("TODO")

    # build the Mark
    mark = AnnotationRect(
        ntable=coords,
        xtable=xtable,
        ytable=ytable,
        colors=colors,
        opacity=opacity,
        xshift=xshift,
        yshift=yshift,
        style=style,
    )

    # extend the domain to ensure bars fit
    mark._annotation = True

    # z-index: option to set markers to appear UNDER the tree Mark
    axes._scenegraph._relationships['render']._targets[axes].insert(z_index, mark)
    axes._scenegraph._relationships['map']._targets[axes.x].insert(z_index, mark)
    axes._scenegraph._relationships['map']._targets[axes.y].insert(z_index, mark)
    return mark


# def add_clade_box(
#     tree: ToyTree,
#     axes: Cartesian,
# ):
#     pass


if __name__ == "__main__":

    import toytree

    # base tree drawing
    tree = toytree.rtree.unittree(12)
    c, a, m = tree.draw(layout='r', scale_bar=True, node_sizes=5, width=400)
    m0 = tree.annotate.add_node_markers(
        a, 
        # color="idx",
        color=('idx',),
        yshift=-15, 
        opacity=0.3,
        # style={"fill-opacity": 0.1, "stroke-opacity": 0.5},
        )
    # m1 = tree.annotate.add_node_labels(a, font_size=20, yshift=-15)
    # m2 = tree.annotate.add_node_bars(
    #     a,
    #     bar_min=tree.get_node_data("height").values * 0.8,
    #     bar_max=tree.get_node_data("height").values * 2,
    #     size=0.33,
    #     z_index=-1,
    #     color='purple',
    #     opacity=1.0,
    #     style={"fill-opacity": 0.3, "stroke": None},
    #     # yshift=15,
    #     # xshift=15,
    # )
    toytree.utils.show(c, tmpdir="~")
