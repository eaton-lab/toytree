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
import inspect
import toytree.mod
from toytree.mod._src.mod_edges import (
    edges_scale_to_root_height,
    edges_slider,
    edges_multiplier,
    edges_set_node_heights,
    edges_extend_tips_to_align,
)
from toytree.mod._src.mod_topo import (
    ladderize,
    collapse_nodes,
    remove_unary_nodes,
    rotate_node,
    extract_subtree,
    prune,
    drop_tips,
    resolve_polytomies,

    add_child_node,
    add_sister_node,
    add_internal_node,
    add_internal_node_and_child,
    add_internal_node_and_subtree,
)
from toytree.mod._src.root_unroot import (
    unroot,
    root,
)
from toytree.mod._src.root_funcs import (
    root_on_midpoint,
    root_on_minimal_ancestor_deviation,
)
# from toytree import Node
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
        """Docstring inherited from toytree.mod._src.mod_edges"""
        return edges_scale_to_root_height(self._tree, treeheight, include_stem, inplace)

    def edges_slider(
        self,
        prop: float = 0.999,
        seed: Optional[int] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod._src.mod_edges"""
        return edges_slider(self._tree, prop, seed, inplace)

    def edges_multiplier(
        self,
        multiplier: float = 1.0,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod._src.mod_edges"""
        return edges_multiplier(self._tree, multiplier=multiplier, inplace=inplace)

    def edges_extend_tips_to_align(self, inplace: bool = False) -> ToyTree:
        """Docstring inherited from toytree.mod._src.mod_edges"""
        return edges_extend_tips_to_align(self._tree, inplace=inplace)

    def edges_set_node_heights(
        self, mapping: Dict[Query, float], inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod._src.mod_edges"""
        return edges_set_node_heights(self._tree, mapping=mapping, inplace=inplace)

    def ladderize(self, direction: bool = False, inplace: bool = False) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return ladderize(self._tree, direction=direction, inplace=inplace)

    def collapse_nodes(
        self,
        *query: Query,
        min_dist: float = 1e-6,
        min_support: float = 0,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return collapse_nodes(self._tree, *query, min_dist=min_dist, min_support=min_support, inplace=inplace)

    def remove_unary_nodes(self, inplace: bool = False) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return remove_unary_nodes(self._tree, inplace=inplace)

    def rotate_node(self, *query: Query, regex: bool = False, inplace: bool = False) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return rotate_node(self._tree, *query, regex=regex, inplace=inplace)

    def extract_subtree(self, *query: Query, regex: bool = False) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return extract_subtree(self._tree, *query, regex=regex)

    def prune(
        self,
        *query: Query,
        regex: bool = False,
        preserve_branch_length: bool = True,
        require_root: bool = True,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return prune(
            self._tree, *query, regex=regex, preserve_branch_length=preserve_branch_length,
            require_root=require_root, inplace=inplace)

    def drop_tips(
        self,
        *query: Query,
        regex: bool = False,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return drop_tips(self._tree, *query, regex=regex, inplace=inplace)

    def resolve_polytomies(
        self,
        *query: Query,
        regex: bool = False,
        dist: float = 1.0,
        support: float = 100,
        recursive: bool = True,
        seed: Optional[int] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring inherited from toytree.mod."""
        return resolve_polytomies(
            self._tree, *query, regex=regex, dist=dist, support=support,
            recursive=recursive, seed=seed, inplace=inplace)

    def add_internal_node(
        self,
        *query: Query,
        regex: bool = False,
        dist: Optional[float] = None,
        name: Optional[str] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring is copied from mod_topo.py"""
        return add_internal_node(self._tree, *query, regex=regex, dist=dist, name=name, inplace=inplace)

    def add_child_node(
        self,
        *query: Query,
        regex: bool = False,
        name: Optional[str] = None,
        dist: Optional[float] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring is copied from mod_topo.py"""
        return add_child_node(self._tree, *query, regex=regex, name=name, dist=dist, inplace=inplace)

    def add_sister_node(
        self,
        *query: Query,
        regex: bool = False,
        name: Optional[str] = None,
        dist: Optional[float] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring is copied from mod_topo.py"""
        return add_sister_node(self._tree, *query, regex=regex, name=name, dist=dist, inplace=inplace)

    def add_internal_node_and_child(
        self,
        *query: Query,
        regex: bool = False,
        name: Optional[str] = None,
        dist: Optional[float] = None,
        parent_dist: Optional[float] = None,
        parent_name: Optional[str] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring is copied from mod_topo.py"""
        return add_internal_node_and_child(
            self._tree, *query, regex=regex, name=name, dist=dist, parent_dist=parent_dist,
            parent_name=parent_name, inplace=inplace)

    def add_internal_node_and_subtree(
        self,
        *query: Query,
        regex: bool = False,
        subtree: ToyTree,
        subtree_stem_dist: Optional[float] = None,
        subtree_rescale: bool = False,
        parent_dist: Optional[float] = None,
        parent_name: Optional[str] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring is copied from mod_topo.py"""
        return add_internal_node_and_subtree(
            self._tree, *query, regex=regex, subtree=subtree, subtree_stem_dist=subtree_stem_dist,
            subtree_rescale=subtree_rescale, parent_dist=parent_dist, parent_name=parent_name, inplace=inplace)

    ###################################################################
    def root(
        self,
        *query: Query,
        regex: bool = False,
        root_dist: Optional[float] = None,
        edge_features: Optional[Sequence[str]] = None,
        inplace: bool = False,
    ) -> ToyTree:
        """Docstring is inherited from toytree.mod._src.root_unroot.py"""
        return root(
            self._tree, *query, regex=regex, root_dist=root_dist,
            edge_features=edge_features, inplace=inplace
        )

    def unroot(self, inplace: bool = False) -> ToyTree:
        """Docstring is inherited from toytree.mod._src.root_unroot.py"""
        return unroot(self._tree, inplace=inplace)

    def root_on_midpoint(self, inplace: bool = False) -> ToyTree:
        """Docstring is inherited from toytree.mod._src.root_unroot.py"""
        return root_on_midpoint(self._tree, inplace=inplace)

    def root_on_minimal_ancestor_deviation(self, *query: Query, inplace: bool = False, return_stats: bool = False) -> ToyTree:
        """Docstring is inherited"""
        return root_on_minimal_ancestor_deviation(self._tree, *query, inplace=inplace, return_stats=return_stats)


########################################################################
# COPY DOCUMENTATION STRINGS TO API FUNCS FROM THE MODULE-LEVEL FUNCS
########################################################################
for name, module_func in inspect.getmembers(toytree.mod):
    if inspect.isfunction(module_func):

        api_func = getattr(TreeModAPI, name)
        api_func.__doc__ = module_func.__doc__
########################################################################
########################################################################
########################################################################

if __name__ == "__main__":
    help(TreeModAPI.root)
