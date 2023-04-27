#!/usr/bin/env python

"""Add a color_scale to Cartesian axes.

"""

import toyplot
from toyplot.coordinates import Cartesian


def add_marker_legend(
    tree: ToyTree,
    axes: Cartesian,
    colormap: toyplot.color.Map,
) -> None:
    """...

    """
    # get_last_cartesian_axes_from_toytree()
    axes = tree._last_axes
    


def add_color_scale(
    axes: Cartesian,
    colormap: toyplot.color.Map,
) -> None:
    """Return ... with color_scale ...

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
