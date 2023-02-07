#!/usr/bin/env python

"""...

"""

from typing import Tuple
import numpy as np
from loguru import logger
from toytree.layout.src.layout_base import BaseLayout


logger = logger.bind(name="toytree")


class CircularLayout(BaseLayout):
    """Layout for circular tree projection."""

    def run(self):
        """Fills .coords array with x, y values."""
        self.coords = self.get_fan_coords()
        # self.angles = get_tip_labels_angles(self.tree, self.coords)
        # circular layout can evenly space between start and end angle
        # elif self.layout[0] == 'c':
            # tip_radians = np.linspace(0, np.pi * 2, self.tree.ntips + 1)[:-1]
            # angles = np.array([np.rad2deg(abs(i)) for i in tip_radians])

    def get_fan_coords(self):
        """Return array with x, y Node coordinates."""
        coords = np.zeros(shape=(self.tree.nnodes, 2))

        # position of the *aligned* tips on the fan circumference, the
        # first tips will be at 'start' (e.g., 0) and the final will be
        # at 'end' (e.g., 360 - unit) where unit is space between tips.
        start, end = self._get_start_and_end_angles()
        endpoint = end - start != 360
        angles = np.linspace(start, end, self.tree.ntips, endpoint=endpoint)
        self.angles = angles
        radians = np.deg2rad(angles)

        # the root Node is at position (0, 0), plus any offset style
        hub = self.style.xbaseline, self.style.ybaseline
        coords[self.tree.treenode.idx, :] = hub

        # tip node positions will be on a straight lines (spokes) from
        # the root hub to the circum_points.
        for idx in range(self.tree.ntips):
            node = self.tree[idx]
            hypo = self.tree.treenode.height - node.height
            theta = radians[idx]
            delta_y = hypo * np.sin(theta)
            delta_x = hypo * np.cos(theta)
            # logger.warning(hub)
            coords[idx, :] = (hub[0] + delta_x, hub[1] + delta_y)
            node.theta = theta

        # internal node positions are on a spoke pointing towards a
        # circumferal position intermediate between its children's.
        for idx in range(self.tree.ntips, self.tree.nnodes - 1):
            node = self.tree[idx]
            hypo = self.tree.treenode.height - node.height
            theta = np.mean([i.theta for i in node.children])
            delta_y = hypo * np.sin(theta)
            delta_x = hypo * np.cos(theta)
            coords[idx, :] = (hub[0] + delta_x, hub[1] + delta_y)
            node.theta = theta
        return coords

    def _get_start_and_end_angles(self) -> Tuple[int, int]:
        """Return a tuple with start and end angles as ints.

        Users can enter style as 'c', 'c90', or 'c0-90'. All values
        will be converted to range such that the first is in 0-359,
        and the second is in 1-719.
        - 90,180  -> 90,180
        - 300,100 -> 300,460
        - 359,340 -> 359,609
        - 359,359 -> 359,719  # equivalent to 0-360 starting at -1.
        """
        angles = str(self.style.layout[1:]).strip()

        # if None then use 0-360, if 1 then 0-int, else int-int.
        if not angles:
            start, end = 0, 360
        elif "-" not in angles:
            start, end = 0, int(angles)
        else:
            start, end = (int(i) for i in angles.split("-"))

        # ...
        msg = "circular style malformed. Should be, e.g., 'c', 'c90', 'c0-180'"
        while start < 0:
            start += 360
        while end < start:
            end += 360
        assert end > start, msg
        if end - start > 360:
            end = start + 359
        logger.debug(f"{start}-{end}")
        return start, end

    # def get_radial_coords(self, use_edge_lengths=True):
    #     """
    #     Assign .edges and .verts for node positions in a fan tree.
    #     The farthest tip aligns at the circumference.
    #     """
    #     circ = Circle(self.ttree)
    #     verts = np.zeros((self.ttree.nnodes, 2), dtype=float)

    #     # shortname
    #     if not use_edge_lengths:
    #         nbits = self.ttree.treenode.get_farthest_leaf(True)[1]

    #     # use cache to fill edges array
    #     for idx in range(self.ttree.nnodes):
    #         node = self.ttree[idx]

    #         # leaves: x positions are evenly spaced around circumference
    #         if node.is_leaf() and (not node.is_root()):

    #             # store radians (how far around from zero to 2pi)
    #             node.radians = circ.tip_radians[idx]

    #             # get positions of tips using radians and radius
    #             if use_edge_lengths:
    #                 node.radius = circ.radius - node.height
    #                 node.x, node.y = circ.get_node_coords(node)
    #             else:
    #                 node.radius = nbits
    #                 node.x, node.y = circ.get_node_coords(node)

    #         # internal nodes comes after tips. Inherit position from children.
    #         else:

    #             # height is either distance or nodes from root
    #             if use_edge_lengths:
    #                 node.radius = circ.radius - node.height
    #             else:
    #                 node.radius = sum(1 for i in node.iter_ancestors())
    #                 # max([i.radius for i in node.children]) - 1

    #             # x position is halfway between children x-pos
    #             node.radians = np.mean([i.radians for i in node.children])
    #             node.x, node.y = circ.get_node_coords(node)

    #         # store the x,y vertex positions
    #         verts[node.idx] = [node.x, node.y]
    #     return verts

if __name__ == "__main__":

    import toyplot
    import toytree
    from toytree.drawing.src.draw_toytree import get_tree_style, get_layout

    tre = toytree.rtree.rtree(10)
    sty = tre.style
    lay = CircularLayout(tre, sty)

    canvases = []
    for lay in ["c0-360", "c90-180", "c0-90", "c0-180", "c180-0"]:
        sty = get_tree_style(
            tree=tre,
            layout=lay,
            # edge_type='p',
            fixed_order=tre.get_tip_labels()[::-1],
            fixed_position=None,
            xbaseline=10,
        )
        LAY = get_layout(tre, sty)
        canvas = toyplot.Canvas(400, 300)
        axes = canvas.cartesian()
        axes.graph(
            tre.get_edges().values,
            vcoordinates=LAY.coords,
            # vsize=16,
            estyle={"stroke-width": 2},
        )
        canvases.append(canvas)
    toytree.utils.show(canvases)
