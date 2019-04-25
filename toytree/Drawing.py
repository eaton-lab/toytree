#!/usr/bin/env python

"""
A class creating Drawings from Toytrees.
"""
from copy import deepcopy
import numpy as np
import toyplot
from .utils import ToytreeError

# should we store node_labels, node_sizes, etc here or in Style?
# It could be that style is just the rules for filling the drawing attrs...
# and the actual drawing features are storing in ._drawing. 


class Drawing:
    def __init__(self, ttree, **kwargs):
        # input objects
        self.ttree = ttree
        self.coords = ttree._coords
        self.style = ttree.style
        self.kwargs = kwargs
        self.nedges = self.ttree._coords.edges.shape[0]

        # mutable plotting attributes pulled from styles and tree
        self.node_labels = [""] * self.ttree.nnodes
        self.node_colors = [None] * self.ttree.nnodes
        self.node_sizes = [0] * self.ttree.nnodes
        self.node_markers = ["o"] * self.ttree.nnodes

        self.tip_colors = None
        self.tip_labels = None

        # todo: allow itemized versions of these...
        self.edge_colors = [None] * self.nedges
        self.edge_widths = [None] * self.nedges

        #self.nedges = self.ttree._coords.lines.shape[0]        
        # store whether external axes were passed in 
        self._external_axis = False


    def update(self, axes=None):

        # always update coords in case style params affect the node placement
        self.coords.update()

        # set up base canvas and axes
        self.get_dims_from_tree_size()
        self.get_canvas_and_axes(axes)
        self.set_baselines()

        # update attrs for style entries. Some of these can be set with style, 
        # or as a list, e.g., node_style={'fill':'red'} or node_color="red".
        self.assign_node_labels_and_sizes()
        self.assign_node_colors_and_style()
        self.assign_tip_labels_and_colors()
        self.assign_edge_colors_and_widths()

        # draw tree, nodes, tips, axes on canvas.
        self.add_tip_lines_to_axes()
        self.add_tip_labels_to_axes()
        self.add_tree_to_axes()
        self.add_nodes_to_axes()
        self.add_axes_style()

        # add extra display space for tips on the end of tree
        self.fit_tip_labels()
        return self.canvas, self.axes
        #return self.canvas, self.axes, tuple(self.axes._children)


    def set_baselines(self):
        """
        Modify coords to shift tree position for x,y baseline arguments. This
        is useful for arrangeing trees onto a Canvas with other plots, but 
        still sharing a common cartesian axes coordinates. 
        """
        if self.style.xbaseline:
            if self.style.orient in ("up", "down"):
                self.coords.coords[:, 0] += self.style.xbaseline
                self.coords.verts[:, 0] += self.style.xbaseline                
            else:
                self.coords.coords[:, 1] += self.style.xbaseline
                self.coords.verts[:, 1] += self.style.xbaseline                

    # -----------------------------------------------------------------
    # Node and Node Labels 
    # -----------------------------------------------------------------
    def add_tip_labels_to_axes(self):
        """
        Add text offset from tips of tree with correction for orientation, 
        and fixed_order which is usually used in multitree plotting.
        """
        # get tip-coords and replace if using fixed_order
        xpos = self.ttree.get_tip_coordinates('x')
        ypos = self.ttree.get_tip_coordinates('y')

        if self.style.orient in ("up", "down"):
            if self.ttree._fixed_order:
                xpos = list(range(self.ttree.ntips))
                ypos = ypos[self.ttree._fixed_idx]
            if self.style.tip_labels_align:
                ypos = np.zeros(self.ttree.ntips)

        if self.style.orient in ("right", "left"):
            if self.ttree._fixed_order:
                xpos = xpos[self.ttree._fixed_idx]
                ypos = list(range(self.ttree.ntips))
            if self.style.tip_labels_align:
                xpos = np.zeros(self.ttree.ntips)

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
            self.style.edge_align_style["stroke-width"] = (
                self.style.edge_style["stroke-width"])


    def add_tip_lines_to_axes(self):
        "add lines to connect tips to zero axis for tip_labels_align=True"

        # get tip-coords and align-coords from verts
        xpos, ypos, aedges, averts = self.get_tip_label_coords() 
        if self.style.tip_labels_align:
            self.axes.graph(
                aedges,
                vcoordinates=averts,
                estyle=self.style.edge_align_style, 
                vlshow=False,
                vsize=0,
            )


    def fit_tip_labels(self):
        """
        Modifies display range to ensure tip labels fit. This is a bit hackish
        still. The problem is that the 'extents' range of the rendered text
        is totally correct. So we add a little buffer here. Should add for 
        user to be able to modify this if needed. If not using edge lengths
        then need to use unit length for treeheight.
        """
        # user entered values
        #if self.style.axes.x_domain_max or self.style.axes.y_domain_min:
        #    self.axes.x.domain.max = self.style.axes.x_domain_max
        #    self.axes.y.domain.min = self.style.axes.y_domain_min            

        # IF USE WANTS TO CHANGE IT THEN DO IT AFTER USING AXES
        # or auto-fit (tree height)
        #else:
        if self.style.use_edge_lengths:
            addon = self.ttree.treenode.height * .85
        else:
            addon = self.ttree.treenode.get_farthest_leaf(True)[1]

        # modify display for orientations
        if self.style.tip_labels:
            if self.style.orient == "right":
                self.axes.x.domain.max = addon
            elif self.style.orient == "down":
                self.axes.y.domain.min = -1 * addon



    def assign_node_colors_and_style(self):
        """
        Resolve conflict of 'node_color' and 'node_style['fill'] args which are
        redundant. Default is node_style.fill unless user entered node_color.
        To enter multiple colors user must use node_color not style fill. 
        Either way, we build a list of colors to pass to Drawing.node_colors 
        which is then written to the marker as a fill CSS attribute.
        """
        # SET node_colors and POP node_style.fill
        colors = self.style.node_colors
        style = self.style.node_style
        if colors is None:
            if style["fill"] in (None, "none"):
                style.pop("fill")
            else:
                if isinstance(style["fill"], (list, tuple)):
                    raise ToytreeError(
                        "Use node_color not node_style for multiple node colors")
                # check the color
                color = style["fill"]
                if isinstance(color, (np.ndarray, np.void, list, tuple)):
                    color = toyplot.color.to_css(color)
                self.node_colors = [color] * self.ttree.nnodes

        # otherwise parse node_color
        else:
            style.pop("fill")
            if isinstance(colors, str):
                # check the color
                color = colors
                if isinstance(color, (np.ndarray, np.void, list, tuple)):
                    color = toyplot.color.to_css(color)
                self.node_colors = [color] * self.ttree.nnodes

            elif isinstance(colors, (list, tuple)):
                if len(colors) != len(self.node_colors):
                    raise ToytreeError("node_colors arg is the wrong length")
                for cidx in range(len(self.node_colors)):
                    color = colors[cidx]
                    if isinstance(color, (np.ndarray, np.void, list, tuple)):
                        color = toyplot.color.to_css(color)                   
                    self.node_colors[cidx] = color

        # use CSS none for stroke=None
        if self.style.node_style["stroke"] is None:
            self.style.node_style.stroke = "none"

        # apply node markers
        markers = self.style.node_markers
        if markers is None:
            self.node_markers = ["o"] * self.ttree.nnodes
        else:
            if isinstance(markers, str):
                self.node_markers = [markers] * self.ttree.nnodes
            elif isinstance(markers, (list, tuple)):
                for cidx in range(len(self.node_markers)):
                    self.node_markers[cidx] = markers[cidx]



    def assign_node_labels_and_sizes(self):
        "assign features of nodes to be plotted based on user kwargs"

        # shorthand
        nvals = self.ttree.get_node_values()

        # False == Hide nodes and labels unless user entered size 
        if self.style.node_labels is False:
            self.node_labels = ["" for i in nvals]           
            if self.style.node_sizes is not None:
                if isinstance(self.style.node_sizes, (list, tuple, np.ndarray)):
                    assert len(self.node_sizes) == len(self.style.node_sizes)
                    self.node_sizes = self.style.node_sizes

                elif isinstance(self.style.node_sizes, (int, str)):
                    self.node_sizes = (
                        [int(self.style.node_sizes)] * len(nvals)
                    )
                self.node_labels = [" " if i else "" for i in self.node_sizes]
                    
                    
        # True == Show nodes, label=idx, and show hover
        elif self.style.node_labels is True:
            # turn on node hover even if user did not set it explicit
            self.style.node_hover = True

            # get idx labels
            self.node_labels = self.ttree.get_node_values('idx', 1, 1)

            # use default node size as a list if not provided
            if not self.style.node_sizes:
                self.node_sizes = [18] * len(nvals)
            else:
                assert isinstance(self.style.node_sizes, (int, str))
                self.node_sizes = (
                    [int(self.style.node_sizes)] * len(nvals)
                )

        # User entered lists or other for node labels or sizes; check lengths.
        else:
            # make node labels into a list of values 
            if isinstance(self.style.node_labels, list):
                assert len(self.style.node_labels) == len(nvals)
                self.node_labels = self.style.node_labels

            # check if user entered a feature else use entered val
            elif isinstance(self.style.node_labels, str):
                self.node_labels = [self.style.node_labels] * len(nvals)
                if self.style.node_labels in self.ttree.features:
                    self.node_labels = self.ttree.get_node_values(
                        self.style.node_labels, 1, 0)

            # default to idx at internals if nothing else
            else:
                self.node_labels = self.ttree.get_node_values("idx", 1, 0)

            # make node sizes as a list; set to zero if node label is ""
            if isinstance(self.style.node_sizes, list):
                assert len(self.style.node_sizes) == len(nvals)
                self.node_sizes = self.style.node_sizes
            elif isinstance(self.style.node_sizes, (str, int, float)):
                self.node_sizes = [int(self.style.node_sizes)] * len(nvals)
            else:
                self.node_sizes = [18] * len(nvals)

            # override node sizes to hide based on node labels
            for nidx, node in enumerate(self.node_labels):
                if self.node_labels[nidx] == "":
                    self.node_sizes[nidx] = 0

        # ensure string type
        self.node_labels = [str(i) for i in self.node_labels]


    def assign_tip_labels_and_colors(self):
        "assign tip labels based on user provided kwargs"
        # COLOR
        # tip color overrides tipstyle.fill
        if self.style.tip_labels_colors:
            #if self.style.tip_labels_style.fill:
            #    self.style.tip_labels_style.fill = None
            if self.ttree._fixed_order:
                if isinstance(self.style.tip_labels_colors, (list, np.ndarray)):                                     
                    cols = np.array(self.style.tip_labels_colors)
                    orde = cols[self.ttree._fixed_idx]
                    self.style.tip_labels_colors = list(orde)

        # LABELS
        # False == hide tip labels
        if self.style.tip_labels is False:
            self.style.tip_labels_style["-toyplot-anchor-shift"] = "0px"
            self.tip_labels = ["" for i in self.ttree.get_tip_labels()]

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
                if self.ttree._fixed_order:
                    self.tip_labels = self.ttree._fixed_order
                else:
                    self.tip_labels = self.ttree.get_tip_labels()
    

    def assign_edge_colors_and_widths(self):
        """
        Resolve conflict of 'node_color' and 'node_style['fill'] args which are
        redundant. Default is node_style.fill unless user entered node_color.
        To enter multiple colors user must use node_color not style fill. 
        Either way, we build a list of colors to pass to Drawing.node_colors 
        which is then written to the marker as a fill CSS attribute.
        """
        # node_color overrides fill. Tricky to catch cuz it can be many types.

        # SET edge_widths and POP edge_style.stroke-width
        if self.style.edge_widths is None:
            if not self.style.edge_style["stroke-width"]:
                self.style.edge_style.pop("stroke-width")
                self.style.edge_style.pop("stroke")
                self.edge_widths = [None] * self.nedges
            else:
                if isinstance(self.style.edge_style["stroke-width"], (list, tuple)):
                    raise ToytreeError(
                        "Use edge_widths not edge_style for multiple edge widths")
                # check the color
                width = self.style.edge_style["stroke-width"]
                self.style.edge_style.pop("stroke-width")
                self.edge_widths = [width] * self.nedges
        else:
            self.style.edge_style.pop("stroke-width")            
            if isinstance(self.style.edge_widths, (str, int)):
                self.edge_widths = [int(self.style.edge_widths)] * self.nedges

            elif isinstance(self.style.edge_widths, (list, tuple)):
                if len(self.style.edge_widths) != self.nedges:
                    raise ToytreeError("edge_widths arg is the wrong length")
                for cidx in range(self.nedges):
                    self.edge_widths[cidx] = self.style.edge_widths[cidx]

        # SET edge_colors and POP edge_style.stroke
        if self.style.edge_colors is None:
            if self.style.edge_style["stroke"] is None:
                self.style.edge_style.pop("stroke")
                self.edge_colors = [None] * self.nedges
            else:
                if isinstance(self.style.edge_style["stroke"], (list, tuple)):
                    raise ToytreeError(
                        "Use edge_colors not edge_style for multiple edge colors")
                # check the color
                color = self.style.edge_style["stroke"]
                if isinstance(color, (np.ndarray, np.void, list, tuple)):
                    color = toyplot.color.to_css(color)
                self.style.edge_style.pop("stroke")                    
                self.edge_colors = [color] * self.nedges

        # otherwise parse node_color
        else:
            self.style.edge_style.pop("stroke")                                
            if isinstance(self.style.edge_colors, (str, int)):
                # check the color
                color = self.style.edge_colors
                if isinstance(color, (np.ndarray, np.void, list, tuple)):
                    color = toyplot.color.to_css(color)
                self.edge_colors = [color] * self.nedges

            elif isinstance(self.style.edge_colors, (list, tuple)):
                if len(self.style.edge_colors) != self.nedges:
                    raise ToytreeError("edge_colors arg is the wrong length")
                for cidx in range(self.nedges):
                    self.edge_colors[cidx] = self.style.edge_colors[cidx]

        # do not allow empty edge_colors or widths
        self.edge_colors = [i if i else "#262626" for i in self.edge_colors]
        self.edge_widths = [i if i else 2 for i in self.edge_widths]

    # -----------------------------------------------------------------
    # Tree / Graph plotting
    # -----------------------------------------------------------------
    def add_tree_to_axes(self):

        # if edge color or widths then override style stroke and stroke-width
        if self.style.edge_type == 'c':
            self.axes.graph(
                self.coords.edges,
                vcoordinates=self.coords.verts,
                vlshow=False,
                vsize=0,
                estyle=self.style.edge_style,
                ewidth=self.edge_widths,
                ecolor=self.edge_colors,
            )
        # for unrooted graph tip coordinates are auto-fit, so we need to store
        # the vertex locations.
        elif self.style.edge_type == 'u':
            self.axes.graph(
                self.coords.edges,
                #vcoordinates=self.coords.verts,
                vlshow=False,
                vsize=0,
                estyle=self.style.edge_style, 
                # ecolor=...
            )            
        else:
            self.expand_edges_to_lines("edge_colors")
            self.expand_edges_to_lines("edge_widths")
            self.axes.graph(
                self.coords.lines,
                vcoordinates=self.coords.coords,
                vlshow=False,
                vsize=0.,
                estyle=self.style.edge_style, 
                ewidth=self.edge_widths,
                ecolor=self.edge_colors,
            )
  

    def expand_edges_to_lines(self, attr):

        # set default values
        if attr == "edge_colors":
            arr = ["#262626"] * self.coords.lines.shape[0]
        else:
            arr = [2] * self.coords.lines.shape[0]

        # build dict from edges
        cdict = {
            self.coords.edges[i, 1]: getattr(self, attr)[i]
            for i in range(len(self.coords.edges))
        }

        # build new values from lines
        for idx in range(len(arr)):
            edge = self.coords.lines[idx]
            
            # this edge goes into x
            into = edge[1]
            
            # colors going into x in edges is
            val = cdict.get(into)
            
            if val:
                # apply this val to every line into x
                lidx = np.where(self.coords.lines[:, 1] == into)
                arr[lidx[0][0]] = val
                
                # and into y
                y = edge[0]
                lidx = np.where(self.coords.lines[:, 1] == y)
                arr[lidx[0][0]] = val
        
        # update the value list        
        setattr(self, attr, arr)  # edge_colors = arr

    # -----------------------------------------------------------------
    # Node and Node Labels 
    # -----------------------------------------------------------------   
    def add_nodes_to_axes(self):
        """
        Creates a new marker for every node from idx indexes and lists of 
        node_values, node_colors, node_sizes, node_style, node_labels_style.
        Pulls from node_color and adds to a copy of the style dict for each 
        node to create marker.

        Node_colors has priority to overwrite node_style['fill']
        """
        # bail out if not any visible nodes (e.g., none w/ size>0)
        if all([i == "" for i in self.node_labels]):
            return
       
        # build markers for each node.
        marks = []
        for nidx in self.ttree.get_node_values('idx', 1, 1):

            # select node value from deconstructed lists
            nlabel = self.node_labels[nidx]
            nsize = self.node_sizes[nidx]
            nmarker = self.node_markers[nidx]

            # get styledict copies
            nstyle = deepcopy(self.style.node_style)
            nlstyle = deepcopy(self.style.node_labels_style)

            # and mod style dict copies from deconstructed lists
            nstyle["fill"] = self.node_colors[nidx]

            # create mark if text or node
            if (nlabel or nsize):
                mark = toyplot.marker.create(
                    shape=nmarker, 
                    label=str(nlabel),
                    size=nsize,
                    mstyle=nstyle,
                    lstyle=nlstyle,
                )
            else:
                mark = ""

            # store the nodes/marks
            marks.append(mark)

        # node_hover == True to show all features interactive
        if self.style.node_hover is True:
            title = self.get_hover()

        elif isinstance(self.style.node_hover, list):
            # todo: return advice if improperly formatted
            title = self.style.node_hover

        # if hover is false then no hover
        else:
            title = None

        # add nodes
        self.axes.scatterplot(
            self.coords.verts[:, 0],
            self.coords.verts[:, 1],
            marker=marks,
            title=title,
        )

    # -----------------------------------------------------------------
    # Axes styling / scale bar / padding
    # -----------------------------------------------------------------        
    def add_axes_style(self):

        # style axes with padding and show axes
        self.axes.padding = self.style.padding

        if not self._external_axis:
            self.axes.show = True
            if not self.style.scalebar:
                self.axes.show = False
        
        # scalebar        
        if self.style.scalebar and self.style.orient == "right":
            nticks = max((3, np.floor(self.style.width / 100).astype(int)))
            self.axes.y.show = False
            self.axes.x.show = True
            self.axes.x.ticks.show = True

            # generate locations
            locs = np.linspace(0, self.ttree.treenode.height, nticks) * -1

            # generate labels formatted depending on range of locs
            fmt = "{:.2f}"
            if np.abs(locs).max() > 6:
                fmt = "{:.1f}"
            elif np.abs(locs).max() > 10:
                fmt = "{:.0f}"
            self.axes.x.ticks.locator = toyplot.locator.Explicit(
                locations=locs,
                labels=[fmt.format(i) for i in np.abs(locs)],
                )
        elif self.style.scalebar and self.style.orient == "down":
            nticks = max((3, np.floor(self.style.height / 100).astype(int)))
            self.axes.x.show = False
            self.axes.y.show = True
            self.axes.y.ticks.show = True            

            # generate locations
            locs = np.linspace(0, self.ttree.treenode.height, nticks)

            # generate labels formatted depending on range of locs
            fmt = "{:.2f}"
            if np.abs(locs).max() > 6:
                fmt = "{:.1f}"
            elif np.abs(locs).max() > 10:
                fmt = "{:.0f}"
            self.axes.y.ticks.locator = toyplot.locator.Explicit(
                locations=locs,
                labels=[fmt.format(i) for i in np.abs(locs)],
                )

    # ------------------------------------------------------------------
    # Other helper functions
    # ------------------------------------------------------------------
    def get_tip_label_coords(self):
        """
        Get starting position of tip labels text based on locations of the 
        leaf nodes on the tree and style offset and align options. Node
        positions are found using the .verts attribute of coords and is 
        already oriented for the tree face direction. 
        """
        # number of tips
        ns = self.ttree.ntips

        # x-coordinate of tips assuming down-face
        tip_xpos = self.coords.verts[:ns, 0]
        tip_ypos = self.coords.verts[:ns, 1]
        align_edges = None
        align_verts = None

        # handle orientations
        if self.style.orient in (0, 'down'):
            # align tips at zero
            if self.style.tip_labels_align:
                tip_yend = np.zeros(ns)
                align_edges = np.array([
                    (i + len(tip_ypos), i) for i in range(len(tip_ypos))
                ])
                align_verts = np.array(
                    list(zip(tip_xpos, tip_ypos)) + \
                    list(zip(tip_xpos, tip_yend))
                )
                tip_ypos = tip_yend
        else:
            # tip labels align finds the zero axis for orientation...
            if self.style.tip_labels_align:
                tip_xend = np.zeros(ns)
                align_edges = np.array([
                    (i + len(tip_xpos), i) for i in range(len(tip_xpos))
                ])
                align_verts = np.array(
                    list(zip(tip_xpos, tip_ypos)) + \
                    list(zip(tip_xend, tip_ypos))
                )
                tip_xpos = tip_xend
        return tip_xpos, tip_ypos, align_edges, align_verts
        

    def get_hover(self, ordered_features=["idx", "name", "dist", "support"]):
        # build full features titles
        lfeatures = list(set(self.ttree.features) - set(ordered_features))       
        ordered_features += lfeatures

        # build list of hoverstrings in order of idxs
        title = [" "] * self.ttree.nnodes
        for nidx in self.ttree.get_node_values('idx', True, True):
            feats = []
            for feature in ordered_features:
                val = self.ttree.get_node_values(feature, True, True)[nidx]
                if isinstance(val, float):
                    feats.append("{}: {:.4f}".format(feature, val))
                else:
                    feats.append("{}: {}".format(feature, val))
            title[nidx] = feats

        # concatenate into strings for each sample
        title = ["\n".join(i) for i in title]

        # order of hover can depend on the orientation...
        title = title[::-1]
        return title


    def get_dims_from_tree_size(self):
        "Calculate reasonable canvas height and width for tree given N tips" 
        ntips = len(self.ttree)
        if self.style.orient in ("right", "left"):
            # height is long tip-wise dimension
            if not self.style.height:
                self.style.height = max(275, min(1000, 18 * ntips))
            if not self.style.width:
                self.style.width = max(350, min(500, 18 * ntips))
        else:
            # width is long tip-wise dimension
            if not self.style.height:
                self.style.height = max(275, min(500, 18 * ntips))
            if not self.style.width:
                self.style.width = max(350, min(1000, 18 * ntips))


    def get_canvas_and_axes(self, axes):
        if axes: 
            self.canvas = None
            self.axes = axes
            self._external_axis = True
        else:
            self.canvas = toyplot.Canvas(
                height=self.style.height,
                width=self.style.width,
            )
            self.axes = self.canvas.cartesian(
                padding=self.style.padding
            )
        
        # return nothing if tree is empty
        if not self.ttree.treenode.children:
            raise ToytreeError("Tree is empty")
