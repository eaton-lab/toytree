#!/usr/bin/env python

"""Object API to make distance subpackage accessible from ToyTrees.

Distance functions take Node int idx labels as selectors.
"""

from typing import List, Optional, TypeVar
import pandas as pd
from toytree.distance._src.nodedist import (
    get_mrca_from_idxs,
    get_node_distance,
    get_internal_node_distance_matrix,
    get_node_distance_matrix,
    get_tip_distance_matrix,
    get_farthest_node,
    get_farthest_node_distance,
)

Node = TypeVar("Node")
ToyTree = TypeVar("ToyTree")


class DistanceAPI:
    def __init__(self, tree):
        self._tree = tree

    def get_mrca_from_idxs(self, *idxs:int) -> Node:
        """Return Node that is MRCA common ancestor to a set of Nodes.

        Nodes are selected by their int idx labels. This function is
        analagous to `ToyTree.get_mrca` but is slightly faster by
        allowing only ints as selectors rather than flexible input types.

        Parameters
        ----------
        tree: toytree.ToyTree
            An input ToyTree instance.
        *idxs: int
            Two or more Node int idx labels to select Nodes for which
            to find the most recent common ancestor of.

        Returns
        -------
        mrca: toytree.Node
            A Node object that is common ancestor of the selected nodes.

        See Also
        --------
        `ToyTree.get_mrca`

        Examples
        --------
        >>> tree = toytree.rtree.unittree(ntips=10)
        >>> tree.distance.get_mrca_from_idxs(tree, 1, 2, 3)
        """
        return get_mrca_from_idxs(self._tree, *idxs)

    def get_node_distance(self, idx0:int, idx1:int, topology_only:bool=False) -> float:
        """Return patristic distance between two nodes on a ToyTree.

        Parameters
        ----------
        tree: toytree.ToyTree
            A ToyTree instance.
        idx0: int
            The node idx label of the first node.
        idx1: int
            The node idx label of the second node.
        topology_only: bool
            If True then all edge lengths are set 1 so that the returned
            distance represents the number of nodes between nodes.

        Returns
        -------
        distance: float
            The patristic distance between two nodes (the minimum
            distance along edges connecting them that passes through
            their common ancestor).

        Example
        -------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> toytree.distance.get_node_distance(tree, 0, 1)
        """
        return get_node_distance(self._tree, idx0, idx1, topology_only)

    def get_internal_node_distance_matrix(self, topology_only:bool=False) -> pd.DataFrame:
        """Return patristic distances between all internal nodes in a ToyTree.

        Parameters
        ----------
        tree: toytree.ToyTree
            The input ToyTree instance.
        topology_only: bool
            If True then all edges lengths are set to 1.

        Returns
        -------
        node_distance_matrix: pd.DataFrame
            A DataFrame with node idx labels as the rows and columns
            and float values indicating the patristic distances between
            each pair of nodes.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> toytree.distance.get_internal_node_distance_matrix(tree)
        """
        return get_internal_node_distance_matrix(self._tree, topology_only)

    def get_node_distance_matrix(self, topology_only:bool=False) -> pd.DataFrame:
        """Return patristic distances between all nodes in a ToyTree.

        Parameters
        ----------
        tree: toytree.ToyTree
            The input ToyTree instance.
        topology_only: bool
            If True then all edges lengths are set to 1.

        Returns
        -------
        node_distance_matrix: pd.DataFrame
            A DataFrame with node idx labels as the rows and columns
            and float values indicating the patristic distances between
            each pair of nodes.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> toytree.distance.get_node_distance_matrix(tree)
        """
        return get_node_distance_matrix(self._tree, topology_only)

    def get_tip_distance_matrix(self, topology_only:bool=False) -> pd.DataFrame:
        """Return patristic distances between tip Nodes in a ToyTree.

        Parameters
        ----------
        tree: toytree.ToyTree
            The input ToyTree instance.
        topology_only: bool
            If True then all edges lengths are set to 1.

        Returns
        -------
        node_distance_matrix: pd.DataFrame
            A DataFrame with node idx labels as the rows and columns
            and float values indicating the patristic distances between
            each pair of nodes.

        Examples
        --------
        >>> tree = toytree.rtree.unittree(10, seed=123)
        >>> toytree.distance.get_tip_distance_matrix(tree)
        """
        return get_tip_distance_matrix(self._tree, topology_only)

    def get_farthest_node(
        self,
        idx: Optional[int] = None,
        topology_only: bool = False,
        descendants_only: bool = False,
        ) -> Node:
        """Return the farthest descendant Node from a selected Node.

        Parameters
        ----------
        idx: int
            The int idx label of a Node from which to measure distances
            from. Default is None, which uses the root Node.
        topology_only: bool
            If True distances are measured as number of edges between
            two Nodes, rather than the sum of edge distances.
        descendants_only: bool
            If True then the farthest descendant Node is returned, rather
            than the farthest Node spanning any path on the tree.
        
        Note
        ----
        If >1 Nodes are equally distance the one w/ lowest idx is returned.
        """
        return get_farthest_node(
            self._tree, idx, topology_only, descendants_only)

    def get_farthest_node_distance(
        self,
        idx: Optional[int] = None,
        topology_only: bool = False,
        descendants_only: bool = False,
        ) -> Node:
        """Return distance to the farthest descendant Node from a selected Node.

        Parameters
        ----------
        idx: int
            The int idx label of a Node from which to measure distances
            from. Default is None, which uses the root Node.
        topology_only: bool
            If True distances are measured as number of edges between
            two Nodes, rather than the sum of edge distances.
        descendants_only: bool
            If True then the farthest descendant Node is returned, rather
            than the farthest Node spanning any path on the tree.
        """
        return get_farthest_node_distance(
            self._tree, idx, topology_only, descendants_only)

    def get_treedist_rf(self, tree, ):
        raise NotImplementedError("coming soon.")

    def get_treedist_quartets(self, *args):
        raise NotImplementedError("coming soon.")

    def get_treedist_other(self, *args):
        raise NotImplementedError("coming soon.")

    def treedist_table(self, treelist:List, metric:str="rf"):
        """
        Returns a DataFrame with pairwise tree distances between
        this tree and a list of other trees calculated using the
        entered metric.
        """
        raise NotImplementedError("coming soon.")



# class NodeDistances:
#     pass


# class SequenceDistances:
#     pass


# class TreeDistances:
#     pass
