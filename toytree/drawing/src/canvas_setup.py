#!/usr/bin/env python

"""Canvas setup functions for single or grids of trees."""

import numpy as np
import toyplot


class GridSetup:
    """Return Canvas and Cartesian axes objects to fit a grid of trees."""

    def __init__(
        self,
        nrows,
        ncols,
        width,
        height,
        layout,
        margin,
        padding,
        scale_bar,
    ):

        # style args can include height/width, nrows, ncols, shared,...
        self.nrows = nrows
        self.ncols = ncols
        self.width = width
        self.height = height
        self.layout = layout
        self.margin = margin
        self.padding = padding
        self.scale_bar = scale_bar

        # get .canvas and .axes
        self.get_tree_dims()
        self.canvas = toyplot.Canvas(
            height=self.height,
            width=self.width,
        )
        self.axes = []
        self.get_axes()
        # self.get_axes_list()

    def get_axes(self):
        """
        Get a list of axes in the grid shape, and set margins to
        to make space for optional scale_bars and axes labels.
        """
        nplots = self.nrows * self.ncols
        grid = np.arange(nplots).reshape((self.nrows, self.ncols))

        for idx in range(nplots):
            if self.margin:
                margin = self.margin
            else:
                if self.nrows == 1:
                    margin = [50, 10, 50, 30]
                    # else:
                    # margin = [50, 20, 50, 20]
                else:
                    margin = [30, 30, 30, 30]
                    row, _ = np.where(grid == idx)
                    if row == 0:
                        margin[0] += 10
                        margin[2] -= 10
                    if row == self.nrows - 1:
                        margin[2] += 10
                        margin[0] -= 10
                # ...
                if self.scale_bar:
                    if self.layout in "du":
                        margin[3] += 20
                    elif self.layout in "lr":
                        margin[2] += 20
                margin = tuple(margin)

            axes = self.canvas.cartesian(
                grid=(self.nrows, self.ncols, idx),
                padding=self.padding,
                margin=margin,
            )
            axes.margin = margin
            self.axes.append(axes)

    def get_tree_dims(self):
        """
        get height and width if not set by user
        """
        # wider than tall
        if self.layout in ("d", "u"):
            minx = 225
            miny = 250
            self.width = self.width if self.width else min(750, minx * self.ncols)
            self.height = self.height if self.height else min(750, miny * self.nrows)

        else:
            minx = 250
            miny = 225
            self.height = self.height if self.height else min(750, minx * self.nrows)
            self.width = self.width if self.width else min(750, miny * self.ncols)


class CanvasSetup:
    """Return Canvas and Cartesian axes objects for drawing size.

    Sets values to style.height and style.width if not present. If a
    Canvas already exists a set of axes can be entered, instead of
    being generated anew.
    """

    def __init__(self, tree, axes, style):

        # args includes axes
        self.tree = tree
        self.axes = axes
        self.style = style
        self.canvas = None
        self.external_axis = False

        # get the longest name for dimension fitting
        self.lname = 0
        if self.style.tip_labels is not None:
            self.lname = max([len(str(i)) for i in self.style.tip_labels])

        # ntips and shape to fit with provided args
        self.get_canvas_height_and_width()

        # fills canvas and axes
        self.get_canvas_and_axes()

        # ticks for tree and scale_bar
        if self.style.scale_bar is False:
            if not self.external_axis:
                self.axes.x.show = False
                self.axes.y.show = False
        else:
            if style.use_edge_lengths:
                theight = self.tree.treenode.height
            else:
                # get number of nodes from farthest leaf to root
                ndists = self.tree.distance.get_node_distance_matrix(True)
                theight = ndists[self.tree.treenode.idx].max()
            set_axes_ticks_style(theight, self.axes, self.style, True)

    def get_canvas_height_and_width(self):
        """Calculate default canvas height&width given N tips and style."""
        if self.style.layout[0] == "c":
            radius = max([0] + [i for i in [self.style.height, self.style.width] if i])
            if not radius:
                radius = 400
            self.style.width = self.style.height = radius
            return

        # fit height and width by tree size.
        if self.style.layout in ("r", "l"):
            if not self.style.height:
                self.style.height = max(275, min(1000, 18 * self.tree.ntips))
            if not self.style.width:
                self.style.width = max(250, min(500, 250 + 5 * self.lname))
        else:
            if not self.style.height:
                self.style.height = max(250, min(500, 250 + 5 * self.lname))
            if not self.style.width:
                self.style.width = max(350, min(1000, 18 * self.tree.ntips))

    def get_canvas_and_axes(self):
        """Sets canvas and axes with dimensions and padding."""
        if self.axes is not None:
            self.canvas = None
            self.external_axis = True
        else:
            self.canvas = toyplot.Canvas(
                height=self.style.height,
                width=self.style.width,
            )
            self.axes = self.canvas.cartesian(padding=self.style.padding)


def set_axes_ticks_style(
    tree_height: float,
    axes: "toyplot.coordinates.Cartesian",
    style: "toytree.core.style.tree_style.TreeStyle",
    only_inside: bool = True,
) -> "toyplot.coordinates.Cartesian":
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
    style: TreeStyle
        A TreeStyle object with options for styling axes.
    only_inside: bool
        Option used by toyplot.locator.Extended to automatically find
        tick marks given the data range.
    """
    # the axes is either new or passed as an arg, and the scale_bar
    # arg is True or a (float, int), so we need to style the ticks.
    if style.layout in ("r", "l"):
        nticks = max((4, np.floor(style.width / 75).astype(int)))
        axes.y.show = False
        axes.x.show = True
        axes.x.ticks.show = True
    elif style.layout in ("u", "d"):
        nticks = max((4, np.floor(style.height / 75).astype(int)))
        axes.x.show = False
        axes.y.show = True
        axes.y.ticks.show = True
    # e.g., unrooted layout with axes shown (e.g., ts='p')
    else:
        # nticks = max((4, np.floor(style.height / 75).astype(int)))
        nticks = 5
        axes.x.show = False
        axes.y.show = False

    # get tick locator
    lct = toyplot.locator.Extended(count=nticks, only_inside=only_inside)

    # get root tree height
    if style.layout in ("r", "u"):
        locs = lct.ticks(-tree_height, -0)[0]
    else:
        locs = lct.ticks(0, tree_height)[0]

    # apply unit scaling
    if style.scale_bar is False:
        labels = abs(locs.copy())
    elif isinstance(style.scale_bar, (int, float)):
        labels = abs(locs / style.scale_bar)
    else:
        labels = abs(locs.copy())
    labels = [np.format_float_positional(i, precision=6, trim="-") for i in labels]

    # set the ticks locator
    if style.layout in ("r", "l"):
        axes.x.ticks.locator = toyplot.locator.Explicit(
            locations=locs + style.xbaseline,
            labels=labels,
        )
    elif style.layout in ("u", "d"):
        axes.y.ticks.locator = toyplot.locator.Explicit(
            locations=locs + style.ybaseline,
            labels=labels,
        )
    # print(locs, labels)
    return axes
