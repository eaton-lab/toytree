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
        opacity: float,
        xshift: float, # pixel units left/right
        yshift: float, # pixel units up/down
        style: Mapping[str, Any],
    ):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ['x', 'y']
        self.ntable = ntable
        self.sizes = sizes
        self.shapes = shapes
        self.colors = colors
        self.opacity = opacity
        self.xshift = xshift
        self.yshift = yshift
        self.style = style

    def domain(self, axis: str) -> Tuple[float, float]:
        """Return domain defined by the marker positions."""
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """Return extents defined by the marker shape and size."""
        coords = ()
        if 'x' in axis:
            coords += (self.ntable[:, 0], )
        if 'y' in axis:
            coords += (self.ntable[:, 1], )

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
        self._coordinate_axes = ['x', 'y']
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
        # domain = toyplot.data.minimax([
        #     self.ntable[:, index], self.bar_min, self.bar_max,
        #     self.ntable[:, index] + self.bar_max,
        # ])
        # # print(f"X--- {index}, {self.widths}, {self.heights}\n\n")
        # return domain


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
    xext = xext / 2. + width
    yext = yext / 2. + width

    # set extents (implement shift)
    extents[0] = np.min([extents[0], -xext + mark.xshift], axis=0)
    extents[1] = np.max([extents[1], xext + mark.xshift], axis=0)
    extents[2] = np.min([extents[2], -yext + mark.yshift], axis=0)
    extents[3] = np.max([extents[3], yext + mark.yshift], axis=0)
    return extents


if __name__ == "__main__":
    pass
