#!/usr/bin/env python

"""Canvas setup functions for single or grids of trees."""

from typing import Optional, Tuple, TypeVar, Union
from loguru import logger

from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian
from toyplot.mark import Mark

logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")


def get_linear_width_and_height(mark: Mark) -> Tuple[int, int]:
    """Get width,height to fit the ToyTree Mark given its extents.
    """
    # get space needed for tip labels to not overlap
    ext = mark.extents(['x', 'y'])[1]
    if mark.layout in "rl":
        exts = ext[3] - ext[2]
    else:
        exts = ext[1] - ext[0]
    name_vspace = sum(exts[:mark.ttable.shape[0]]) * 1.15

    # get space needed for tip labels to fit on canvas
    ext = mark.extents(['x', 'y'])[1]
    if mark.layout in "rl":
        exts = ext[1] - ext[0]
    else:
        exts = ext[3] - ext[2]
    name_hspace = max(exts[:mark.ttable.shape[0]])# 2

    # get depth of tree to show edge, nodes, etc.
    tree_depth = max(100, 5 * mark.ttable.shape[0])
    tree_depth = min(300, 5 * mark.ttable.shape[0])

    # add 100 to each dimension for margin; limit w,h = (800, 1000)
    width = tree_depth + name_hspace + 100
    height = name_vspace + 100

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
    """TODO."""
    return 500, 500


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
        canvas = Canvas(height=height, width=width)
        axes = canvas.cartesian(padding=padding, margin=margin)

    # tree is being plotted on an existing set of axes
    else:
        canvas = None
    return canvas, axes


# class CanvasSetup:
#     """Return Canvas and Cartesian axes objects for drawing size.

#     Sets values to style.height and style.width if not present. If a
#     Canvas already exists a set of axes can be entered, instead of
#     being generated anew.
#     """

#     def __init__(self, tree, axes, style):

#         # args includes axes
#         self.tree = tree
#         self.axes = axes
#         self.style = style
#         self.canvas = None
#         self.external_axis = False

#         # get the longest name for dimension fitting
#         self.lname = 0
#         if self.style.tip_labels is not None:
#             self.lname = max([len(str(i)) for i in self.style.tip_labels])

#         # ntips and shape to fit with provided args
#         self.get_canvas_height_and_width()

#         # fills canvas and axes
#         self.get_canvas_and_axes()

#         # ticks for tree and scale_bar
#         if self.style.scale_bar is False:
#             if not self.external_axis:
#                 self.axes.x.show = False
#                 self.axes.y.show = False
#         else:
#             if style.use_edge_lengths:
#                 theight = self.tree.treenode.height
#             else:
#                 # get number of nodes from farthest leaf to root
#                 ndists = self.tree.distance.get_node_distance_matrix(True)
#                 theight = ndists[self.tree.treenode.idx].max()
#             set_axes_ticks_style(theight, self.axes, self.style, True)

#     def get_canvas_height_and_width(self):
#         """Calculate default canvas height&width given N tips and style."""
#         if self.style.layout[0] == "c":
#             radius = max([0] + [i for i in [self.style.height, self.style.width] if i])
#             if not radius:
#                 radius = 400
#             self.style.width = self.style.height = radius
#             return

#         # fit height and width by tree size.
#         if self.style.layout in ("r", "l"):
#             if not self.style.height:
#                 self.style.height = max(275, min(1000, 18 * self.tree.ntips))
#             if not self.style.width:
#                 self.style.width = max(250, min(500, 250 + 5 * self.lname))
#         else:
#             if not self.style.height:
#                 self.style.height = max(250, min(500, 250 + 5 * self.lname))
#             if not self.style.width:
#                 self.style.width = max(350, min(1000, 18 * self.tree.ntips))

#     def get_canvas_and_axes(self):
#         """Sets canvas and axes with dimensions and padding."""
#         if self.axes is not None:
#             self.canvas = None
#             self.external_axis = True
#         else:
#             self.canvas = toyplot.Canvas(
#                 height=self.style.height,
#                 width=self.style.width,
#             )
#             self.axes = self.canvas.cartesian(padding=self.style.padding)


# def set_axes_ticks_style(
#     tree_height: float,
#     axes: Cartesian,
#     style: TreeStyle,
#     only_inside: bool = True,
# ) -> Cartesian:
#     """Return a toyplot Cartesian object with custom tick marks.

#     This gets tick locations first using toyplot.locator.Extended and
#     then sets labels on them using toyplot.locator.Explicit, because
#     we need time scale bar to be non-negative when axes are rotated
#     for trees facing different directions.

#     Note
#     -----
#     Some work is done internally to try to nicely handle floating point
#     precision.

#     Parameters
#     ----------
#     ...
#     style: TreeStyle
#         A TreeStyle object with options for styling axes.
#     only_inside: bool
#         Option used by toyplot.locator.Extended to automatically find
#         tick marks given the data range.
#     """
#     # the axes is either new or passed as an arg, and the scale_bar
#     # arg is True or a (float, int), so we need to style the ticks.
#     if style.layout in ("r", "l"):
#         nticks = max((4, np.floor(style.width / 75).astype(int)))
#         axes.y.show = False
#         axes.x.show = True
#         axes.x.ticks.show = True
#     elif style.layout in ("u", "d"):
#         nticks = max((4, np.floor(style.height / 75).astype(int)))
#         axes.x.show = False
#         axes.y.show = True
#         axes.y.ticks.show = True
#     # e.g., unrooted layout with axes shown (e.g., ts='p')
#     else:
#         # nticks = max((4, np.floor(style.height / 75).astype(int)))
#         nticks = 5
#         axes.x.show = False
#         axes.y.show = False

#     # get tick locator
#     lct = toyplot.locator.Extended(count=nticks, only_inside=only_inside)

#     # get root tree height
#     if style.layout in ("r", "u"):
#         locs = lct.ticks(-tree_height, -0)[0]
#     else:
#         locs = lct.ticks(0, tree_height)[0]

#     # apply unit scaling
#     if style.scale_bar is False:
#         labels = abs(locs.copy())
#     elif isinstance(style.scale_bar, (int, float)):
#         labels = abs(locs / style.scale_bar)
#     else:
#         labels = abs(locs.copy())
#     labels = [np.format_float_positional(i, precision=6, trim="-") for i in labels]

#     # set the ticks locator
#     if style.layout in ("r", "l"):
#         axes.x.ticks.locator = toyplot.locator.Explicit(
#             locations=locs + style.xbaseline,
#             labels=labels,
#         )
#     elif style.layout in ("u", "d"):
#         axes.y.ticks.locator = toyplot.locator.Explicit(
#             locations=locs + style.ybaseline,
#             labels=labels,
#         )
#     # print(locs, labels)
#     return axes


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

