#!/usr/bin/env python

"""
New Drawing class to create new mark and style on axes.
"""

# from copy import deepcopy, copy
import numpy as np
import toyplot

# for setting values from iterables
ITERABLE = (list, tuple, np.ndarray)


class GridSetup:
    """
    Returns Canvas and Cartesian axes objects to fit a grid of trees.
    """
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
                    row, _ = np.where(grid==idx)
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
            self.width = (
                self.width if self.width else min(750, minx * self.ncols)
            )
            self.height = (
                self.height if self.height else min(750, miny * self.nrows)
            )

        else:
            minx = 250
            miny = 225
            self.height = (
                self.height if self.height else min(750, minx * self.nrows)
            )
            self.width = (
                self.width if self.width else min(750, miny * self.ncols)
            )



class CanvasSetup:
    """
    Returns Canvas and Cartesian axes objects, and sets values to
    style.height and style.width if not present.
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
        if not self.style.tip_labels is None:
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
                theight = self.tree.treenode.get_farthest_leaf(True)[1] + 1
            style_ticks(theight, self.axes, self.style, True)


    def get_canvas_height_and_width(self):
        """
        Calculate reasonable canvas height and width for tree given
        N tips and set values to self.style.
        """
        if self.style.layout == "c":
            radius = max(
                [0] + [i for i in [self.style.height, self.style.width] if i])
            if not radius:
                radius = 400
            self.style.width = self.style.height = radius
            return

        if self.style.layout in ("r", "l"):
            # height fit by tree size
            if not self.style.height:
                self.style.height = max(275, min(1000, 18 * self.tree.ntips))
            # width fit by name size
            if not self.style.width:
                self.style.width = max(250, min(500, 250 + 5 * self.lname))
        else:
            # height fit by name size
            if not self.style.height:
                self.style.height = max(250, min(500, 250 + 5 * self.lname))
            # width fit by tree size
            if not self.style.width:
                self.style.width = max(350, min(1000, 18 * self.tree.ntips))


    def get_canvas_and_axes(self):
        """
        Sets canvas and axes with dimensions and padding.
        """
        if self.axes is not None:
            self.canvas = None
            self.external_axis = True
        else:
            self.canvas = toyplot.Canvas(
                height=self.style.height,
                width=self.style.width,
            )
            self.axes = self.canvas.cartesian(
                padding=self.style.padding
            )


def style_ticks(
    tree_height: float,
    axes: 'toyplot.coordinates.Cartesian',
    style: 'toytree.core.style.tree_style.TreeStyle',
    only_inside: bool=True,
    ) -> 'toyplot.coordinates.Cartesian':
    """
    Returns a Cartesian axes object with toyplot.locator.Extended
    ticks locations and labels set as Explicit ticks (wont't change
    even if data change) and are styled according to a style dict and
    the only_side arg.
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
    labels = [np.format_float_positional(i, precision=6, trim='-') for i in labels]

    # set the ticks locator
    if style.layout in ("r", "l"):
        axes.x.ticks.locator = toyplot.locator.Explicit(
            locations=locs + style.xbaseline,
            labels=labels,
        )
    else:
        axes.y.ticks.locator = toyplot.locator.Explicit(
            locations=locs + style.ybaseline,
            labels=labels,
        )
    # print(locs, labels)
    return axes
