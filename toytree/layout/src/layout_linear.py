#!/usr/bin/env python

"""Get node coordinate layouts from a tree and style arguments.

This class is primarily intended for internal use.

The Layout class will parse the style args to project Nodes into
their proper coordinates for plotting. This is done very quickly
using cached heights, but if fixed-order or fixed-position args are
used then it requires a tree traversal and to make a copy of the
style dict.
"""

from typing import Optional, Sequence, TypeVar

import numpy as np

from toytree.core import TreeStyle
from toytree.layout.src.layout_base import BaseLayout
from toytree.utils import ToytreeError

ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")

# pylint: disable=too-many-branches, too-many-statements


# this enum not yet used
class InteriorAlgorithm:
    """Enumerate supported internal-node placement algorithms."""

    INTERMEDIATE = 0
    CENTERED = 1
    WEIGHTED = 2


class LinearLayout(BaseLayout):
    """Layout for linear drawing styles: ``r``, ``l``, ``u``, and ``d``.

    The interior_node_layout string is optionally entered as a
    number after the linear style, e.g., "r0", "r1", "u2", etc.
    The options implement 'intermediate', 'centered', or 'weighted',
    positioning of internal nodes relative to their descendants or
    tips.
    """

    def __init__(
        self,
        tree: ToyTree,
        style: TreeStyle,
        fixed_order: Optional[Sequence[str]] = None,
        fixed_position: Optional[Sequence[float]] = None,
        interior_algorithm: int = 0,
    ):
        self.interior_algorithm = interior_algorithm
        super().__init__(tree, style, fixed_order, fixed_position)

    def run(self) -> None:
        """Fill ``.coords`` with x/y positions for the current layout.

        mode: int
            0 = midpoint of immediate children (default)
            1 = mean of descendant tip positions
            2 = weighted midpoint of immediate children (robust)
            3 = median of descendant tip positions
            4 = trimmed mean of descendant tip positions
        """
        # generate new (x, y) linear coordinates
        if (
            bool(self.interior_algorithm)
            | (self.fixed_order is not None)
            | (self.fixed_position is not None)
        ):
            self.coords = self._get_fixed_order_and_position_coords()
        else:
            self.coords = np.array(list(self.tree._iter_node_coordinates()))

        # update coordinates for 'use_edge_lengths' and orientation.
        self._update_coordinates()

    def _update_coordinates(self) -> None:
        """Set starting values that will be updated by style args.

        For a linear layout this sets the Node and Tip coordinates. It
        starts with layout='d' and then reorients to any linear: 'rlud'
        """
        # Sets internal dists to 1 and extends leaf edges to align at 0.
        if not self.style.use_edge_lengths:
            self._assign_unit_length_edges()

        # re-orient for layout direction: right, left or down.
        if self.style.layout == "d":
            self.angles = np.repeat(-90, self.tree.ntips)
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[: self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 1] = self.style.ybaseline

        elif self.style.layout == "u":
            self.angles = np.repeat(-90, self.tree.ntips)
            self.coords[:, 1] *= -1
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[: self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 1] = self.style.ybaseline

        elif self.style.layout == "l":
            self.angles = np.zeros(self.tree.ntips)
            self.coords = self.coords[:, [1, 0]]
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[: self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 0] = self.style.xbaseline

        else:
            self.angles = np.zeros(self.tree.ntips)
            self.coords = self.coords[:, [1, 0]]
            self.coords[:, 0] *= -1
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[: self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 0] = self.style.xbaseline

    def _assign_unit_length_edges(self) -> None:
        """Set all branch distances to unit length when disabled."""
        for node in self.tree:  # .traverse("postorder"):
            if node.is_leaf():
                self.coords[node.idx, 1] = 0
            else:
                cys = [self.coords[child.idx, 1] for child in node.children]
                self.coords[node.idx, 1] = max(cys) + 1

    def _get_fixed_order_and_position_coords(self) -> np.ndarray:
        """Return coords using fixed args. Requires a tree traversal.

        The idx order of the tips is overriden to re-order them
        according an ordered list of names. This is often used to
        visualize discordance among different trees.
        """
        # get user fixed-positions or use the default range of 0-Ntips
        if self.fixed_position is None:
            positions = np.arange(self.tree.ntips, dtype=float)
        else:
            positions = np.array(self.fixed_position, dtype=float)
            assert (
                positions.size == self.tree.ntips
            ), "fixed_position arg must be same len as ntips."

        # get user fixed-order as the index of tip name strings
        if self.fixed_order is None:
            idxorder = np.arange(self.tree.ntips)
        else:
            idxorder = np.zeros(self.tree.ntips, dtype=int)
            assert (
                len(self.fixed_order) == self.tree.ntips
            ), "fixed order arg must be same len as ntips."

            # get indices at which user wants Nodes to be displayed
            tipnames = self.tree.get_tip_labels()
            tipnames_set = set(tipnames)
            fixed_lookup = {}
            for idx, name in enumerate(self.fixed_order):
                if name not in tipnames_set:
                    raise ToytreeError(f"name {name} not in tree.")
                fixed_lookup[name] = idx
            for tip_idx, name in enumerate(tipnames):
                idxorder[tip_idx] = fixed_lookup[name]

        coords = np.zeros((self.tree.nnodes, 2), dtype=float)
        if self.interior_algorithm == 1:
            # Cache descendant x-sums/counts so centered cloud-tree layouts
            # do one postorder pass instead of recomputing leaves per node.
            desc_sums = np.zeros(self.tree.nnodes, dtype=float)
            desc_counts = np.zeros(self.tree.nnodes, dtype=int)
        else:
            desc_sums = None
            desc_counts = None

        for node in self.tree:  # .traverse("idxorder"):
            coords[node.idx, 1] = node._height
            if node.is_leaf():
                coords[node.idx, 0] = positions[idxorder[node.idx]]
                if desc_sums is not None and desc_counts is not None:
                    desc_sums[node.idx] = coords[node.idx, 0]
                    desc_counts[node.idx] = 1
            else:
                # set internal node at midpoint between its children
                # centered placement
                if not self.interior_algorithm:
                    newx = (
                        sum(
                            [
                                coords[min(node.children).idx, 0],
                                coords[max(node.children).idx, 0],
                            ]
                        )
                        / 2
                    )
                # mean placement over all descendant tip positions
                elif self.interior_algorithm == 1:
                    child_idxs = [child.idx for child in node.children]
                    total_sum = float(np.sum(desc_sums[child_idxs]))
                    total_count = int(np.sum(desc_counts[child_idxs]))
                    desc_sums[node.idx] = total_sum
                    desc_counts[node.idx] = total_count
                    newx = total_sum / total_count
                # robust weighted midpoint of immediate children
                elif self.interior_algorithm == 2:
                    minc = min(node.children)
                    maxc = max(node.children)
                    mind = minc.dist
                    maxd = maxc.dist
                    minx = coords[minc.idx, 0]
                    maxx = coords[maxc.idx, 0]
                    eps = 1e-12
                    if (mind <= eps) and (maxd <= eps):
                        newx = (minx + maxx) / 2
                    elif mind <= eps:
                        newx = minx
                    elif maxd <= eps:
                        newx = maxx
                    else:
                        newx = (((1 / mind) * minx) + ((1 / maxd) * maxx)) / (
                            (1 / mind) + (1 / maxd)
                        )
                # median over descendant tip x positions
                elif self.interior_algorithm == 3:
                    tips = node.get_leaves()
                    newx = float(np.median([coords[i.idx, 0] for i in tips]))
                # trimmed mean over descendant tip x positions
                elif self.interior_algorithm == 4:
                    tips = node.get_leaves()
                    vals = np.sort(
                        np.array([coords[i.idx, 0] for i in tips], dtype=float)
                    )
                    nvals = vals.size
                    k = int(np.floor(0.1 * nvals))
                    if nvals >= 3 and (2 * k) < nvals:
                        vals = vals[k : nvals - k]
                    newx = float(np.mean(vals))
                # unknown mode -> fallback to default midpoint
                else:
                    newx = (
                        sum(
                            [
                                coords[min(node.children).idx, 0],
                                coords[max(node.children).idx, 0],
                            ]
                        )
                        / 2
                    )

                coords[node.idx, 0] = newx
        return coords


if __name__ == "__main__":
    import toytree

    toytree.set_log_level("INFO")

    a = toytree.Node("a", dist=1.0)
    b = toytree.Node("b", dist=1.5)
    ab = toytree.Node("ab", dist=0.0)
    ab._add_child(a)
    ab._add_child(b)
    ts = toytree.tree(a)
    ll = toytree.layout.LinearLayout(ts, ts.style)

    # tre = toytree.rtree.rtree(5)
    # tre.style.tip_labels_align = True
    # tre.style.xbaseline = 5
    # tre.style.ybaseline = 2.5
    # tre.style.layout = 'u'
    # lay = LinearLayout(tre, tre.style, None, None, interior_algorithm=1)
    # lay.run()
    # print(lay.coords)
    # print(lay.tcoords)
    # print(lay.interior_algorithm)
