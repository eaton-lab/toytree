#!/usr/bin/env python

"""A custom toyplot mark Class built from the toyplot Mark constructor.

The purpose of a Mark is to set the `domain` and `extents` of an
mark, so that it can be fit on coordinate axes. This object stores
this info along with the input Node coordinates and style args that
have already been checked for validity.
"""

from typing import List
import toyplot
import numpy as np
from loguru import logger
from toyplot.mark import Mark
import toyplot.text

logger = logger.bind(name="toytree")


class ToytreeMark(Mark):
    """Custom mark for tree edges, nodes, and node_labels.

    This is a super class of toyplot.mark.Mark. All styles that affect
    the Node coordinates have already been applied (e.g., xbaseline),
    however, layout is still useful for setting tip extents.
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
        # self.ntable[:, 0] += xbaseline
        # self.ntable[:, 1] += ybaseline

        # radial positioning
        self.radii = np.sqrt(self.ntable[:, 0] ** 2 + self.ntable[:, 1] ** 2)

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
        if self.layout[0] == "c":
            domain = toyplot.data.minimax(self.ntable[:, :])
            absdomain = max(abs(i) for i in domain)
            # print(absdomain)
            return -absdomain, absdomain
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain

    def extents(self, axes):
        """Testing a new simpler extents for [left-, right+, top-, bottom+]
        """
        # get tip label text extents
        marker_extents = self._get_marker_extents()
        edge_extents = self._get_edge_extents()
        text_extents = self._get_node_label_extents()
        tip_extents = self._get_tip_label_extents()

        arrs = []
        for ext in [marker_extents, edge_extents, text_extents, tip_extents]:
            assert all(i.size == self.nnodes for i in ext), "extents error."
            arrs.append(ext)

        # extents as a tuple[left, right, bottom, top]
        extents = [np.zeros(self.nnodes) for i in range(4)]
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
        if self.layout[0] == 'c':
            max_extent = (np.max(np.abs(extents)) * 1.5) + self.shrink
            extents = tuple([
                np.repeat(-max_extent, self.nnodes),
                np.repeat(max_extent, self.nnodes),
                np.repeat(-max_extent, self.nnodes),
                np.repeat(max_extent, self.nnodes),
            ])
        else:
            pass
            # TODO: what is happending? do we need to project?
            # if self.tip_labels_align:
                # coords[0][:self.tip_labels_angles.size] = self.xbaseline
        return coords, extents


    def _get_tip_label_extents(self) -> List[np.ndarray]:
        """Return extents for each tip label text string."""
        if self.tip_labels is None:
            return [np.zeros(self.nnodes) for i in range(4)]

        # add layout-based angles and styles.
        angles = self.tip_labels_angles
        if self.layout in ['u', 'l']:
            angles = self.tip_labels_angles - 180

        # set empty strings for all internal nodes for now b/c they
        # have their own separate style dict but we want this to
        # still be of length nnodes.
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

        # TODO: trigonometry for tip extents and shrink
        elif self.layout[0] == "c":
            tip_extents[0] *= 1.5
            tip_extents[1] *= 1.5
            tip_extents[2] *= 1.5
            tip_extents[3] *= 1.5
            tip_extents[0] -= self.shrink
        elif self.layout[:3] == "unr":
            logger.debug("unrooted layout needs custom tip extents!")
        return tip_extents

    def _get_node_label_extents(self) -> List[np.ndarray]:
        """Return extents of node label text string extents."""
        if self.node_labels is None:
            return [np.zeros(self.nnodes) for i in range(4)]
        text_extents = toyplot.text.extents(
            text=self.node_labels,
            angle=0,
            style=self.node_labels_style
        )
        return text_extents

    def _get_edge_extents(self) -> List[np.ndarray]:
        """Return extents of edge stroke widths (usually small)."""
        if self.edge_widths is None:
            return [np.repeat(self.edge_style['stroke-width'] / 2., self.nnodes)] * 4
        ewidths = self.edge_widths / 2.
        edge_extents = [ewidths.copy() for i in range(4)]
        edge_extents[0] *= -1
        edge_extents[2] *= -1
        return edge_extents

    def _get_marker_extents(self) -> List[np.ndarray]:
        """Return extent of marker objects given size, etc.

        Usually equal width x height except for rectangle markers.
        """
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
        return node_extents


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")
    tree = toytree.rtree.unittree(5)
    tree._draw_browser(
        edge_widths=np.arange(9),
        node_markers="r2x1",
        node_labels=None,
    )
    # tree.style._validate()
    # mark_ = ToytreeMark(
    #     ntable=tree.get_node_coordinates(),
    #     node_mask=tree.get
    #     node_colors=np.array(["black", "black", "black"]),
    #     node_sizes=np.array([2, 3, 4]),
    #     node_style={},
    #     node_markers=np.array(["o", "o", "o"]),
    #     node_hover=True,
    #     etable=np.array([[0, 1], [0, 2], [2, 2]]),
    #     edge_colors=["red", "red", "red"],
    #     edge_widths=np.array([3.0, 2.0, 1.0]),
    #     edge_type="p",
    #     edge_style={"stroke": "black", "stroke-width": 2},
    #     edge_align_style={},
    #     tip_labels=['a', 'b', 'c', 'd'],
    #     tip_labels_angles=None,#np.array([90]),
    #     tip_labels_colors=None,#np.array(['red']),
    #     tip_labels_style={},
    #     node_labels=None, #["", "", ""],
    #     node_labels_style={},
    #     tip_labels_align=True,
    #     layout="r",
    #     xbaseline=0,
    #     ybaseline=0,
    #     admixture_edges=None,
    #     shrink=0.0,
    # )
    # print(mark_.extents(["x", "y"]))
