#!/usr/bin/env python

"""Project tree nodes into full-circle or fan-layout coordinates.

Circular layouts accept three string forms:

- ``"c"`` for a full 360-degree layout.
- ``"cN"`` for a fan that spans ``N`` degrees starting at 0.
- ``"cA-B"`` for a fan that starts at ``A`` degrees and ends at ``B``
  degrees, wrapping across 360 when ``B <= A``.

When edge lengths are disabled, or when all branch lengths are zero,
radial positions fall back to cladogram heights measured in unit steps
from each node to its farthest descendant tip. This keeps all tips on
one ring while preserving the nested internal levels.
"""

from typing import Tuple

import numpy as np

from toytree.layout.src.layout_base import BaseLayout
from toytree.utils import ToytreeError


def _parse_circular_layout(layout: str) -> tuple[int, int, int, bool]:
    """Return normalized circular-layout bounds and full-circle state.

    Parameters
    ----------
    layout : str
        Circular layout string in one of the supported forms: ``"c"``,
        ``"cN"``, or ``"cA-B"``.

    Returns
    -------
    tuple[int, int, int, bool]
        Normalized ``(start, end, span, is_full_circle)`` where ``start``
        is in ``[0, 360)``, ``end`` is an unwrapped angle greater than
        ``start``, ``span`` is in ``(0, 360]``, and ``is_full_circle`` is
        ``True`` only when the span is exactly 360 degrees.

    Raises
    ------
    ToytreeError
        If ``layout`` is not a supported circular layout string or if the
        requested angular span is not in ``(0, 360]``.
    """
    msg = "circular style malformed. Should be, e.g., 'c', 'c90', 'c0-180'"
    if not layout or layout[0] != "c":
        raise ToytreeError(msg)

    angles = str(layout[1:]).strip()
    if not angles:
        start = 0
        span = 360
    elif "-" not in angles:
        try:
            span = int(angles)
        except ValueError as exc:
            raise ToytreeError(msg) from exc
        start = 0
    else:
        try:
            raw_start_str, raw_end_str = angles.split("-", 1)
            raw_start = int(raw_start_str)
            raw_end = int(raw_end_str)
        except ValueError as exc:
            raise ToytreeError(msg) from exc
        if raw_start < 0 or raw_end < 0 or raw_start == raw_end:
            raise ToytreeError(msg)
        start = raw_start % 360
        # Convert wrapped fans such as ``c350-10`` into a strictly increasing
        # angular interval so descendant clades occupy contiguous tip spans.
        while raw_end <= raw_start:
            raw_end += 360
        span = raw_end - raw_start

    if not 0 < span <= 360:
        raise ToytreeError(msg)

    end = start + span
    return start, end, span, span == 360


class CircularLayout(BaseLayout):
    """Layout for circular tree projection.

    This layout places tips on a circumference or fan arc and positions
    internal nodes on the spoke midway between their descendant clades.
    Radial distances come from branch lengths when available, otherwise
    from unit cladogram heights that align all tips.
    """

    def run(self):
        """Fill coordinate tables for node and aligned-tip positions."""
        self.coords = np.zeros(shape=(self.tree.nnodes, 2))
        self.tcoords = np.zeros(shape=(self.tree.ntips, 2))
        self.set_fan_coords()

    def _get_root_and_node_heights(self) -> Tuple[float, np.ndarray]:
        """Return root height and node heights for layout projection.

        Circular layouts need non-zero radial distances. If edge lengths
        are disabled or all dists are zero, fall back to unit cladogram
        heights without mutating the tree.
        """
        if self.style.use_edge_lengths and not np.isclose(
            self.tree.treenode.height, 0.0
        ):
            node_heights = np.fromiter(
                (node.height for node in self.tree),
                dtype=float,
                count=self.tree.nnodes,
            )
            return self.tree.treenode.height, node_heights

        node_heights = np.zeros(self.tree.nnodes, dtype=float)
        # Compute unit cladogram heights in idx order so each internal node
        # can reuse already-computed child heights without mutating the tree.
        for idx in range(self.tree.ntips, self.tree.nnodes):
            node = self.tree[idx]
            child_heights = [node_heights[child.idx] for child in node.children]
            node_heights[idx] = max(child_heights, default=-1.0) + 1.0
        root_height = float(node_heights[self.tree.treenode.idx])
        return root_height, node_heights

    def set_fan_coords(self):
        """Fill node and aligned-tip coordinate arrays."""
        root_height, node_heights = self._get_root_and_node_heights()
        start, end, _, is_full_circle = _parse_circular_layout(self.style.layout)
        endpoint = not is_full_circle

        angles = np.linspace(start, end, self.tree.ntips, endpoint=endpoint)
        self.angles = angles
        theta = np.full(self.tree.nnodes, np.nan, dtype=float)
        theta[: self.tree.ntips] = np.deg2rad(angles)
        radii = root_height - node_heights

        # Tip coordinates are the dominant work for large trees, so compute
        # those in one vectorized pass instead of per-tip Python loops.
        hub = np.array([self.style.xbaseline, self.style.ybaseline], dtype=float)
        tip_cos = np.cos(theta[: self.tree.ntips])
        tip_sin = np.sin(theta[: self.tree.ntips])
        self.coords[: self.tree.ntips, 0] = hub[0] + radii[: self.tree.ntips] * tip_cos
        self.coords[: self.tree.ntips, 1] = hub[1] + radii[: self.tree.ntips] * tip_sin
        if self.style.tip_labels_align:
            label_radius = float(np.max(radii[: self.tree.ntips], initial=0.0))
            label_radii = np.repeat(label_radius, self.tree.ntips)
        else:
            label_radii = radii[: self.tree.ntips]
        self.tcoords[:, 0] = hub[0] + label_radii * tip_cos
        self.tcoords[:, 1] = hub[1] + label_radii * tip_sin
        self.coords[self.tree.treenode.idx, :] = hub

        # Internal clades occupy contiguous tip intervals in tree order, so
        # averaging unwrapped child angles yields the correct spoke midpoint.
        for idx in range(self.tree.ntips, self.tree.nnodes - 1):
            node = self.tree[idx]
            theta[idx] = theta[[child.idx for child in node.children]].mean()
            self.coords[idx, 0] = hub[0] + radii[idx] * np.cos(theta[idx])
            self.coords[idx, 1] = hub[1] + radii[idx] * np.sin(theta[idx])
