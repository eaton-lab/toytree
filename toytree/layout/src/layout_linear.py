#!/usr/bin/env python

"""Get node coordinate layouts from a tree and style arguments.

This class is primarily intended for internal use.

The Layout class will parse the style args to project Nodes into
their proper coordinates for plotting. This is done very quickly
using cached heights, but if fixed-order or fixed-position args are
used then it requires a tree traversal and to make a copy of the
style dict.
"""

from typing import TypeVar, Optional, Sequence
# from enum import Enum
import numpy as np
from loguru import logger
from toytree.utils import ToytreeError
from toytree.style import TreeStyle
from toytree.layout.src.layout_base import BaseLayout

ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
logger = logger.bind(name="toytree")

# pylint: disable=too-many-branches, too-many-statements


# this enum not yet used
class InteriorAlgorithm:
    INTERMEDIATE = 0
    CENTERED = 1
    WEIGHTED = 2


class LinearLayout(BaseLayout):
    """Layout for linear drawing styles: "r", "l", "u", "d"

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
        interior_algorithm: int = 0
    ):
        self.interior_algorithm = interior_algorithm
        super().__init__(tree, style, fixed_order, fixed_position)

    def run(self) -> None:
        """Fills the .coords array with x, y coordinates.

        mode: int
            0 = intermediate (mean of children; default)
            1 = centered (mean of descendant tips; used in cloud trees)
            2 = weighted (TODO: not implemented)
        """
        # generate new (x, y) linear coordinates
        if bool(self.interior_algorithm) | (self.fixed_order is not None) | (self.fixed_position is not None):
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
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 1] = self.style.ybaseline

        elif self.style.layout == "u":
            self.angles = np.repeat(-90, self.tree.ntips)
            self.coords[:, 1] *= -1
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 1] = self.style.ybaseline

        elif self.style.layout == "l":
            self.angles = np.zeros(self.tree.ntips)
            self.coords = self.coords[:, [1, 0]]
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 0] = self.style.xbaseline

        else:
            self.angles = np.zeros(self.tree.ntips)
            self.coords = self.coords[:, [1, 0]]
            self.coords[:, 0] *= -1
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 0] = self.style.xbaseline

    def _assign_unit_length_edges(self) -> None:
        """When use_edge_length=False this sets all dists to unit 1"""
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
            positions = np.arange(self.tree.ntips)
        else:
            positions = np.array(self.fixed_position)
            assert positions.size == self.tree.ntips, (
                "fixed_position arg must be same len as ntips.")

        # get user fixed-order as the index of tip name strings
        if self.fixed_order is None:
            idxorder = np.arange(self.tree.ntips)
        else:
            idxorder = np.zeros(self.tree.ntips, dtype=int)
            assert len(self.fixed_order) == self.tree.ntips, (
                "fixed order arg must be same len as ntips.")

            # get indices at which user wants Nodes to be displayed
            tipnames = self.tree.get_tip_labels()
            for idx, name in enumerate(self.fixed_order):
                if name not in tipnames:
                    raise ToytreeError(f"name {name} not in tree.")
                idxorder[tipnames.index(name)] = idx

        # return coordinates using the new fixed_order
        coords = []
        for node in self.tree:  # .traverse("idxorder"):
            if node.is_leaf():
                newx = positions[idxorder[node.idx]]
                coords.append((newx, node._height))
            else:
                # set internal node at midpoint between its children
                # centered placement
                if not self.interior_algorithm:
                    newx = sum([
                        coords[min(node.children).idx][0],
                        coords[max(node.children).idx][0],
                    ]) / 2
                    # newx = np.mean([coords[i.idx][0] for i in node.children])
                # intermediate placement
                elif self.interior_algorithm == 1:
                    tips = node.get_leaves()
                    newx = sum([
                        coords[min(tips).idx][0],
                        coords[max(tips).idx][0],
                    ]) / 2
                # weighted
                else:
                    minc = min(node.children)
                    maxc = max(node.children)
                    mind = minc.dist
                    maxd = maxc.dist
                    minx = coords[minc.idx][0]
                    maxx = coords[maxc.idx][0]
                    newx = (((1 / mind) * minx) + ((1 / maxd) * maxx)) / ((1 / mind) + (1 / maxd))

                coords.append((newx, node._height))
        return np.array(coords)


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
