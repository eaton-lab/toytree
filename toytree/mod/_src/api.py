#!/usr/bin/env python

"""API class for accessing `mod` subpackage functions from ToyTrees.

The `TreeModAPI` can be accessed either at the package level as 
`toytree.mod` or from the object level as `ToyTree.mod`. In the latter
case the default argument to all functions is the ToyTree object from
which the function is called.

Examples
--------
>>> tree = toytree.rtree.unittree(10)
>>> toytree.mod.unroot(tree)
>>> tree.mod.unroot()
"""

from typing import Dict, Optional, TypeVar, Sequence
from toytree.mod._src.mod_edges import (
    edges_scale_to_root_height,
    edges_slider,
    edges_multiplier,
    edges_set_node_heights,
    edges_extend_tips_to_align,
)
from toytree.mod._src.mod_topo import (
    ladderize, collapse_nodes, rotate_node, prune,
    drop_tips, resolve_polytomies, remove_unary_nodes,
    add_internal_node, add_tip_node,
)
from toytree.mod._src.root_unroot import unroot, root
# from toytree import Node
# from toytree.core.tree2 import ToyTree
# from toytree.mod.penalized_likelihood import Chronos

Node = TypeVar("Node")
ToyTree = TypeVar("ToyTree")
Query = TypeVar("Query", str, int, Node)


class TreeModAPI:
    """ToyTree modify tree topology API.

    Accessible from ToyTree class objects at .mod.[function].
    """
    def __init__(self, tree: ToyTree):
        self._tree = tree
        """Refto a ToyTree instance, hidden for API tab-complete."""

    def edges_scale_to_root_height(
        self, 
        treeheight: float = 1., 
        include_stem: bool = False, 
        inplace: bool = False,
        ) -> ToyTree:
        """Return ToyTree w/ new root height and all descendant nodes 
        scaled proportionately.
    
        Parameters
        ----------
        treeheight: float
            New height of the root Node, or, if include_stem=True, the
            height of the root stem (root.height + root.dist).
        include_stem: bool
            If True then the stem height is set instead of node height.
        inplace: bool
            If True the tree is modified, else a copy is returned.

        Returns
        -------
        ToyTree

        Example
        -------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> tree = tree.mod.edges_scale_to_root_height(1000)
        >>> tree.draw(scale_bar=True);
        """
        return edges_scale_to_root_height(
            self._tree, treeheight, include_stem, inplace)

    def edges_slider(
        self, 
        prop: float = 0.999, 
        seed: Optional[int] = None,
        ) -> ToyTree:
        """Return a ToyTree with node heights randomly jittered within bounds.

        Node heights are moved up or down uniformly between their parent
        and highest child node heights in 'levelorder', from root to 
        tips. The root and tip heights are fixed, only internal node
        heights are changed.

        Parameters
        ----------
        prop: float
            The proportion or percentile of the edge bounds from which
            to sample new heights from.
        seed: int
            Random number generator seed used to sample new heights.
        """
        return edges_slider(self._tree, prop, seed)

    def edges_multiplier(
        self, 
        multiplier: float = 1.0,
        inplace: bool = False,
        ) -> ToyTree:
        """Return a ToyTree with all nodes multiplied by a constant.

        Parameters
        ----------
        multiplier: float
            The multipier constant to use.
        """
        return edges_multiplier(self._tree, multiplier=multiplier, inplace=inplace)

    def edges_extend_tips_to_align(self, inplace: bool = False) -> ToyTree:
        """Return a ToyTree with tips aligned at height=0.

        Leaf Node dists are extended to align with the Node that is 
        farthest from the root (at height=0).

        Parameters
        ----------
        inplace: bool
            If True tree is modified in place, else a copy is
        """
        return edges_extend_tips_to_align(self._tree, inplace=inplace)

    def edges_set_node_heights(
        self, mapping: Dict[int, float], inplace: bool = False) -> ToyTree:
        """Return a ToyTree with edge lengths modified to explicitly
        set one or more node heights.

        Enter a dictionary mapping node idx to heights. Node idxs that
        are not included as keys will remain at there existing height.

        Note
        ----
        Changing the height of one or more Nodes requires changing the
        edge lengths (dist attributes) of two or more Node instances.

        Parameters
        ----------
        mapping: Dict
            A dict mapping node idx labels to their new heights.

        Examples
        --------
        >>> tre = toytree.rtree.unitree(10)
        >>> tre = tre.mod.edges_set_node_heights({10: 55, 11: 60, 12: 100})
        """
        return edges_set_node_heights(self._tree, mapping=mapping, inplace=inplace)

    def ladderize(self, direction: bool=True, inplace: bool=False) -> ToyTree:
        """Return a ladderized tree (ordered descendants)

        In a ladderized tree nodes are rotated so that the left/ 
        right child always has fewer/more descendants.

        Parameters
        ----------
        direction: bool
            Reverse the laddizered order.
        """
        return ladderize(self._tree, direction=direction, inplace=inplace)

    def collapse_nodes(
        self,
        *query: Query,
        regex: bool=False,        
        min_dist: float=1e-6,
        min_support: float=0,
        inplace: bool=False,
        ) -> ToyTree:
        """Return ToyTree with some internal nodes collapsed.

        Nodes can be entered as Node instances, Node names strings,
        or Node int idx labels, and/or Nodes can be selected by 
        minimum dist or support values. Selected Nodes are collapsed
        into multi-furcating polytomies. For example, set
        min_support=50 to collapse all nodes with support < 50, and/or
        select Node idx 10 to collapse Node 10.

        Note
        ----
        Both query-selected Nodes and min_dist or min_support Nodes
        will be collapsed. To only collapse query-selected Nodes set
        the other values arbitrarily low. To only collapse on the 
        threshold values do not enter any args to query.

        Parameters
        ----------
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names, 
            or int idx labels.
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.      
        min_dist: float
            The minimum dist (edge length) value allowed.
        min_support: float
            The minimum support (e.g., bootstrap) value allowed.
        inplace: bool
            If True then the original tree is changed in-place, and 
            returned, rather than leaving original tree unchanged.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=20)
        >>> tree = tree.set_node_data("dist", {22: 0.005, 23: 0.005})
        >>> tree = tree.set_node_data("support", {25: 50}, default=100)
        >>> tree = tree.collapse_nodes(min_dist=0.01, min_support=45)
        """
        return collapse_nodes(self._tree, 
            *query, regex=regex,
            min_dist=min_dist, min_support=min_support, inplace=inplace)

    def remove_unary_nodes(self, inplace: bool=False) -> ToyTree:
        """Return ToyTree with any unary Nodes removed.
        
        Parameters
        ----------
        inplace: bool
            If True then the original tree is changed in-place, and 
            returned, rather than leaving original tree unchanged.    
        """
        return remove_unary_nodes(self._tree, inplace=inplace)

    def rotate_node(self, *query: Query, regex: bool=False, inplace: bool=False) -> ToyTree:
        """Return ToyTree with a selected Node rotated (children reversed).

        Rotates only one Node per call. Internal Nodes are easiest selected
        by idx label, or by selecting multiple Nodes names from which the 
        MRCA will be selected.

        Parameters
        ----------
        *query: str, int, or Node
            The Node to rotate can be selected by entering the Node object,
            or its idx label, or name str. For internal Nodes, multiple
            queries can be entered and their MRCA will be rotated.
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.
        inplace: bool
            If True then the original tree is changed in-place, and 
            returned, rather than leaving original tree unchanged.
                    
        Examples
        --------
        >>> tree = toytree.rtree.unittree(10)
        >>> toytree.mod.rotate_node(tree, 12)
        >>> toytree.mod.rotate_node(tree, 'r0', 'r1')
        >>> toytree.mod.rotate_node(tree, 'r[0-3]$', regex=True)
        """
        return rotate_node(self._tree, *query, regex=regex, inplace=inplace)

    def prune(
        self,
        *query: Query,
        regex: bool=False,
        preserve_branch_length: bool=True,
        require_root: bool=True,
        inplace: bool=False,
        ) -> ToyTree:
        r"""Return a ToyTree as a subtree extracted from an existing tree.

        All nodes not included in the entered 'nodes' list will be
        removed from the topology, and the mininal spanning edges to
        connect the remaining nodes are retained. The root node is
        always preserved if 'require_root=True', otherwise the lowest
        mrca connecting the selected nodes will be kept as the new root.

                    4      prune([0,2])     4     
                   / \                     / \   
                  3   \      ------>      /   \  
                 / \   \                 /     \ 
                0   1   2               0       2

        Parameters
        ----------
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names, 
            or int idx labels.
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.
        preserve_branch_length: bool
            If True then the edge lengths of internal nodes that are
            removed are merged into the 'dist' attribute of their
            descendant node that is preserved.
        require_root: bool
            If True then the root node is always preserved. If False
            then the root is only preserved if is it the mrca of the
            selected nodes, otherwise the mrca Node is returned.
        inplace: bool
            If True then the original tree is changed in-place, and 
            returned, rather than leaving original tree unchanged.
        """
        return prune(self._tree, *query, regex=regex, 
            preserve_branch_length=preserve_branch_length,
            require_root=require_root, inplace=inplace)

    def drop_tips(
        self,
        *query: Query, 
        regex: bool=False, 
        inplace: bool=False,
        ) -> ToyTree:
        """Return a ToyTree with some tip Nodes removed.

        The ToyTree with the selected tip Nodes (and any remaining internal 
        nodes without children) are removed while retaining the original
        edge lengths between remaining nodes. This is effectively the 
        inverse of `prune`. Tip names can be selected using a Query method
        of Node instances, Node names, or Node idx int labels. Only 
        selected tip Nodes affect the result.

        Parameters
        ----------
        tree: ToyTree
            An input ToyTree to perform function on.
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names, 
            or int idx labels.
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.        
        inplace: bool
            If True then the original tree is changed in-place, and 
            returned, rather than leaving original tree unchanged.

        See Also
        --------
        prune: Extract a subtree from tree. The inverse of this function.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10)
        >>> tree.mod.drop_tips(1, 2, 3).draw()
        >>> tree.mod.drop_tips('r[0-3]$', regex=True).draw()
        >>> tree.mod.drop_tips('r1', 'r2')
        """
        return drop_tips(self._tree, *query, regex=regex, inplace=inplace)

    def resolve_polytomies(
        self,
        *query: Query,
        regex: bool=False,
        dist: float=1.0,
        support: float=100,
        recursive: bool=True,
        seed: Optional[int]=None,
        inplace: bool=False,
        ) -> ToyTree:
        """Return ToyTree with one or more polytomies randomly resolved.
            
        Parameters
        ----------
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names, 
            or int idx labels. If no Nodes are selected then ALL nodes
            that are multifurcating will be resolved.
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.     
        dist: float
            The dist value to set on newly created nodes.
        support: float
            The support value to set on newly created nodes.
        recursive: bool
            Recursively resolve nested polytomies (default=True); if False
            then a n-tomy will only be resolved into a (n-1)-tomy. 
        seed: int or None
            A seed for numpy random generator for reproducible resolving.
        inplace: bool
            If True then the original tree is changed in-place, and 
            returned, rather than leaving original tree unchanged.

        Examples
        --------
        >>> tree = toytree.tree("((a,b,c),d);")
        >>> tree.resolve_polytomy().draw();
        """
        return resolve_polytomies(
            self._tree, *query, regex=regex,
            dist=dist, support=support, recursive=recursive,
            seed=seed, inplace=inplace)

    def root(
        self,
        *query: Query,
        regex: bool=False,
        root_dist: Optional[float] = None,
        edge_features: Optional[Sequence[str]] = None,
        inplace: bool = False,
        ) -> ToyTree:
        """Return Toytree"""
        return root(
            self._tree, *query, regex=regex, root_dist=root_dist,
            edge_features=edge_features, inplace=inplace
        )

    def unroot(self, *query: Query, inplace: bool = False) -> ToyTree:
        """Return Toytree with binary root Node collapsed.
        """
        return unroot(self._tree, *query, inplace=inplace)

    def add_tip_node(
        self,
        *query: Query,
        regex: bool=False,
        name: Optional[str]=None,
        dist: Optional[float]=None,
        parent_dist: Optional[float]=None,
        parent_name: Optional[str]=None,
        inplace: bool=False,
        ) -> ToyTree:
        r"""Add a tip node by splitting an edge to create a new parent 
        and descendant node pair.

        Splits a branch spanning from node idx (A) to its parent (B)
        to create a new ancestral node (C) and descendant (D). The
        new nodes can be given names and dist values. By default, if
        only a dist is entered for the new sister (D) then the new
        ancestor node (C) dist value will be automated to make node
        D align at the same height as node A.

                    B                      B
                   / \                    / \
                  /   \      ---->       C   \
                 /     \                / \   \
                A       X              A   D   X

        Parameters
        ----------
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names, 
            or int idx labels. If multiple are entered the MRCA node will
            be used as the base of the edge to split. 
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.
        name: str
            Optional name for the new sister node.
        dist: float
            The dist (edge length) of the new sister node. If None
            this will be set to 1/2 of the sister's original dist.
            If parent_dist is None then the parent_dist will be set
            automatically to make the new sister node height align
            with its sister.
        parent_dist: float
            The dist (edge length) of the new ancestral node. If left
            at None then this value is automatically set to make node
            D align with A. Changing this value does not affect the
            height of node A, but does affect both nodes C and D.
            By setting parent_dist and dist both you can explicitly
            define any heights for the new nodes.
        parent_name: str
            Optional name for the new internal parent node.
        inplace: bool
            If False (default) a copy of the original tree is returned.

        Examples
        --------
        >>> # add a new tip node
        >>> tree = toytree.rtree.imbtree(5, treeheight=1e6)
        >>> tree = tree.mod.add_tip_node(3).draw();
        >>>
        >>> # add a ghost lineage, and draw as introgressing taxon.
        >>> tree = toytree.rtree.imbtree(5, treeheight=1e6)
        >>> tree = tree.mod.add_tip_node(
        >>>     idx=3, name="x", parent_dist=2e5, dist=3e5)
        >>> tree.ladderize().draw(ts='c', admixture_edges=(['r0', 'r1'], 'x'));
        """
        return add_tip_node(
            self._tree, *query, regex=regex,
            name=name, dist=dist, 
            parent_dist=parent_dist, parent_name=parent_name,
            inplace=inplace)

    def add_internal_node(
        self,
        *query: Query, 
        regex: bool=False,
        dist: Optional[float]=None,
        name: Optional[str]=None, 
        inplace: bool=False,
        ) -> ToyTree:
        r"""Add an internal node by splitting an edge to create new node.

        Splits a branch spanning from node idx (A) to its parent (B)
        to create a new internal node (C). This is not an especially
        useful operation except for internal usage by toytree.

                    B                      B
                   / \                    / \
                  /   \      ---->       C   \
                 /     \                /     \
                A       X              A       X

        See Also
        --------
        :func:`.add_tip_node`:
            Similar to this function but adds a tip node descending from C.
        
        Parameters
        ----------
        *query: str, int, or Node
            One or more Node selectors, which can be Node objects, names, 
            or int idx labels. If multiple are entered the MRCA node will
            be used as the base of the edge to split.
        regex: bool
            If True then Node name strings are treated as regular 
            expressions that can match to multiple Nodes.
        dist: float
            The distance from the selected Node at which to insert
            the new Node. This will be set as the dist of the 
            descendant (A) whereas the new Node's dist (C) will be 
            the descendants prior dist minus this dist value. If 
            no dist value is set then the edge midpoint is used.
        name: Optional[str]
            A name string to apply to the new Node.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=5, seed=123)
        >>> tree = tree.mod.topo_new_internal_node(0, dist=0.25)
        >>> tree.draw(ts='n', node_sizes=10);
        """
        return add_internal_node(
            self._tree, *query, regex=regex,
            dist=dist, name=name, inplace=inplace)


if __name__ == "__main__":

    print("TESTING")
