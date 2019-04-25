#!/usr/bin/env python

"""
Classes for Drawings from MultiTrees.
"""
import numpy as np
import toyplot
from .TreeStyle import TreeStyle


class TreeGrid:
    """
    Easily create Toyplot gridded canvases for plotting multiple trees.
    """
    def __init__(self, treelist):
        
        # plot objects are init on update()
        self.canvas = None
        self.treelist = treelist
        self.treeslice = []

        # subtree styles are stripped when MultiTree init, but can be added.
        #self.style = TreeStyle('n')

        # to be filled
        self.x = None
        self.y = None


    def update(self, x, y, start, shared_axis, **kwargs):

        # store plot dims and assert that they fit well enough
        self.x = x
        self.y = y
        self.treeslice = self.treelist[start:start + self.x * self.y]

        # TODO: mess with padding and margins...
        wdef = min(1000, self.y * 300)
        hdef = min(1000, self.x * 300)
        self.canvas = toyplot.Canvas(
            width=(kwargs.get('width') if kwargs.get('width') else wdef), 
            height=(kwargs.get('height') if kwargs.get('height') else hdef),

        ) 

        if not shared_axis:
            # get max treeheight
            for tidx, tree in enumerate(self.treeslice):
                # set ymax on cartesian so that trees are on same scale
                axes = self.canvas.cartesian(
                    grid=(self.x, self.y, tidx),
                    margin=(20, 20, 35, 35),
                    padding=10,
                )
                # update tree style with any new arguments
                tree.draw(axes=axes)
                axes.show = False

        # TODO: shared axis
        else:    
            # only one axis allowed?... x=1 or y=1
            kwargs["orient"] = "down"
            axes = self.canvas.cartesian(padding=15)
            xbaseline = 0
            maxheight = 0
            for tidx, tree in enumerate(self.treeslice):
                tree.draw(axes=axes, xbaseline=xbaseline, **kwargs)
                xbaseline += tree.ntips + 1
                maxheight = max(maxheight, tree.treenode.height)

            nticks = 5  # max((3, np.floor(self.style.height / 100).astype(int)))
            if kwargs.get("orient") == "down":
                axes.x.show = False
                axes.y.show = True
                axes.y.ticks.show = True            

                # generate locations
                locs = np.linspace(0, maxheight, nticks)

                # generate labels formatted depending on range of locs
                fmt = "{:.2f}"
                if np.abs(locs).max() > 6:
                    fmt = "{:.1f}"
                elif np.abs(locs).max() > 10:
                    fmt = "{:.0f}"
                axes.y.ticks.locator = toyplot.locator.Explicit(
                    locations=locs,
                    labels=[fmt.format(i) for i in np.abs(locs)],
                    )

        return self.canvas, axes


class CloudTree:
    """
    Overlay many tree plots on the same Canvas and Axes.
    """
    def __init__(self, treelist, **kwargs):
        
        # base style
        self.treelist = treelist

        # set tip names
        if self.treelist[0].style.tip_labels is True:
            self.tip_labels = self.treelist[0].get_tip_labels()

        elif isinstance(self.treelist[0].style.tip_labels, (list, tuple)):
            self.tip_labels = self.treelist[0].style.tip_labels

        else:
            self.tip_labels = self.treelist[0].get_tip_labels()

        # 
        self.ntips = len(self.treelist[0])
        self.style = TreeStyle('m')
        self.style.update(kwargs)


    def update(self, axes=None): 

        # set reasonable dims if not user entered
        self.set_dims_from_tree_size()

        # if not canvas then creates one else uses the existing
        # sets self.canvas and self.axes
        self.get_canvas_and_axes(axes)

        # plot trees on the same axes with shared style dict
        self.axes.show = False
        for tre in self.treelist:
            tre.draw(axes=self.axes, tip_labels=False)

        # add a single call to tip labels
        self.add_tip_labels_to_axes()
        self.fit_tip_labels()
        return self.canvas, self.axes


    def get_canvas_and_axes(self, axes):
        if axes: 
            self.canvas = None
            self.axes = axes
        else:
            self.canvas = toyplot.Canvas(
                height=self.style.height,
                width=self.style.width,
            )
            self.axes = self.canvas.cartesian(
                padding=self.style.padding,
            )


    def set_dims_from_tree_size(self):
        "Calculate reasonable height and width for tree given N tips"
        tlen = len(self.treelist[0])
        if self.style.orient in ("right", "left"):
            # long tip-wise dimension
            if not self.style.height:
                self.style.height = max(275, min(1000, 18 * (tlen)))
            if not self.style.width:
                self.style.width = max(300, min(500, 18 * (tlen)))
        else:
            # long tip-wise dimension
            if not self.style.width:
                self.style.width = max(275, min(1000, 18 * (tlen)))
            if not self.style.height:
                self.style.height = max(225, min(500, 18 * (tlen)))


    def add_tip_labels_to_axes(self):
        """
        Add text offset from tips of tree with correction for orientation, 
        and fixed_order which is usually used in multitree plotting.
        """
        # get tip-coords and replace if using fixed_order
        if self.style.orient in ("up", "down"):
            ypos = np.zeros(self.ntips)
            xpos = np.arange(self.ntips)

        if self.style.orient in ("right", "left"):
            xpos = np.zeros(self.ntips)
            ypos = np.arange(self.ntips)

        # pop fill from color dict if using color
        if self.style.tip_labels_colors:
            self.style.tip_labels_style.pop("fill")

        # fill anchor shift if None 
        # (Toytrees fill this at draw() normally when tip_labels != None)
        if self.style.tip_labels_style["-toyplot-anchor-shift"] is None:
            self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"

        # add tip names to coordinates calculated above
        self.axes.text(
            xpos, 
            ypos,
            self.tip_labels,
            angle=(0 if self.style.orient in ("right", "left") else -90),
            style=self.style.tip_labels_style,
            color=self.style.tip_labels_colors,
        )
        # get stroke-width for aligned tip-label lines (optional)
        # copy stroke-width from the edge_style unless user set it
        if not self.style.edge_align_style.get("stroke-width"):
            self.style.edge_align_style['stroke-width'] = (
                self.style.edge_style['stroke-width'])


    def fit_tip_labels(self):
        """
        Modifies display range to ensure tip labels fit. This is a bit hackish
        still. The problem is that the 'extents' range of the rendered text
        is totally correct. So we add a little buffer here. Should add for 
        user to be able to modify this if needed. If not using edge lengths
        then need to use unit length for treeheight.
        """

        if not self.tip_labels:
            return 

        # longest name (this will include html hacks)
        longest_name = max([len(i) for i in self.tip_labels])
        if longest_name > 10:
            multiplier = 0.85
        else:
            multiplier = 0.25

        if self.style.use_edge_lengths:
            addon = (self.treelist[0].treenode.height + (
                self.treelist[0].treenode.height * multiplier))
        else:
            addon = self.treelist[0].treenode.get_farthest_leaf(True)[1]

        # modify display for orientations
        if self.style.orient == "right":
            self.axes.x.domain.max = addon
        elif self.style.orient == "down":
            self.axes.y.domain.min = -1 * addon


    # def assign_tip_labels_and_colors(self):
    #     "assign tip labels based on user provided kwargs"
    #     # COLOR
    #     # tip color overrides tipstyle.fill
    #     # if self.style.tip_labels_color:

    #     #     if self.fixed_order:
    #     #         if isinstance(self.style.tip_labels_color, (list, np.ndarray)):
    #     #             cols = np.array(self.style.tip_labels_color)
    #     #             orde = cols[self.fixed_idx]

    #     #     if self.style.tip_labels_style.fill:
    #     #         self.style.tip_labels_style.fill = None

    #     # LABELS
    #     # False == hide tip labels
    #     if self.style.tip_labels is False:
    #         self.style.tip_labels_style["-toyplot-anchor-shift"] = "0px"
    #         self.tip_labels = [
    #             "" for i in self.mtree._cons_order]

    #     # (True or None) == use user or cons order
    #     if self.style.tip_labels is True:
    #         if self.mtree._user_order:
    #             self.tip_labels = self.mtree._user_order
    #         else:
    #             self.tip_labels = self.mtree._cons_order

    #     # LABELS
    #     # user entered something...
    #     elif isinstance(self.style.tip_labels, list):
    #         # if user did not change label-offset then shift it here
    #         if not self.style.tip_labels_style["-toyplot-anchor-shift"]:
    #             self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"
    #         self.tip_labels = self.style.tip_labels
