#!/usr/bin/env python

"""Add Pie Chart Marks at nodes or edges.

"""

from typing import Sequence, Union, TypeVar

from loguru import logger
import numpy as np
from toytree.core import ToyTree, Cartesian, Mark
from toytree.style import check_arr, get_color_mapped_values
from toytree.annotate.src.checks import get_last_toytree_mark, assert_tree_matches_mark
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.annotate.src.add_edge_markers import get_edge_midpoints
from toytree.drawing.src.mark_pie import PieChartMark
from toytree.style.src.validate_data import (
    validate_numeric,
    validate_mask,
)

logger = logger.bind(name="toytree")
Color = TypeVar("Color", str, tuple, np.ndarray)
__all__ = [
    "add_node_pie_charts",
    "add_edge_pie_charts",
]


def validate_pie_data(
    tree: ToyTree,
    data: np.ndarray,
    # min_size: float = 1e-9,
    # mask: np.ndarray = None,
) -> np.ndarray:
    """Return cleaned pie chart data.

    Checks pie chart data for correct shape and type, and that the row
    values sum to 1.

    Formats
    -------
    - 1-D array -> 2-D array
    - 2-D array -> 2-D array sums to 1
    """
    assert data.min() >= 0, "negative values are not allowed in pie chart data."
    assert data.shape[0] in (tree.nnodes, tree.nnodes - 1), (
        f"pie chart data must be shape (nnodes, nvalues), your data is {data.shape}.")

    # allow single value arrays in [0, 1] to represent two categories
    if data.ndim == 1:
        if data.max() > 1:
            raise ValueError(
                "1 dimensional array data for pie charts must be < 1 to "
                "be expanded to 2 categories: (value, 1 - value).")
        return np.column_stack([data, 1 - data])

    # 2D arrays represent (ntips, ntraits) data.
    else:
        assert np.allclose(data.sum(axis=1), 1), "pie chart data row values must sum to 1."
    return data


@add_subpackage_method(AnnotationAPI)
def add_node_pie_charts(
    tree: ToyTree,
    axes: Cartesian,
    data: np.ndarray,
    size: Union[int, Sequence[int]] = 10,
    colors: Union[Sequence[Color], Color] = None,
    ostroke: Color = "#262626",
    ostroke_width: float = 1.5,
    istroke: Color = "#262626",
    istroke_width: float = 0.,
    rotate: int = -45,
    mask: Union[bool, np.ndarray, tuple] = False,
    xshift: int = 0,
    yshift: int = 0,
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
    colors: None, str, tuple, or array, or Sequence
        Color for each category/trait or the name of a colormap.
    ostroke: Color
        Color of the stroke on the outside of the Mark.
    ostroke_width: float
        Width of the stroke on the outside of the Mark
    istroke: Color
        Color of the stroke on the inside of the Mark between wedges.
    istroke_width: float
        Width of the stroke on the inside of the Mark between wedges.
    rotate: int
        Rotate the starting point of the wedges.
    mask: bool, np.ndarray, or tuple
        Node mask to hide/show some or all Nodes.
    xshift: int
        Shift marker horizontally by px units (+=right, -=left).
    yshift: int
        Shift marker vertically by px units (+=down, -=up).

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
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # get mask
    mask = validate_mask(tree, style={"node_mask": mask})

    # check and cleanup data input.
    # TODO: option to collapse categories below a minimum percentage
    data = validate_pie_data(tree, data)

    # expand colormap to an array of colors
    if colors is None:
        colors = "Set2"
    if isinstance(colors, (tuple, list, np.ndarray)):
        pass
    else:
        colors = get_color_mapped_values(range(data.shape[1]), colors)

    # ensure conversion of colors to array type and size=ncategories
    colors = check_arr(
        values=colors,
        label="colors (pie chart category colors)",
        size=data.shape[1],
        ctype=np.void,
    )
    sizes = validate_numeric(
        tree, key="size", size=tree.nnodes, style={"size": size})[mask]

    # mask some Nodes
    data = data[mask, :]
    coords = mark.ntable[mask, :]

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
        xshift=xshift,
        yshift=yshift,
    )
    axes.add_mark(mark)
    return mark


@add_subpackage_method(AnnotationAPI)
def add_edge_pie_charts(
    tree: ToyTree,
    axes: Cartesian,
    data: np.ndarray,
    size: Union[int, Sequence[int]] = 10,
    colors: Union[Sequence[Color], Color] = None,
    ostroke: Color = "#262626",
    ostroke_width: float = 1.5,
    istroke: Color = "#262626",
    istroke_width: float = 0.,
    rotate: int = -45,
    mask: Union[bool, np.ndarray, tuple] = False,
    xshift: int = 0,
    yshift: int = 0,
) -> Mark:
    """Return a toyplot Mark of edge pie charts added to a tree plot.

    This adds edge pie chart markers to the last tree drawn on the
    Cartesian axes.

    Parameters
    ----------
    axes: Cartesian
        A toyplot Cartesian axes object containing a tree drawing.
    data: numpy.ndarray
        Array of shape(ncategories, nnodes) with rows summing to 1. 
    size: int or Sequence[int]
        Size of markers as single int or Sequence of ints, in px units.
    colors: None, str, tuple, or array, or Sequence
        Color for each category/trait or the name of a colormap.
    ostroke: Color
        Color of the stroke on the outside of the Mark.
    ostroke_width: float
        Width of the stroke on the outside of the Mark
    istroke: Color
        Color of the stroke on the inside of the Mark between wedges.
    istroke_width: float
        Width of the stroke on the inside of the Mark between wedges.
    rotate: int
        Rotate the starting point of the wedges.
    mask: bool, np.ndarray, or tuple
        Node mask to hide/show some or all Nodes.
    xshift: int
        Shift marker horizontally by px units (+=right, -=left).
    yshift: int
        Shift marker vertically by px units (+=down, -=up).

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
    >>> tree.annotate.add_edge_pie_charts(
    >>>     axes=axes, data=arr, size=20, mask=False,
    >>>     istroke_width=0.75, istroke="black", rotate=-45,
    >>> )
    """
    # get mark for coordinates on plotted tree.
    mark = get_last_toytree_mark(axes)
    assert_tree_matches_mark(tree, mark)

    # get coordinates of all real edges
    nedges = tree.nnodes - 2 if tree.is_rooted() else tree.nnodes - 1
    #coords = _get_edge_midpoints(tree, mark.ntable, mark.layout, mark.edge_type)
    coords = get_edge_midpoints(mark.etable, mark.ntable, mark.layout, mark.edge_type)

    mask = validate_mask(tree, style={"node_mask": mask})[:nedges]

    # validate data.
    # TODO: option to collapse categories below a minimum percentage
    data = validate_pie_data(tree, data)

    # expand colormap to ncolor (note: not nedges)
    if colors is None:
        colors = "Set2"
    if isinstance(colors, (tuple, list, np.ndarray)):
        pass
    else:
        colors = get_color_mapped_values(range(data.shape[1]), colors)

    # ensure conversion of colors to array type and size=ncategories
    colors = check_arr(
        values=colors,
        label="colors (pie chart category colors)",
        size=data.shape[1],
        ctype=np.void,
    )

    # mask some Nodes
    data = data[:nedges][mask, :]
    sizes = validate_numeric(
        tree, key="size", size=tree.nnodes, style={"size": size})[:nedges][mask]

    coords = coords[:nedges][mask, :]

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
        xshift=xshift,
        yshift=yshift,
    )
    axes.add_mark(mark)
    return mark


if __name__ == "__main__":

    import toytree
    tree = toytree.rtree.unittree(6, seed=123)
    canvas, axes, m0 = tree.draw()
    # generate random pie-like (proportion) data array
    import numpy as np
    ncategories = 3
    arr = np.random.random(size=(tree.nnodes, ncategories))
    arr = (arr.T / arr.sum(axis=1)).T

    # add pie charts to all internal Nodes
    tree.annotate.add_node_pie_charts(
        axes=axes,
        data=arr,
        size=20,
        mask=False,
        istroke_width=0.75,
        istroke="black",
        rotate=0,
        colors="Greys"
    )
    toytree.utils.show(canvas)
