#!/usr/bin/env python

"""..."""

from typing import Any, List, Mapping, Sequence, Tuple

import numpy as np
import toyplot
from toyplot.mark import Mark


class AnnotationMarker(Mark):
    """Custom rendered markers that allow a transform to shift position by px units."""

    def __init__(
        self,
        ntable: np.ndarray,
        sizes: np.ndarray,
        shapes: np.ndarray,
        colors: np.ndarray,
        opacity: np.ndarray,
        xshift: float | np.ndarray,  # pixel units left/right
        yshift: float | np.ndarray,  # pixel units up/down
        style: Mapping[str, Any],
        local_span: np.ndarray | None = None,  # pixel units along arc span
        local_depth: np.ndarray | None = None,  # pixel units along arc depth
        root_xy: np.ndarray | None = None,
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ["x", "y"]
        self.ntable = ntable
        self.sizes = sizes
        self.shapes = shapes
        self.colors = colors
        self.opacity = opacity
        nmarks = int(ntable.shape[0])
        self.xshift = (
            np.repeat(float(xshift), nmarks)
            if np.isscalar(xshift)
            else np.asarray(xshift, dtype=float)
        )
        self.yshift = (
            np.repeat(float(yshift), nmarks)
            if np.isscalar(yshift)
            else np.asarray(yshift, dtype=float)
        )
        self.local_span = (
            None if local_span is None else np.asarray(local_span, dtype=float)
        )
        self.local_depth = (
            None if local_depth is None else np.asarray(local_depth, dtype=float)
        )
        self.root_xy = None if root_xy is None else np.asarray(root_xy, dtype=float)
        self.style = style

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return domain defined by the marker positions."""
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return extents defined by the marker shape and size."""
        coords = ()
        if "x" in axis:
            coords += (self.ntable[:, 0],)
        if "y" in axis:
            coords += (self.ntable[:, 1],)

        # get marker/label extents and update minmax for each feature
        extents = [np.zeros(self.ntable.shape[0])] * 4
        extents = set_marker_extents(self, extents)
        return coords, extents


class AnnotationRect(Mark):
    """Custom rendered rectangle Mark.

    The rectangle annotation is used to create clade outlines, bars.
    These Marks can be defined both in terms of data width,height as
    well as in terms of additional canvas px units.
    """

    def __init__(
        self,
        ntable: np.ndarray,
        xtable: np.ndarray,
        ytable: np.ndarray,
        # heights: np.ndarray,
        colors: np.ndarray,
        opacity: float,
        xshift: float,
        yshift: float,
        style: Mapping[str, Any],
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ["x", "y"]
        self.ntable = ntable
        """: array of (nmarks, 2) ..."""
        self.xtable = xtable
        self.ytable = ytable

        self.colors = colors
        self.opacity = opacity
        self.xshift = xshift
        self.yshift = yshift
        self.style = style

    def domain(self, axis: str) -> Tuple[float, float]:
        """Define the domain of data."""
        index = self._coordinate_axes.index(axis)
        if index == 0:
            return toyplot.data.minimax(self.xtable)
        return toyplot.data.minimax(self.ytable)


class AnnotationLine(Mark):
    """Polyline annotation Mark used for edge overlay rendering."""

    def __init__(
        self,
        xpaths: Sequence[np.ndarray],
        ypaths: Sequence[np.ndarray],
        colors: np.ndarray | None,
        widths: np.ndarray,
        opacity: np.ndarray,
        use_group_opacity: bool,
        group_opacity: float | None,
        style: Mapping[str, Any],
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ["x", "y"]
        self.xpaths = xpaths
        self.ypaths = ypaths
        self.colors = colors
        self.widths = widths
        self.opacity = opacity
        self.use_group_opacity = use_group_opacity
        self.group_opacity = group_opacity
        self.style = style

        # Cache per-line bounds used by domain/extents.
        nlines = len(self.xpaths)
        self._xmin = np.zeros(nlines, dtype=float)
        self._xmax = np.zeros(nlines, dtype=float)
        self._ymin = np.zeros(nlines, dtype=float)
        self._ymax = np.zeros(nlines, dtype=float)
        for idx in range(nlines):
            self._xmin[idx] = np.min(self.xpaths[idx])
            self._xmax[idx] = np.max(self.xpaths[idx])
            self._ymin[idx] = np.min(self.ypaths[idx])
            self._ymax[idx] = np.max(self.ypaths[idx])

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return min/max domain spanned by all line coordinates."""
        index = self._coordinate_axes.index(axis)
        if index == 0:
            return float(np.min(self._xmin)), float(np.max(self._xmax))
        return float(np.min(self._ymin)), float(np.max(self._ymax))

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return zero extra text / marker extents for line annotations."""
        if axis == "x":
            coords = ((self._xmin + self._xmax) / 2.0,)
        elif axis == "y":
            coords = ((self._ymin + self._ymax) / 2.0,)
        else:
            coords = ((self._xmin + self._xmax) / 2.0, (self._ymin + self._ymax) / 2.0)
        nlines = len(self.xpaths)
        extents = (
            np.zeros(nlines, dtype=float),
            np.zeros(nlines, dtype=float),
            np.zeros(nlines, dtype=float),
            np.zeros(nlines, dtype=float),
        )
        return coords, extents


class AnnotationGradientLine(AnnotationLine):
    """Polyline annotation Mark rendered with per-edge linear gradients."""

    def __init__(
        self,
        xpaths: Sequence[np.ndarray],
        ypaths: Sequence[np.ndarray],
        start_colors: np.ndarray,
        end_colors: np.ndarray,
        widths: np.ndarray,
        opacity: np.ndarray,
        use_group_opacity: bool,
        group_opacity: float | None,
        style: Mapping[str, Any],
    ):
        super().__init__(
            xpaths=xpaths,
            ypaths=ypaths,
            colors=None,
            widths=widths,
            opacity=opacity,
            use_group_opacity=use_group_opacity,
            group_opacity=group_opacity,
            style=style,
        )
        self.start_colors = start_colors
        self.end_colors = end_colors


class AnnotationStochasticMapLine(AnnotationLine):
    """Polyline annotation mark for stochastic-map edge segments."""

    def __init__(
        self,
        xpaths: Sequence[np.ndarray],
        ypaths: Sequence[np.ndarray],
        colors: np.ndarray,
        widths: np.ndarray,
        opacity: np.ndarray,
        map_id: int,
        style: Mapping[str, Any],
    ):
        super().__init__(
            xpaths=xpaths,
            ypaths=ypaths,
            colors=colors,
            widths=widths,
            opacity=opacity,
            use_group_opacity=False,
            group_opacity=None,
            style=style,
        )
        self.map_id = int(map_id)


class AnnotationTipTileMark(Mark):
    """Polygon path annotation mark for tip-aligned tile rendering."""

    def __init__(
        self,
        ntable: np.ndarray,
        root_xy: np.ndarray,
        layout: str,
        depth: float,
        offset: float,
        show: np.ndarray,
        colors: np.ndarray | None,
        fill_color: Any,
        opacity: np.ndarray,
        stroke_color: Any,
        style: Mapping[str, Any],
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ["x", "y"]
        self.ntable = ntable
        self.root_xy = root_xy
        self.layout = layout
        self.depth = depth
        self.offset = offset
        self.show = show
        self.colors = colors
        self.fill_color = fill_color
        self.opacity = opacity
        self.stroke_color = stroke_color
        self.style = style
        self.tip_indices = np.array([], dtype=int)
        self.paths: list[str] = []
        self.slot_min = np.array([], dtype=float)
        self.slot_max = np.array([], dtype=float)
        self.slot_kind = ""

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return domain based on tip coordinates."""
        index = self._coordinate_axes.index(axis)
        return toyplot.data.minimax(self.ntable[:, index])

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return layout-aware extents for tile offset / depth in px units."""
        if axis == "x":
            coords = (self.ntable[:, 0],)
        elif axis == "y":
            coords = (self.ntable[:, 1],)
        else:
            coords = (self.ntable[:, 0], self.ntable[:, 1])

        ntips = self.ntable.shape[0]
        a0 = float(self.offset)
        a1 = float(self.offset + self.depth)
        min_d = min(a0, a1)
        max_d = max(a0, a1)
        # Add small room for optional stroke outlines.
        stroke_pad = 1.0 if self.stroke_color is not None else 0.0

        left = np.zeros(ntips, dtype=float)
        right = np.zeros(ntips, dtype=float)
        top = np.zeros(ntips, dtype=float)
        bottom = np.zeros(ntips, dtype=float)

        if self.layout == "r":
            left[:] = min(0.0, min_d) - stroke_pad
            right[:] = max(0.0, max_d) + stroke_pad
            top[:] = -stroke_pad
            bottom[:] = stroke_pad
        elif self.layout == "l":
            left[:] = -max(0.0, max_d) - stroke_pad
            right[:] = -min(0.0, min_d) + stroke_pad
            top[:] = -stroke_pad
            bottom[:] = stroke_pad
        elif self.layout == "d":
            left[:] = -stroke_pad
            right[:] = stroke_pad
            top[:] = min(0.0, min_d) - stroke_pad
            bottom[:] = max(0.0, max_d) + stroke_pad
        elif self.layout == "u":
            left[:] = -stroke_pad
            right[:] = stroke_pad
            top[:] = -max(0.0, max_d) - stroke_pad
            bottom[:] = -min(0.0, min_d) + stroke_pad
        else:
            # Circular tiles can extend in any direction around each tip.
            # Use symmetric reach so autosizing does not clip outer arcs.
            reach = max(abs(min_d), abs(max_d)) + stroke_pad
            left[:] = -reach
            right[:] = reach
            top[:] = -reach
            bottom[:] = reach

        extents = (left, right, top, bottom)
        return coords, extents


def _visible_stroke_pad(style: Mapping[str, Any]) -> float:
    """Return a conservative fit pad for visible stroke width."""
    stroke = style.get("stroke")
    if stroke is None or str(stroke).strip().lower() == "none":
        return 0.0

    value = style.get("stroke-width", 1.0)
    if isinstance(value, (int, float)):
        return max(0.0, float(value))

    text = str(value).strip().lower()
    if text.endswith("px"):
        text = text[:-2]
    try:
        return max(0.0, float(text))
    except ValueError:
        return 1.0


class AnnotationTipBarMark(Mark):
    """Polygon path annotation mark for tip-aligned bar rendering."""

    def __init__(
        self,
        ntable: np.ndarray,
        root_xy: np.ndarray,
        layout: str,
        offset: float,
        width: float,
        show: np.ndarray,
        values: np.ndarray,
        value_min: float,
        value_max: float,
        max_bar_depth: float,
        bar_depths: np.ndarray,
        colors: np.ndarray | None,
        fill_color: Any,
        opacity: np.ndarray,
        hover_labels: np.ndarray | None,
        style: Mapping[str, Any],
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ["x", "y"]
        self.ntable = ntable
        self.root_xy = root_xy
        self.layout = layout
        self.offset = offset
        self.width = width
        self.show = show
        self.values = values
        self.data = values
        self.value_min = value_min
        self.value_max = value_max
        self.max_bar_depth = max_bar_depth
        self.bar_depths = bar_depths
        self.colors = colors
        self.fill_color = fill_color
        self.opacity = opacity
        self.hover_labels = hover_labels
        self.style = style
        self.tip_indices = np.array([], dtype=int)
        self.paths: list[str] = []
        self.slot_min = np.array([], dtype=float)
        self.slot_max = np.array([], dtype=float)
        self.occupied_min = np.array([], dtype=float)
        self.occupied_max = np.array([], dtype=float)
        self.slot_kind = ""
        self._cached_raw_domain: dict[str, tuple[float, float]] = {}
        self._cached_extents_xy: tuple[np.ndarray, ...] | None = None
        self._cached_coords_xy: tuple[np.ndarray, np.ndarray] = (
            self.ntable[:, 0].copy(),
            self.ntable[:, 1].copy(),
        )

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return the raw anchor-coordinate domain for shown bar geometry."""
        cached = self._cached_raw_domain.get(axis)
        if cached is not None:
            return cached

        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        cached = (float(domain[0]), float(domain[1]))
        self._cached_raw_domain[axis] = cached
        return cached

    def _get_cached_extents_xy(self) -> tuple[np.ndarray, ...]:
        """Return immutable cached extents for repeated finalize passes."""
        if self._cached_extents_xy is not None:
            return self._cached_extents_xy

        ntips = self.ntable.shape[0]
        a0 = np.repeat(float(self.offset), ntips)
        a1 = a0 + np.asarray(self.bar_depths, dtype=float)
        min_d = np.minimum(a0, a1)
        max_d = np.maximum(a0, a1)
        stroke_pad = _visible_stroke_pad(self.style)

        left = np.zeros(ntips, dtype=float)
        right = np.zeros(ntips, dtype=float)
        top = np.zeros(ntips, dtype=float)
        bottom = np.zeros(ntips, dtype=float)

        # Convert outward bar depth into Cartesian extents relative to each tip
        # anchor: r/l consume x-range, while u/d consume y-range.
        if self.layout == "r":
            left = np.minimum(0.0, min_d) - stroke_pad
            right = np.maximum(0.0, max_d) + stroke_pad
            top[:] = -stroke_pad
            bottom[:] = stroke_pad
        elif self.layout == "l":
            left = -np.maximum(0.0, max_d) - stroke_pad
            right = -np.minimum(0.0, min_d) + stroke_pad
            top[:] = -stroke_pad
            bottom[:] = stroke_pad
        elif self.layout == "d":
            left[:] = -stroke_pad
            right[:] = stroke_pad
            top = np.minimum(0.0, min_d) - stroke_pad
            bottom = np.maximum(0.0, max_d) + stroke_pad
        elif self.layout == "u":
            left[:] = -stroke_pad
            right[:] = stroke_pad
            # Canvas y increases downward, so upward bars become negative top
            # extents with the mirrored bottom bound near the anchor point.
            top = -np.maximum(0.0, max_d) - stroke_pad
            bottom = -np.minimum(0.0, min_d) + stroke_pad
        else:
            reach = np.maximum(np.abs(min_d), np.abs(max_d)) + stroke_pad
            left = -reach
            right = reach
            top = -reach
            bottom = reach
        self._cached_extents_xy = (left, right, top, bottom)
        return self._cached_extents_xy

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return layout-aware extents for bar offset / depth in px units."""
        axes = [axis] if axis in self._coordinate_axes else list(axis)
        coords = tuple(
            self._cached_coords_xy[self._coordinate_axes.index(ax)].copy()
            for ax in axes
        )
        extents = tuple(arr.copy() for arr in self._get_cached_extents_xy())
        return coords, extents

    def get_companion_scale_spec(
        self,
        axes,
        *,
        axis: str = "auto",
        padding: float = 15.0,
    ):
        """Return companion scale metadata for rendering a mark ruler."""
        from toytree.annotate.src.add_scale_bar import (
            _get_linear_tip_bar_scale_bounds_finalized,
            _resolve_tip_bar_axis_domain,
            _resolve_tip_bar_scale_axis,
            _validate_scale_padding,
        )
        from toytree.drawing.src.scale_axes import CompanionScaleSpec
        from toytree.utils import ToytreeError

        resolved_axis = _resolve_tip_bar_scale_axis(self, axis)
        resolved_padding = _validate_scale_padding(padding, "mark")
        tmin = float(self.value_min)
        tmax = float(self.value_max)
        if tmax <= tmin:
            raise ToytreeError(
                "Tip-bar data have zero range; add_axes_scale_bar_to_mark() "
                "requires at least two distinct values."
            )
        # Some layouts display the axis in reverse, but tick generation still
        # needs the increasing raw value domain for consistent labels.
        domain_min, domain_max = _resolve_tip_bar_axis_domain(self, tmin, tmax)
        return CompanionScaleSpec(
            key="mark",
            axis=resolved_axis,
            data_domain=(float(domain_min), float(domain_max)),
            locator_domain=(float(tmin), float(tmax)),
            bounds_getter=lambda: _get_linear_tip_bar_scale_bounds_finalized(
                axes,
                self,
                resolved_padding,
            ),
            label_midpoint=0.5 * float(domain_min + domain_max),
        )


class AnnotationTipLabelMark(Mark):
    """Text annotation mark with per-tip styles and exact text extents."""

    def __init__(
        self,
        ntable: np.ndarray,
        labels: np.ndarray,
        angles: np.ndarray,
        colors: np.ndarray | None,
        opacity: np.ndarray,
        styles: Sequence[Mapping[str, Any]],
    ):
        Mark.__init__(self, annotation=False)
        self._coordinate_axes = ["x", "y"]
        self.ntable = ntable
        self.labels = labels
        self.angles = angles
        self.colors = colors
        self.opacity = opacity
        self.styles = [dict(i) for i in styles]

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return domain based on tip coordinates."""
        index = self._coordinate_axes.index(axis)
        return toyplot.data.minimax(self.ntable[:, index])

    def extents(
        self, axis: str | Sequence[str]
    ) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return exact per-tip text extents for the final angle and style."""
        axes = [axis] if isinstance(axis, str) else list(axis)
        coords = tuple(self.ntable[:, self._coordinate_axes.index(ax)] for ax in axes)

        nvals = self.ntable.shape[0]
        left = np.zeros(nvals, dtype=float)
        right = np.zeros(nvals, dtype=float)
        top = np.zeros(nvals, dtype=float)
        bottom = np.zeros(nvals, dtype=float)
        for idx in range(nvals):
            ext = toyplot.text.extents(
                [str(self.labels[idx])],
                [float(self.angles[idx])],
                self.styles[idx],
            )
            left[idx] = ext[0][0]
            right[idx] = ext[1][0]
            top[idx] = ext[2][0]
            bottom[idx] = ext[3][0]
        return coords, (left, right, top, bottom)


def set_marker_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of node label text string extents."""
    # markers are symmetrical NxN unless 'rNxM'
    yext = np.zeros(mark.ntable.shape[0])
    xext = np.zeros(mark.ntable.shape[0])

    iter_data = zip(mark.shapes, mark.sizes)
    for idx, (marker, size) in enumerate(iter_data):
        if marker.startswith("r"):
            width, height = [int(i) for i in marker[1:].split("x")]
        else:
            width, height = 1, 1
        yext[idx] = height * size
        xext[idx] = width * size

    # extent is half the markers dimension in either direction
    width = mark.style.get("stroke-width", 0)
    xext = xext / 2.0 + width
    yext = yext / 2.0 + width

    # Circular local-frame shifts are orientation dependent at render time.
    # Use conservative isotropic reach so autosizing does not clip markers.
    local_reach = np.zeros(mark.ntable.shape[0], dtype=float)
    if getattr(mark, "local_span", None) is not None:
        local_reach = np.hypot(mark.local_span, mark.local_depth)

    # set extents (implement global + local shifts)
    extents[0] = np.min([extents[0], -xext + mark.xshift - local_reach], axis=0)
    extents[1] = np.max([extents[1], xext + mark.xshift + local_reach], axis=0)
    extents[2] = np.min([extents[2], -yext + mark.yshift - local_reach], axis=0)
    extents[3] = np.max([extents[3], yext + mark.yshift + local_reach], axis=0)
    return extents


if __name__ == "__main__":
    pass
