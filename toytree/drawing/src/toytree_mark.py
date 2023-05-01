#!/usr/bin/env python

"""A custom toyplot mark Class built from the toyplot Mark constructor.

The purpose of a Mark is to set the `domain` and `extents` of an
mark, so that it can be fit on coordinate axes. This object stores
this info along with the input Node coordinates and style args that
have already been checked for validity.
"""

from typing import List, Tuple
import toyplot
import numpy as np
from loguru import logger
from toyplot.mark import Mark
import toyplot.text

logger = logger.bind(name="toytree")


class ToyTreeMark(Mark):
    """

    """
    def __init__(self, **kwargs):
        Mark.__init__(self, annotation=False)

        # relevant for Mark domain and extents
        self._coordinate_axes = ['x', 'y']
        """: names of the Cartesian axes."""
        self.ntable: np.ndarray = kwargs.get("ntable")
        """: coordinates of the Nodes."""
        self.etable: np.ndarray = kwargs.get("etable")
        """: 2D array of edge idx labels."""
        self.ttable: np.ndarray = kwargs.get("ttable")
        """: coordinates of tip Nodes (diff when tip_labels_align=True)"""

        # all validated style values
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def nnodes(self) -> int:
        """The number of nodes in the tree"""
        return self.ntable.shape[0]

    def domain(self, axis: str) -> Tuple[float, float]:
        """The Nodes define the domain of data (tip labels not included).

        The Cartesian axes will only place ticks across the data domain.
        """
        if self.layout[0] == "c":
            domain = toyplot.data.minimax(self.ntable[:, :])
            absdomain = max(abs(i) for i in domain)
            return -absdomain, absdomain
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]] :
        """The tip labels and Node markers define the extents of the data.

        This is extra padding to ensure node markers, e.g., circle doesn't
        get cut off by the axes. But most importantly it is to create
        padding to fit the tip labels. To do so requires parsing info
        about the tip labels style dict.

        Note
        ----
        Extents are [min-x, max-x, min-y, max-y]; remember that larger
        y-values are down on the canvas.

        Returns
        -------
        coords: Tuple[np.ndarray, np.ndarray]
        extents: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        Each ndarray is len=nnodes.
        """
        # this array can be modified during rendering so grab a copy.
        coords = self.ntable.copy()
        coords[:self.ttable.shape[0]] = self.ttable.copy()
        coords = (coords[:, 0], coords[:, 1])

        # get marker/label extents and update minmax for each feature
        extents = [np.zeros(self.nnodes)] * 4
        extents = set_node_label_extents(self, extents)
        extents = set_marker_extents(self, extents)
        extents = set_edge_extents(self, extents)
        extents = set_tip_label_extents(self, extents)

        # self._coordinate_axes[i] for in list(axis)
        return coords, extents


# class ToyTreeMark2(Mark):
#     """Custom mark for tree edges, nodes, and node_labels.

#     This is a super class of toyplot.mark.Mark. All styles that affect
#     the Node coordinates have already been applied (e.g., xbaseline),
#     however, layout is still useful for setting tip extents.
#     """
#     def __init__(
#         self,
#         ntable,
#         node_mask,
#         node_colors,
#         node_sizes,
#         node_style,
#         node_markers,
#         node_hover,
#         etable,
#         edge_colors,
#         edge_widths,
#         edge_type,
#         edge_style,
#         edge_align_style,
#         tip_labels,
#         tip_labels_angles,
#         tip_labels_colors,
#         tip_labels_style,
#         node_labels,
#         node_labels_style,
#         tip_labels_align,
#         layout,
#         xbaseline,
#         ybaseline,
#         shrink,
#         **kwargs,
#     ):

#         # inherit type: Tree marks should always be part of the
#         # data domain, whereas tip-labels are not.
#         Mark.__init__(self, annotation=False)

#         # check arg types
#         self._coordinate_axes = ['x', 'y']
#         self.layout = layout
#         self.shrink = (shrink if shrink else 0)

#         # store anything here that you want available as tool-tip hovers
#         self.ntable = ntable
#         self.etable = etable

#         # positioning: coordinates will be shifted during rendering.
#         self.xbaseline = xbaseline
#         self.ybaseline = ybaseline
#         # self.ntable[:, 0] += xbaseline
#         # self.ntable[:, 1] += ybaseline

#         # radial positioning: only calculate this if layout == 'c'
#         if layout == "c":
#             self.radii = np.sqrt(self.ntable[:, 0] ** 2 + self.ntable[:, 1] ** 2)

#         # node plotting args
#         self.node_mask = node_mask
#         self.node_colors = node_colors
#         self.node_sizes = node_sizes
#         self.node_markers = node_markers
#         self.node_style = node_style
#         self.node_hover = node_hover

#         # edge (tree) plotting args
#         self.edge_colors = edge_colors
#         self.edge_widths = edge_widths
#         self.edge_style = edge_style
#         self.edge_type = edge_type
#         self.edge_align_style = edge_align_style

#         # tip labels
#         self.tip_labels = tip_labels
#         self.tip_labels_angles = tip_labels_angles
#         self.tip_labels_colors = tip_labels_colors
#         self.tip_labels_style = tip_labels_style
#         self.tip_labels_align = tip_labels_align

#         # node labels
#         self.node_labels = node_labels
#         self.node_labels_style = node_labels_style

#     @property
#     def nnodes(self):
#         """The number of nodes in the tree"""
#         return self.ntable.shape[0]

#     def domain(self, axis):
#         """The domain of data that will be tracked."""
#         if self.layout[0] == "c":
#             domain = toyplot.data.minimax(self.ntable[:, :])
#             absdomain = max(abs(i) for i in domain)
#             # print(absdomain)
#             return -absdomain, absdomain
#         index = self._coordinate_axes.index(axis)
#         domain = toyplot.data.minimax(self.ntable[:, index])
#         return domain

#     def extents(self, axes):
#         """Testing a new simpler extents for [left-, right+, top-, bottom+]
#         """
#         # get tip label text extents
#         marker_extents = self._get_marker_extents()
#         edge_extents = self._get_edge_extents()
#         text_extents = self._get_node_label_extents()
#         tip_extents = self._get_tip_label_extents()

#         arrs = []
#         for ext in [marker_extents, edge_extents, text_extents, tip_extents]:
#             assert all(i.size == self.nnodes for i in ext), "extents error."
#             arrs.append(ext)

#         # extents as a tuple[left, right, bottom, top]
#         extents = [np.zeros(self.nnodes) for i in range(4)]
#         for nidx in range(self.nnodes):
#             extents[0][nidx] = min(arr[0][nidx] for arr in arrs)
#             extents[1][nidx] = max(arr[1][nidx] for arr in arrs)
#             extents[2][nidx] = min(arr[2][nidx] for arr in arrs)
#             extents[3][nidx] = max(arr[3][nidx] for arr in arrs)

#         # coordinates as a tuple[x, y] for linear or circular layouts
#         coords = (
#             self.ntable[:, 0].copy(),
#             self.ntable[:, 1],
#         )
#         if self.layout[0] == 'c':
#             max_extent = (np.max(np.abs(extents)) * 1.5) + self.shrink
#             extents = tuple([
#                 np.repeat(-max_extent, self.nnodes),
#                 np.repeat(max_extent, self.nnodes),
#                 np.repeat(-max_extent, self.nnodes),
#                 np.repeat(max_extent, self.nnodes),
#             ])
#         else:
#             pass
#             # TODO: what is happending? do we need to project?
#             # if self.tip_labels_align:
#                 # coords[0][:self.tip_labels_angles.size] = self.xbaseline
#         return coords, extents

#     def _get_tip_label_extents(self) -> List[np.ndarray]:
#         """Return extents for each tip label text string."""
#         if self.tip_labels is None:
#             return [np.zeros(self.nnodes) for i in range(4)]

#         # add layout-based angles and styles.
#         angles = self.tip_labels_angles
#         if self.layout in ['u', 'l']:
#             angles = self.tip_labels_angles - 180

#         # set empty strings for all internal nodes for now b/c they
#         # have their own separate style dict but we want this to
#         # still be of length nnodes.
#         tip_extents = list(toyplot.text.extents(
#             text=list(self.tip_labels) + [""] * (self.nnodes - len(self.tip_labels)),
#             angle=angles,
#             style=self.tip_labels_style
#         ))
#         if self.layout == "r":
#             tip_extents[1] *= 2
#             tip_extents[1] += self.shrink
#         elif self.layout == "d":
#             tip_extents[3] *= 2
#             tip_extents[3] += self.shrink
#         elif self.layout == "u":
#             tip_extents[2] *= 2
#             tip_extents[2] -= self.shrink
#         elif self.layout == "l":
#             tip_extents[0] *= 2
#             tip_extents[0] -= self.shrink

#         # TODO: trigonometry for tip extents and shrink
#         elif self.layout[0] == "c":
#             tip_extents[0] *= 1.5
#             tip_extents[1] *= 1.5
#             tip_extents[2] *= 1.5
#             tip_extents[3] *= 1.5
#             tip_extents[0] -= self.shrink
#         elif self.layout[:3] == "unr":
#             logger.debug("unrooted layout needs custom tip extents!")
#         return tip_extents

#     def _get_node_label_extents(self) -> List[np.ndarray]:
#         """Return extents of node label text string extents."""
#         if self.node_labels is None:
#             return [np.zeros(self.nnodes) for i in range(4)]
#         text_extents = toyplot.text.extents(
#             text=self.node_labels,
#             angle=0,
#             style=self.node_labels_style
#         )
#         return text_extents

#     def _get_edge_extents(self) -> List[np.ndarray]:
#         """Return extents of edge stroke widths (usually small)."""
#         if self.edge_widths is None:
#             return [np.repeat(self.edge_style['stroke-width'] / 2., self.nnodes)] * 4
#         ewidths = self.edge_widths / 2.
#         edge_extents = [ewidths.copy() for i in range(4)]
#         edge_extents[0] *= -1
#         edge_extents[2] *= -1
#         return edge_extents

#     def _get_marker_extents(self) -> List[np.ndarray]:
#         """Return extent of marker objects given size, etc.

#         Usually equal width x height except for rectangle markers.
#         """
#         marker_heights = np.zeros(self.node_markers.size)
#         marker_widths = np.zeros(self.node_markers.size)
#         for idx, marker in enumerate(self.node_markers):
#             if marker.startswith("r"):
#                 width, height = [int(i) for i in marker[1:].split("x")]
#             else:
#                 width, height = 1, 1
#             marker_widths[idx] = width
#             marker_heights[idx] = height
#         node_extents = [self.node_sizes / 2. for i in range(4)]
#         node_extents[0] *= marker_widths * -1
#         node_extents[1] *= marker_widths
#         node_extents[2] *= marker_heights * -1
#         node_extents[3] *= marker_heights
#         return node_extents


def set_node_label_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of node label text string extents.
    """
    # return if no labels
    if mark.node_labels is None:
        return extents

    # else return the calculated text extents
    ext = toyplot.text.extents(
        text=mark.node_labels,
        angle=0,
        style=mark.node_labels_style
    )
    extents[0] = np.min([extents[0], ext[0]], axis=0)
    extents[1] = np.max([extents[1], ext[1]], axis=0)
    extents[2] = np.min([extents[2], ext[2]], axis=0)
    extents[3] = np.max([extents[3], ext[3]], axis=0)
    return extents


def set_marker_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of node label text string extents.
    """
    # return if no nodes
    if not any(mark.node_sizes):
        return extents

    # markers are symmetrical NxN unless 'rNxM'
    yext = np.zeros(mark.nnodes)
    xext = np.zeros(mark.nnodes)

    iter_data = zip(mark.node_markers, mark.node_sizes)
    for idx, (marker, size) in enumerate(iter_data):
        if marker.startswith("r"):
            width, height = [int(i) for i in marker[1:].split("x")]
        else:
            width, height = 1, 1
        yext[idx] = height * size
        xext[idx] = width * size

    # extent is half the markers dimension in either direction
    xext = xext / 2. + mark.node_style["stroke-width"]
    yext = yext / 2. + mark.node_style["stroke-width"]

    # set extents
    extents[0] = np.min([extents[0], -xext], axis=0)
    extents[1] = np.max([extents[1], xext], axis=0)
    extents[2] = np.min([extents[2], -yext], axis=0)
    extents[3] = np.max([extents[3], yext], axis=0)
    return extents


def set_edge_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of edge stroke widths (usually small)."""
    if mark.edge_widths is None:
        widths = np.repeat(mark.edge_style["stroke-width"] / 2., mark.nnodes)
    else:
        widths = mark.edge_widths / 2.

    extents[0] = np.min([extents[0], -widths], axis=0)
    extents[1] = np.max([extents[1], widths], axis=0)
    extents[2] = np.min([extents[2], -widths], axis=0)
    extents[3] = np.max([extents[3], widths], axis=0)
    return extents


def set_tip_label_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents for each tip label text string.

    TODO
    ----
    - check -180 on 'ud'
    - support 'c', 'unr'
    - censor vertical text extent
    - support 'shrink' space
    """
    # return if not tip labels
    if mark.tip_labels is None:
        return extents

    # add layout-based angles and styles.
    angles = mark.tip_labels_angles
    if mark.layout in ['u', 'l']:
        angles = mark.tip_labels_angles - 180

    # else return the calculated text extents
    ext = toyplot.text.extents(
        text=mark.tip_labels,
        angle=angles,
        style=mark.tip_labels_style
    )

    # only concerned with tip Nodes
    ntips = len(mark.tip_labels)

    # TEMPORARY HACK: until toyplot extents is fixed.
    # extend the tip label direction extra space.
    if mark.layout == "r":
        ext[1][:ntips] *= 2
        ext[1][:ntips] += mark.shrink
    elif mark.layout == "d":
        ext[3][:ntips] *= 2
        ext[3][:ntips] += mark.shrink
    elif mark.layout == "u":
        ext[2][:ntips] *= 2
        ext[2][:ntips] -= mark.shrink
    elif mark.layout == "l":
        ext[0][:ntips] *= 2
        ext[0][:ntips] -= mark.shrink

    # Not important b/c we use fit-range later.
    elif mark.layout[0] == "c":
        ext[0][:ntips] *= 1.5
        ext[1][:ntips] *= 1.5
        ext[2][:ntips] *= 1.5
        ext[3][:ntips] *= 1.5
        ext[0][:ntips] -= mark.shrink
    elif mark.layout[:3] == "unr":
        logger.debug("unrooted layout needs custom tip ext!")

    # only allow increasing extents
    extents[0][:ntips] = np.min([extents[0][:ntips], ext[0]], axis=0)
    extents[1][:ntips] = np.max([extents[1][:ntips], ext[1]], axis=0)
    extents[2][:ntips] = np.min([extents[2][:ntips], ext[2]], axis=0)
    extents[3][:ntips] = np.max([extents[3][:ntips], ext[3]], axis=0)
    return extents


if __name__ == "__main__":

    import toytree
    from toytree.style import validate_style
    from toytree.drawing.src.draw_toytree import (
        get_tree_style_base, get_layout, tree_style_to_css_dict)

    toytree.set_log_level("DEBUG")
    tree = toytree.rtree.rtree(5, seed=123)
    tree[2].name = "hello world"

    kwargs = tree.draw(
        debug=True,
        tip_labels=True,
        tip_labels_angles=0,
        tip_labels_style={'font-size': 15},
        node_sizes=16,
        node_mask=False,
    )

    style = get_tree_style_base(tree, tree_style=kwargs.pop("tree_style"))
    logger.warning(style.tip_labels_style.font_size)
    style = validate_style(tree, style, **kwargs)
    logger.warning(style.tip_labels_style.font_size)
    layout = get_layout(tree, style)
    logger.warning(style.tip_labels_style.font_size)

    ntable = layout.coords
    etable = tree.get_edges("idx")
    mark = ToyTreeMark(ntable=ntable, etable=etable, **tree_style_to_css_dict(style))
    logger.info(style.tip_labels_angles)
    print(f"domain x = {mark.domain('x')}")
    print(f"domain y = {mark.domain('y')}")
    print(mark.extents('x')[0])
    print(mark.extents('x')[1][0])
    print(mark.extents('x')[1][1])
    print(mark.extents('x')[1][2])
    print(mark.extents(['x', 'y'])[1][3])

    # mark = ToyTreeMark2(ntable=ntable, etable=etable, **tree_style_to_css_dict(style))
    # print(f"domain x = {mark.domain('x')}")
    # print(f"domain y = {mark.domain('y')}")
    # print(mark.extents('x')[0])
    # print(mark.extents('x')[1][0])
    # print(mark.extents('x')[1][1])
    # print(mark.extents('x')[1][2])
    # print(mark.extents(['x', 'y'])[1][3])
