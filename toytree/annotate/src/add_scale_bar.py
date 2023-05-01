#!/usr/bin/env python

"""Modify ticks and labels on tree time axis into a scale bar.

"""

import numpy as np
from toytree import ToyTree
import toyplot
from toyplot.coordinates import Cartesian

from toytree.core.apis import add_subpackage_method, AnnotationAPI
from toytree.annotate.src.annotation_mark import (
    get_last_toytree_mark_from_cartesian,
    assert_tree_matches_mark)

__all__ = [
    "add_axes_scale_bar",
]


@add_subpackage_method(AnnotationAPI)
def add_axes_scale_bar(
    tree: ToyTree,
    axes: Cartesian,
    only_inside: bool = True,
    # above/below,
    # padding,margin,near,far...
    # positive/negative time,
) -> Cartesian:
    """Return a toyplot Cartesian object with custom tick marks.

    This gets tick locations first using toyplot.locator.Extended and
    then sets labels on them using toyplot.locator.Explicit, because
    we need time scale bar to be non-negative when axes are rotated
    for trees facing different directions.

    Note
    -----
    Some work is done internally to try to nicely handle floating point
    precision.

    Parameters
    ----------
    ...
    only_inside: bool
        Option used by toyplot.locator.Extended to automatically find
        tick marks given the data range.
    """
    mark = get_last_toytree_mark_from_cartesian(axes)
    assert_tree_matches_mark(tree, mark)

    # the axes is either new or passed as an arg, and the scale_bar
    # arg is True or a (float, int), so we need to style the ticks.
    if mark.layout in ("r", "l"):
        cwidth = axes._xmax_range - axes._xmin_range
        nticks = max((5, np.floor(cwidth / 75).astype(int)))
        axes.show = True
        axes.y.show = False
        axes.x.show = True
        axes.x.ticks.show = True
        left, right = mark.domain('x')
        tree_height = right - left

    # ...
    elif mark.layout in ("u", "d"):
        cheight = axes._ymax_range - axes._ymin_range
        nticks = max((5, np.floor(cheight / 75).astype(int)))
        axes.show = True
        axes.x.show = False
        axes.y.show = True
        axes.y.ticks.show = True
        bottom, top = mark.domain('y')
        tree_height = top - bottom

    # e.g., unrooted layout with axes shown (e.g., ts='p')
    else:
        # nticks = max((4, np.floor(style.height / 75).astype(int)))
        nticks = 5
        axes.x.show = False
        axes.y.show = False
        raise NotImplementedError("get tree_height")

    # get tick locator
    # lct = toyplot.locator.Extended(count=nticks, only_inside=only_inside)
    lct = toyplot.locator.Extended(count=nticks, only_inside=False)

    # get root tree height
    if mark.layout in ("r", "u"):
        locs = lct.ticks(-tree_height, -0)[0]
        locs = locs[locs >= -tree_height]
    else:
        locs = lct.ticks(0, tree_height)[0]
        locs = locs[locs <= tree_height]

    # apply unit scaling
    if mark.scale_bar is False:
        labels = abs(locs.copy())
    elif isinstance(mark.scale_bar, (int, float)):
        labels = abs(locs / mark.scale_bar)
    else:
        labels = abs(locs.copy())
    labels = [np.format_float_positional(i, precision=6, trim="-") for i in labels]

    # set the ticks locator
    if mark.layout in ("r", "l"):
        axes.x.ticks.locator = toyplot.locator.Explicit(
            locations=locs + mark.xbaseline,
            labels=labels,
        )
    elif mark.layout in ("u", "d"):
        axes.y.ticks.locator = toyplot.locator.Explicit(
            locations=locs + mark.ybaseline,
            labels=labels,
        )
    # print(locs, labels)
    return axes


if __name__ == "__main__":

    pass
