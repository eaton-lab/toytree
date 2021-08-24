#/usr/bin/env python

"""
Node distance functions.
"""

import itertools
import numpy as np
import pandas as pd
from toytree.utils.exceptions import ToytreeError
# import toytree


# put functions here to have then exposed to Toytree API
__all__ = [
    "get_mrca",
    "get_node_distance",
    "get_internal_node_distance_matrix",
    "get_node_distance_matrix",
    "get_tip_distance_matrix",    
]


# about 3X faster than TreeNode.get_common_ancestor()
def get_mrca(tree: 'toytree.ToyTree', *node_idxs: int):
    """Get the TreeNode that is common ancestor to a set of nodes.

    Parameters
    ----------
    tree: toytree.ToyTree
        An input ToyTree instance.
    *node_idxs
        Two or more node index labels (idxs) as integers.

    Returns
    -------
    mrca: toytree.TreeNode
        The TreeNode object representing the node that is common 
        ancestor of the selected nodes.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10)
    >>> toytree.distance.get_mrca(tree, 1, 2, 3)
    """
    node_sets = []

    # find every idx on way up to the root, and add the nidx itself
    for nidx in node_idxs:
        nset = set((i.idx for i in tree.idx_dict[nidx].iter_ancestors()))
        nset.add(nidx)
        node_sets.append(nset)

    # bad set of node idxs
    if not node_sets:
        raise ToytreeError("No common ancestor of {}".format(node_idxs))

    # get the lowest idx shared
    mrca = min(set.intersection(*node_sets))
    return tree.idx_dict[mrca]


# >3X faster than TreeNode.get_distance(), and scales better.
# If the tree is ultrametric we could calculate 2X faster by just 
# doubling the distance to mrca...
def get_node_distance(
    tree: 'toytree.ToyTree', 
    idx0: int, 
    idx1: int, 
    topology_only: bool=False,
    ) -> float:
    """Get the patristic distance between two nodes on a ToyTree.

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
    # return zero is they are the same node
    if idx0 == idx1:
        return 0

    # get the common 
    mrca = get_mrca(tree, idx0, idx1)

    # store total distance
    dist = 0

    # count from each node up to mrca
    for idx in (idx0, idx1):
        # skip if node == mrca
        if mrca.idx != idx:
            # get 1 or dist for every node up to the mrca
            node = tree.idx_dict[idx]
            if topology_only:
                dist += sum(1 for i in node.iter_ancestors(mrca.up))
            else:
                dist += sum(i.dist for i in node.iter_ancestors(mrca.up))
    return dist


def get_internal_node_distance_matrix(
    tree: 'toytree.ToyTree', 
    topology_only: bool=False,
    ) -> pd.DataFrame:
    """Get patristic distances between all internal nodes in a ToyTree.

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
    inodes = np.arange(tree.ntips, tree.nnodes)
    dists = pd.DataFrame(
        columns=inodes,
        index=inodes,
        data=np.zeros((inodes.size, inodes.size))
    )
    for nodepair in itertools.permutations(inodes, 2):
        idx, jdx = nodepair
        dist = get_node_distance(tree, idx, jdx, topology_only)
        dists.loc[idx, jdx] = dist
        dists.loc[jdx, idx] = dist
    return dists


def get_node_distance_matrix(
    tre: 'toytree.ToyTree', 
    topology_only: bool=False,
    ) -> pd.DataFrame:
    """Get patristic distances between all nodes in a ToyTree.

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
    inodes = np.arange(tre.nnodes)
    dists = pd.DataFrame(
        columns=inodes,
        index=inodes,
        data=np.zeros((inodes.size, inodes.size))
    )
    for nodepair in itertools.permutations(inodes, 2):
        idx, jdx = nodepair
        dist = get_node_distance(tre, idx, jdx, topology_only)
        dists.loc[idx, jdx] = dist
        dists.loc[jdx, idx] = dist
    return dists


def get_tip_distance_matrix(
    tre: 'toytree.ToyTree', 
    topology_only: bool=False,
    ) -> pd.DataFrame:
    """Get pairwise patristic distances between tip nodes in a ToyTree.

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
    inodes = np.arange(tre.ntips)
    dists = pd.DataFrame(
        columns=inodes,
        index=inodes,
        data=np.zeros((inodes.size, inodes.size))
    )
    for nodepair in itertools.permutations(inodes, 2):
        idx, jdx = nodepair
        dist = get_node_distance(tre, idx, jdx, topology_only)
        dists.loc[idx, jdx] = dist
        dists.loc[jdx, idx] = dist
    return dists
