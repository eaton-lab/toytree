#!/usr/bin/env python

"""
API to make distance calls accessible from ToyTree objects.
"""

from typing import List
from toytree.distance.nodedist import (
    get_mrca,
    get_node_distance,
    get_tip_distance_matrix,
    get_internal_node_distance_matrix,
    get_node_distance_matrix,
)


class DistanceAPI:
    def __init__(self, tree):
        self._tree = tree

    def get_mrca(self, *node_idxs:int):
        """
        Returns the TreeNode that is the common ancestor of the
        set of input nodes (entered as int idx labels).

        Examples:
        ---------
        tre = toytree.tree("((a,b),(c,d));")
        tre.distance.get_mrca(0, 1, 2)            # call from ToyTree
        toytree.distance.get_mrca(tre, 0, 1, 2)   # or from module
        """
        return get_mrca(self._tree, *node_idxs)

    def get_node_distance(self, idx0:int, idx1:int, topology_only:bool=False):
        """
        Returns the patristic distance between two nodes on a tree.

        Examples:
        ----------
        tre = toytree.tree("((a,b),(c,d));")
        tre.distance.get_node_distance(0, 2)
        """
        return get_node_distance(self._tree, idx0, idx1, topology_only)

    def get_internal_node_distance_matrix(self, topology_only:bool=False):
        """
        Return DataFrame with internal node distances between
        all internal (non-tip) nodes of a tree.
        """
        return get_internal_node_distance_matrix(self._tree, topology_only)

    def get_node_distance_matrix(self, topology_only:bool=False):
        """
        Return DataFrame with node distances between all nodes.
        """
        return get_node_distance_matrix(self._tree, topology_only)

    def get_tip_distance_matrix(self, topology_only:bool=False):
        """
        Return DataFrame with node distances between all tip nodes.
        """
        return get_tip_distance_matrix(self._tree, topology_only)

    def treedist_rf(self, tree, ):
        raise NotImplementedError("coming soon.")

    def treedist_quartets(self, *args):
        raise NotImplementedError("coming soon.")

    def treedist_other(self, *args):
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
