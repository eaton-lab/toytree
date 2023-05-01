#!/usr/bin/env python

"""Get node coordinate layouts from a tree and style arguments.

This class is primarily intended for internal use.

The Layout class will parse the style args to project Nodes into
their proper coordinates for plotting. This is done very quickly
using cached heights, but if fixed-order or fixed-position args are
used then it requires a tree traversal and to make a copy of the
style dict.
"""

from typing import TypeVar
import numpy as np
from loguru import logger
from toytree.utils import ToytreeError
from toytree.layout.src.layout_base import BaseLayout

ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
logger = logger.bind(name="toytree")

# pylint: disable=too-many-branches, too-many-statements


class LinearLayout(BaseLayout):
    """Layout for linear drawing styles: "r", "l", "u", "d"

    The interior_node_layout string is optionally entered as a
    number after the linear style, e.g., "r0", "r1", "u2", etc.
    The options implement 'intermediate', 'centered', or 'weighted',
    positioning of internal nodes relative to their descendants or 
    tips.
    """
    # TODO perhaps.
    # def __init__(self, interior_node_pos: int = 0):
    # self.interior_node_pos = interior_node_pos

    def run(self):
        """Fills the .coords array with x, y coordinates."""

        # get coordinates from current x,y attributes unless fixed args,
        # in which case a new traversal is required to get coords.
        if (self.fixed_order is None) and (self.fixed_position is None):
            self.coords = np.array(list(self.tree._iter_node_coordinates()))
        else:
            self.coords = self._get_fixed_order_and_position_coords()

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
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 1] = self.style.ybaseline

        elif self.style.layout == "u":
            self.coords[:, 1] *= -1
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 1] = self.style.ybaseline

        elif self.style.layout == "l":
            self.coords = self.coords[:, [1, 0]]
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 0] = self.style.xbaseline

        else:
            self.coords = self.coords[:, [1, 0]]
            self.coords[:, 0] *= -1
            self.coords[:, 0] += self.style.xbaseline
            self.coords[:, 1] += self.style.ybaseline
            self.tcoords = self.coords[:self.tree.ntips, :].copy()
            if self.style.tip_labels_align:
                self.tcoords[:, 0] = self.style.xbaseline

    def _assign_unit_length_edges(self) -> None:
        """When use_edge_length=False this sets all dists to unit 1"""
        for node in self.tree.traverse("postorder"):
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
                newx = np.mean([coords[i.idx][0] for i in node.children])
                coords.append((newx, node._height))
        return np.array(coords)


if __name__ == "__main__":

    import toytree
    tre = toytree.rtree.rtree(5)
    tre.style.tip_labels_align = True
    tre.style.xbaseline = 5
    tre.style.ybaseline = 2.5
    tre.style.layout = 'u'
    lay = LinearLayout(tre, tre.style, None, None)
    print(lay.coords)
    print(lay.tcoords)
