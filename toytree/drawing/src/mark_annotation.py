#!/usr/bin/env python

"""...

"""

from typing import Tuple, List, Mapping, Any
import numpy as np
import toyplot
from toyplot.mark import Mark
from loguru import logger

logger = logger.bind(name="toytree")


class AnnotationMarker(Mark):
    """TipMarkers are Point markers with a custom render function that
    allows for adding a transform to shift position by px units.
    """
    def __init__(
        self,
        ntable: np.ndarray,
        sizes: np.ndarray,
        shapes: np.ndarray,
        colors: np.ndarray,
        opacity: float,
        xshift: float,
        yshift: float,
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
        """The markers define the domain of data"""
        index = self._coordinate_axes.index(axis)
        domain = toyplot.data.minimax(self.ntable[:, index])
        return domain

    def extents(self, axis: str) -> Tuple[Tuple[np.ndarray], Tuple[np.ndarray]]:
        """The marker shape and size define the extents of the data."""
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
    """Rectangles annotation Mark.

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
        """The markers define the domain of data"""
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


def set_marker_extents(mark: Mark, extents: List[np.ndarray]) -> List[np.ndarray]:
    """Return extents of node label text string extents.
    """
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
