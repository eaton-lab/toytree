#!/usr/bin/env python

"""Compute tip angles given the current layout.

The layouts differ in how tip angles should be computed. The linear
layouts are simple, but users can still optionally modify angles. The
circular layout is also pretty straightforward, but needs to be flipped
when the names cross the 0-axis. The unrooted layout tip names are
unique for each edge, requiring computation.
"""

from typing import TypeVar
import numpy as np
from loguru import logger


logger = logger.bind(name="toytree")
ToyTree = TypeVar("ToyTree")


def get_tip_labels_angles(tree: ToyTree, coords: np.ndarray) -> np.ndarray:
    """Get tip label angles given the current layout.

    For unrooted and circular layouts the best angle to project
    tip labels depends on the coordinate layout, and so it is
    easiest to re-compute for nodes after projecting.
    """
    angles = np.zeros(tree.ntips, dtype=float)
    for node in tree.traverse():
        if node.is_leaf():
            cx, cy = coords[node.idx]

            # from grandparent, the tip label spread generally improves.
            if node.up.up:
                px, py = coords[node.up.up.idx]
            else:
                px, py = coords[node.up.idx]

            # alternative unrooted project tips from origin, sometimes
            # this is better, would be nice to make this an option.
            # px, py = coords[-1]

            # get angle based on difference between nodes
            dx = cx - px
            dy = cy - py

            # sin(x) = opp / hyp; tan_(x) = opp/adj
            if dx == 0 :
                theta = np.pi / 2
            else :
                theta = np.arctan(dy / dx)
            
            if dx < 0:
                theta += np.pi
            angles[node.idx] = np.rad2deg(theta)
            # logger.info(f"arctan2 {node.name}, {np.arctan2(dy, dx)}")
            # logger.info(
            #     f"{node.name}, {dx:.2f}, {dy:.2f}, {theta:.2f}, {angles[node.idx]:.2f}")
    return angles


if __name__ == "__main__":
    pass
