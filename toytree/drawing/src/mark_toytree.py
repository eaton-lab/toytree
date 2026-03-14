#!/usr/bin/env python

"""A custom toyplot mark Class built from the toyplot Mark constructor.

The purpose of a Mark is to set the `domain` and `extents` of an
mark, so that it can be fit on coordinate axes. This object stores
this info along with the input Node coordinates and style args that
have already been checked for validity.
"""

from typing import List, Sequence, Tuple, Union

import numpy as np
import toyplot
import toyplot.text
from toyplot.mark import Mark

from toytree.layout.src.layout_circular import _parse_circular_layout
from toytree.utils import ToytreeError


# Note: see toytree/drawing/src/render_tree.py for rendering code.
def _is_full_circle_layout(layout: str) -> bool:
    """Return ``True`` if a circular layout spans 360 degrees."""
    try:
        return _parse_circular_layout(layout)[3]
    except ToytreeError:
        return False


class ToyTreeMark(Mark):
    """Tree Mark optionally including Node markers and tip labels."""

    def __init__(self, **kwargs):
        Mark.__init__(self, annotation=False)

        # relevant for Mark domain and extents
        self._coordinate_axes = ["x", "y"]
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

        self._cached_domain: dict[str, tuple[float, float]] = {}
        self._cached_extents_xy: tuple[np.ndarray, ...] | None = None
        self._cached_coords_xy: tuple[np.ndarray, np.ndarray] | None = None

    @property
    def nnodes(self) -> int:
        """The number of nodes in the tree."""
        return self.ntable.shape[0]

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return node-coordinate domain for one Cartesian axis.

        For full-circle layouts (e.g., ``c`` or ``c0-360``) this returns a
        symmetric square domain so x/y scales remain identical. For fan
        layouts (e.g., ``c0-180``), axis domains use true x/y minimax values
        to avoid allocating empty space.
        """
        cached = self._cached_domain.get(axis)
        if cached is not None:
            return cached

        if self.layout[0] == "c" and _is_full_circle_layout(self.layout):
            domain = toyplot.data.minimax(self.ntable[:, :])
            absdomain = max(abs(i) for i in domain)
            cached = (-absdomain, absdomain)
        else:
            index = self._coordinate_axes.index(axis)
            domain = toyplot.data.minimax(self.ntable[:, index])
            cached = (float(domain[0]), float(domain[1]))
        self._cached_domain[axis] = cached
        return cached

    def _get_cached_coords_xy(self) -> tuple[np.ndarray, np.ndarray]:
        """Return immutable cached coordinates used by extent calculations."""
        if self._cached_coords_xy is None:
            coords = self.ntable.copy()
            coords[: self.ttable.shape[0], :] = self.ttable
            self._cached_coords_xy = (coords[:, 0], coords[:, 1])
        return self._cached_coords_xy

    def _get_cached_extents_xy(self) -> tuple[np.ndarray, ...]:
        """Return immutable cached extents for repeated finalize passes."""
        if self._cached_extents_xy is None:
            extents = [np.zeros(self.nnodes, dtype=float) for _ in range(4)]
            extents = set_node_label_extents(self, extents)
            extents = set_marker_extents(self, extents)
            extents = set_edge_extents(self, extents)
            extents = set_tip_label_extents(self, extents)
            self._cached_extents_xy = tuple(
                np.asarray(arr, dtype=float).copy() for arr in extents
            )
        return self._cached_extents_xy

    def extents(
        self, axis: Union[str, Sequence[str]]
    ) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return extents defined by tip labels and Node markers.

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
        axes = (
            [axis]
            if isinstance(axis, str) and axis in self._coordinate_axes
            else list(axis)
        )
        coords_xy = self._get_cached_coords_xy()
        extents_xy = self._get_cached_extents_xy()

        # Renderers may adjust returned arrays in-place, so preserve the cache
        # and hand out fresh copies on every call.
        coords = tuple(coords_xy[self._coordinate_axes.index(ax)].copy() for ax in axes)
        extents = tuple(arr.copy() for arr in extents_xy)
        return coords, extents

    def get_companion_scale_spec(
        self,
        axes,
        *,
        axis: str = "auto",
        padding: float = 15.0,
        domain_override: tuple[float, float] | None = None,
    ):
        """Return companion scale metadata for rendering a tree ruler."""
        from toytree.annotate.src.add_scale_bar import (
            _get_tree_scale_bounds_finalized,
            _resolve_internal_tree_scale_domain,
            _resolve_tree_scale_axis,
            _validate_scale_padding,
        )
        from toytree.drawing.src.scale_axes import CompanionScaleSpec

        resolved_axis = _resolve_tree_scale_axis(self, axis)
        resolved_padding = _validate_scale_padding(padding, "tree")
        tmin, tmax = _resolve_internal_tree_scale_domain(
            self,
            resolved_axis,
            domain_override,
        )
        shift = self.xbaseline if resolved_axis == "x" else self.ybaseline
        # Tree rulers label tree-depth coordinates, but their companion bounds
        # still come from finalized host pixel geometry around the rendered tree.
        return CompanionScaleSpec(
            key="tree",
            axis=resolved_axis,
            data_domain=(float(tmin), float(tmax)),
            locator_domain=(float(tmin), float(tmax)),
            bounds_getter=lambda: _get_tree_scale_bounds_finalized(
                axes,
                self,
                resolved_axis,
                resolved_padding,
            ),
            label_midpoint=0.5 * float(tmin + tmax),
            shift=float(shift),
            use_tree_domain_mark=True,
        )


def set_node_label_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of node label text string extents."""
    # return if no labels
    if mark.node_labels is None:
        return extents

    # else return the calculated text extents
    ext = toyplot.text.extents(
        text=mark.node_labels, angle=0, style=mark.node_labels_style
    )
    extents[0] = np.min([extents[0], ext[0]], axis=0)
    extents[1] = np.max([extents[1], ext[1]], axis=0)
    extents[2] = np.min([extents[2], ext[2]], axis=0)
    extents[3] = np.max([extents[3], ext[3]], axis=0)
    return extents


def set_marker_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of node label text string extents."""
    # return if no nodes
    if not any(mark.node_sizes):
        return extents

    # markers are symmetrical NxN unless 'rNxM'
    yext = np.zeros(mark.nnodes)
    xext = np.zeros(mark.nnodes)

    iter_data = zip(mark.node_markers, mark.node_sizes)
    for idx, (marker, size) in enumerate(iter_data):
        if marker.startswith("r"):
            width, height = [float(i) for i in marker[1:].split("x")]
        else:
            width, height = 1, 1
        yext[idx] = height * size
        xext[idx] = width * size

    # extent is half the markers dimension in either direction
    xext = xext / 2.0 + mark.node_style["stroke-width"]
    yext = yext / 2.0 + mark.node_style["stroke-width"]

    # set extents
    extents[0] = np.min([extents[0], -xext], axis=0)
    extents[1] = np.max([extents[1], xext], axis=0)
    extents[2] = np.min([extents[2], -yext], axis=0)
    extents[3] = np.max([extents[3], yext], axis=0)
    return extents


def set_edge_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of edge stroke widths (usually small)."""
    if mark.edge_widths is None:
        widths = np.repeat(mark.edge_style["stroke-width"] / 2.0, mark.nnodes)
    else:
        widths = mark.edge_widths / 2.0

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
    """
    # return if not tip labels
    if mark.tip_labels is None:
        return extents

    # add layout-based angles and styles.
    angles = mark.tip_labels_angles
    tip_style = mark.tip_labels_style
    if mark.layout in ["u", "l"]:
        angles = mark.tip_labels_angles - 180
        tip_style = mark.tip_labels_style.copy()
        offset = toyplot.units.convert(
            tip_style["-toyplot-anchor-shift"],
            "px",
            "px",
        )
        tip_style["text-anchor"] = "end"
        tip_style["-toyplot-anchor-shift"] = -offset

    # only concerned with tip Nodes
    ntips = len(mark.tip_labels)

    # set extents for unrooted layout
    is_unrooted = mark.layout not in ["r", "l", "u", "d"] and mark.layout[0] != "c"
    if is_unrooted:
        left = np.zeros(ntips)
        right = np.zeros(ntips)
        top = np.zeros(ntips)
        bottom = np.zeros(ntips)
        for idx, tip in enumerate(mark.tip_labels):
            angle = mark.tip_labels_angles[idx]
            style = mark.tip_labels_style.copy()
            offset = toyplot.units.convert(
                style["-toyplot-anchor-shift"],
                "px",
                "px",
            )
            if 90 < angle < 270:
                style["text-anchor"] = "end"
                style["-toyplot-anchor-shift"] = -offset
                angle -= 180
            ext = toyplot.text.extents(
                text=[tip],
                angle=[angle],
                style=style,
            )
            left[idx] = ext[0][0]
            right[idx] = ext[1][0]
            top[idx] = ext[2][0]
            bottom[idx] = ext[3][0]

        extents[0][:ntips] = np.min([extents[0][:ntips], left], axis=0)
        extents[1][:ntips] = np.max([extents[1][:ntips], right], axis=0)
        extents[2][:ntips] = np.min([extents[2][:ntips], top], axis=0)
        extents[3][:ntips] = np.max([extents[3][:ntips], bottom], axis=0)
        return extents

    # else return the calculated text extents
    ext = toyplot.text.extents(
        text=mark.tip_labels, angle=angles, style=mark.tip_labels_style
    )

    # only allow increasing extents
    extents[0][:ntips] = np.min([extents[0][:ntips], ext[0]], axis=0)
    extents[1][:ntips] = np.max([extents[1][:ntips], ext[1]], axis=0)
    extents[2][:ntips] = np.min([extents[2][:ntips], ext[2]], axis=0)
    extents[3][:ntips] = np.max([extents[3][:ntips], ext[3]], axis=0)
    return extents
