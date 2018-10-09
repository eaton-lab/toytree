#!/usr/bin/env python

"""
A class object for storing Toyplot objects for a Toyplot drawing.
"""

from copy import deepcopy
import numpy as np
import toyplot
import toytree
from .utils import ToytreeError

# should we store node_labels, node_sizes, etc here or in Style?
# It could be that style is just the rules for filling the drawing attrs...
# and the actual drawing features are storing in ._drawing. 


class Drawing:
    def __init__(self, ttree, **kwargs):
        # input objects
        self.ttree = ttree
        self.coords = ttree._coords
        self.style = ttree._style
        self.kwargs = kwargs

        # mutable plotting attributes pulled from styles and tree
        self.node_labels = [""] * self.ttree.nnodes
        self.node_sizes = [0] * self.ttree.nnodes

        # color can be node_style={"fill":x}, or node_color=[...]
        self.tip_labels = None

        # todo...
        self.tip_colors = None
        self.edge_colors = None


    def update(self, axes=None):

        # always update coords in case style params affect the node placement
        self.coords.update()

        # set up base canvas and axes
        self.get_dims_from_tree_size()
        self.get_canvas_and_axes(axes)

        # update attrs for style entries. Some of these can be set with style, 
        # or as a list, e.g., node_style={'fill':'red'} or node_color="red".
        self.assign_node_labels_and_sizes()
        #self.assign_nodes_sizes()
        #self.assign_node_colors()
        self.assign_tip_labels_and_colors()

        # draw tree, nodes, tips, axes on canvas.
        self.add_tree_to_axes()
        self.add_tip_labels_to_axes()
        self.add_nodes_to_axes()
        self.add_axes_style()
        return self.canvas, self.axes
    
    # -----------------------------------------------------------------
    # Sets Drawing.node_labels
    # -----------------------------------------------------------------
    def assign_node_labels_and_sizes(self):
        "assign features of nodes to be plotted based on user kwargs"

        # shorthand
        nvals = self.ttree.get_node_values()

        # False == Hide nodes and labels unless user entered size 
        if self.style["node_labels"] is False:
            self.style["vlshow"] = False            
            self.node_labels = ["" for i in nvals]           
            if self.style["node_size"]:
                assert isinstance(self.style["node_size"], (int, str))
                self.node_sizes = (
                    [int(self.style["node_size"])] * len(nvals)
                )
                    
        # True == Show nodes, label=idx, and show hover
        elif self.style["node_labels"] is True:
            self.style["vlshow"] = True
            #self.style["node_hover"] = True
            self.node_labels = self.ttree.get_node_values('idx', 1, 1)
            # use default node size as a list if not provided
            if not self.style["node_size"]:
                self.node_sizes = [20] * len(nvals)
            else:
                assert isinstance(self.style["node_size"], (int, str))
                self.node_sizes = (
                    [int(self.style["node_size"])] * len(nvals)
                )

        # User entered lists or other for node labels or sizes; check lengths.
        else:
            # show labels
            self.style["vlshow"] = True

            # make node labels into a list of values 
            if isinstance(self.style["node_labels"], list):
                assert len(self.style["node_labels"]) == len(nvals)
                self.node_labels = self.style["node_labels"]

            elif isinstance(self.style["node_labels"], str):
                # check if user entered a feature
                if self.style["node_labels"] in self.ttree.features:
                    self.node_labels = self.ttree.get_node_values(
                        self.style["node_labels"], 1, 0)
                else:
                    self.node_labels = [self.style["node_labels"]] * len(nvals)
            else:
                self.node_labels = self.ttree.get_node_values("idx", 1, 0)

            # make node sizes as a list; set to zero if node label is ""
            if isinstance(self.style["node_size"], list):
                assert len(self.style["node_size"], list) == len(nvals)
                self.node_sizes = self.style["node_size"]

            elif isinstance(self.style["node_size"], (str, int, float)):
                tmpns = float(self.style["node_size"])
                # set default size if none
                if tmpns in (None, False, 0):
                    self.node_sizes = [20] * len(nvals)
                else:
                    self.node_sizes = [int(tmpns)] * len(nvals)
            else:
                self.node_sizes = [20] * len(nvals)

            # override node sizes to hide based on node labels
            for nidx, node in enumerate(self.node_labels):
                if self.node_labels[nidx] == "":
                    self.node_sizes[nidx] = 0

    
    def assign_tip_labels_and_colors(self):
        "assign tip labels based on user provided kwargs"
        # shorthand label
        anchorshift = "-toyplot-anchor-shift"

        # COLOR
        # tip color overrides tipstyle[fill]
        if self.style.get("tip_labels_color"):
            if 'fill' in self.style["tip_labels_style"]:
                self.style["tip_labels_style"].pop("fill")

        # LABELS
        # False == hide tip labels
        if self.style["tip_labels"] is False:
            self.style["tip_labels_style"][anchorshift] = "0px"
            self.tip_labels = ["" for i in self.ttree.get_tip_labels()]

        # LABELS
        # user entered something...
        else:
            # if user did not change label-offset then shift it here
            if not self.style["tip_labels_style"][anchorshift]:
                self.style["tip_labels_style"][anchorshift] = "15px"

            # if user entered list in get_tip_labels order [reversed] then flip 
            if isinstance(self.style["tip_labels"], list):
                self.tip_labels = self.style["tip_labels"][::-1]

            # True assigns tip labels from tree
            else:
                #self._style["tip_labels"] = self.get_tip_labels()
                if self.ttree._fixed_order:
                    self.tip_labels = self.ttree._fixed_order
                else:
                    self.tip_labels = self.ttree.get_tip_labels()[::-1]
    
    # -----------------------------------------------------------------
    # 
    # -----------------------------------------------------------------
    def add_tree_to_axes(self):
        if self.style["edge_type"] == 'c':
            mark = self.axes.graph(
                self.coords.edges,
                vcoordinates=self.coords.verts,
                vlshow=False,
                vsize=0,
                estyle=self.style["edge_style"],
                # ecolor=self._style["edge_color"], ## ...
            )
        else:
            mark = self.axes.graph(
                self.coords.lines,
                vcoordinates=self.coords.coords,
                vlshow=False,
                vsize=0.,
                estyle=self.style["edge_style"],
                # ecolor=self._style["edge_color"], ## ...
            )
        return mark


    def add_tip_labels_to_axes(self):
        # get tip-coords and align-coords from verts
        xpos, ypos, aedges, averts = self.get_tip_label_coords()

        # add tip names to coordinates calculated above
        mark = self.axes.text(
            xpos, 
            ypos,
            self.tip_labels, 
            angle=(0 if self.style["orient"] in ("right", "left") else -90),
            style=self.style["tip_labels_style"],
            color=self.style["tip_labels_color"],
        )

        # get stroke-width for aligned tip-label lines (optional)
        # copy stroke-width from the edge_style unless user set it
        if not self.style["edge_align_style"].get("stroke-width"):
            self.style["edge_align_style"]["stroke-width"] = (
                self.style["edge_style"]["stroke-width"]
            )

        # add lines to connect tree tips to aligned tips. We don't
        # return this mark since it's optional.
        if self.style["tip_labels_align"]:
            self.axes.graph(
                aedges,
                vcoordinates=averts,
                estyle=self.style["edge_align_style"],
                vlshow=False,
                vsize=0,
            )
        return mark
    
    
    def add_nodes_to_axes(self):
        """
        Creates a new marker for every node from idx indexes and lists of 
        node_values, node_colors, node_sizes, node_style, node_label_style.
        Pulls from node_color and adds to a copy of the style dict for each 
        node to create marker.

        Node_colors has priority to overwrite node_style['fill']
        """
        # bail out if not any visible nodes (e.g., none w/ size>0)
        if not self.style["node_labels"]:
            return

        # build markers for each node.
        marks = []
        for nidx in self.ttree.get_node_values('idx', 1, 1):

            # select node value
            nlabel = self.node_labels[nidx]
            nsize = self.node_sizes[nidx]
            nstyle = deepcopy(self.style["node_style"])
            nlstyle = deepcopy(self.style["node_labels_style"])

            # get node color
            if self.style["node_color"]:
                # parsing color is tricky b/c there are many accepted formats
                if isinstance(self.style["node_color"], str):
                    nstyle["fill"] = self.style["node_color"]
                elif isinstance(self.style["node_color"], (np.ndarray, list, tuple)):
                    color = self.style["node_color"][nidx]
                    if isinstance(color, (np.ndarray, np.void, list, tuple)):
                        color = toyplot.color.to_css(color)
                    nstyle["fill"] = color
                else:
                    pass

            # create mark if text or node
            if (nlabel or nsize):
                mark = toyplot.marker.create(
                    shape="o",
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
        if self.style["node_hover"] is True:
            title = self.get_hover()

        elif isinstance(self.style["node_hover"], list):
            # todo: return advice if improperly formatted
            title = self.style["node_hover"]

        # if hover is false then no hover
        else:
            title = None

        # add nodes
        mark = self.axes.scatterplot(
            self.coords.verts[:, 0],
            self.coords.verts[:, 1],
            marker=marks,
            title=title,
        )
        return mark
    
    
    def add_axes_style(self):
        self.axes.padding = self.style["axes"]["padding"]
        self.axes.show = self.style["axes"]["show"]
        
        # scalebar        
        self.axes.x.show = self.style["axes"]["x.show"]
        self.axes.x.ticks.show = self.style["axes"]["x.ticks.show"]
        self.axes.x.ticks.labels.angle = self.style["axes"]["x.ticks.labels.angle"]
        self.axes.x.domain.min = self.style["axes"]["x.domain.min"]
        self.axes.x.domain.max = self.style["axes"]["x.domain.max"]        

        # scalebar
        self.axes.y.show = self.style["axes"]["y.show"]
        self.axes.y.ticks.show = self.style["axes"]["y.ticks.show"]
        self.axes.y.ticks.labels.angle = self.style["axes"]["y.ticks.labels.angle"]
        self.axes.y.domain.min = self.style["axes"]["y.domain.min"]
        self.axes.y.domain.max = self.style["axes"]["y.domain.max"]        

        # allow coloring axes
        if (self.style["axes"]["x_label_color"] or self.style["axes"]["y_label_color"]):
            self.axes.x.spine.style.update(
                {"stroke": self.style["axes"]["x_label_color"]})
            self.axes.x.ticks.style.update(
                {"stroke": self.style["axes"]["x_label_color"]})            
            self.axes.x.ticks.labels.style.update(
                {"stroke": self.style["axes"]["x_label_color"]})                        
            self.axes.y.spine.style.update(
                {"stroke": self.style["axes"]["y_label_color"]})                                    
            self.axes.y.ticks.style.update(
                {"stroke": self.style["axes"]["y_label_color"]})                                                
            self.axes.y.ticks.labels.style.update(
                {"stroke": self.style["axes"]["y_label_color"]})                                                            

    # ------------------------------------------------------------------
    #
    # ------------------------------------------------------------------
    def get_tip_label_coords(self):
        """
        Get starting position of tip labels text based on locations of the 
        leaf nodes on the tree and style offset and align options. Node
        positions are found using the .verts attribute of coords and is 
        already oriented for the tree face direction. 
        """
        # number of tips
        ns = len(self.ttree)

        # x-coordinate of tips assuming down-face
        tip_xpos = self.coords.verts[:ns, 0]
        tip_ypos = self.coords.verts[:ns, 1]
        align_edges = None
        align_verts = None

        # handle orientations
        if self.style['orient'] in (0, 'down'):
            # align tips at zero
            if self.style["tip_labels_align"]:               
                tip_yend = np.zeros(ns)
                align_edges = np.array([
                    (i, i + len(tip_ypos)) for i in range(len(tip_ypos))
                ])
                align_verts = np.array(
                    list(zip(tip_xpos, tip_ypos)) + \
                    list(zip(tip_xpos, tip_yend))
                )
                tip_ypos = tip_yend
        else:
            # tip labels align finds the zero axis for orientation...
            if self.style["tip_labels_align"]:
                tip_xend = np.zeros(ns)
                align_edges = np.array([
                    (i, i + len(tip_xpos)) for i in range(len(tip_xpos))
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
        "Calculate reasonable height and width for tree given N tips" 
        ntips = len(self.ttree)
        if self.style.get("orient") in ["right", "left"]:
            # long tip-wise dimension
            if not self.style.get("height"):
                self.style["height"] = max(275, min(1000, 18 * ntips))
            if not self.style.get("width"):
                self.style["width"] = max(225, min(500, 18 * ntips))
        else:
            # long tip-wise dimension
            if not self.style.get("width"):
                self.style["width"] = max(275, min(1000, 18 * ntips))
            if not self.style.get("height"):
                self.style["height"] = max(225, min(500, 18 * ntips))


    def get_canvas_and_axes(self, axes):
        if axes: 
            self.canvas = None
            self.axes = axes
        else:
            self.canvas = toyplot.Canvas(
                height=self.style["height"],
                width=self.style["width"],
            )
            self.axes = self.canvas.cartesian(
                padding=self.style["axes"]["padding"]
            )
            self.axes.show = False
        
        # return nothing if tree is empty
        if not self.ttree.tree.children:
            raise ToytreeError("Tree is empty")
