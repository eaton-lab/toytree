#!/usr/bin/env python

"""Canvas setup functions for single or grids of trees."""

from typing import Optional, Tuple, TypeVar, Union

from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark

ToyTree = TypeVar("ToyTree")

# Heuristic sizing constants for linear layouts.
SPAN_SCALE = 1.15
TREE_DEPTH_PER_TIP = 5.0
TREE_DEPTH_MIN = 100.0
TREE_DEPTH_MAX = 300.0
LABEL_SPAN_MIN = 175.0
LABEL_SPAN_MAX = 900.0
LABEL_DEPTH_MIN = 0.0
LABEL_DEPTH_MAX = 600.0
MARGIN_PAD = 100.0

# Heuristic sizing constants for circular and fan layouts.
CIRCULAR_BASE_SIZE = 500
CIRCULAR_MIN_SHORT = 280
CIRCULAR_MAX_LONG = 900
_SPAN_EPS = 1e-9


def get_linear_width_and_height(mark: Mark) -> Tuple[int, int]:
    """Return (width, height) px units to fit ToyTree Mark.

    Using the calculated extents of the tip labels, and the linear layout
    direction, and the tree size, calculate a reasonable canvas size to
    fit the tree -- in the case that user did not enter a height or width
    override.
    """
    _, ext = mark.extents(["x", "y"])
    ntips = int(mark.ttable.shape[0])

    # Choose span/depth extents relative to linear layout direction.
    if mark.layout in "rl":
        span_ext = ext[3][:ntips] - ext[2][:ntips]
        depth_ext = ext[1][:ntips] - ext[0][:ntips]
    else:
        span_ext = ext[1][:ntips] - ext[0][:ntips]
        depth_ext = ext[3][:ntips] - ext[2][:ntips]

    # first calculate space needed for the labels
    label_depth_max = float(max(depth_ext)) if ntips else 0.0

    # also get the span space needed
    label_span_total = float(sum(span_ext)) * SPAN_SCALE

    # ...
    tree_depth = TREE_DEPTH_PER_TIP * ntips

    # Apply per-component bounds before combining into width / height.
    label_span_total = max(LABEL_SPAN_MIN, min(LABEL_SPAN_MAX, label_span_total))
    label_depth_max = max(LABEL_DEPTH_MIN, min(LABEL_DEPTH_MAX, label_depth_max))
    tree_depth = max(TREE_DEPTH_MIN, min(TREE_DEPTH_MAX, tree_depth))

    width = tree_depth + label_depth_max + MARGIN_PAD
    height = label_span_total + MARGIN_PAD

    # ... min: (350, 300)
    if mark.layout in "ud":
        width, height = height, width
        height = max(300, min(600, height))
        width = max(300, min(800, width))

    # ... min: (350, 1000)
    else:
        width = max(300, min(800, width))
        height = min(1000, max(275, height))
    return width, height


def get_circular_width_and_height(mark: Mark) -> Tuple[int, int]:
    """Return ``(width, height)`` px units to fit circular / fan layouts.

    The mark domain already encodes whether a circular layout is full
    circle or partial fan. Full-circle domains are square while fans are
    rectangular. We keep the long axis at ``CIRCULAR_BASE_SIZE`` and scale
    the short axis by domain ratio so fan layouts use space efficiently.
    """
    xmin, xmax = mark.domain("x")
    ymin, ymax = mark.domain("y")
    xspan = max(abs(float(xmax - xmin)), _SPAN_EPS)
    yspan = max(abs(float(ymax - ymin)), _SPAN_EPS)

    if xspan >= yspan:
        width = CIRCULAR_BASE_SIZE
        height = int(round(CIRCULAR_BASE_SIZE * (yspan / xspan)))
    else:
        height = CIRCULAR_BASE_SIZE
        width = int(round(CIRCULAR_BASE_SIZE * (xspan / yspan)))

    width = max(CIRCULAR_MIN_SHORT, min(CIRCULAR_MAX_LONG, width))
    height = max(CIRCULAR_MIN_SHORT, min(CIRCULAR_MAX_LONG, height))
    return int(width), int(height)


def get_canvas_and_axes(
    axes: Optional[Cartesian],
    mark: Mark,
    width: Optional[int],
    height: Optional[int],
    padding: int = 15,
    margin: int = 50,
) -> Union[Tuple[Canvas, Cartesian], Tuple[None, Cartesian]]:
    """Get Canvas, Cartesian for a ToyTree drawing."""
    # Create new Carteian to plot tree onto
    if axes is None:
        if mark.layout in "rlud":
            _width, _height = get_linear_width_and_height(mark)
            if width is None:
                width = _width
            if height is None:
                height = _height
        else:
            _width, _height = get_circular_width_and_height(mark)
            if width is None:
                width = _width
            if height is None:
                height = _height

        # create canvas and axes
        # cast height/width to float to avoid bug with toyplot.Canvas
        # passing np.float() into the output javascript, which killed rendering
        canvas = Canvas(height=float(height), width=float(width))
        axes = canvas.cartesian(padding=padding, margin=margin)

    # tree is being plotted on an existing set of axes
    else:
        canvas = None
    return canvas, axes


if __name__ == "__main__":
    import toytree

    t0 = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")
    t0 = t0.root("~.*prz*")
    c0, _, _ = t0.draw()
    print(c0.width, c0.height)

    t1 = toytree.rtree.unittree(26)
    c1, _, _ = t1.draw()
    print(c1.width, c1.height)

    toytree.utils.show([c0, c1])
