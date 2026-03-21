#!/usr/bin/env python

"""Shared utilities to construct tree edge paths."""

from __future__ import annotations

from typing import List, Literal, Tuple

import numpy as np
from toyplot.coordinates import Cartesian

from toytree.drawing.src.mark_toytree import ToyTreeMark

# SVG path formats for creating edges in tree drawings
PATH_FORMAT = {
    "c": "M {px:.1f} {py:.1f} L {cx:.1f} {cy:.1f}",
    "b1": (
        "M {px:.1f} {py:.1f} C {px:.1f} {cy:.1f}, "
        "{px:.1f} {cy:.1f}, {cx:.1f} {cy:.3f}"
    ),
    "b2": (
        "M {px:.1f} {py:.1f} C {cx:.1f} {py:.1f}, "
        "{cx:.1f} {py:.1f}, {cx:.1f} {cy:.3f}"
    ),
    "p1": "M {px:.1f} {py:.1f} L {px:.1f} {cy:.1f} L {cx:.1f} {cy:.1f}",
    "p2": "M {px:.1f} {py:.1f} L {cx:.1f} {py:.1f} L {cx:.1f} {cy:.1f}",
    "pc": (
        "M {cx:.1f} {cy:.1f} L {dx:.1f} {dy:.1f} "
        "A {rr:.1f} {rr:.1f} 0 0 {sweep} {px:.1f} {py:.1f}"
    ),
}


def _get_edge_data(
    axes: Cartesian,
    mark: ToyTreeMark,
    *,
    space: Literal["pixel", "data"] = "pixel",
):
    """Return node coordinates plus circular helpers used by path builders."""
    if space == "pixel":
        nodes_x = axes.project("x", mark.ntable[:, 0])
        nodes_y = axes.project("y", mark.ntable[:, 1])
    else:
        nodes_x = mark.ntable[:, 0].astype(float, copy=False)
        nodes_y = mark.ntable[:, 1].astype(float, copy=False)

    # Circular helper arrays are only needed for circular phylogram edges.
    radii = None
    radians = None
    root_x = float(mark.ntable[-1, 0])
    root_y = float(mark.ntable[-1, 1])
    if mark.edge_type in ("p", "b") and mark.layout[0] == "c":
        xdiffs = mark.ntable[:, 0] - root_x
        ydiffs = mark.ntable[:, 1] - root_y
        radii = np.sqrt(xdiffs**2 + ydiffs**2)
        radians = np.arctan2(ydiffs, xdiffs)
        radians[radians < 0] = (2 * np.pi) + radians[radians < 0]
    return nodes_x, nodes_y, radii, radians, root_x, root_y


def get_tree_edge_svg_paths(
    axes: Cartesian, mark: ToyTreeMark
) -> Tuple[List[str], List[str]]:
    """Return SVG paths and edge keys for each drawable tree edge."""
    nodes_x, nodes_y, radii, radians, root_x, root_y = _get_edge_data(
        axes, mark, space="pixel"
    )

    # Select path format based on edge type and layout.
    if mark.edge_type in ("p", "b"):
        if mark.layout[0] == "c":
            path_format = PATH_FORMAT["pc"]
        elif mark.layout in ("u", "d"):
            path_format = PATH_FORMAT[f"{mark.edge_type}2"]
        else:
            path_format = PATH_FORMAT[f"{mark.edge_type}1"]
    else:
        path_format = PATH_FORMAT[mark.edge_type]

    paths: List[str] = []
    keys: List[str] = []

    for idx in range(mark.nnodes - 1):
        cidx, pidx = mark.etable[idx]
        child_x, child_y = nodes_x[cidx], nodes_y[cidx]
        parent_x, parent_y = nodes_x[pidx], nodes_y[pidx]

        if "A" not in path_format:
            keys.append(f"{pidx},{cidx}")
            paths.append(
                path_format.format(
                    **{"cx": child_x, "cy": child_y, "px": parent_x, "py": parent_y}
                )
            )
        else:
            xdiff = parent_x - nodes_x[-1]
            ydiff = parent_y - nodes_y[-1]
            parent_radius = np.sqrt(xdiff**2 + ydiff**2)
            mid_x = root_x + radii[pidx] * np.cos(radians[cidx])
            mid_y = root_y + radii[pidx] * np.sin(radians[cidx])
            px_mid_x = axes.project("x", mid_x)
            px_mid_y = axes.project("y", mid_y)
            # Use the same shortest-path angular delta as the polyline
            # builder so wrapped fan layouts choose the correct SVG arc
            # direction when parent / child angles straddle the seam.
            dtheta = (radians[pidx] - radians[cidx] + np.pi) % (2 * np.pi) - np.pi
            keys.append(f"{pidx},{cidx}")
            paths.append(
                path_format.format(
                    **{
                        "cx": child_x,
                        "cy": child_y,
                        "px": parent_x,
                        "py": parent_y,
                        "dx": px_mid_x,
                        "dy": px_mid_y,
                        "rr": parent_radius,
                        "sweep": int(dtheta < 0),
                    }
                )
            )
    return paths, keys


def get_tree_edge_polylines(
    axes: Cartesian,
    mark: ToyTreeMark,
    *,
    space: Literal["pixel", "data"] = "pixel",
    arc_steps: int = 24,
    bezier_steps: int = 24,
) -> Tuple[List[np.ndarray], List[np.ndarray], List[str]]:
    """Return edge polylines and keys for each drawable tree edge."""
    nodes_x, nodes_y, radii, radians, root_x_data, root_y_data = _get_edge_data(
        axes, mark, space=space
    )

    xpaths: List[np.ndarray] = []
    ypaths: List[np.ndarray] = []
    keys: List[str] = []

    for idx in range(mark.nnodes - 1):
        cidx, pidx = mark.etable[idx]
        cx, cy = nodes_x[cidx], nodes_y[cidx]
        px, py = nodes_x[pidx], nodes_y[pidx]
        keys.append(f"{pidx},{cidx}")

        if mark.edge_type == "c":
            xpaths.append(np.array([px, cx], dtype=float))
            ypaths.append(np.array([py, cy], dtype=float))
            continue

        if mark.layout[0] == "c":
            # Circular path: line from child to ring, then arc to parent.
            th0 = float(radians[cidx])
            th1 = float(radians[pidx])
            # SVG renderer uses large-arc=0, so the arc must always follow the
            # shorter angular path between child and parent.
            dtheta = (th1 - th0 + np.pi) % (2 * np.pi) - np.pi
            thetas = np.linspace(th0, th0 + dtheta, arc_steps)
            xarc_data = root_x_data + radii[pidx] * np.cos(thetas)
            yarc_data = root_y_data + radii[pidx] * np.sin(thetas)
            if space == "pixel":
                xarc = axes.project("x", xarc_data)
                yarc = axes.project("y", yarc_data)
            else:
                xarc = xarc_data
                yarc = yarc_data
            midx = xarc[0]
            midy = yarc[0]
            xpaths.append(np.concatenate(([cx, midx], xarc[1:])))
            ypaths.append(np.concatenate(([cy, midy], yarc[1:])))
            continue

        if mark.edge_type == "p":
            if mark.layout in ("u", "d"):
                xpaths.append(np.array([px, cx, cx], dtype=float))
                ypaths.append(np.array([py, py, cy], dtype=float))
            else:
                xpaths.append(np.array([px, px, cx], dtype=float))
                ypaths.append(np.array([py, cy, cy], dtype=float))
            continue

        # Bezier edge: sample a cubic with duplicated controls to match renderer.
        t = np.linspace(0.0, 1.0, bezier_steps)
        if mark.layout in ("u", "d"):
            c1x, c1y = cx, py
            c2x, c2y = cx, py
        else:
            c1x, c1y = px, cy
            c2x, c2y = px, cy
        omt = 1 - t
        x = (
            (omt**3) * px
            + 3 * (omt**2) * t * c1x
            + 3 * omt * (t**2) * c2x
            + (t**3) * cx
        )
        y = (
            (omt**3) * py
            + 3 * (omt**2) * t * c1y
            + 3 * omt * (t**2) * c2y
            + (t**3) * cy
        )
        xpaths.append(x.astype(float))
        ypaths.append(y.astype(float))
    return xpaths, ypaths, keys
