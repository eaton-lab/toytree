#!/usr/bin/env python

"""
Classes for Drawings from MultiTrees.
"""
#from __future__ import print_function, absolute_import

from copy import deepcopy
import numpy as np
import toyplot
from .TreeStyle import TreeStyle
#from .utils import ToytreeError


class TreeGrid:
    """
    Easily create Toyplot gridded canvases for plotting multiple trees.
    """
    def __init__(self, mtree, fixed_order):
        
        # plot objects are init on update()
        self.canvas = None
        self.cartesian = None
        self.mtree = mtree
        self.style = TreeStyle('n')

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
                tree.draw(axes=axes, **kwargs)
                axes.show = False

        else:
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
    def __init__(self, mtree, fixed_order):  # , fixed_order=None):
        
        # base style
        self.style = mtree.style
        self.mtree = mtree
        self.fixed_order = fixed_order
        #self.fixed_idx = list(range(self.ntips))
        #self._fixed_idx = [names.index(i) for i in self._fixed_order]
        # # inherit fixed order, take arg, or use True
        # self.fixed_order = mtree._fixed_order
        # if fixed_order:
        #     self.fixed_order = fixed_order
        # if not self.fixed_order:
        #     self.fixed_order = True

        # # make new mtree using fixed order
        # self.mtree = MultiTree(mtree.treelist, fixed_order=self.fixed_order)

        # tip labels get updated
        self.tip_labels = None


    def update(self, **kwargs):

        # return nothing if tree is empty
        if not self.mtree.treelist:
            print("Tree is empty")
            return

        # allow ts as a shorthand for tree_style
        if kwargs.get("ts"):
            kwargs["tree_style"] = kwargs.get("ts")

        # update tree_style base if entered as an argument
        if kwargs.get('tree_style'):
            newstyle = TreeStyle(kwargs.get('tree_style')[0])
            self.style.__dict__.update(newstyle.__dict__)

        # store entered args
        userkeys = [
            "height",
            "width",
            "orient",       
            "tip_labels",
            "tip_labels_color",
            "tip_labels_align",
            "node_labels",
            "node_size",
            "node_color",
            "node_hover",
            "edge_type",
            "use_edge_lengths",
            "scalebar",
            "padding",
        ]       
        userargs = {i: j for (i, j) in kwargs.items() if i in userkeys}
        dictkeys = [
            "edge_style",
            "edge_align_style",
            "tip_labels_style",
            "node_style",
            "node_labels_style",
        ]
        dictargs = {i: j for (i, j) in kwargs.items() if i in dictkeys}

        # update tree_style to custom style with user entered args
        censored = {i: j for (i, j) in userargs.items() if j is not None}
        self.style.__dict__.update(censored)

        # update style dicts
        censored = [i for i in dictargs if i is not None]
        for styledict in censored:
            sdict = dictargs[styledict]
            if sdict:
                self.style.__setattr__(styledict, sdict)

        # set reasonable dims if not user entered
        self.set_dims_from_tree_size()

        # if not canvas then creates one else uses the existing
        # sets self.canvas and self.axes
        self.get_canvas_and_axes(kwargs.get('axes'))

        # grab debug flag and pop it from dict
        debug = False
        if kwargs.get("debug"):
            debug = True

        # Decompoase edge_style list into list of dicts
        # could put something here to apply styles based on some calculation
        # such as different colors for different topologies...
        if isinstance(kwargs.get('edge_style'), list):
            if not len(kwargs['edge_style']) == len(self.mtree):
                raise IndexError('stylelist length must match treelist length')
            for idx, tre in enumerate(self.mtree.treelist):
                self.style.edge_style = kwargs['edge_style'][idx]

        # pop tip labels and styles since they'll be blocked from subtrees
        tip_labels = deepcopy(self.style.tip_labels)
        tip_labels_style = deepcopy(self.style.tip_labels_style)
        self.style.tip_labels = False

        # unpack lists of style if applied to trees differently. Here we
        # can allow node_colors, node_sizes, edge_styles, 

        # plot trees on the same axes with shared style dict
        self.axes.show = False
        for tre in self.mtree.treelist:           
            tre.draw(axes=self.axes, **self.style.__dict__)

        # add a single call to tip labels
        self.style.tip_labels = tip_labels
        self.style.tip_labels_style = tip_labels_style
        self.assign_tip_labels_and_colors()
        self.add_tip_labels_to_axes()
        self.fit_tip_labels()

        # debug returns CloudTree object
        if debug:
            return self
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
        if self.style.tip_labels_color:
            tstyle.pop("fill")

        # add tip names to coordinates calculated above
        self.axes.text(
            xpos, 
            ypos,
            self.tip_labels,  
            angle=(0 if self.style.orient in ("right", "left") else -90),
            style=tstyle,
            color=self.style.tip_labels_color,
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
                "" for i in self.mtree.treelist[0].get_tip_labels()]

        # LABELS
        # user entered something...
        else:
            # if user did not change label-offset then shift it here
            if not self.style.tip_labels_style["-toyplot-anchor-shift"]:
                self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"

            # if user entered list in get_tip_labels order reverse it for plot
            if isinstance(self.style.tip_labels, list):
                self.tip_labels = self.style.tip_labels

            # True assigns tip labels from tree
            else:
                self.tip_labels = self.fixed_order
                #mtree.treelist[0].get_tip_labels()
