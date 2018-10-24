#!/usr/bin/env python

"""
Classes for Drawings from MultiTrees.
"""
from copy import deepcopy
import numpy as np
import toyplot
from .TreeStyle import TreeStyle


class TreeGrid:
    """
    Easily create Toyplot gridded canvases for plotting multiple trees.
    """
    def __init__(self, mtree):
        
        # plot objects are init on update()
        self.canvas = None
        self.cartesian = None
        self.mtree = mtree

        # subtree styles are stripped when MultiTree init, but can be added.
        #self.style = TreeStyle('n')

        # to be filled
        self.x = None
        self.y = None
        self.treelist = []


    def update(self, x, y, start, shared_axis, **kwargs):

        # store plot dims and assert that they fit well enough
        self.x = x
        self.y = y
        self.treelist = self.mtree.treelist[start:start + self.x * self.y]

        # todo: mess with padding and margins...
        wdef = min(1000, self.y * 300)
        hdef = min(1000, self.x * 300)
        self.canvas = toyplot.Canvas(
            width=(kwargs.get('width') if kwargs.get('width') else wdef), 
            height=(kwargs.get('height') if kwargs.get('height') else hdef),
        ) 

        # todo: test with kwargs
        if not shared_axis:
            # get max treeheight
            for tidx, tree in enumerate(self.treelist):
                # set ymax on cartesian so that trees are on same scale
                axes = self.canvas.cartesian(
                    grid=(self.x, self.y, tidx),
                    margin=(20, 20, 35, 35),
                    padding=10,
                )
                # update tree style with any new arguments
                tree.draw(axes=axes, **kwargs)
                axes.show = False

        else:
            raise NotImplementedError("coming soon")
            axes = self.canvas.cartesian(
                    #bounds=()
                    #margin=35,
                    padding=10,
                    )
            # axes = self.axes.share(...)
            for tidx, tree in enumerate(self.treelist):
                pass
                # add +x to their verts?
                # or use share-axis args for axes <- yes.
        #return self.canvas, axes


class CloudTree:
    """
    Overlay many tree plots on the same Canvas and Axes.
    """
    def __init__(self, mtree, edge_styles=None):
        
        # base style
        self.mtree = mtree
        self.style = deepcopy(self.mtree.style)
        self.tip_labels = self.mtree.get_tip_labels()
        self.edge_styles = edge_styles


    def update(self, axes=None): 

        # apply mtree style to all subtrees
        self.apply_style_to_subtrees()

        # check style lists
        self.apply_edge_styles_to_subtrees()

        # set reasonable dims if not user entered
        self.set_dims_from_tree_size()

        # if not canvas then creates one else uses the existing
        # sets self.canvas and self.axes
        self.get_canvas_and_axes(axes)

        # plot trees on the same axes with shared style dict
        # this clobberes the 
        self.axes.show = False
        for tre in self.mtree.treelist:
            tstyle = deepcopy(tre.style)  # .__dict__)
            tre.draw(axes=self.axes, **tstyle.to_dict())

        # add a single call to tip labels
        self.assign_tip_labels_and_colors()
        self.add_tip_labels_to_axes()
        self.fit_tip_labels()
        return self.canvas, self.axes


    def apply_style_to_subtrees(self):
        "Apply mtree style to subtrees except tip_labels which are suppressed."
        for idx, tre in enumerate(self.mtree.treelist):
            self.mtree.treelist[idx].style.update(self.style)
            self.mtree.treelist[idx].style.tip_labels = False


    def apply_edge_styles_to_subtrees(self):
        """
        Users can enter _some_ kwargs as list values to apply different styles
        to each tree in the treelist. Check and break them down here.
        """
        # Decompoase edge_style list into list of dicts
        # could put something here to apply styles based on some calculation
        # such as different colors for different topologies.
        if self.edge_styles:
            # check length of the list
            if not len(self.edge_styles) == len(self.mtree):
                raise IndexError(
                    'edge_styles length must match treelist length')

            # set style element
            for idx, tre in enumerate(self.mtree.treelist):
                self.mtree.treelist[idx].style.__setattr__(
                    "edge_style", 
                    self.edge_styles[idx]
                    )
                # if color then ensure it's CSS compatible.
                if isinstance(
                    self.mtree.treelist[idx].style.edge_style.stroke, 
                        (np.void, np.ndarray, tuple)):
                    self.mtree.treelist[idx].style.edge_style.stroke = (
                        toyplot.color.to_css(
                            self.mtree.treelist[idx].style.edge_style.stroke)
                        )


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
        tlen = len(self.mtree.treelist[0])
        if self.style.orient in ("right", "left"):
            # long tip-wise dimension
            if not self.style.height:
                self.style.height = max(275, min(1000, 18 * (tlen)))
            if not self.style.width:
                self.style.width = max(225, min(500, 18 * (tlen)))
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
            ypos = np.zeros(self.mtree.ntips)
            xpos = np.arange(self.mtree.ntips)

        if self.style.orient in ("right", "left"):
            xpos = np.zeros(self.mtree.ntips)
            ypos = np.arange(self.mtree.ntips)

        # pop fill from color dict if using color
        tstyle = deepcopy(self.style.tip_labels_style)
        if self.style.tip_labels_colors:
            tstyle.pop("fill")

        # add tip names to coordinates calculated above
        self.axes.text(
            xpos, 
            ypos,
            self.tip_labels,  
            angle=(0 if self.style.orient in ("right", "left") else -90),
            style=tstyle,
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
        if self.style.use_edge_lengths:
            addon = (self.mtree.treelist[0].treenode.height + \
                (self.mtree.treelist[0].treenode.height * 0.25))
        else:
            addon = self.mtree.treelist[0].treenode.get_farthest_leaf(True)[1]

        # modify display for orientations
        if self.style.tip_labels:
            if self.style.orient == "right":
                self.axes.x.domain.max = addon
            elif self.style.orient == "down":
                self.axes.y.domain.min = -1 * addon


    def assign_tip_labels_and_colors(self):
        "assign tip labels based on user provided kwargs"
        # COLOR
        # tip color overrides tipstyle.fill
        # if self.style.tip_labels_color:

        #     if self.fixed_order:
        #         if isinstance(self.style.tip_labels_color, (list, np.ndarray)):
        #             cols = np.array(self.style.tip_labels_color)
        #             orde = cols[self.fixed_idx]

        #     if self.style.tip_labels_style.fill:
        #         self.style.tip_labels_style.fill = None

        # LABELS
        # False == hide tip labels
        if self.style.tip_labels is False:
            self.style.tip_labels_style["-toyplot-anchor-shift"] = "0px"
            self.tip_labels = [
                "" for i in self.mtree._cons_order]

        # (True or None) == use user or cons order
        if self.style.tip_labels is True:
            if self.mtree._user_order:
                self.tip_labels = self.mtree._user_order
            else:
                self.tip_labels = self.mtree._cons_order

        # LABELS
        # user entered something...
        elif isinstance(self.style.tip_labels, list):
            # if user did not change label-offset then shift it here
            if not self.style.tip_labels_style["-toyplot-anchor-shift"]:
                self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"
            self.tip_labels = self.style.tip_labels
