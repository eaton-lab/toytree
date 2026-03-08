#!/usr/bin/env python

"""Minimal mark used to define tree-only data domain for scale axes."""

from __future__ import annotations

from typing import Sequence

import numpy as np
import toyplot.data
from toyplot.mark import Mark


def _is_full_circle_layout(layout: str) -> bool:
    """Return ``True`` if a circular layout string spans 360 degrees."""
    if not layout or layout[0] != "c":
        return False
    angles = str(layout[1:]).strip()
    if not angles:
        start, end = 0, 360
    elif "-" not in angles:
        start, end = 0, int(angles)
    else:
        start, end = (int(i) for i in angles.split("-", 1))

    while start < 0:
        start += 360
    while end < start:
        end += 360
    if end - start > 360:
        end = start + 359
    return (end - start) == 360


class TreeDomainMark(Mark):
    """Mark that contributes only tree node domain (no label extents)."""

    def __init__(self, ntable: np.ndarray, layout: str):
        Mark.__init__(self, annotation=False)
        self._coordinate_axes = ["x", "y"]
        self.ntable = ntable
        self.layout = layout

    def domain(self, axis: str) -> tuple[float, float]:
        """Return node-coordinate domain for one Cartesian axis.

        Full-circle layouts use a symmetric square domain. Partial circular
        fan layouts use axis-specific minimax domains.
        """
        if (
            self.layout
            and self.layout[0] == "c"
            and _is_full_circle_layout(self.layout)
        ):
            domain = toyplot.data.minimax(self.ntable[:, :])
            absdomain = max(abs(i) for i in domain)
            return -absdomain, absdomain
        index = self._coordinate_axes.index(axis)
        return toyplot.data.minimax(self.ntable[:, index])

    def extents(
        self,
        axis: str | Sequence[str],
    ) -> tuple[
        tuple[np.ndarray, ...], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    ]:  # noqa: E501
        """Return zero extents so only node coordinates define the scale domain."""
        axes = [axis] if isinstance(axis, str) else list(axis)
        coords = tuple(self.ntable[:, self._coordinate_axes.index(ax)] for ax in axes)
        nvals = self.ntable.shape[0]
        zeros = np.zeros(nvals, dtype=float)
        return coords, (zeros, zeros, zeros, zeros)


class HostDomainMark(Mark):
    """Annotation mark that mirrors a host axes domain onto scale axes."""

    def __init__(self, host_axes):
        Mark.__init__(self, annotation=True)
        self._coordinate_axes = ["x", "y"]
        self.host_axes = host_axes
        self._dummy = np.array([0.0], dtype=float)

    def domain(self, axis: str) -> tuple[float, float]:
        """Return current finalized host-axis domain for projection matching."""
        self.host_axes._finalize()
        if axis == "x":
            proj = self.host_axes._x_projection
        else:
            proj = self.host_axes._y_projection
        return float(proj._segments[0].domain.min), float(proj._segments[-1].domain.max)

    def extents(
        self,
        axis: str | Sequence[str],
    ) -> tuple[
        tuple[np.ndarray, ...], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    ]:  # noqa: E501
        """Return zero extents so this mark only contributes display domain."""
        axes = [axis] if isinstance(axis, str) else list(axis)
        coords = tuple(self._dummy for _ in axes)
        zeros = np.zeros(1, dtype=float)
        return coords, (zeros, zeros, zeros, zeros)
