#!/usr/bin/env python

"""
New Drawing class to create new mark and style on axes.
"""

# from copy import deepcopy, copy
from decimal import Decimal
import numpy as np
import toyplot

# for setting values from iterables
ITERABLE = (list, tuple, np.ndarray)


class GridSetup:
    """
    Returns Canvas and Cartesian axes objects to fit a grid of trees.
    """
    def __init__(self, nrows, ncols, width, height, layout, margin):

        # style args can include height/width, nrows, ncols, shared,...
        self.nrows = nrows
        self.ncols = ncols
        self.width = width
        self.height = height
        self.layout = layout
        self.margin = margin

        # get .canvas and .axes
        self.get_tree_dims()
        self.get_canvas_and_axes()


    def get_canvas_and_axes(self):
        """
        Set .canvas and .axes objects
        """
        self.canvas = toyplot.Canvas(
            height=self.height,
            width=self.width,
        )

        # set larger margin on top and bottom rows, and even margin
        # for middle rows.
        self.axes = []
        nplots = self.nrows * self.ncols
        grid = np.arange(nplots).reshape((self.nrows, self.ncols))

        for idx in range(nplots):
            if self.margin:
                margin = self.margin

            else:
                row, col = np.where(grid==idx)
                if row == 0:
                    top = 50
                    bottom = 25
                elif row == self.nrows - 1:
                    top = 25
                    bottom = 50
                else:
                    if row == (self.nrows - 1) / 2:
                        top = bottom = 75 / 2.
                    elif row < (self.nrows - 1) / 2:
                        top = 42.5
                        bottom = 32.5
                    else:
                        top = 32.5
                        bottom = 42.5

                if col == 0:
                    left = 50
                    right = 25
                elif col == self.ncols - 1:
                    right = 50
                    left = 25
                else:
                    if col == (self.ncols - 1) / 2:
                        left = right = 75 / 2
                    elif col < (self.ncols - 1) / 2:
                        left = 42.5
                        right = 32.5
                    else:
                        left = 32.5
                        right = 42.5

                margin = (top, right, bottom, left)

            axes = self.canvas.cartesian(
                grid=(self.nrows, self.ncols, idx),
                padding=10,
                margin=margin,
            )
            self.axes.append(axes)


    def get_tree_dims(self):
        """
        get height and width if not set by user
        """
        if self.ncols * self.nrows < 4:
            minx = 250
            miny = 250
        else:
            minx = 200
            miny = 200

        # wider than tall
        if self.layout in ("d", "u"):
            self.width = (
                self.width if self.width
                else min(750, minx * self.ncols)
            )
            self.height = (
                self.height if self.height
                else min(750, miny * self.nrows)
            )

        else:
            self.height = (
                self.height if self.height
                else min(750, minx * self.nrows)
            )
            self.width = (
                self.width if self.width
                else min(750, miny * self.ncols)
            )



class CanvasSetup:
    """
    Returns Canvas and Cartesian axes objects
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
            # all([i is None for i in self.style.tip_labels]):
            self.lname = max([len(str(i)) for i in self.style.tip_labels])

        # ntips and shape to fit with provided args
        self.get_dims_from_tree_size()

        # fills canvas and axes
        self.get_canvas_and_axes()

        # expand the domain/extents for the text
        # self.fit_tip_labels()

        # ticks for tree and scale_bar
        self.add_axes_style()


    def get_dims_from_tree_size(self):
        """
        Calculate reasonable canvas height and width for tree given N tips
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


    def add_axes_style(self):
        """
        Adds scale_bar and attempts nice tick formatting
        TODO: can be improved, especially for small int intervals.
        """
        # style axes with padding and show axes
        self.axes.padding = self.style.padding

        if not self.external_axis:
            self.axes.show = True
            if not self.style.scale_bar:
                self.axes.show = False

        # scale_bar
        if self.style.scale_bar:
            if self.style.layout in ("r", "l"):
                nticks = max((4, np.floor(self.style.width / 75).astype(int)))
                self.axes.y.show = False
                self.axes.x.show = True
                self.axes.x.ticks.show = True
                lct = toyplot.locator.Extended(count=nticks, only_inside=True)

                # get root tree height
                if self.style.use_edge_lengths:
                    theight = self.tree.treenode.height
                else:
                    theight = self.tree.treenode.get_farthest_leaf(True)[1] + 1
                if self.style.layout == "r":
                    locs = lct.ticks(-theight, 0)[0]
                else:
                    locs = lct.ticks(0, theight)[0]
                float_limit = abs(min([0] + [
                    Decimal(i).adjusted() for i in locs
                ]))
                if abs(locs).max() < 3 and locs.size < 3:
                    float_limit += 1
                fmt = "{:." + str(float_limit) + "f}"
                self.axes.x.ticks.locator = toyplot.locator.Explicit(
                    locations=locs + self.style.xbaseline,
                    labels=[fmt.format(i) for i in np.abs(locs)],
                )

            elif self.style.layout in ("u", "d"):
                nticks = max((4, np.floor(self.style.height / 75).astype(int)))
                self.axes.x.show = False
                self.axes.y.show = True
                self.axes.y.ticks.show = True
                lct = toyplot.locator.Extended(count=nticks, only_inside=True)

                # generate locations
                if self.style.use_edge_lengths:
                    theight = self.tree.treenode.height
                else:
                    theight = self.tree.treenode.get_farthest_leaf(True)[1] + 1
                if self.style.layout == "u":
                    locs = lct.ticks(-theight, 0)[0]
                else:
                    locs = lct.ticks(0, theight)[0]
                float_limit = abs(min([0] + [
                    Decimal(i).adjusted() for i in locs
                ]))
                if abs(locs).max() < 3 and locs.size < 3:
                    float_limit += 1
                fmt = "{:." + str(float_limit) + "f}"
                self.axes.y.ticks.locator = toyplot.locator.Explicit(
                    locations=locs + self.style.ybaseline,
                    labels=[fmt.format(i) for i in np.abs(locs)],
                )
