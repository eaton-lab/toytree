#!/usr/bin/env python

"""
A class object for generating and storing Toytree plotting coordinates.
"""

import numpy as np


class Coords:
    """
    Generates and stores plotting coordinates for nodes and edges of a tree. 
    Uses the toytree _style information (e.g., orient, use_edge_lengths).

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
    """
    def __init__(self, ttree):
        self.ttree = ttree
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.ttree.nnodes, 2), dtype=float)
        self.lines = []
        self.coords = []
        # not automatically run in init bc we want to keep toytrees light
        # self.update()

    # it may be useful to separate these so we can sometimes keep idxs static
    # while only changing the plotting coordinates...
    def update(self, fan=False):
        "Updates cartesian coordinates for drawing tree graph"              
        # get new shape and clear for attrs
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.ttree.nnodes, 2), dtype=float)
        self.lines = []
        self.coords = []

        # fill with updates
        self.update_idxs()             # get dimensions of tree
        self.update_fixed_order()      # in case ntips changed
        if not fan:
            self.assign_vertices()         # get node locations
            self.assign_coordinates()      # get edge locations
            self.reorient_coordinates()    # orientation can reorder dimensions
        else:           
            self.assign_fan_vertices()     # get node locations
            self.assign_coordinates()      # get edge locations
            self.reorient_coordinates()    # orientation can reorder dimensions


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


    def assign_fan_vertices(self):
        """
        Assign .edges and .verts for node positions in a fan tree.
        The farthest tip aligns at the circumference.
        """
        # cirlce object for pulling coordinates
        self.circ = Circle(self.ttree)

        # shortname 
        uselen = bool(self.ttree.style.use_edge_lengths)

        # store edge array for connecting child nodes to parent nodes
        nidx = 0
        for node in self.ttree.treenode.traverse("postorder"):            
            if not node.is_root():
                self.edges[nidx, :] = [node.up.idx, node.idx]
                nidx += 1

        # height is distance towards the radius from the root.
        _root = self.ttree.treenode.get_tree_root()
        _treeheight = _root.get_distance(_root.get_farthest_leaf()[0])

        # store verts 
        tidx = len(self.ttree) - 1
        for node in self.ttree.treenode.traverse("postorder"):

            # leaves: x positions are evenly spaced around circumference
            if node.is_leaf() and (not node.is_root()):
                
                # get positions of tips using radians and radius
                node.radians = self.circ.tip_radians[node.idx]
                if uselen:
                    node.radius = _root.get_distance(node)
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
                    node.radius = _root.get_distance(node)
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
                coords[nidx] = (node.x, node.up.y)
                edges.append((nidx, node.idx))
                node.nup = nidx
                nidx += 1

        # add side edges
        for node in self.ttree.treenode.traverse():
            if not node.is_leaf():
                for child in node.children:
                    edges.append((node.idx, child.nup))

        # store 
        self.coords = np.array([coords[i] for i in range(len(coords))])
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

        # down is the default orientation
        # down-facing tips align at y=0, first ladderized tip at x=0
        if self.ttree.style.orient == 'down':
            pass

        # right-facing tips align at x=0, last ladderized tip at y=0
        elif self.ttree.style.orient == 'right':

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

        elif self.ttree.style.orient == 'left':
            raise NotImplementedError("todo: left facing")

        else:
            raise NotImplementedError("TODO: orient directions up, left...")



class Circle:
    def __init__(self, tre):
        
        # 
        self.tre = tre
        self.radius = self.tre.treenode.get_distance(self.tre.treenode.get_farthest_leaf()[0])
        self.depth = self.tre.treenode.get_farthest_leaf(topology_only=True)[1]
        self.step = self.radius / self.depth
        self.v = []
        self.o = (0, 0)
                
        # 
        self.tip_radians = np.linspace(0, np.pi * 2, self.tre.ntips + 1)[:-1]
        # self.tip_coords = self.get_tip_end_coords()
        
        # to fill
        self.edges = np.zeros((self.tre.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.tre.nnodes, 2), dtype=float)
        self.lines = []
        self.coords = []
        

    def get_parent_coords(self, node):
        """
        get x,y coordinates of parent based on radians of children
        """
        # calculate x, y coords
        x = self.o[0] + node.radius * np.cos(midradian)
        y = self.o[1] + node.radius * np.sin(midradian)
        return x, y


    def get_node_coords(self, node):
        x = self.o[0] + node.radius * np.cos(node.radians)
        y = self.o[1] + node.radius * np.sin(node.radians)
        return x, y


    def get_tip_end_angles(self):
        """
        node radians for printing tip labels should be from the root (0,0)
        """
        return np.array([np.rad2deg(i) -90 for i in self.tip_radians])


    def get_tip_end_coords(self, node, offset=None):
        """
        node tip coords must calculate new radian angle relative to parent 
        node and then add offset amount to radius when calculating (x, y).
        """
        if offset is None:
            offset = 0.0

        # store new coords
        points = []

        parent = node.up
        if not parent:
            return node.x, node.y

        else:
            # get angle in radians from parent coords
            radians = np.arcsin(node.y - parent.y)

            # get new coords from radian and radius from parent coords
            x = parent.x + node.dist + offset * np.cos(radians)
            y = parent.y + node.dist + offset * np.sin(radians)
            return x, y    
