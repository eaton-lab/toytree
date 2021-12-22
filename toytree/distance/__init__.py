#!/usr/bin/env python

"""Functions for `distance` based calculations in toytree. 

Distances can be measured between Nodes of the same ToyTree, or among
different ToyTrees. The first represents either the number of Nodes 
separating two or more Nodes, or the sum of edge lengths separating 
them. Tree distance measurements can use topologies and/or edge 
lengths. Each can be returned for individual pairs, or as a table
with pairwise distances among many objects.

These functions are accessible either at (:mod:`toytree.distance`) 
subpackage, or in the tree-level API at (:mod:`ToyTree.distance`).

Examples
--------
>>> tree1 = toytree.rtree.unittree(ntips=10, seed=123)
>>> tree2 = toytree.rtree.unittree(ntips=10, seed=321)

>>> # get distances from data from tip Nodes (scipy wrapper)
>>> dists = toytree.distance.get_data_distance_matrix()
>>> dists = toytree.distance.get_data_distance_matrix(method='other')

>>> # get tree from distances (nj, bionj, upgma, ...)
>>> tree = toytree.distance.get_tree_from_distances(dists, method='...')

>>> # get distances between Nodes of the same tree
>>> dist_01 = toytree.distance.get_node_distance(tree1, 0, 1)
>>> dists = toytree.distance.get_node_distance_matrix(tree1)
>>> dists_1234 = toytree.distance.get_node_distance_matrix(tree1, 1, 2, 3, 4)

>>> # get distance between ToyTrees
>>> dist_t01 = toytree.distance.get_tree_distance_quartets(*trees, args=...)
>>> dist_t01 = toytree.distance.get_tree_distance_rf(tree1, tree2)

>>> # tree API usage (funcs accessible from trees for convenience)
>>> tree.distance.get_node_distance
>>> tree.distance.get_node_distance_matrix
>>> tree.distance.get_tree_distance
>>> tree.distance.get_tree_distance_matrix
>>> tree.distance.get_tree_distance_spatial
"""

# Note
# -----
# TODO: Kune-Felsenstein distance (topo and bls)

from . import api
from . import nodedist
from . import treedist
# from distance_funcs import *
