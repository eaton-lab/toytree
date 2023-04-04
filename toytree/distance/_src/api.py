#!/usr/bin/env python

"""Object API to make distance subpackage accessible from ToyTrees.

Distance functions take Node int idx labels as selectors.
"""

from typing import List, TypeVar, Union
import inspect
import numpy as np
import pandas as pd

import toytree.distance
from toytree.distance._src.nodedist import (
    get_node_path,
    get_node_distance,
    get_node_distance_matrix,
    get_internal_node_distance_matrix,
    get_tip_distance_matrix,
    get_farthest_node,
    get_farthest_node_distance,
)
from toytree.distance._src.treedist import (
    get_treedist_rf,
    get_treedist_rfi,
)

Node = TypeVar("Node")
ToyTree = TypeVar("ToyTree")
Query = TypeVar("Query", str, int, Node, None)


class DistanceAPI:
    def __init__(self, tree):
        self._tree = tree

    def get_node_path(self, node0: Query, node1: Query) -> List[Node]:
        """Docstring inherited"""
        return get_node_path(self._tree, node0=node0, node1=node1)

    def get_node_distance(self, node0: Query, node1: Query, topology_only: bool = False) -> float:
        """Docstring inherited"""
        return get_node_distance(self._tree, node0=node0, node1=node1, topology_only=topology_only)

    def get_node_distance_matrix(self, topology_only: bool = False, df: bool = False) -> Union[np.array, pd.DataFrame]:
        """Docstring inherited"""
        return get_node_distance_matrix(self._tree, topology_only=topology_only, df=df)

    def get_internal_node_distance_matrix(self, topology_only: bool = False, df: bool = False) -> Union[np.array, pd.DataFrame]:
        """Docstring inherited"""
        return get_internal_node_distance_matrix(self._tree, topology_only=topology_only, df=df)

    def get_tip_distance_matrix(self, topology_only: bool = False, df: bool = False) -> Union[np.array, pd.DataFrame]:
        """Docstring inherited"""
        return get_tip_distance_matrix(self._tree, topology_only=topology_only, df=df)

    def get_farthest_node(self, node: Query = None, topology_only: bool = False, descendants_only: bool = False) -> Node:
        """Docstring inherited"""
        return get_farthest_node(self._tree, node=node, topology_only=topology_only, descendants_only=descendants_only)

    def get_farthest_node_distance(self, node: Query = None, topology_only: bool = False, descendants_only: bool = False) -> Node:
        """Docstring inherited"""
        return get_farthest_node_distance(self._tree, node=node, topology_only=topology_only, descendants_only=descendants_only)

    ####################################################################
    #
    ####################################################################

    def get_treedist_rf(self, tree, normalize):
        """Docstring inherited"""
        return get_treedist_rf(self._tree, tree, normalize)

    def get_treedist_rfi(self, tree, normalize):
        """Docstring inherited"""
        return get_treedist_rfi(self._tree, tree, normalize)

    def get_treedist_qrt(self, *args):
        raise NotImplementedError("coming soon.")

    def get_treedist_other(self, *args):
        raise NotImplementedError("coming soon.")

    def treedist_table(self, treelist: List, metric: str = "rf"):
        """
        Returns a DataFrame with pairwise tree distances between
        this tree and a list of other trees calculated using the
        entered metric.
        """
        raise NotImplementedError("coming soon.")


########################################################################
# COPY DOCUMENTATION STRINGS TO API FUNCS FROM THE MODULE-LEVEL FUNCS
########################################################################
for name, module_func in inspect.getmembers(toytree.distance):
    if inspect.isfunction(module_func):

        api_func = getattr(DistanceAPI, name)
        api_func.__doc__ = module_func.__doc__
########################################################################
########################################################################
########################################################################

if __name__ == "__main__":
    help(DistanceAPI.root)
