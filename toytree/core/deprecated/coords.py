#!/usr/bin/env python

"""A class for generating and storing Toytree plotting coordinates.
"""

from typing import Optional, List
import numpy as np
from toytree.utils import ToytreeError


class BaseCoords:
    """Store edge table and node layout coordinates for tree drawings.

    """
    ttree: 'ToyTree'
    edges: np.ndarray = None
    verts: np.ndarray = None

    def update(self):
        """Fill the idx_dict of self.tree with updated node instances.

        This function call is the main utility of the Coords class.
        
        Note
        ----
        Each TreeNode will have a .x and .y attribute with coordinates.
        This function is called frequently by ToyTree objects to keep
        coordinates updated anytime the tree changes, and so it is 
        optimized for speed as much as possible. See RawTree for an 
        class with faster operations b/c it does not need to keep 
        plotting coordinates updated.

        Two traversals: one to count nodes, next to assign labels.
        """
        self.ttree.idx_dict = {}
        self.ttree.nnodes = 0
        self.ttree.ntips = 0

        self.count_nodes()
        self.assign_idxs()
        self.get_edges()
        self.get_layout()

    def count_nodes(self):
        """Sets the count for number of nodes and tips. 

        This needs to be performed before assign_idxs b/c the counts
        are used when assigning idx labels to nodes.
        """
        for node in self.ttree.treenode.traverse():
            self.ttree.nnodes += 1
            if node.is_leaf():
                self.ttree.ntips += 1

    def assign_idxs(self):
        """Assigns idx labels in toytree's 'idx traversal order'.

        This order is a root-to-tip traversal the same as 'level-order'
        for all internal nodes, however, the tip nodes are assigned idx
        values in order from the bottom to top most order of the leaves
        when plotted.
        """
        # internal nodes: root is highest idx
        idx = self.ttree.nnodes - 1

        for node in self.ttree.treenode.traverse("levelorder"):
            if not node.is_leaf():
                node.idx = idx
                self.ttree.idx_dict[idx] = node
                if not node.name:
                    node.name = str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.ttree.treenode.get_leaves():
            node.idx = idx
            self.ttree.idx_dict[idx] = node
            if not node.name:
                node.name = str(idx)
            idx -= 1

        # Reorder: not really necessary, but reduces user error
        self.ttree.idx_dict = {
            i: self.ttree.idx_dict[i] for i in range(self.ttree.nnodes)}

    def get_edges(self):
        """This could change if a tree dropped nodes.

        """
        self.edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        for idx in range(self.ttree.nnodes - 1):
            parent = self.ttree.idx_dict[idx].up
            if parent:
                self.edges[idx, :] = (parent.idx, idx)

    def get_layout(self):
        """Fills the .x and .y coordinates and .verts array.

        This will raise an error if called from this Base Class, since
        it does not have a proper get_layout function. The super classes
        LinearCoords, RadialCoords, and ...Coords have different layout
        funcs in this place.
        """
        raise NotImplementedError(
            "Use a superclass of BaseCoords to get a node layout.")


class LinearCoords2(BaseCoords):
    """Linear tree layout.

    Sets .verts and node .x and y. for node positions.
    X and Y positions here refer to base assumption that tree is right
    facing, reorient_coordinates() will handle re-translating this.

    Parameters
    ----------
    layout: str
        A categorical linear layout in ['r', 'l', 'u', 'd'].
    use_edge_lengths: bool
        If not using edge lengths then tips are extended to align at 
        zero.
    fixed_order: List[str]
        A list of len(tree.ntips) of tip names in the order they 
        should be plotted. Using a fixed order can cause the tree edges
        to overlap, which is often used to show discordance.
    fixed_position: List[float]
        A list or array of float values representing the x position
        (spacing) among tips on a down-facing tree. By default all tips
        are spaced 1 unit apart, but this can be modified here for 
        various reasons.
    """
    layout: str
    use_edge_lengths: bool = True
    fixed_order: Optional[List] = None
    fixed_position: Optional[List] = None

    def __post_init__(self):
        """Calls the base class update() function."""
        self.update()

    def get_layout(self):
        """Fill the verts array with x, y coordinates for a 'd' layout.

        TODO
        ----
        traverse and use parent distances to root to get faster
        calculation of toroot height values.
        """
        verts = np.zeros((self.ttree.nnodes, 2), dtype=float)

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

            # position the x-labels
            if node.is_leaf() and (not node.is_root()):
                if self.use_edge_lengths:
                    toroot = sum(
                        i.dist for i in node.iter_ancestors()
                        if not i.is_root()
                    )
                    # limit on precision to avoid zero buffer errors
                    node.y = round(hgt - (node.dist + toroot), 8)
                else:
                    node.y = 0.

                # order of xlabels
                if self.fixed_order is not None:

                    # the position is explicit
                    if self.fixed_position is not None:
                        node.x = self.fixed_position[self.fixed_order.index(node.name)]

                    # simply use the index as position
                    else:
                        node.x = self.fixed_order.index(node.name)
                else:

                    # the position is explicit
                    if self.fixed_position is not None:
                        node.x = self.fixed_position[node.idx]

                    # simply use the index as position
                    else:
                        node.x = node.idx

            else:
                nch = node.children
                # empty trees only
                if not nch:
                    node.x = node.y = 0

                # all other trees
                else:
                    if self.use_edge_lengths:
                        node.y = nch[0].y + nch[0].dist
                    else:
                        node.y = max((i.y for i in nch)) + 1

                    # internal node at midpoint of children
                    node.x = sum(i.x for i in nch) / float(len(nch))

            # store the vertex
            verts[idx] = [node.x, node.y]

        # scale so that node idx 0 (or fixed_order x) is at (0, 0)
        if self.use_edge_lengths:
            adjust = verts[:, 1].min()
            verts[:, 1] -= adjust

        # check layout is in directionals
        if self.layout not in "drlu":
            raise ToytreeError("layout not recognized")

        # default: Down-facing tips align at y=0, first ladderized tip at x=0            
        if self.layout == 'd':
            tmp = verts

        # right-facing tips align at x=0, last ladderized tip at y=0
        elif self.layout == 'r':
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(verts.shape)
            tmp[:, 1] = verts[:, 0]
            tmp[:, 0] = verts[:, 1] * -1

        elif self.layout == 'l':
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(verts.shape)
            tmp[:, 1] = verts[:, 0]
            tmp[:, 0] = verts[:, 1] 

        # elif layout == 'u':
        else:
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(verts.shape)
            tmp[:, 1] = verts[:, 1] * -1
            tmp[:, 0] = verts[:, 0]
        return tmp
       




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
        ...
    """
    def __init__(self, ttree):
        # the toytree
        self.ttree = ttree

        # the vertices and edge tuples for normal layouts ('n')
        self.edges = None
        self.verts = None


    def update(self, layout=None):
        """
        Updates idx_dict and coordinates for drawing tree graph.
        """
        # new idx_dict (can't just overwrite existing b/c nnodes may changed)
        self.ttree.idx_dict = {}

        # update tree dimensions by traversal
        self.ttree.nnodes = 0
        self.ttree.ntips = 0
        for node in self.ttree.treenode.traverse():
            self.ttree.nnodes += 1
            if node.is_leaf():
                self.ttree.ntips += 1

        # update idxs by traversing tree in levelorder
        self.update_idxs()

        # update edges table
        self.edges = self.get_edges()

        # update node coordinates table
        layout = self.ttree.style.layout
        if layout == 'c':
            self.verts = self.get_radial_coords()
        else:
            self.verts = self.get_linear_coords(layout=layout)

    def update_idxs(self):
        """
        set root idx highest, then all internal nodes are numbered down
        in levelorder traversal, but tips are ordered numerically from
        bottom to top in right facing ladderized tree plot order.
        """
        # internal nodes: root is highest idx
        idx = self.ttree.nnodes - 1

        for node in self.ttree.treenode.traverse("levelorder"):
            if not node.is_leaf():
                node.idx = idx
                self.ttree.idx_dict[idx] = node
                if not node.name:
                    node.name = str(idx)
                idx -= 1

        # external nodes: lowest numbers are for tips (0-N)
        for node in self.ttree.treenode.get_leaves():
            node.idx = idx
            self.ttree.idx_dict[idx] = node
            if not node.name:
                node.name = str(idx)
            idx -= 1

        # TODO: not really necessary, but reduces user error
        self.ttree.idx_dict = {
            i: self.ttree.idx_dict[i] for i in range(self.ttree.nnodes)}

    def get_edges(self):
        """
        This could change if a tree dropped nodes.
        """
        # use cache to fill edges array
        edges = np.zeros((self.ttree.nnodes - 1, 2), dtype=int)
        for idx in range(self.ttree.nnodes - 1):
            parent = self.ttree.idx_dict[idx].up
            if parent:
                edges[idx, :] = (parent.idx, idx)
        return edges

    def get_radial_coords(self, use_edge_lengths=True):
        """
        Assign .edges and .verts for node positions in a fan tree.
        The farthest tip aligns at the circumference.
        """
        circ = Circle(self.ttree)
        verts = np.zeros((self.ttree.nnodes, 2), dtype=float)

        # shortname
        if not use_edge_lengths:
            nbits = self.ttree.treenode.get_farthest_leaf(True)[1]

        # use cache to fill edges array
        for idx in range(self.ttree.nnodes):
            node = self.ttree.idx_dict[idx]

            # leaves: x positions are evenly spaced around circumference
            if node.is_leaf() and (not node.is_root()):

                # store radians (how far around from zero to 2pi)
                node.radians = circ.tip_radians[idx]

                # get positions of tips using radians and radius
                if use_edge_lengths:
                    node.radius = circ.radius - node.height
                    node.x, node.y = circ.get_node_coords(node)
                else:
                    node.radius = nbits
                    node.x, node.y = circ.get_node_coords(node)

            # internal nodes comes after tips. Inherit position from children.
            else:

                # height is either distance or nodes from root
                if use_edge_lengths:
                    node.radius = circ.radius - node.height
                else:
                    node.radius = sum(1 for i in node.iter_ancestors())
                    # max([i.radius for i in node.children]) - 1

                # x position is halfway between children x-pos
                node.radians = np.mean([i.radians for i in node.children])
                node.x, node.y = circ.get_node_coords(node)

            # store the x,y vertex positions
            verts[node.idx] = [node.x, node.y]
        return verts

    def get_linear_coords(
        self,
        layout=None,
        use_edge_lengths:bool=True,
        fixed_order:Optional[List]=None,
        fixed_position:Optional[List]=None,
        ):
        """
        Sets .verts and node .x and y. for node positions.
        X and Y positions here refer to base assumption that tree is right
        facing, reorient_coordinates() will handle re-translating this.        
        """
        verts = np.zeros((self.ttree.nnodes, 2), dtype=float)

        # store verts array with x,y positions of nodes (lengths of branches)
        # we want tips to align at the right face (larger axis number)
        fartip = self.ttree.treenode.get_farthest_leaf()[0]
        hgt = sum([
            fartip.dist,
            sum(i.dist for i in fartip.iter_ancestors() if not i.is_root())
        ])

        # TODO: traverse and use parent distances to root to get faster
        # calculation of toroot height values.

        # finding tip distance from root is a little slow, it would be faster
        # just progress forward from root, but this wouldn't easily allow for
        # spacing fixed order tips. So instead we start from tips. 
        for idx in range(self.ttree.nnodes):
            node = self.ttree.idx_dict[idx]

            # position the x-labels
            if node.is_leaf() and (not node.is_root()):
                if use_edge_lengths:
                    toroot = sum(
                        i.dist for i in node.iter_ancestors()
                        if not i.is_root()
                    )
                    # limit on precision to avoid zero buffer errors
                    node.y = round(hgt - (node.dist + toroot), 8)
                else:
                    node.y = 0.

                # order of xlabels
                if fixed_order is not None:

                    # the position is explicit
                    if fixed_position is not None:
                        node.x = fixed_position[fixed_order.index(node.name)]

                    # simply use the index as position
                    else:
                        node.x = fixed_order.index(node.name)
                else:

                    # the position is explicit
                    if fixed_position is not None:
                        node.x = fixed_position[node.idx]

                    # simply use the index as position
                    else:
                        node.x = node.idx

            else:
                nch = node.children
                # empty trees only
                if not nch:
                    node.x = node.y = 0

                # all other trees
                else:
                    if use_edge_lengths:
                        node.y = nch[0].y + nch[0].dist
                    else:
                        node.y = max((i.y for i in nch)) + 1

                    # internal node at midpoint of children
                    node.x = sum(i.x for i in nch) / float(len(nch))

            # store the vertex
            verts[idx] = [node.x, node.y]

        # scale so that node idx 0 (or fixed_order x) is at (0, 0)
        if use_edge_lengths:
            adjust = verts[:, 1].min()
            verts[:, 1] -= adjust

        # check layout is in directionals
        if layout not in "drlu":
            raise ToytreeError("layout not recognized")

        # default: Down-facing tips align at y=0, first ladderized tip at x=0            
        if layout == 'd':
            tmp = verts

        # right-facing tips align at x=0, last ladderized tip at y=0
        elif layout == 'r':
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(verts.shape)
            tmp[:, 1] = verts[:, 0]
            tmp[:, 0] = verts[:, 1] * -1

        elif layout == 'l':
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(verts.shape)
            tmp[:, 1] = verts[:, 0]
            tmp[:, 0] = verts[:, 1] 

        # elif layout == 'u':
        else:
            # verts swap x and ys and make xs 0 to negative
            tmp = np.zeros(verts.shape)
            tmp[:, 1] = verts[:, 1] * -1
            tmp[:, 0] = verts[:, 0]
        return tmp
       

    # def get_radii(self, layout):
    #     """
    #     radius of every node relative to 0,0 origin.
    #     """
    #     # custom request layout
    #     if layout is None:
    #         layout = self.ttree.layout

    #     # get circular layout
    #     if layout == 'c':
    #         self.radii = np.array(
    #             [self.ttree.idx_dict[i].radius for i in range(self.nnodes)])
    #     else:
    #         self.radii = np.repeat(0, self.ntips)


    # def get_unrooted_coords(self, layout):
    #     """
    #     Project nodes onto an unrooted layout of either type A or B.
    #     """
        
    #     # get projection
    #     return self






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


    # def get_node_lines(self, node):
    #     x = self.o[0] + node.up.radius * np.cos(node.radians)
    #     y = self.o[1] - node.up.radius * np.sin(node.radians)
    #     return x, y      


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

