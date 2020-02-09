#!/usr/bin/env python

"""
A class object for generating and storing Toytree plotting coordinates.
"""

import numpy as np
# from .utils import ToyTreeError


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
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.ttree.nnodes, 2), dtype=float)
        self.lines = []
        self.coords = []

        # the class object for transforming to radial coords ('r').
        # init'ing this is pretty lightweight, so might as well default it.
        self.circ = Circle(self.ttree)

        # the class object for transforming to force-directed layout ('u') 
        # ...

        # not automatically run in init bc we want to keep toytrees light
        # self.update()


    # it may be useful to separate these so we can sometimes keep idxs static
    # while only changing the plotting coordinates...
    def update(self):
        "Updates cartesian coordinates for drawing tree graph"              
        # get new shape and clear for attrs
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.ttree.nnodes, 2), dtype=float)
        self.lines = []
        self.coords = []
        self.circ = Circle(self.ttree)

        # updates idxs and fixed_idx for any tree manipulations
        self.update_idxs()             # get dimensions of tree
        self.update_fixed_order()      # in case ntips changed

        # get edges and verts (node locations)
        if self.ttree.style.layout in ("c", "circ", "circular", "x", "unrooted"):
            self.assign_radial_vertices()

        else:           
            self.assign_vertices()

        # if unrooted use these vertices as start in a force directed push
        # if self.ttree.style.layout in ("x", "unrooted"):
        # self.force_directed_verts()

        # get lines and coords (node neighbor locations for 'p' edges)
        # self.new_assign_coordinates()      # get edge locations
        self.assign_coordinates()      # get edge locations        
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
                if not node.name:
                    node.name = str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.ttree.treenode.get_leaves():
            node.add_feature("idx", idx)
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
                i for i in fixed_order if i in self.ttree.get_tip_labels()]
            self.ttree._set_fixed_order(fixed_order)
        else:
            self.ttree._fixed_idx = list(range(self.ttree.ntips))


    def assign_radial_vertices(self):
        """
        Assign .edges and .verts for node positions in a fan tree.
        The farthest tip aligns at the circumference.
        """
        # shortname 
        uselen = bool(self.ttree.style.use_edge_lengths)

        # store edge array for connecting child nodes to parent nodes
        nidx = 0
        for node in self.ttree.treenode.traverse("postorder"):            
            if not node.is_root():
                self.edges[nidx, :] = [node.up.idx, node.idx]
                nidx += 1

        # used for fixed-order setting
        # tidx = len(self.ttree) - 1

        # store verts 
        for node in self.ttree.treenode.traverse("postorder"):

            # leaves: x positions are evenly spaced around circumference
            if node.is_leaf() and (not node.is_root()):

                # get positions of tips using radians and radius
                node.radians = self.circ.tip_radians[node.idx]
                if uselen:
                    node.radius = self.circ.radius - node.height
                    node.x, node.y = self.circ.get_node_coords(node)
                else:
                    node.radius = self.circ.radius
                    node.x, node.y = self.circ.get_node_coords(node)

                # TODO: allow fixed order in fan
                # if self.ttree._fixed_order:
                    # node.x = self.ttree._fixed_order.index(node.name)
                # else:
                    # node.x = tidx
                    # tidx -= 1
                # node.x = circ.circ[node.x][0]
                self.verts[node.idx] = [node.x, node.y]

            # internal nodes comes after tips. Inherit position from children.
            else:

                # height is either distance or nodes from root
                if uselen:
                    node.radius = self.circ.radius - node.height
                else:
                    node.radius = max([i.radius for i in node.children]) - 1

                # x position is halfway between children x-pos
                node.radians = np.mean([i.radians for i in node.children])
                node.x, node.y = self.circ.get_node_coords(node)
                # if node.children:
                    # node.x = circ.get_circumference_midpoint(*node.children)
                # else:
                    # node.x = circ.circ[tidx]

                # store the x,y vertex positions
                self.verts[node.idx] = [node.x, node.y]


    def assign_vertices(self):
        """
        Sets .edges, .verts for node positions. 
        X and Y positions here refer to base assumption that tree is right
        facing, reorient_coordinates() will handle re-translating this.        
        """
        # shortname 
        uselen = bool(self.ttree.style.use_edge_lengths)

        # postorder: children then parents (nidxs from 0 up)
        # store edge array for connecting child nodes to parent nodes
        nidx = 0
        for node in self.ttree.treenode.traverse("postorder"):            
            if not node.is_root():
                self.edges[nidx, :] = [node.up.idx, node.idx]
                nidx += 1

        # store verts array with x,y positions of nodes (lengths of branches)
        # we want tips to align at the right face (larger axis number)
        _root = self.ttree.treenode.get_tree_root()
        _treeheight = _root.get_distance(_root.get_farthest_leaf()[0])

        # set node x, y
        tidx = len(self.ttree) - 1
        for node in self.ttree.treenode.traverse("postorder"):

            # Just leaves: x positions are evenly spread and ordered on axis
            if node.is_leaf() and (not node.is_root()):

                # set y-positions (heights). Distance from root or zero
                node.y = _treeheight - _root.get_distance(node)
                if not uselen:
                    node.y = 0.0

                # set x-positions (order of samples)
                if self.ttree._fixed_order:
                    node.x = self.ttree._fixed_order.index(node.name)# - tidx
                else:
                    node.x = tidx
                    tidx -= 1

                # store the x,y vertex positions
                self.verts[node.idx] = [node.x, node.y]

            # All internal node positions are not evenly spread or ordered
            else:
                # height is either distance or nnodes from root
                node.y = _treeheight - _root.get_distance(node)
                if not uselen:
                    node.y = max([i.y for i in node.children]) + 1

                # x position is halfway between childrens x-positions
                if node.children:
                    nch = node.children
                    node.x = sum(i.x for i in nch) / float(len(nch))
                else:
                    node.x = tidx

                # store the x,y vertex positions                    
                self.verts[node.idx] = [node.x, node.y]


    # IN DEVELOPMENT: 
    # this will recude lines and allow curved eges on circular trees.
    #
    def new_assign_coordinates(self):
        """
        coords span from left most to right most child.
        """
        if len(self.ttree) < 2:
            return 

        # a list for storing edge tuples
        edges = []

        # a dict of all existing nodes indexed by idx, we will add to this.
        coords = {i: tuple(j) for (i, j) in enumerate(self.verts)}

        # idx of the next node that will be created
        nidx = self.ttree.treenode.idx + 1

        # add edges connecting tips up to their bracket edge
        for node in self.ttree.treenode.traverse():
            if not node.is_root():

                # connect node: ##  x-v-n  ################
                # y to x            |   |
                #                   y   z
                #                 
                # get coordinates for the new node nidx          
                if self.ttree.style.layout == 'c':
                    x, y = self.circ.get_node_lines(node)
                else:
                    x, y = (node.x, node.up.y)

                # store coordinates of new node nidx
                coords[nidx] = x, y

                # add connection of new node to its child
                edges.append((nidx, node.idx))

                # store node is the child of nidx
                node.nup = nidx

                # advance node counter
                nidx += 1
            else:
                edges.append((node.idx, node.idx))

        # add side edges connecting bracket arms
        for node in self.ttree.treenode.traverse("levelorder"):
            if len(node.children) > 1:
                # connect node: ##  x-v-n  ################
                # x to n            |   |
                #                   y   z
                #                 
                # get coordinates for the new node nidx
                edges.append((node.children[0].nup, node.children[-1].nup))

        # store coords and lines back into ndarrays
        self.coords = np.array([coords[i] for i in range(len(coords))])
        self.lines = np.array(edges)


    def assign_coordinates(self):
        """
        coords and lines allow 'p' type edges (not all straight lines)
        """
        if len(self.ttree) < 2:
            return 

        edges = []
        coords = {i: tuple(j) for (i, j) in enumerate(self.verts)}
        nidx = self.ttree.treenode.idx + 1

        # add up nodes and edges
        for node in self.ttree.treenode.traverse():
            if not node.is_root():
                if self.ttree.style.layout == 'c':
                    coords[nidx] = self.circ.get_node_lines(node)
                else:
                    coords[nidx] = (node.x, node.up.y)
                edges.append((nidx, node.idx))
                node.nup = nidx
                nidx += 1

        # add side edges
        for node in self.ttree.treenode.traverse():
            if not node.is_leaf():
                for child in node.children:
                    edges.append((node.idx, child.nup))

        # store the vertex coordinates as an array
        self.coords = np.array([coords[i] for i in range(len(coords))])

        # store the edges as an array
        self.lines = np.array(edges)


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
            raise ToyTreeError("layout not recognized")



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

