#!/usr/bin/env python

"""
A class wrapper for treemod funcs to make accessible from toytrees.
"""

from typing import Dict, Optional, Iterable
from toytree.mod._src.mod_edges import (
    edges_scale_to_root_height,
    edges_slider,
    edges_multiplier,
    edges_set_node_heights,
    edges_extend_tips_to_align,
)
from toytree.mod._src.mod_topo import (
    rotate_node,
)
# from toytree.core.tree2 import ToyTree
# from toytree.mod.penalized_likelihood import Chronos

class TreeModAPI:
    """ToyTree modify tree topology API.

    Accessible from ToyTree class objects at .mod.[function].
    """
    def __init__(self, tree: "ToyTree"):
        self._tree = tree

    def edges_scale_to_root_height(
        self, 
        treeheight: float = 1., 
        include_stem: bool = False, 
        inplace: bool = False,
        ) -> 'ToyTree':
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
        ) -> "ToyTree":
        """Return a ToyTree with node heights jittered within bounds.

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
        multiplier: float = 0.5, 
        seed: int = None, 
        inplace: bool = False,
        ) -> "ToyTree":
        """Return a ToyTree with all nodes multiplied by a constant.

        Node heights are multiplied by a constant sampled uniformly 
        between (multiplier, 1/multiplier).

        Parameters
        ----------
        multiplier: float
            The multipier constant to use.
        seed: int
            Seed for random number generator.
        """
        return edges_multiplier(self._tree, multiplier=multiplier, seed=seed, inplace=inplace)

    def edges_extend_tips_to_align(self, inplace: bool = False):
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
        self, mapping: Dict[int, float], inplace: bool = False) -> 'ToyTree':
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

    def topo_ladderize(self):
        """Return ToyTree"""

    def topo_collapse_nodes(self):
        """Return ToyTree"""

    def topo_prune(self):
        """Return Toytree"""

    def topo_drop_tips(self):
        """Return Toytree"""

    def topo_resolve_polytomy(self):
        """Return Toytree"""

    def topo_rotate_node(
        self,
        idx: int,
        inplace: bool = False,
        ) -> "ToyTree":
        """Return ToyTree with a Node rotated.

        Parameters
        ----------
        idx: int
            Select a Node to rotate by its unique int idx label.
        """
        return rotate_node(self, idx=idx, inplace=inplace)

    def topo_root(self):
        """Return Toytree"""

    def topo_unroot(self):
        """Return Toytree"""

    def topo_add_tip_node(self):
        """Return Toytree"""

    def topo_add_internal_node(self):
        """Return Toytree"""

                        