#!/usr/bin/env python

"""Project rooted or unrooted trees into unrooted Cartesian coordinates.

Unrooted drawings are initialized with the equal-angle algorithm and then
optionally refined with the equal-daylight algorithm to distribute clades
more evenly around internal vertices. Tip label angles are derived from the
final projected coordinates rather than from branch metadata, so rooted and
unrooted input trees both use the same geometric label logic.
"""

from typing import List, Tuple, TypeVar

import numpy as np

from toytree.layout.src.layout_base import BaseLayout
from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")


def _get_tip_label_angles(tree: ToyTree, coords: np.ndarray) -> np.ndarray:
    """Return tip label angles from finalized unrooted node coordinates.

    Using the grandparent direction when available spreads neighboring tip
    labels more evenly than using only the terminal branch direction.
    """
    angles = np.zeros(tree.ntips, dtype=float)
    for node in tree.traverse():
        if not node.is_leaf():
            continue

        cx, cy = coords[node.idx]
        if node.up.up:
            px, py = coords[node.up.up.idx]
        else:
            px, py = coords[node.up.idx]

        dx = cx - px
        dy = cy - py
        angles[node.idx] = np.rad2deg(np.arctan2(dy, dx))
    return angles


class UnrootedLayout(BaseLayout):
    """Project a tree into unrooted coordinates and tip label angles."""

    def run(self):
        """Fill node coordinates and tip-label angles for unrooted drawing."""
        coords = equal_daylight_algorithm(
            tree=self.tree,
            max_iter=50,
            use_edge_lengths=self.style.use_edge_lengths,
        )
        coords = coords - coords[self.tree.treenode.idx]
        offset = np.array(
            [self.style.xbaseline, self.style.ybaseline],
            dtype=float,
        )
        coords = coords + offset

        self.coords = coords
        self.tcoords = coords[: self.tree.ntips, :].copy()
        self.angles = _get_tip_label_angles(self.tree, coords)
        self.style_overwrite()

    def style_overwrite(self):
        """Apply unrooted-layout style constraints and defaults."""
        self.style.tip_labels_align = False
        self.style.edge_type = "c"


#####################################################
# UNROOTED LAYOUT UTILITIES
#####################################################


def rotate_arr(
    points: np.ndarray,
    origin: Tuple[float, float] = (0, 0),
    degrees: float = 0,
) -> np.ndarray:
    """Return coordinates rotated around an origin by degrees."""
    angle = np.deg2rad(degrees)
    rotation_matrix = np.array(
        [
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)],
        ],
        dtype=float,
    )
    points_arr = np.asarray(points, dtype=float)
    origin_arr = np.asarray(origin, dtype=float)
    centered = points_arr - origin_arr
    return (centered @ rotation_matrix.T) + origin_arr


def _validate_equal_daylight_args(max_iter: int, min_delta: float) -> Tuple[int, float]:
    """Return validated equal-daylight stopping parameters."""
    if isinstance(max_iter, bool) or not isinstance(max_iter, (int, np.integer)):
        raise ToytreeError("max_iter must be an integer >= 0.")
    if max_iter < 0:
        raise ToytreeError("max_iter must be an integer >= 0.")

    if isinstance(min_delta, bool) or not isinstance(
        min_delta,
        (int, float, np.integer, np.floating),
    ):
        raise ToytreeError("min_delta must be a finite number >= 0.")
    min_delta = float(min_delta)
    if (not np.isfinite(min_delta)) or (min_delta < 0):
        raise ToytreeError("min_delta must be a finite number >= 0.")
    return int(max_iter), min_delta


def _precompute_daylight_subsets(
    tree: ToyTree,
) -> Tuple[List[object], List[Tuple[np.ndarray, ...]]]:
    """Return focal nodes and rotating node-index subsets for daylight updates.

    The equal-daylight refinement revisits the same topology-derived clade
    memberships on every iteration. Precomputing them once avoids repeated
    descendant traversals and `Node`-set hashing inside the hot loop.
    """
    all_indices = np.arange(tree.nnodes, dtype=int)
    descendant_indices: List[np.ndarray] = [
        np.empty(0, dtype=int) for _ in range(tree.nnodes)
    ]
    focal_nodes = []
    focal_subsets = []

    for node in tree.traverse("postorder"):
        descendant_indices[node.idx] = np.fromiter(
            (desc.idx for desc in node.iter_descendants()),
            dtype=int,
        )

    for fnode in tree.traverse("levelorder"):
        if fnode.is_leaf():
            continue

        subsets = [descendant_indices[child.idx] for child in fnode.children]
        blocked = np.concatenate(([fnode.idx], *subsets))
        other_mask = np.ones(tree.nnodes, dtype=bool)
        other_mask[blocked] = False
        other = all_indices[other_mask]
        if other.size:
            subsets.append(other)

        focal_nodes.append(fnode)
        focal_subsets.append(tuple(subsets))
    return focal_nodes, focal_subsets


def equal_daylight_algorithm(
    tree: ToyTree,
    max_iter: int = 1,
    min_delta: float = 1,
    use_edge_lengths: bool = True,
) -> np.ndarray:
    """Return unrooted coordinates refined under the equal-daylight algorithm.

    The layout starts from equal-angle coordinates and iteratively rotates
    clades around internal vertices to reduce large daylight gaps. This is
    the layout used by :class:`UnrootedLayout`.

    Parameters
    ----------
    tree : ToyTree
        Tree whose nodes will be projected into unrooted coordinates.
    max_iter : int, default=1
        Maximum number of refinement passes after the equal-angle start.
    min_delta : float, default=1
        Stop once the mean angular change per pass drops below this value.
    use_edge_lengths : bool, default=True
        If False, treat every branch as unit length during projection.

    Returns
    -------
    np.ndarray
        Array of shape ``(tree.nnodes, 2)`` with x/y node coordinates.

    Notes
    -----
    Trees with fewer than five tips return the equal-angle layout directly.
    Refinement is also rejected when it generates obviously worse or
    overlapping angular configurations.

    References
    ----------
    - Felsenstein 2004, page 582 (and see Figure 34.6).
    """
    max_iter, min_delta = _validate_equal_daylight_args(
        max_iter=max_iter,
        min_delta=min_delta,
    )

    # Use the equal-angle geometry as the starting configuration and then
    # iteratively rotate connected clades around focal internal vertices.
    coords = equal_angle_algorithm(tree, use_edge_lengths=use_edge_lengths)

    # return equal-angles for <= 4-taxon trees
    if tree.ntips < 5 or max_iter == 0:
        return coords

    focal_nodes, focal_subsets = _precompute_daylight_subsets(tree)

    # for Y internal nodes we expect an average rotation of X, thus
    # any solution with more delta than 3 * Y * X is almost surely
    # worse than the equal-angles layout and should be discarded.
    n_internal = tree.nnodes - tree.ntips - 1
    min_angles = n_internal * 3
    avg_change = 30
    max_change = (min_angles * avg_change) / 3  # .5

    # Perform multiple passes through the tree stopping when either
    # the improvement falls below a threshold, max_iters is reached,
    # or the iteration results in more changes than a previous one.
    sum_deltas = []  # list of sum change in angles each iter
    full_circle = None  # record whether full circle encountered.
    niter = 0
    while True:
        # create a copy of coords to modify
        icoords = coords.copy()

        # record the sum of changed angles this iter
        sum_delta = 0

        # visit each internal node in levelorder and rotate other nodes
        # relative to the position of this one. Skip root and leaves,
        # they only rotate relative to internals.
        for fnode, subsets in zip(focal_nodes, focal_subsets):
            if len(subsets) < 2:
                continue

            # get current focal node coordinates
            pos = icoords[fnode.idx]

            # get shaded sectors by subtrees.
            shade = np.zeros((len(subsets), 2), dtype=float)
            last_angle = 0.0
            for sidx, subset in enumerate(subsets):
                rel = icoords[subset] - pos
                rads = np.arctan2(rel[:, 1], rel[:, 0]) + (np.pi / 2)
                rads[rads < 0] += 2 * np.pi
                rads[rads < last_angle] += 2 * np.pi
                shade[sidx, 0] = float(rads.min())
                shade[sidx, 1] = float(rads.max())
                last_angle = shade[sidx, 1]

            # Sort by unwrapped sector starts so the daylight gaps reflect
            # the actual order of clades around the focal vertex.
            order = np.argsort(shade[:, 0])
            gaps = [(order[i], order[i + 1]) for i in range(len(order) - 1)]
            gaps += [(order[-1], order[0])]

            # get daylight as sectors between ordered shaded regions
            # e.g., (0, 1), (1, 2), ...
            light = np.zeros(len(gaps), dtype=float)
            for gidx, gap in enumerate(gaps):
                gap_end, next_start = shade[gap[0], 1], shade[gap[1], 0]
                if gap_end > next_start:
                    next_start += 2 * np.pi
                light[gidx] = np.rad2deg(next_start - gap_end)

            # if subtree angles sum to more than a full circle it is
            # impossible to find a positive angle between subtrees and
            # they will overlap. So we stop the iteration and return
            # last set of coordinates. This will not occur when starting
            # from the equal-angles layout, but can on any subsequent iters.
            if (shade[order[-1], 1] - (2 * np.pi)) > shade[order[0], 0]:
                full_circle = fnode.idx
                break

            # change angles
            optimal = float(light.mean())
            rotated = np.zeros(len(subsets), dtype=float)
            for gidx, gap in enumerate(gaps[:-1]):
                # how far the gap[1] needs to be rotated
                gap_to_next = light[gidx] + rotated[gidx]
                angle_to_rotate = gap_to_next - optimal
                rotated[gidx + 1] = angle_to_rotate

                nodes_to_rotate = subsets[gap[1]]
                icoords[nodes_to_rotate, :] = rotate_arr(
                    points=icoords[nodes_to_rotate],
                    origin=pos,
                    degrees=-angle_to_rotate,
                )

            # record how much change has happened
            avg_delta = float(np.mean(np.abs(rotated[1:])))
            sum_delta += avg_delta

        # causes to not accept the proposed coordinate change.
        if full_circle is not None:
            break
        if sum_delta > max_change:
            break
        if sum_deltas:
            prev_sum_delta = sum_deltas[-1]
            if sum_delta > (prev_sum_delta + prev_sum_delta * 0.1):
                break

        # accept the coordinates change
        niter += 1
        sum_deltas.append(sum_delta)
        coords = icoords

        if niter == max_iter:
            break
        if sum_delta < min_delta:
            break

    return coords


def equal_angle_algorithm(
    tree: ToyTree,
    use_edge_lengths: bool = True,
) -> np.ndarray:
    """Return unrooted coordinates under the equal-angle algorithm.

    The root receives the full 360-degree sector and each descendant clade
    receives a sector proportional to its number of leaf descendants.

    Parameters
    ----------
    tree : ToyTree
        Tree whose nodes will be projected into unrooted coordinates.
    use_edge_lengths : bool, default=True
        If False, treat every branch as unit length during projection.

    Returns
    -------
    np.ndarray
        Array of shape ``(tree.nnodes, 2)`` with x/y node coordinates.

    References
    ----------
    - Felsenstein (2004), page 578.
    """
    coords = np.zeros(shape=(tree.nnodes, 2), dtype=float)

    # if tree is rooted then use root Node as the central vertex.
    ntips = tree.ntips
    radians_per_tip = 2 * np.pi / ntips

    # store {Node: value}
    radian_sums = {}
    sectors = {}

    # record the sum of sector area for each Node as its N
    # descendants * the radians per tip.
    for node in tree.traverse("postorder"):
        if node.is_leaf():
            # node.radian_sum = radians_per_tip
            radian_sums[node] = radians_per_tip
        else:
            # node.radian_sum = sum(i.radian_sum for i in node.children)
            radian_sums[node] = sum(radian_sums[i] for i in node.children)

    # assign radian sectors in levelorder.
    for node in tree.traverse("levelorder"):
        if node.is_root():
            coords[node.idx] = (0, 0)
            sectors[node] = [0, 2 * np.pi]
        else:
            cohort = node.up.children
            idx = cohort.index(node)
            if not idx:
                start = sectors[node.up][0]
            else:
                start = sectors[cohort[idx - 1]][1]
            sectors[node] = [start, start + radian_sums[node]]
            mid = sum(sectors[node]) / 2.0

            # geometry relative to parent position and angle
            parent_pos = coords[node.up.idx]
            hypo = node.dist if use_edge_lengths else 1.0
            newx = parent_pos[0] + (hypo * np.sin(mid))
            newy = parent_pos[1] - (hypo * np.cos(mid))
            coords[node.idx] = (newx, newy)
    return coords
