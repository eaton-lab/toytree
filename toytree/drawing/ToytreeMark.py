#!/usr/bin/env python

"""
A toytree Mark Class object built on the toyplot Mark constructor. 
This simply inits the Style arguments passed from draw that have 
already been checked by StyleChecker and it established the 
domain and extents.

TODO: maybe make an Extents class to construct more clearly.
"""

from loguru import logger
import toyplot
import numpy as np
from toyplot.mark import Mark



class ToytreeMark(Mark):
    """
    Custom mark testing.
    """
    def __init__(
        self,
        ntable, 
        node_colors, 
        node_sizes, 
        node_style,
        node_markers,
        node_hover,
        etable,
        edge_colors,
        edge_widths,
        edge_type,
        edge_style,
        edge_align_style,
        tip_labels,
        tip_labels_angles,
        tip_labels_colors,
        tip_labels_style,
        node_labels,
        node_labels_style,
        tip_labels_align,
        layout,
        xbaseline,
        ybaseline,
        admixture_edges,
        shrink,
        **kwargs):

        # inherit type
        Mark.__init__(self)

        # check arg types
        self._coordinate_axes = ['x', 'y']  
        self.layout = layout
        self.shrink = (shrink if shrink else 0)

        # store anything here that you want available as tool-tip hovers
        self.ntable = ntable
        self.etable = etable

        # positioning
        self.xbaseline = xbaseline
        self.ybaseline = ybaseline
        self.ntable[:, 0] += xbaseline
        self.ntable[:, 1] += ybaseline

        # radial positioning
        self.radii = np.sqrt(
            self.ntable[:, 0] ** 2 + self.ntable[:, 1] ** 2 
        )

        # node plotting args
        self.node_colors = node_colors
        self.node_sizes = node_sizes
        self.node_markers = node_markers
        self.node_style = node_style
        self.node_hover = node_hover

        # edge (tree) plotting args
        self.edge_colors = edge_colors
        self.edge_widths = edge_widths
        self.edge_style = edge_style
        self.edge_type = edge_type
        self.edge_align_style = edge_align_style

        # tip labels
        self.tip_labels = tip_labels
        self.tip_labels_angles = tip_labels_angles
        self.tip_labels_colors = tip_labels_colors
        self.tip_labels_style = tip_labels_style
        self.tip_labels_align = tip_labels_align

        # node labels
        self.node_labels = node_labels
        self.node_labels_style = node_labels_style

        # admix edges
        self.admixture_edges = admixture_edges


    @property
    def nnodes(self):
        return self.ntable.shape[0]


    def domain(self, axis):
        """
        The domain of data that will be tracked.
        """
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain


    def extents(self, axes):
        """
        Extends domain to fit tip names or mars based on their size, but 
        does not extend the data domain. 
        The main component to worry about here is tip labels text, especially
        for weird layouts that make it angled. For circular we project text
        at angle and inverted angle to get projection from anchor start,end.
        But node markers also contribute to this since extents=0 would cut a
        circular 15px node marker in half at the root. So we would need at 
        least 15px left extent.

        Further modification is made by the argument 'scale' which can
        compress the tree to allow more space for names. This is done by 
        making the extents larger.

        extents is [l, r, b, t] for each textbox
        """
        if self.layout != "c":
            # coordinates of all nodes on the tree.
            coords = (
                self.ntable[:, 0],
                self.ntable[:, 1],
            )

            # extents of all node markers
            ntips = len(self.tip_labels)
            nnodes = len(coords[0])

            # get tip label text extents
            if np.any(self.tip_labels):
                text_extents = toyplot.text.extents(
                    self.tip_labels,
                    self.tip_labels_angles,
                    style={
                        "-toyplot-vertical-align": "middle",
                        "font-family": "helvetica",
                        "font-weight": "normal",
                        "stroke": "none",
                        "font-size": toyplot.units.convert(
                            self.tip_labels_style['font-size'], "px") + 10,
                    }
                )

            else:
                text_extents = [[0, 0, 0, 0]] * ntips

            # check node extents
            xnode_sizes = self.node_sizes.copy()
            xnode_sizes[self.node_sizes == None] = 0

            # check edge widths
            # tmp fix for multitrees popping stroke-width currently
            try:
                xedge_widths = self.node_sizes.copy()
                xedge_widths[:-1] = self.edge_widths.copy()
                xedge_widths[xedge_widths == None] = self.edge_style['stroke-width']
            except KeyError:
                xedge_widths = np.repeat(2, self.nnodes)

            # empty extents for filling
            extents = (
                np.zeros(nnodes), np.zeros(nnodes),
                np.zeros(nnodes), np.zeros(nnodes),
            )

            # fill each node 
            for nidx in range(nnodes):

                # check tips extents 
                if nidx < ntips:
                    node_extent = np.array([xnode_sizes[nidx]] * 4)
                    node_extent *= [-1, 1, -1, 1]
                    edge_extent = np.array([xedge_widths[nidx]] * 4)
                    edge_extent *= [-1, 1, -1, 1]

                    if not np.any(self.tip_labels):
                        text_extent = np.array([0, 0, 0, 0])
                    else:
                        text_extent = [
                            text_extents[0][nidx],
                            text_extents[1][nidx],
                            text_extents[2][nidx],
                            text_extents[3][nidx],
                        ]

                        offset = toyplot.units.convert(
                            self.tip_labels_style["-toyplot-anchor-shift"],
                            "px",
                        )

                        # shrink extends the extents in the angle of the tips x layout
                        if self.layout == 'd':
                            width = abs(text_extent[2]) + abs(text_extent[3])
                            text_extent[3] = width + self.shrink + offset
                            text_extent[2] = 0

                        elif self.layout == 'u':
                            width = abs(text_extent[2]) + abs(text_extent[3])
                            text_extent[2] = -(width + offset + self.shrink)
                            text_extent[3] = 0

                        elif self.layout == 'r':
                            width = text_extent[1] - text_extent[0]
                            text_extent[0] = 0
                            text_extent[1] = width + offset * self.shrink

                        elif self.layout == 'l':
                            width = text_extent[1] - text_extent[0]
                            text_extent[0] = -(width + offset + self.shrink)
                            text_extent[1] = 0


                # check tips extents 
                else:
                    node_extent = np.array([xnode_sizes[nidx]] * 4)
                    node_extent *= [-1, 1, -1, 1]
                    edge_extent = np.array([xedge_widths[nidx]] * 4)
                    edge_extent *= [-1, 1, -1, 1]
                    text_extent = np.array([0, 0, 0, 0])

                # store extent nidx
                extents[0][nidx] = min([node_extent[0], edge_extent[0], text_extent[0]])
                extents[1][nidx] = max([node_extent[1], edge_extent[1], text_extent[1]])
                extents[2][nidx] = min([node_extent[2], edge_extent[2], text_extent[2]])
                extents[3][nidx] = max([node_extent[3], edge_extent[3], text_extent[3]])


        # for radial trees we want extents to fit similar in all directions
        # regardless of branch and tip name lengths. So find the radius of 
        # the circle + anchor shift + longest name and pass in all directions.
        else:
            coords = (
                max(self.radii) * np.array([-1, 0, 1, 0]),
                max(self.radii) * np.array([0, 1, 0, -1]),
            )

            # no tip labels for extends
            if all([i is None for i in self.tip_labels]):

                # no extents necessary
                if all([i is None for i in self.node_sizes]):
                    coords = tuple([np.array([])] * 2)
                    extents = tuple([np.array([])] * 4)

                # extend by node size                    
                else:
                    extents = (
                        np.repeat(max(self.node_sizes) * -1, 4),
                        np.repeat(max(self.node_sizes), 4),
                        np.repeat(max(self.node_sizes), 4),
                        np.repeat(max(self.node_sizes) * -1, 4),                                                                        
                    )

            # get the maxwidth of any tips ignoring positioning
            else:
                tips = self.tip_labels
                exts = toyplot.text.extents(
                    tips,
                    0, 
                    style={
                        "-toyplot-vertical-align": "middle",
                        "font-family": "helvetica",
                        "font-weight": "normal",
                        "stroke": "none",
                        "font-size": toyplot.units.convert(
                            self.tip_labels_style['font-size'], "px") + 10,
                    }
                )
                maxw = max([exts[1][i] - exts[0][i] for i in range(len(tips))])
                ashift = toyplot.units.convert(
                    self.tip_labels_style["-toyplot-anchor-shift"], "px")
                extents = (
                    np.repeat(-self.shrink - ashift - maxw * 1.5, 4),  # left ext
                    np.repeat(self.shrink + ashift + maxw * 1.5, 4),  # right ext
                    np.repeat(-self.shrink - ashift - maxw * 1.5, 4),  # bottom
                    np.repeat(self.shrink + ashift + maxw * 1.5, 4),  # top
                )

        # # all other layouts 
        # else:
        #     coords = (
        #         self.ntable[:len(self.tip_labels), 0],
        #         self.ntable[:len(self.tip_labels), 1],
        #     )
        #     style = {
        #         'font-size': toyplot.units.convert(self.tip_labels_style['font-size'], "px") + 5,
        #         '-toyplot-anchor-shift': self.tip_labels_style['-toyplot-anchor-shift']
        #     }
        #     extents = toyplot.text.extents(
        #         self.tip_labels,
        #         self.tip_labels_angles,
        #         style,
        #         #(self.tip_labels_style if self.tip_labels[0] else {}),
        #     )

        return coords, extents
