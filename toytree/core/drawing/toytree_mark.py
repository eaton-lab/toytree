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
        Testing a new simpler extents for [left-, right+, top-, bottom+]
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
