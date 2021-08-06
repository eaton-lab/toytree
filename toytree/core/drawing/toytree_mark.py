#!/usr/bin/env python

"""
A toytree Mark Class object built on the toyplot Mark constructor.
This simply inits the Style arguments passed from draw that have
already been checked by StyleChecker and it established the
domain and extents.

TODO: maybe make an Extents class to construct more clearly.
"""

import toyplot
import numpy as np
from toyplot.mark import Mark


class ToytreeMark(Mark):
    """
    Custom mark for tree edges, nodes, and node_labels.
    """
    def __init__(
        self,
        ntable,
        node_mask,
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
        **kwargs,
        ):

        # inherit type: Tree marks should always be part of the
        # data domain, whereas tip-labels are not.
        Mark.__init__(self, annotation=False)

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
        self.node_mask = node_mask
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
        """The number of nodes in the tree"""
        return self.ntable.shape[0]

    def domain(self, axis):
        """The domain of data that will be tracked."""
        #if self.layout == "c":
        #    return toyplot.data.minimax(self.ntable)
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain

    def extents(self, axes):
        """
        Testing a new simpler extents for [left, right bottom, top]
        """
        # get tip label text extents
        if self.tip_labels is None:
            tip_extents = [np.zeros(self.nnodes) for i in range(4)]
        else:
            # add layout-based angles and styles.
            angles = self.tip_labels_angles
            if self.layout in ['u', 'l']:
                angles = self.tip_labels_angles - 180
            tip_extents = list(toyplot.text.extents(
                text=list(self.tip_labels) + [""] * (self.nnodes - len(self.tip_labels)),
                angle=angles,
                style=self.tip_labels_style
            ))
            if self.layout == "r":
                tip_extents[1] *= 2
                tip_extents[1] += self.shrink
            elif self.layout == "d":
                tip_extents[3] *= 2
                tip_extents[3] += self.shrink
            elif self.layout == "u":
                tip_extents[2] *= 2
                tip_extents[2] -= self.shrink
            elif self.layout == "l":
                tip_extents[0] *= 2
                tip_extents[0] -= self.shrink
            elif self.layout == "c":
                # TODO: trigonometry for tip extents and shrink
                tip_extents[0] *= 1.5
                tip_extents[1] *= 1.5
                tip_extents[2] *= 1.5
                tip_extents[3] *= 1.5
                # tip_extents[0] -= self.shrink

        # get node labels text extents
        if self.node_labels is None:
            text_extents = tuple(np.zeros(self.nnodes) for i in range(4))
        else:
            text_extents = toyplot.text.extents(
                text=self.node_labels,
                angle=0,
                style=self.node_labels_style
            )

        # get edge width extents (usually quite small)
        if self.edge_widths is None:
            ewidths = np.repeat(self.edge_style['stroke-width'] / 2., self.nnodes)
        else:
            ewidths = self.edge_widths / 2.
        edge_extents = [ewidths.copy() for i in range(4)]
        edge_extents[0] *= -1
        edge_extents[2] *= -1

        # get node marker size extents (usually equal width x height except
        # for rectangle markers, which we accommodate.
        marker_heights = np.zeros(self.node_markers.size)
        marker_widths = np.zeros(self.node_markers.size)
        for idx, marker in enumerate(self.node_markers):
            if marker.startswith("r"):
                width, height = [int(i) for i in marker[1:].split("x")]
            else:
                width, height = 1, 1
            marker_widths[idx] = width
            marker_heights[idx] = height
        node_extents = [self.node_sizes / 2. for i in range(4)]
        node_extents[0] *= marker_widths * -1
        node_extents[1] *= marker_widths
        node_extents[2] *= marker_heights * -1
        node_extents[3] *= marker_heights

        # extents as a tuple[left, right, bottom, top]
        extents = [np.zeros(self.nnodes) for i in range(4)]
        arrs = [node_extents, edge_extents, text_extents, tip_extents]
        for nidx in range(self.nnodes):
            extents[0][nidx] = min(arr[0][nidx] for arr in arrs)
            extents[1][nidx] = max(arr[1][nidx] for arr in arrs)
            extents[2][nidx] = min(arr[2][nidx] for arr in arrs)
            extents[3][nidx] = max(arr[3][nidx] for arr in arrs)

        # coordinates as a tuple[x, y] for linear or circular layouts
        coords = (
            self.ntable[:, 0].copy(),
            self.ntable[:, 1],
        )
        if self.layout == 'c':
            max_extent = (np.max(np.abs(extents)) * 1.5) + self.shrink
            extents = tuple([
                np.repeat(-max_extent, self.nnodes),
                np.repeat(max_extent, self.nnodes),
                np.repeat(-max_extent, self.nnodes),
                np.repeat(max_extent, self.nnodes),
            ])
        else:
            if self.tip_labels_align:
                coords[0][:self.tip_labels_angles.size] = 0
        return coords, extents


    # def old_extents(self, axes):
    #     """
    #     Extends domain to fit tip names or marks based on their size,
    #     but does not extend the data domain.

    #     The main component to worry about here is tip labels text, especially
    #     for weird layouts that make it angled. For circular we project text
    #     at angle and inverted angle to get projection from anchor start,end.
    #     But node markers also contribute to this since extents=0 would cut a
    #     circular 15px node marker in half at the root. So we would need at
    #     least 15px left extent.

    #     Further modification is made by the argument 'scale' which can
    #     compress the tree to allow more space for names. This is done by
    #     making the extents larger.

    #     extents is [l, r, b, t] for each textbox
    #     """
    #     if self.layout != "c":
    #         # coordinates of all nodes on the tree.
    #         coords = (
    #             self.ntable[:, 0].copy(),
    #             self.ntable[:, 1].copy(),
    #         )

    #         # extents of all node markers
    #         ntips = len(self.tip_labels_angles)
    #         nnodes = len(coords[0])

    #         # set terminal nodes to align at zero for tipname extents
    #         if self.tip_labels_align:
    #             coords[0][:ntips] = 0.

    #         # get tip label text extents
    #         if self.tip_labels is None:
    #             text_extents = [[0, 0, 0, 0]] * ntips
    #         else:
    #             # expand font size for extra fit
    #             expanded_font_size = 0 + toyplot.units.convert(
    #                 self.tip_labels_style['font-size'], "px", "px")

    #             # get text extents
    #             text_extents = toyplot.text.extents(
    #                 self.tip_labels,
    #                 self.tip_labels_angles,
    #                 style={
    #                     "-toyplot-vertical-align": "middle",
    #                     "font-family": "helvetica",
    #                     "font-weight": "normal",
    #                     "stroke": "none",
    #                     "font-size": expanded_font_size,
    #                 }
    #             )

    #         # check edge widths
    #         try:
    #             if self.edge_widths is not None:
    #                 xedge_widths = self.edge_widths / 2.
    #             else:
    #                 xedge_widths = [self.edge_style['stroke-width'] / 2.] * self.nnodes
    #         except KeyError:
    #             xedge_widths = np.repeat(1, self.nnodes)

    #         # empty extents for filling
    #         extents = (
    #             np.zeros(nnodes), np.zeros(nnodes),
    #             np.zeros(nnodes), np.zeros(nnodes),
    #         )

    #         # fill each node
    #         for nidx in range(nnodes):

    #             # check tips extents
    #             if nidx < ntips:
    #                 if self.node_mask[nidx]:
    #                     node_extent = np.array([0, 0, 0, 0] * 4)
    #                 else:
    #                     node_extent = np.array([self.node_sizes[nidx] / 2.] * 4)
    #                     node_extent *= [-1, 1, -1, 1]
    #                 edge_extent = np.array([xedge_widths[nidx]] * 4)
    #                 edge_extent *= [-1, 1, -1, 1]

    #                 # get indexed text-extents: l, r, b, t
    #                 if self.tip_labels is None:
    #                     text_extent = np.array([0, 0, 0, 0])
    #                 else:
    #                     text_extent = [
    #                         text_extents[0][nidx],
    #                         text_extents[1][nidx],
    #                         text_extents[2][nidx],
    #                         text_extents[3][nidx],
    #                     ]

    #                     offset = toyplot.units.convert(
    #                         self.tip_labels_style["-toyplot-anchor-shift"],
    #                         "px", "px",
    #                     )

    #                     # shrink extends the extents in the angle of the tips x layout
    #                     if self.layout == 'd':
    #                         width = abs(text_extent[2]) + abs(text_extent[3])
    #                         text_extent[3] = width + self.shrink + offset
    #                         text_extent[2] = 0

    #                     elif self.layout == 'u':
    #                         width = abs(text_extent[2]) + abs(text_extent[3])
    #                         text_extent[2] = -(width + offset + self.shrink)
    #                         text_extent[3] = 0

    #                     elif self.layout == 'r':
    #                         width = text_extent[1] - text_extent[0]
    #                         text_extent[0] = 0
    #                         # text_extent[1] = width + offset + self.shrink
    #                         text_extent[1] = (offset + width) * 2 + self.shrink

    #                     elif self.layout == 'l':
    #                         width = text_extent[1] - text_extent[0]
    #                         text_extent[0] = -((offset + width) * 2 + self.shrink)
    #                         text_extent[1] = 0

    #             # check tips extents
    #             else:
    #                 node_extent = np.array([self.node_sizes[nidx] / 2.] * 4)
    #                 node_extent *= [-1, 1, -1, 1]
    #                 edge_extent = np.array([xedge_widths[nidx] / 2.] * 4)
    #                 edge_extent *= [-1, 1, -1, 1]
    #                 text_extent = np.array([0, 0, 0, 0])

    #             # store extent nidx
    #             extents[0][nidx] = min([node_extent[0], edge_extent[0], text_extent[0]])
    #             extents[1][nidx] = max([node_extent[1], edge_extent[1], text_extent[1]])
    #             extents[2][nidx] = min([node_extent[2], edge_extent[2], text_extent[2]])
    #             extents[3][nidx] = max([node_extent[3], edge_extent[3], text_extent[3]])

    #     # for radial trees we want extents to fit similar in all directions
    #     # regardless of branch and tip name lengths. So find the radius of
    #     # the circle + anchor shift + longest name and pass in all directions.
    #     else:
    #         coords = (
    #             max(self.radii) * np.array([-1, 0, 1, 0]),
    #             max(self.radii) * np.array([0, 1, 0, -1]),
    #         )

    #         # no tip labels for extends
    #         if self.tip_labels is None:

    #             # no extents necessary
    #             extents = (
    #                 np.repeat(max(self.node_sizes) * -1, 4),
    #                 np.repeat(max(self.node_sizes), 4),
    #                 np.repeat(max(self.node_sizes), 4),
    #                 np.repeat(max(self.node_sizes) * -1, 4),
    #             )

    #         # get the maxwidth of any tips ignoring positioning
    #         else:
    #             tips = self.tip_labels
    #             expanded_font_size = 10 + toyplot.units.convert(
    #                 self.tip_labels_style['font-size'], "px", "px")
    #             exts = toyplot.text.extents(
    #                 tips,
    #                 0,
    #                 style={
    #                     "-toyplot-vertical-align": "middle",
    #                     "font-family": "helvetica",
    #                     "font-weight": "normal",
    #                     "stroke": "none",
    #                     "font-size": expanded_font_size,
    #                 }
    #             )
    #             maxw = max([exts[1][i] - exts[0][i] for i in range(len(tips))])
    #             ashift = toyplot.units.convert(
    #                 self.tip_labels_style["-toyplot-anchor-shift"], "px", "px")
    #             extents = (
    #                 np.repeat(-self.shrink - ashift - maxw * 1.5, 4),  # left ext
    #                 np.repeat(self.shrink + ashift + maxw * 1.5, 4),  # right ext
    #                 np.repeat(-self.shrink - ashift - maxw * 1.5, 4),  # bottom
    #                 np.repeat(self.shrink + ashift + maxw * 1.5, 4),  # top
    #             )
    #     for i in extents:
    #         print(i)
    #     # for i in coords:
    #     #     print(i)
    #     # print("")
    #     return coords, extents
