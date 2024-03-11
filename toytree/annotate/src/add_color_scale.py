#!/usr/bin/env python

"""Add a color_scale to Cartesian axes.

"""

from typing import Optional, Mapping, Any
from loguru import logger
import toyplot
from toytree import ToyTree
from toytree.core import Cartesian
from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.style.src.validate_utils import substyle_dict_to_css_dict
# from toytree.annotate.src.checks import get_last_toytree_mark, assert_tree_matches_mark
from toytree.drawing.src.mark_annotation import AnnotationRect  # AnnotationMarker


logger = logger.bind(name="toytree")


# def add_marker_legend(
#     tree: ToyTree,
#     axes: Cartesian,
#     colormap: toyplot.color.Map,
# ) -> None:
#     """...

#     """
#     # get_last_cartesian_axes_from_toytree()
#     axes = tree._last_axes


def add_color_scale_from_feature(
    tree: ToyTree,
    axes: Cartesian,
    feature: str,
    colormap: toyplot.color.Map = None,
    width: Optional[int] = None,
    angle: float = 0.,
    style: Mapping[str, Any] = None,
) -> AnnotationRect:
    """Return color map...

    Extracts the colormap and data domain range from the ToyTreeMark
    which has a plotted feature.

    Examples
    --------
    >>> c, a, m = tree.draw(node_labels="dist")
    >>> tree.annotate.add_color_scale_from_feature("node_labels", xpos=50, ypos=-50)
    >>> # ...
    """


# @add_subpackage_method(AnnotationAPI)
def add_color_scale(
    axes: Cartesian,
    xpos: float = 50,
    ypos: float = -50,
    colormap: toyplot.color.Map = None,
    min: float = 0.,
    max: float = 1.,
    width: Optional[int] = None,
    angle: float = 0.,
    style: Mapping[str, Any] = None,
) -> AnnotationRect:
    """Return ... with color_scale ...

    Add a color scale to a Canvas as a rectangle filled with a color or
    linear gradient of colors. This is an alternative implementation of
    toyplot's add_color_scale method with the aim of having the color
    scale act as a Mark instead of a Numberline axis.

    Parameters
    ----------
    axes: Cartesian
        ...
    xpos: float
        Horizontal position of color scale bar start.
    ypos: float
        Vertical position of color scale bar start.
    colormap: str, toyplot.color.Map, or None
        ...
    min: float
        Value mapped to the minimum (start) color in map.
    max: float
        Value mapped to the maximum (end) color in map.

    See Also
    --------
    toyplot.coordinates.Cartesian.add_color_scale

    Examples
    --------
    # create a color scale given 
    """
    canvas = axes._scenegraph.source("render", axes)
    canvas.color_scale(
        colormap=colormap,
        x1=self._xmax_range + width + self._padding,
        x2=self._xmax_range + width + self._padding,
        y1=self._ymax_range,
        y2=self._ymin_range,
        width=width,
        padding=padding,
        show=True,
        label=label,
        ticklocator=tick_locator,
        scale="linear",
        )
    return axis    


if __name__ == "__main__":
    pass
