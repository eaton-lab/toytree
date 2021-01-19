#/usr/bin/env python

"""
A collection of distance functions for:
    1. distances between nodes on a tree (e.g., patristic).
    2. distances between trees (e.g., RF)
    3. distances between sequences (int or str/bytes seq arrays).
"""

import itertools
import numpy as np
import pandas as pd
from toytree.utils import ToytreeError



class NodeDistances:
    pass


class SequenceDistances:
    pass


class TreeDistances:
    pass



# about 3X faster than TreeNode.get_common_ancestor()
def get_mrca(tre, *node_idxs):
    """
    Returns the TreeNode object that is the common ancestor of the 
    set of input nodes (entered by their idx label) on the input tree.

    Example 1:
        toytree.distance.get_mrca(tre, 1, 2, 3)

    Example 2:
        tre.distance.get_mrca(1, 2, 3)
    """
    node_sets = []

    # find every idx on way up to the root, and add the nidx itself
    for nidx in node_idxs:
        nset = set((i.idx for i in tre.idx_dict[nidx].iter_ancestors()))
        nset.add(nidx)
        node_sets.append(nset)

    # bad set of node idxs
    if not node_sets:
        raise ToytreeError("No common ancestor of {}".format(node_idxs))

    # get the lowest idx shared
    mrca = min(set.intersection(*node_sets))
    return tre.idx_dict[mrca]



# >3X faster than TreeNode.get_distance(), and scales better.
# If the tree is ultrametric we could calculate 2X faster by just 
# doubling the distance to mrca...
def get_patristic_distance(tre, idx0, idx1, topology_only=False):
    """
    Returns the patristic distance between two nodes on a tree.
    """
    # return zero is they are the same node
    if idx0 == idx1:
        return 0

    # get the common 
    mrca = get_mrca(tre, idx0, idx1)

    # store total distance
    dist = 0

    # count from each node up to mrca
    for idx in (idx0, idx1):
        # skip if node == mrca
        if mrca.idx != idx:
            # get 1 or dist for every node up to the mrca
            node = tre.idx_dict[idx]
            if topology_only:
                dist += sum(1 for i in node.iter_ancestors(mrca.up))
            else:
                dist += sum(i.dist for i in node.iter_ancestors(mrca.up))
    return dist



# 
def get_internal_node_distance_matrix(tre, topology_only=False):
    """
    Create distance matrix between internal nodes of a tree and 
    returns as a labeled Pandas.DataFrame.
    """
    inodes = np.arange(tre.ntips, tre.nnodes)
    dists = pd.DataFrame(
        columns=inodes,
        index=inodes,
        data=np.zeros((inodes.size, inodes.size))
    )
    for nodepair in itertools.permutations(inodes, 2):
        idx, jdx = nodepair
        dist = get_patristic_distance(tre, idx, jdx, topology_only)
        dists.loc[idx, jdx] = dist
        dists.loc[jdx, idx] = dist
    return dists
