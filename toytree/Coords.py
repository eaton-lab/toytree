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
    def update(self):
        "Updates cartesian coordinates for drawing tree graph"              
        # get new shape and clear for attrs
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        self.verts = np.zeros((self.ttree.nnodes, 2), dtype=float)
        self.lines = []
        self.coords = []

        # fill with updates
        self.update_idxs()             # get dimensions of tree
        self.update_fixed_order()      # in case ntips changed
        self.assign_vertices()         # get node locations
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
                    node.name = "i" + str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.ttree.treenode.get_leaves():  # [::-1]:
            node.add_feature("idx", idx)
            if not node.name:
                node.name = "t" + str(idx)
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
        
        # if tree is empty then bail out
        if len(self.ttree) < 2:
            return

        # things to fill
        edges = []
        nupdict = {}

        # The number of vertices needed to store these edges
        # This depends on polytomies since we skip over some edges.
        nnups = 2 * self.ttree.nnodes + self.ttree.ntips + 100
        verts = np.zeros((nnups, 2))        

        # set new node counter to start at ntips
        nidx = len(self.ttree)
        vidx = 0

        # from tips to root
        for node in self.ttree.treenode.traverse("postorder"):
            
            if node.is_leaf():
                # enter a vertex
                verts[vidx] = (node.x, node.y)
                vidx += 1
                
                # store the nups new nodes vertices
                node.nup = (node.x, node.up.y)
                nupdict[node.nup] = nidx
                verts[nidx] = node.nup
                nidx += 1

                # connect node to its node-up
                edges.append((nidx - 1, vidx - 1))

            else:
                # get nodes of left/right children 
                minx = min(node.children, key=lambda x: x.x)
                maxx = max(node.children, key=lambda x: x.x)
                
                # vert indices of newnodes above the children
                nidxl = nupdict[minx.nup]
                nidxr = nupdict[maxx.nup]

                # store left/right edge
                edges.append((nidxl, nidxr))

                if not node.is_root():
                    # vertex for internal node and edge up to its nup
                    # store internal node
                    verts[nidx] = (node.x, node.y)
                    nidx += 1

                    # store nup new node 
                    node.nup = (node.x, node.up.y)
                    nupdict[node.nup] = nidx
                    verts[nidx] = node.nup
                    nidx += 1

                    # store edge connected internal node to nup
                    edges.append((nidx - 1, nidx - 2))
        
        # store to self
        self.coords = verts[:nidx, :]
        self.lines = np.array(list(edges))


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
        if self.ttree.style.orient in ('down', 0):
            pass

        # right-facing tips align at x=0, last ladderized tip at y=0
        elif self.ttree.style.orient in ('right', 3):

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

        elif self.ttree.style.orient in ('left', 1):
            raise NotImplementedError("todo: left facing")

        else:
            raise NotImplementedError("todo: up facing")