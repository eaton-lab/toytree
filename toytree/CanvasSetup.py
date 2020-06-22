#!/usr/bin/env python

"""
New Drawing class to create new mark and style on axes.
"""

# from copy import deepcopy, copy
from decimal import Decimal
import numpy as np
import toyplot

# from .Admixture import AdmixEdges

# for setting values from iterables
ITERABLE = (list, tuple, np.ndarray)



class GridSetup:
    """
    Returns Canvas and Cartesian axes objects to fit a grid of trees.
    """
    def __init__(self, nrows, ncols, width, height, layout):

        # style args can include height/width, nrows, ncols, shared,...
        self.nrows = nrows
        self.ncols = ncols
        self.width = width
        self.height = height
        self.layout = layout

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

        self.axes = [
            self.canvas.cartesian(
                grid=(self.nrows, self.ncols, i),
                padding=10,
                margin=25,
            )
            for i in range(self.nrows * self.ncols)
        ]


    def get_tree_dims(self):
        """
        get height and width if not set by user
        """
        if self.ncols * self.nrows < 4:
            minx = 250
            miny = 250
        else:
            minx = 200
            miny = 140

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
        if not all([i is None for i in self.style.tip_labels]):
            self.lname = max([len(str(i)) for i in self.style.tip_labels])

        # ntips and shape to fit with provided args
        self.get_dims_from_tree_size()

        # fills canvas and axes
        self.get_canvas_and_axes()

        # expand the domain/extents for the text
        # self.fit_tip_labels()

        # ticks for tree and scalebar
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

        """
        # style axes with padding and show axes
        self.axes.padding = self.style.padding

        if not self.external_axis:
            self.axes.show = True
            if not self.style.scalebar:
                self.axes.show = False

        # scalebar        
        if self.style.scalebar:
            if self.style.layout in ("r", "l"):
                nticks = max((3, np.floor(self.style.width / 100).astype(int)))
                self.axes.y.show = False
                self.axes.x.show = True
                self.axes.x.ticks.show = True

                # generate locations
                if self.style.use_edge_lengths:
                    th = self.tree.treenode.height
                else:
                    th = self.tree.treenode.get_farthest_leaf(True)[1] + 1
                if self.style.layout == "r":
                    top = self.style.xbaseline - th
                else:
                    top = self.style.xbaseline + th
                locs = np.linspace(self.style.xbaseline, top, nticks)

                # auto-formatter for axes ticks labels
                zer = abs(min(0, Decimal(locs[1]).adjusted()))
                fmt = "{:." + str(zer) + "f}"
                self.axes.x.ticks.locator = toyplot.locator.Explicit(
                    locations=locs,
                    labels=[fmt.format(i) for i in np.abs(locs)],
                    )

            elif self.style.layout in ("u", "d"):
                nticks = max((3, np.floor(self.style.height / 100).astype(int)))
                self.axes.x.show = False
                self.axes.y.show = True
                self.axes.y.ticks.show = True

                # generate locations
                if self.style.use_edge_lengths:
                    th = self.tree.treenode.height
                else:
                    th = self.tree.treenode.get_farthest_leaf(True)[1] + 1
                if self.style.layout == "d":
                    top = self.style.ybaseline + th
                else:
                    top = self.style.ybaseline - th
                locs = np.linspace(self.style.ybaseline, top, nticks)

                # auto-formatter for axes ticks labels
                zer = abs(min(0, Decimal(locs[1]).adjusted()))
                fmt = "{:." + str(zer) + "f}"
                self.axes.y.ticks.locator = toyplot.locator.Explicit(
                    locations=locs,
                    labels=[fmt.format(i) for i in np.abs(locs)],
                    )

            # elif self.style.layout == "d":
            #     nticks = max((3, np.floor(self.style.height / 100).astype(int)))
            #     self.axes.x.show = False
            #     self.axes.y.show = True
            #     self.axes.y.ticks.show = True            

            #     # generate locations
            #     locs = np.linspace(0, self.tree.treenode.height, nticks)

            #     # auto-formatter for axes ticks labels
            #     zer = abs(min(0, Decimal(locs[1]).adjusted()))
            #     fmt = "{:." + str(zer) + "f}"
            #     self.axes.y.ticks.locator = toyplot.locator.Explicit(
            #         locations=locs,
            #         labels=[fmt.format(i) for i in np.abs(locs)],
            #         )



    # def fit_tip_labels(self):
    #     """
    #     DEPRECATED SINCE V2 since Mark now sets its own extents correctly.

    #     Modifies display range to ensure tip labels fit. This is a bit hackish
    #     still. The problem is that the 'extents' range of the rendered text
    #     is not totally correct. So we add a little buffer here. Should add for 
    #     user to be able to modify this if needed. If not using edge lengths
    #     then need to use unit length for treeheight.
    #     """
    #     # bail on unrooted for now; TODO
    #     if self.style.layout == "c":
    #         return

    #     # if names
    #     if self.lname:
    #         # get ratio of names to tree in plot
    #         ratio = max(self.lname / 10, 0.15)

    #         # have tree figure make up 85% of plot
    #         if self.style.use_edge_lengths:
    #             addon = self.tree.treenode.height
    #         else:
    #             addon = self.tree.treenode.get_farthest_leaf(True)[1] + 1
    #         addon *= ratio

    #         # modify display for layout
    #         if self.style.layout == "r":
    #             self.axes.x.domain.max = (addon / 2.) + self.style.xbaseline
    #         elif self.style.layout == "l":
    #             self.axes.x.domain.min = (-addon / 2.) + self.style.xbaseline
    #             # self.axes.x.domain.min -= self.style.xbaseline
    #         elif self.style.layout == "d":
    #             self.axes.y.domain.min = (-addon / 2.) + self.style.ybaseline
    #         elif self.style.layout == "u":
    #             self.axes.y.domain.max = (addon / 2.) + self.style.ybaseline

    #         # print(addon, ratio, self.axes.x.domain.min, self.axes.x.domain.max)
