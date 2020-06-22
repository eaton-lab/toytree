#!/usr/bin/env python

"""
Classes for Drawings from MultiTrees.
"""
from decimal import Decimal
import numpy as np
import toyplot
from .TreeStyle import TreeStyle

from toyplot.mark import Mark
import xml.etree.ElementTree as xml

# Register multipledispatch to share with toyplot.html
import functools
from multipledispatch import dispatch
dispatch = functools.partial(dispatch, namespace=toyplot.html._namespace)




class CloudTreeMark(Mark):
    """
    
    """


class RenderCloudTree:
    """

    """


@dispatch(toyplot.coordinates.Cartesian, CloudTreeMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderCloudTree(axes, mark, context)




class TreeGridMark(Mark):
    """
    Multiple toytrees on the same cartesian coordinates axes but spread 
    out non-overlapping on a grid using layout plans. Applies shared tree
    styles to a top-level treegrid to reduce repetition in CSS.
    """
    def __init__(self, trees):

        # inherit type
        Mark.__init__(self)

        # store all needed from subtrees.
        self._coordinate_axes = ['x', 'y']

        # the tree with their styles which will make tree marks
        # from which contex will be extracted 
        self.trees = trees

        # grid layout arguments



class RenderTreeGrid:
    """
    Organized class to call in _render to create a single Mark with 
    multiple trees arranged into a grid using xbaseline, ybaseline, 
    and either scaling trees to fit nicely or using original scales
    (e.g., different root heights) to show differences. 

    Main usage:
        1. comparing topologies (down or right facing; scaled)
        2. comparing coalescence (down facing; not scaled).


    """
    def __init__(self, axes, mark, context):

        # inputs: mark has .trees and its own top-level .style.
        # axes and context/canvas are singular.
        self.mark = mark
        self.axes = axes
        self.context = context

        # to be constructed
        self.mark_xml = None

        # construction funcs
        self.project_grid()
        self.build_dom()


    def build_dom(self):

        # get shared styles


        # build top level dom
        self.mark_treegrid()

        # lay down trees
        self.mark_toytrees()



    def project_grid(self):
        """
        Figure out the grid layout based on the size of each 
        tree, the user-provided width/height, and shared axes args.
        """

        # option 1: no shared axes. Trees are scaled(?)


        # option 2: shared axes. Spacing of tree



    def mark_treegrid(self):
        """
        Creates the top-level Toytree-Grid mark.
        """
        self.mark_xml = xml.SubElement(
            self.context.parent, "g", 
            id=self.context.get_id(self.mark),
            attrib={"class": "toytree-mark-Grid"},
        )


    def mark_toytrees(self):
        """
        Creates toytree marks and appends them in the Grid Mark
        """
        for tre in self.trees:
            # render the edge group
            self.tree_xml = xml.SubElement(
                self.mark_xml, "g", 
                attrib={"class": "toytree-mark-Toytree"}, 
                style=style_to_string(self.mark.edge_style)
            )





@dispatch(toyplot.coordinates.Cartesian, TreeGridMark, toyplot.html.RenderContext)
def _render(axes, mark, context):
    RenderTreeGrid(axes, mark, context)






# class OldTreeGrid(object):
#     """
#     Easily create Toyplot gridded canvases for plotting multiple trees.
#     """
#     def __init__(self, treelist):

#         # plot objects are init on update()
#         self.canvas = None
#         self.treelist = treelist
#         self.treeslice = []

#         # to be filled
#         self.nrows = None
#         self.ncols = None


#     def update(self, axes, nrows, ncols, start, shared_axis, **kwargs):

#         # store plot dims and assert that they fit well enough
#         self.axes = axes
#         self.nrows = nrows
#         self.ncols = ncols
#         self.treeslice = self.treelist[start:start + self.nrows * self.ncols]

#         # TODO: mess with padding and margins...
#         if not self.axes:
#             wdef = min(800, self.ncols * 175)
#             hdef = min(800, self.nrows * 250)
#             self.canvas = toyplot.Canvas(
#                 width=(kwargs.get('width') if kwargs.get('width') else wdef), 
#                 height=(kwargs.get('height') if kwargs.get('height') else hdef),
#             ) 

#         if (not shared_axis) and (not self.axes):
#             # get max treeheight
#             for tidx, tree in enumerate(self.treeslice):

#                 # create grid with a reasonable margin between trees
#                 #if not axes:
#                 axes = self.canvas.cartesian(
#                     grid=(self.nrows, self.ncols, tidx),
#                     margin=(30, 30, 30, 30),
#                     padding=35,
#                 )
#                 axes.show = False

#                 # update tree style with any new arguments
#                 tree.draw(axes=axes)


#         # shared X axis
#         else:    
#             # only one axis allowed?... x=1 or y=1
#             if not self.axes:
#                 axes = self.canvas.cartesian(padding=25)
#             xbaseline = 0
#             maxheight = 0
#             layout = ("d" if not kwargs.get("layout") else kwargs.get("layout"))

#             # COALESCENT TIME COMPARISON TYPE PLOT
#             if layout == "d":
#                 for tidx, tree in enumerate(self.treeslice):
#                     tree.draw(axes=axes, xbaseline=xbaseline, layout='d')
#                     xbaseline += tree.ntips + 1
#                     maxheight = max(maxheight, tree.treenode.height)

#                 if not self.axes:
#                     nticks = max((3, np.floor(hdef / 100).astype(int)))
#                     axes.x.show = False
#                     axes.y.show = True
#                     axes.y.ticks.show = True            

#                     # generate locations
#                     locs = np.linspace(0, maxheight, nticks)

#                     # auto-formatter for axes ticks labels
#                     zer = abs(min(0, Decimal(locs[1]).adjusted()))
#                     fmt = "{:." + str(zer) + "f}"
#                     axes.y.ticks.locator = toyplot.locator.Explicit(
#                         locations=locs,
#                         labels=[fmt.format(i) for i in np.abs(locs)],
#                         )

#             # USUALLY TOPOLOGY COMPARISON PLOT
#             else:
#                 for tidx, tree in enumerate(self.treeslice):
#                     tree = tree.mod.node_scale_root_height(1.0)
#                     tree.draw(axes=axes, xbaseline=xbaseline, layout='r')

#                     if kwargs.get('xbaseline'):
#                         xbaseline += kwargs.get('xbaseline')
#                     else:
#                         if tree.style.use_edge_lengths is False:
#                             shift = tree.treenode.get_farthest_leaf(
#                                 topology_only=True)[1] + 1
#                         else:
#                             shift = 1.0
#                         xbaseline += shift + shift / 2.

#                     maxheight = max(maxheight, tree.ntips)                
#                 axes.show = False

#         # None is placeholder until custom mark is finished
#         return self.canvas, axes, None



# class OldCloudTree:
#     """
#     Overlay many tree plots on the same Canvas and Axes. All ToyTrees in the 
#     treelist have already been fixed_order reordered. 
#     """
#     def __init__(self, treelist, **kwargs):

#         # store list of ordered trees
#         self.treelist = treelist

#         # set tip names 
#         if not kwargs.get("tip_labels"):
#             self.tip_labels = self.treelist[0].get_tip_labels()
#         else:
#             self.tip_labels = [
#                 kwargs.get("tip_labels")[name] 
#                 for name in self.treelist[0].get_tip_labels()
#             ]

#         # base style
#         self.ntips = len(self.treelist[0])
#         self.style = TreeStyle('m')
#         self.style.update(kwargs)


#     def update(self, axes=None): 

#         # set reasonable dims if not user entered
#         self.set_dims_from_tree_size()

#         # if not canvas then creates one else uses the existing
#         # sets self.canvas and self.axes
#         self.get_canvas_and_axes(axes)

#         # plot trees on the same axes with shared style dict
#         self.axes.show = False
#         for tre in self.treelist:
#             tre.draw(axes=self.axes, tip_labels=False)

#         # add a single call to tip labels
#         self.add_tip_labels_to_axes()
#         self.fit_tip_labels()

#         # None is placeholder until custom mark is finished        
#         return self.canvas, self.axes, None


#     def get_canvas_and_axes(self, axes):
#         if axes: 
#             self.canvas = None
#             self.axes = axes
#         else:
#             self.canvas = toyplot.Canvas(
#                 height=self.style.height,
#                 width=self.style.width,
#             )
#             self.axes = self.canvas.cartesian(
#                 padding=self.style.padding,
#             )


#     def set_dims_from_tree_size(self):
#         "Calculate reasonable height and width for tree given N tips"
#         tlen = len(self.treelist[0])
#         if self.style.layout in ("r", "l"):
#             # long tip-wise dimension
#             if not self.style.height:
#                 self.style.height = max(275, min(1000, 18 * (tlen)))
#             if not self.style.width:
#                 self.style.width = max(300, min(500, 18 * (tlen)))
#         else:
#             # long tip-wise dimension
#             if not self.style.width:
#                 self.style.width = max(275, min(1000, 18 * (tlen)))
#             if not self.style.height:
#                 self.style.height = max(225, min(500, 18 * (tlen)))


#     def add_tip_labels_to_axes(self):
#         """
#         Add text offset from tips of tree with correction for orientation, 
#         and fixed_order which is usually used in multitree plotting.
#         """
#         # get tip-coords
#         if self.style.layout in ("u", "d"):
#             ypos = np.zeros(self.ntips)
#             xpos = np.arange(self.ntips)

#         elif self.style.layout in ("r", "l"):
#             xpos = np.zeros(self.ntips)
#             ypos = np.arange(self.ntips)

#         else:
#             raise NotImplementedError(
#                 "multitree layout {} not yet supported"
#                 .format(self.style.layout))

#         # pop fill from color dict if using color
#         if self.style.tip_labels_colors:
#             self.style.tip_labels_style.pop("fill")

#         # fill anchor shift if None 
#         # (Toytrees fill this at draw() normally when tip_labels != None)
#         if self.style.tip_labels_style["-toyplot-anchor-shift"] is None:
#             self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"

#         # add tip names to coordinates calculated above
#         self.axes.text(
#             xpos, 
#             ypos,
#             self.tip_labels,
#             angle=(0 if self.style.layout in ("r", "l") else -90),
#             style=self.style.tip_labels_style,
#             color=self.style.tip_labels_colors,
#         )
#         # get stroke-width for aligned tip-label lines (optional)
#         # copy stroke-width from the edge_style unless user set it
#         if not self.style.edge_align_style.get("stroke-width"):
#             self.style.edge_align_style['stroke-width'] = (
#                 self.style.edge_style['stroke-width'])


#     def fit_tip_labels(self):
#         """
#         Modifies display range to ensure tip labels fit. This is a bit hackish
#         still. The problem is that the 'extents' range of the rendered text
#         is totally correct. So we add a little buffer here. Should add for 
#         user to be able to modify this if needed. If not using edge lengths
#         then need to use unit length for treeheight.
#         """
#         if not self.tip_labels:
#             return 

#         lname = max([len(i) for i in self.tip_labels])

#         # get ratio of names to tree in plot
#         ratio = max(lname / 10, 0.15)

#         # have tree figure make up 85% of plot
#         if self.treelist[0].style.use_edge_lengths:
#             addon = self.treelist[0].treenode.height
#         else:
#             addon = self.treelist[0].treenode.get_farthest_leaf(True)[1] + 1
#         addon *= ratio

#         # modify display for orientations
#         if self.style.tip_labels:
#             if self.style.layout == "r":
#                 self.axes.x.domain.max = addon / 2.
#             elif self.style.layout == "d":
#                 self.axes.y.domain.min = (-1 * addon) / 2

#         # # longest name (this will include html hacks)
#         # longest_name = max([len(i) for i in self.tip_labels])
#         # if longest_name > 10:
#         #     multiplier = 0.85
#         # else:
#         #     multiplier = 0.25

#         # if self.style.use_edge_lengths:
#         #     addon = (self.treelist[0].treenode.height + (
#         #         self.treelist[0].treenode.height * multiplier))
#         # else:
#         #     addon = self.treelist[0].treenode.get_farthest_leaf(True)[1]

#         # # modify display for orientations
#         # if self.style.orient == "right":
#         #     self.axes.x.domain.max = addon
#         # elif self.style.orient == "down":
#         #     self.axes.y.domain.min = -1 * addon


#     # def assign_tip_labels_and_colors(self):
#     #     "assign tip labels based on user provided kwargs"
#     #     # COLOR
#     #     # tip color overrides tipstyle.fill
#     #     # if self.style.tip_labels_color:

#     #     #     if self.fixed_order:
#     #     #         if isinstance(self.style.tip_labels_color, (list, np.ndarray)):
#     #     #             cols = np.array(self.style.tip_labels_color)
#     #     #             orde = cols[self.fixed_idx]

#     #     #     if self.style.tip_labels_style.fill:
#     #     #         self.style.tip_labels_style.fill = None

#     #     # LABELS
#     #     # False == hide tip labels
#     #     if self.style.tip_labels is False:
#     #         self.style.tip_labels_style["-toyplot-anchor-shift"] = "0px"
#     #         self.tip_labels = [
#     #             "" for i in self.mtree._cons_order]

#     #     # (True or None) == use user or cons order
#     #     if self.style.tip_labels is True:
#     #         if self.mtree._user_order:
#     #             self.tip_labels = self.mtree._user_order
#     #         else:
#     #             self.tip_labels = self.mtree._cons_order

#     #     # LABELS
#     #     # user entered something...
#     #     elif isinstance(self.style.tip_labels, list):
#     #         # if user did not change label-offset then shift it here
#     #         if not self.style.tip_labels_style["-toyplot-anchor-shift"]:
#     #             self.style.tip_labels_style["-toyplot-anchor-shift"] = "15px"
#     #         self.tip_labels = self.style.tip_labels
