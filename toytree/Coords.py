#!/usr/bin/env python

"""
A class object for generating and storing Toytree plotting coordinates.
"""

import numpy as np
from .utils import ToytreeError


"""
TODO: 

- it may be useful to decompose update so plotting coords change but not idxs
- 
"""


class Coords:
    """
    Generates and stores plotting coordinates for nodes and edges of a tree. 
    Uses the toytree _style information (e.g., layout, use_edge_lengths).

    Attributes: 
    -----------
    edges: ndarray
        2-d array of pairs showing (parent, child) relationships.
        Rows are ordered in postorder traversal order for plotting.
    verts: ndarray
        2-d array with relative cartesian coordinate positions of nodes (n)
        Rows are ordered by the numbered 'idx' feature of nodes.
    coords: ndarray
        2-d array with cartesian coordinates for tips and node crown positions.
        Rows are ordered postorder idx.
        Used for drawing edges on phylograms, not for nodes.
    lines: ndarray
        ...
    """
    def __init__(self, ttree):

        # the toytree 
        self.ttree = ttree

        # the vertices and edge tuples for normal layouts ('n')
        self.edges = None  # np.zeros((self.nnodes - 1, 2), dtype=int)
        self.verts = None  # np.zeros((self.nnodes, 2), dtype=float)
        self.lines = None
        self.coords = None

        # the class object for transforming to radial coords ('r').
        # init'ing this is pretty lightweight, so might as well default it.
        # update: not so lightweight, makes coords 10X slower...
        # self.circ = Circle(self.ttree)

        # the class object for transforming to force-directed layout ('u') 
        # ...

        # not automatically run in init bc we want to keep toytrees light
        # self.update()



    def update(self):
        """
        Updates cartesian coordinates for drawing tree graph
        """
        # store tree dimensions on update
        self.ttree.nnodes = 0
        self.ttree.ntips = 0
        for node in self.ttree.treenode.traverse():
            self.ttree.nnodes += 1
            if node.is_leaf():
                self.ttree.ntips += 1

        # get new shape and clear for attrs
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.ttree.nnodes, 2), dtype=float)
        self.lines = np.zeros(((self.ttree.nnodes * 2) - 2, 2), dtype=float)
        self.coords = np.zeros(((self.ttree.nnodes * 2) - 1, 2), dtype=float)

        # updates idxs and fixed_idx for any tree manipulations
        self.update_idxs()
        self.update_fixed_order()      # in case ntips changed

        # get edges and verts (node locations)
        if self.ttree.style.layout in ("c", "circ", "circular", "x", "unrooted"):
            self.circ = Circle(self.ttree)
            self.assign_radial_vertices()

        else:           
            self.assign_vertices()

        # if unrooted use these vertices as start in a force directed push
        # if self.ttree.style.layout in ("x", "unrooted"):
        # self.force_directed_verts()

        # get lines and coords (node neighbor locations for 'p' edges)
        # self.new_assign_coordinates()      # get edge locations
        self.assign_coordinates()            # get edge locations        
        # self.assign_coordinates()            # get edge locations        
        self.reorient_coordinates()    # orientation can reorder dimensions


    # # NOT YET IMPLEMENTED
    # def force_directed_verts(self):
    #     # pin 25% of 
    #     c, a, m = toyplot.graph(
    #         self.coords.edges,
    #         layout=toyplot.layout.FruchtermanReingold(
    #             seed=self._seed, 
    #             area=100, 
    #             M=self.ttree.ntips*20, 
    #             temperature=10,
    #             ),
    #     )
    #     # store the coordinates after the push
    #     # self._unrooted_coords = np.array(m.vcoordinates)
    #     # get circular lines and coords
    #     self.assign_coordinates()      # get edge locations
    #     self.reorient_coordinates()    # orientation can reorder dimensions


    def update_idxs(self):
        "set root idx highest, tip idxs lowest ordered as ladderized"

        # internal nodes: root is highest idx
        idx = self.ttree.nnodes - 1

        for node in self.ttree.treenode.traverse("levelorder"):
            if not node.is_leaf():
                node.add_feature("idx", idx)
                self.ttree.idx_dict[idx] = node
                if not node.name:
                    node.name = str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.ttree.treenode.get_leaves():
            node.add_feature("idx", idx)
            self.ttree.idx_dict[idx] = node
            if not node.name:
                node.name = str(idx)
            idx -= 1



    def update_fixed_order(self):
        "after pruning fixed order needs update to match new nnodes/ntips."
        # set tips order if fixing for multi-tree plotting (default None)
        fixed_order = self.ttree._fixed_order
        self.ttree_fixed_order = None
        self.ttree_fixed_idx = list(range(self.ttree.ntips))

        # check if fixed_order changed:
        if fixed_order:
            fixed_order = [
                i for i in fixed_order if i in self.ttree.get_tip_labels()
            ]
            self.ttree._set_fixed_order(fixed_order)
        # else:
            # self.ttree._fixed_idx = list(range(self.ttree.ntips))



    def assign_radial_vertices(self):
        """
        Assign .edges and .verts for node positions in a fan tree.
        The farthest tip aligns at the circumference.
        """
        # shortname 
        uselen = bool(self.ttree.style.use_edge_lengths)
        if not uselen:
            nbits = self.ttree.treenode.get_farthest_leaf(True)[1]

        # use cache to fill edges array 
        for idx in range(self.ttree.nnodes):
            node = self.ttree.idx_dict[idx]
            if node.up:
                self.edges[idx, :] = (node.up.idx, idx)

            # leaves: x positions are evenly spaced around circumference
            if node.is_leaf() and (not node.is_root()):

                # store radians (how far around from zero to 2pi)
                node.radians = self.circ.tip_radians[idx]

                # get positions of tips using radians and radius   
                if uselen:
                    node.radius = self.circ.radius - node.height
                    node.x, node.y = self.circ.get_node_coords(node)
                else:
                    node.radius = nbits
                    node.x, node.y = self.circ.get_node_coords(node)

            # internal nodes comes after tips. Inherit position from children.
            else:

                # height is either distance or nodes from root
                if uselen:
                    node.radius = self.circ.radius - node.height
                else:
                    node.radius = sum(1 for i in node.iter_ancestors())
                    # max([i.radius for i in node.children]) - 1

                # x position is halfway between children x-pos
                node.radians = np.mean([i.radians for i in node.children])
                node.x, node.y = self.circ.get_node_coords(node)

            # store the x,y vertex positions
            self.verts[node.idx] = [node.x, node.y]

        # scale so that node idx 0 (or fixed_order x) is at (0, 0)
        # adjust = self.ttree._coords.verts[:, 1].min()
        # self.ttree._coords.verts[:, 1] -= adjust        



    def assign_vertices(self):
        """
        Sets .edges, .verts for node positions. 
        X and Y positions here refer to base assumption that tree is right
        facing, reorient_coordinates() will handle re-translating this.        
        """
        # shortname 
        uselen = bool(self.ttree.style.use_edge_lengths)

        # use cache to fill edges array 
        for idx in range(self.ttree.nnodes - 1):
            parent = self.ttree.idx_dict[idx].up
            if parent:
                self.edges[idx, :] = (parent.idx, idx)

        # store verts array with x,y positions of nodes (lengths of branches)
        # we want tips to align at the right face (larger axis number)
        fartip = self.ttree.treenode.get_farthest_leaf()[0]
        hgt = sum([
            fartip.dist, 
            sum(i.dist for i in fartip.iter_ancestors() if not i.is_root())
        ])

        # finding tip distance from root is a little slow, it would be faster
        # just progress forward from root, but this wouldn't easily allow for
        # spacing fixed order tips. So instead we start from tips. 
        for idx in range(self.ttree.nnodes):
            node = self.ttree.idx_dict[idx]

            if node.is_leaf() and (not node.is_root()):
                if uselen:
                    toroot = sum(
                        i.dist for i in node.iter_ancestors() 
                        if not i.is_root()
                    )
                    node.y = hgt - (node.dist + toroot)
                else:
                    node.y = 0.
                if self.ttree._fixed_order:
                    node.x = self.ttree._fixed_order.index(node.name)
                else:
                    node.x = node.idx

            else:
                nch = node.children
                # empty trees only
                if not nch:
                    node.x = node.y = 0

                # all other trees
                else:
                    if uselen:
                        node.y = nch[0].y + nch[0].dist
                    else:
                        node.y = max((i.y for i in nch)) + 1

                    # internal node at midpoint of children
                    node.x = sum(i.x for i in nch) / float(len(nch))

                    # staggered midpoints for overlaps
                    # node.x = np.mean([i.x for i in node.iter_leaves()])

            # store the vertex
            self.verts[idx] = [node.x, node.y]

        # scale so that node idx 0 (or fixed_order x) is at (0, 0)
        if uselen:
            adjust = self.verts[:, 1].min()
            self.verts[:, 1] -= adjust



    def assign_coordinates(self):
        """
        coords and lines allow 'p' type edges (not all straight lines)
        """
        for idx in range(self.ttree.nnodes):
            node = self.ttree.idx_dict[idx]

            # store coord of this vertex
            self.coords[idx] = (node.x, node.y)
            if not node.is_root():

                # store coord of hidden vertex
                nidx = idx + self.ttree.nnodes
                if self.ttree.style.layout == 'c':
                    self.coords[nidx] = self.circ.get_node_lines(node)
                else:
                    self.coords[nidx] = (node.x, node.up.y)

                # store line connecting node to hidden vertex
                self.lines[idx] = (idx, nidx)

                # store line connecting hidden vertex to node parent
                self.lines[nidx - 1] = (nidx, node.up.idx)



    def reorient_coordinates(self):
        """
        Returns a modified .verts array with new coordinates for nodes. 
        This does not need to modify .edges. The order of nodes, and therefore
        of verts rows is still the same because it is still based on the tree
        branching order (ladderized usually). 
        """
        # if tree is empty then bail out
        if len(self.ttree) < 2:
            return

        # TODO: orientation for non linear trees
        if self.ttree.style.layout in ('c', 'circular', 'x', 'unrooted'):
            return 

        # default: Down-facing tips align at y=0, first ladderized tip at x=0
        if self.ttree.style.layout in ('d', 'down'):
            pass

        # right-facing tips align at x=0, last ladderized tip at y=0
        elif self.ttree.style.layout in ('r', 'right'):

            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(self.verts.shape)
            tmp[:, 1] = self.verts[:, 0]
            tmp[:, 0] = self.verts[:, 1] * -1
            self.verts = tmp

            # coords...
            tmp = np.zeros(self.coords.shape)
            tmp[:, 1] = self.coords[:, 0]
            tmp[:, 0] = self.coords[:, 1] * -1
            self.coords = tmp

        elif self.ttree.style.layout in ('l', 'left'):

            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(self.verts.shape)
            tmp[:, 1] = self.verts[:, 0]
            tmp[:, 0] = self.verts[:, 1] 
            self.verts = tmp

            # coords...
            tmp = np.zeros(self.coords.shape)
            tmp[:, 1] = self.coords[:, 0]
            tmp[:, 0] = self.coords[:, 1]
            self.coords = tmp

        elif self.ttree.style.layout in ('u', 'up'):
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(self.verts.shape)
            tmp[:, 1] = self.verts[:, 1] * -1
            tmp[:, 0] = self.verts[:, 0] * -1
            self.verts = tmp

            # coords...
            tmp = np.zeros(self.coords.shape)
            tmp[:, 1] = self.coords[:, 1] * -1
            tmp[:, 0] = self.coords[:, 0] * -1
            self.coords = tmp

        else:
            raise ToytreeError("layout not recognized")



class Circle:
    """
    When init from a toytree it can return coordinates based on 
    distributing tips equally in radians from 0-2pi (TODO: allow 
    setting start/end).

    The radius for farthest tip-ends is set to the tree height, 
    and origin is at 0.0.
    """
    def __init__(self, tre):

        # set radius
        self.tre = tre
        self.radius = self.tre.treenode.height 
        # get_distance(self.tre.treenode.get_farthest_leaf()[0])

        # origin
        self.o = (0, 0)
        # self.tre.style.xbaseline, self.tre.style.ybaseline)  # -self.radius, 0)

        # tips (bottom to top) are evenly spread from 0 to -2pi (counter clock)
        self.tip_radians = np.linspace(0, -np.pi * 2, self.tre.ntips + 1)[:-1]


    def get_node_coords(self, node):
        """
        get node coord. Node has radius assigned on the fly.
        """
        x = self.o[0] + node.radius * np.cos(node.radians)
        y = self.o[1] - node.radius * np.sin(node.radians)
        return x, y


    def get_node_lines(self, node):
        x = self.o[0] + node.up.radius * np.cos(node.radians)
        y = self.o[1] - node.up.radius * np.sin(node.radians)
        return x, y      


    def get_tip_end_angles(self):
        """
        node radians for printing tip labels should be from the root (0,0)
        """
        return np.array([np.rad2deg(abs(i)) for i in self.tip_radians])


    def get_tip_end_coords(self):
        """
        node tip coords must calculate new radian angle relative to parent 
        node and then add offset amount to radius when calculating (x, y).
        """
        xs = [self.o[0] + self.radius * np.cos(i) for i in self.tip_radians]        
        ys = [self.o[1] - self.radius * np.sin(i) for i in self.tip_radians]
        return np.stack([xs, ys], axis=1)


    # def get_parent_coords(self, node):
    #     """
    #     get x,y coordinates of parent based on radians of children
    #     """
    #     # calculate x, y coords
    #     x = self.o[0] + node.radius * np.cos(midradian)
    #     y = self.o[1] + node.radius * np.sin(midradian)
    #     return x, y

