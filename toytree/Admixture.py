#!/usr/bin/env python

"""
Draw admixture edges on a tree
"""

import itertools
import numpy as np
from .TreeStyle import COLORS1


class AdmixEdges():
    """
    TODO...

    Parameters
    ----------
    tree: toytree

    tupleargs: list
        A list of admixture tuples.

    layout: int
        0 is 'down' layout and 1 is 'right' layout.
    """
    def __init__(
        self,
        tree,
        axes,
        admixture_edges,
        layout="d",
        edge_type="c",
        ):
        # source, dest, sheight, dheight, offset, layout):

        # store args
        self.tree = tree
        self.axes = axes
        self.tupleargs = admixture_edges

        # edge-type layout
        self.edge_type = bool(edge_type == "c")

        # orientation layout
        self.layout = bool(layout == "d")

        # use a cycling color palette
        self.colors = itertools.cycle(COLORS1)
        next(self.colors)

        # parse tuples into ...
        if self.tupleargs is not None:

            # check and fill tuples
            self.check_tuple_args()

            # draw edges as a toyplot graph on the axes
            self.draw()



    def check_tuple_args(self):
        """
        Split list into bits.
        """
        # check that the argument is a list
        assert isinstance(self.tupleargs, list), (
            "admixture edges should be a list of tuples")

        # iterate over the tuples
        self.admixture_edges = []
        for tup in self.tupleargs:

            # parse required args
            source = tup[0]
            dest = tup[1]

            # parse optional args
            try:
                height = tup[2]
            except IndexError:
                height = None

            try:
                width = (tup[3] if tup[3] else 3)
            except IndexError:
                width = 3

            try:
                color = (tup[4] if tup[4] else next(self.colors))
            except IndexError:
                color = next(self.colors)

            try:
                offset = (tup[5] if tup[5] else 0.05)
            except IndexError:
                offset = 0.05

            # put it back into list as full tuples
            self.admixture_edges.append(
                (source, dest, height, width, color, offset))



    def draw(self):

        # iterate over edge tuples
        for aedge in self.admixture_edges:

            # get vcoordinates for this edge
            vcoords = get_admix_verts(
                self.tree, 
                aedge[0], 
                aedge[1],
                aedge[2],
                aedge[5],
                self.edge_type,
                self.layout,
            )

            # generate marker on axes
            self.axes.graph(
                np.array([[0, 1], [1, 2], [2, 3]]),
                vcoordinates=vcoords,
                vsize=0,
                vlshow=False,
                eopacity=1,
                ewidth=aedge[3],
                ecolor=aedge[4],
                estyle={"stroke-linecap": "round"},
                # mmarker=[None, ">", None]
            )
        return self.axes




def get_admix_verts(tree, source, dest, height, offset, etype, layout):
    """
    Get coordinates for graph edges.
    """
    # get node dictionary
    ndict = tree.get_node_dict(True, True)

    # use midpoint edge if no heights given
    if height is None:
        edgedict = get_all_admix_edges(tree, 0.5, 0.5)
        height = np.mean(edgedict[(source, dest)])

    # get the child vertex coordinates that source starts from
    cy, cx = tree._coords.verts[source]
    py, px = tree._coords.verts[ndict[source].up.idx]
    a, b = cx, cy

    # get the vertex on the edge above source at (x, height)
    if etype:
        theta = np.arctan((px - cx) / (py - cy))
        bx = (np.sin(theta) * (height + cy)) - cx
        by = np.cos(theta) * height
    else:
        bx = -cx
        by = height
    c, d = -bx, -by

    # get the vertex of the parent node of destination
    cy, cx = tree._coords.verts[dest]
    py, px = tree._coords.verts[ndict[dest].up.idx]
    if etype:
        g, h = px, py
    else:
        g, h = cx, py

    # get the vertex on the edge of destination
    if etype:
        theta = np.arctan((px - cx) / (py - cy))
        bx = (np.sin(theta) * (height + cy)) - cx
        by = np.cos(theta) * height
        e, f = -bx, -by
    else:
        e, f, = cx, -height

    # order in final array
    arr = np.array([
        [a + offset, -b],
        [c + offset, -d],
        [e + offset, -f],
        [g + offset, -h],
    ])

    # how is the tree oriented
    if not layout:
        arr = arr[:, ::-1]
        arr[:, 0] = arr[:, 0] * -1

    return arr




def get_all_admix_edges(ttree, lower=0.25, upper=0.75, exclude_sisters=False):
    """
    Find all possible admixture edges on a tree. 

    Edges are unidirectional, so the source and dest need to overlap in
    time interval. To retrict migration to occur away from nodes (these 
    can be harder to detect when validating methods) you can set upper 
    and lower limits. For example, to make all source migrations to occur
    at the midpoint of overlapping intervals in which migration can occur
    you can set upper=.5, lower=.5.   
    """
    # bounds on edge overlaps
    if lower is None:
        lower = 0.0
    if upper is None:
        upper = 1.0

    # for all nodes map the potential admixture interval
    for snode in ttree.treenode.traverse():
        if snode.is_root():
            snode.interval = (None, None)
        else:
            snode.interval = (snode.height, snode.up.height)

    # for all nodes find overlapping intervals
    intervals = {}
    for snode in ttree.treenode.traverse():
        for dnode in ttree.treenode.traverse():
            if not any([snode.is_root(), dnode.is_root(), dnode == snode]):

                # [option] skip sisters
                if (exclude_sisters) & (dnode.up == snode.up):
                    continue

                # check for overlap
                smin, smax = snode.interval
                dmin, dmax = dnode.interval

                # find if nodes have interval where admixture can occur
                low_bin = np.max([smin, dmin])
                top_bin = np.min([smax, dmax])              
                if top_bin > low_bin:

                    # restrict migration within bin to a smaller interval
                    length = top_bin - low_bin
                    low_limit = low_bin + (length * lower)
                    top_limit = low_bin + (length * upper)
                    intervals[(snode.idx, dnode.idx)] = (low_limit, top_limit)
    return intervals
