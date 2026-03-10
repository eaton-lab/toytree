#!/usr/bin/env python

"""Return edge-annotation coordinates for each plotted tree edge."""

from __future__ import annotations

import numpy as np

_LINEAR_LAYOUTS = frozenset({"r", "l", "u", "d"})
_BEZIER_BRANCH_MID_T = float(np.cbrt(0.5))


def _cubic_bezier_point(
    p0: np.ndarray,
    p1: np.ndarray,
    p2: np.ndarray,
    p3: np.ndarray,
    t: float,
) -> np.ndarray:
    """Return a point on a cubic Bezier curve."""
    omt = 1.0 - t
    return (
        (omt**3) * p0 + 3.0 * (omt**2) * t * p1 + 3.0 * omt * (t**2) * p2 + (t**3) * p3
    )


def _get_linear_bezier_midpoint(
    parent: np.ndarray,
    child: np.ndarray,
    layout: str,
) -> np.ndarray:
    """Return a Bezier midpoint at half branch depth for linear layouts."""
    if layout in ("u", "d"):
        control = np.array([child[0], parent[1]], dtype=float)
    else:
        control = np.array([parent[0], child[1]], dtype=float)
    return _cubic_bezier_point(
        parent,
        control,
        control,
        child,
        _BEZIER_BRANCH_MID_T,
    )


def _get_circular_radial_midpoint(
    parent: np.ndarray,
    child: np.ndarray,
    root: np.ndarray,
) -> np.ndarray:
    """Return midpoint on the radial branch segment of circular phylograms."""
    child_vec = child - root
    child_radius = float(np.hypot(child_vec[0], child_vec[1]))
    if np.isclose(child_radius, 0.0):
        return child.copy()

    parent_vec = parent - root
    parent_radius = float(np.hypot(parent_vec[0], parent_vec[1]))
    mid_radius = 0.5 * (child_radius + parent_radius)
    return root + (child_vec * (mid_radius / child_radius))


def get_edge_midpoints(
    etable: np.ndarray,
    ntable: np.ndarray,
    layout: str,
    edge_type: str,
) -> np.ndarray:
    """Return annotation coordinates for plotted edges.

    Returned coordinates are stored in child-index order so the row for a
    plotted edge matches the child index in ``etable``. The root row has no
    corresponding edge and remains ``(0, 0)``.

    Midpoint semantics follow the rendered edge geometry:

    - ``edge_type="c"`` uses the Cartesian midpoint of the straight edge.
    - Linear ``edge_type="p"`` keeps the midpoint on the branch-length
      segment, matching long-standing edge-label placement.
    - Linear ``edge_type="b"`` returns the point on the Bezier curve at half
      branch depth so labels stay on the rendered curve.
    - Circular ``edge_type in {"p", "b"}`` returns the midpoint of the
      radial segment, which is the branch-length-bearing part of the edge.
    """
    nnodes = int(ntable.shape[0])
    midpoints = np.zeros((nnodes, 2), dtype=float)
    root = ntable[-1].astype(float, copy=False)
    layout = str(layout)

    for cidx, pidx in etable:
        child = ntable[cidx].astype(float, copy=False)
        parent = ntable[pidx].astype(float, copy=False)

        if edge_type == "c":
            midpoint = 0.5 * (parent + child)
        elif layout in _LINEAR_LAYOUTS:
            if edge_type == "p":
                if layout in ("u", "d"):
                    midpoint = np.array(
                        [child[0], 0.5 * (parent[1] + child[1])],
                        dtype=float,
                    )
                else:
                    midpoint = np.array(
                        [0.5 * (parent[0] + child[0]), child[1]],
                        dtype=float,
                    )
            elif edge_type == "b":
                midpoint = _get_linear_bezier_midpoint(parent, child, layout)
            else:
                raise ValueError(f"Unsupported edge_type: {edge_type!r}")
        elif layout.startswith("c"):
            if edge_type in ("p", "b"):
                midpoint = _get_circular_radial_midpoint(parent, child, root)
            else:
                raise ValueError(f"Unsupported edge_type: {edge_type!r}")
        else:
            # Unrooted layouts render straight-line edges only.
            if edge_type != "c":
                raise ValueError(
                    "Unsupported edge_type/layout combination: "
                    f"{edge_type!r}, {layout!r}"
                )
            midpoint = 0.5 * (parent + child)

        midpoints[int(cidx)] = midpoint

    return midpoints


if __name__ == "__main__":
    import toytree

    tree = toytree.rtree.unittree(10, seed=123)
    _, _, mark = tree.draw()
    coords = get_edge_midpoints(
        mark.etable,
        mark.ntable,
        mark.layout,
        mark.edge_type,
    )
    print(coords)
