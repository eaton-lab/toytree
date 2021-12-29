#/usr/bin/env python

"""Node distance functions.

These functions take a tree as input and typically allow the user to 
select one or more Nodes by entering either Node objects themselves, 
or, references to them as integer idx labels.
"""

from typing import Union
import itertools
import numpy as np
import pandas as pd
from toytree.utils import ToytreeError


# put functions here to have then exposed to Toytree API
__all__ = [
    "get_mrca",
    "get_node_distance",
    "get_internal_node_distance_matrix",
    "get_node_distance_matrix",
    "get_tip_distance_matrix",    
    "get_farthest_node",
    "get_farthest_node_distance"
]

def _get_dist_to_descendants_dict(
    tree: 'toytree.ToyTree', 
    node: Union[int, 'toytree.Node'],
    topology_only: bool = False,
    ) -> 'toytree.Node':
    """Return all descendant Nodes at farthest distance from a selected Node.

    Distance is measured by the sum of edge lengths separating them, 
    unless `topology_only` is True, in which case it is the number of 
    Nodes separating them (root Node is counted if traversed). If 
    multiple Nodes are equally distance the one with lowest idx is
    returned.

    This is used interally by other node_dist functions.
    """
    # get distances among descendant nodes by traversal
    node = tree[node.idx] if isinstance(node, int) else node
    ndists = {}
    for tnode in tree[node.idx].traverse("preorder"):
        if tnode != node:
            ndists[tnode.idx] = 1 if topology_only else tnode.dist
            if tnode.up.idx in ndists:
                ndists[tnode.idx] += ndists[tnode.up.idx]
    return ndists

def get_farthest_node(
    tree: 'toytree.ToyTree', 
    node: Union[int, 'toytree.Node'],    
    topology_only: bool = False,
    descendants_only: bool = False,
    ) -> 'toytree.Node':
    """Return the farthest descendant Node from a selected Node.

    Distance is measured by the sum of edge lengths separating them, 
    unless `topology_only` is True, in which case it is the number of 
    Nodes separating them (root Node is counted if traversed). If 
    multiple Nodes are equally distance the one with lowest idx is
    returned.
    """
    # get distances to all, or only descendants
    node = tree[node.idx] if isinstance(node, int) else node    
    if descendants_only:
        ndists = _get_dist_to_descendants_dict(tree, node, topology_only)
        nidx = np.argmax(ndists.values())
    else:
        ndists = get_node_distance_matrix(tree, topology_only)
        nidx = ndists[node.idx].argmax()
    return tree[nidx]

def get_farthest_node_distance(
    tree: 'toytree.ToyTree', 
    node: Union[int, 'toytree.Node'],
    topology_only: bool = False,
    descendants_only: bool = False,    
    ) -> 'toytree.Node':
    """Return the distance to the farthest descendant Node from a selected Node.

    Distance is measured by the sum of edge lengths separating them, 
    unless `topology_only` is True, in which case it is the number of 
    Nodes separating them (root Node is counted if traversed). If 
    multiple Nodes are equally distance the one with lowest idx is
    returned.
    """
    node = tree[node.idx] if isinstance(node, int) else node    
    if descendants_only:
        ndists = _get_dist_to_descendants_dict(tree, node, topology_only)
        return max(ndists.values())
    ndists = get_node_distance_matrix(tree, topology_only)
    return max(ndists[node.idx])

def get_mrca(
    tree: 'toytree.ToyTree', 
    *nodes: Union[int, 'toytree.Node'],
    ) -> 'toytree.Node':
    """Get the Node that is common ancestor to a set of Nodes.

    Nodes can be entered as Node objects or as int idx labels.

    Parameters
    ----------
    tree: toytree.ToyTree
        An input ToyTree instance.
    *node_idxs: int or toytree.Node
        Two or more Node objects or node idx labels as integers.

    Returns
    -------
    mrca: toytree.Node
        A Node object that is common ancestor of the selected nodes.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10)
    >>> toytree.distance.get_mrca(tree, tree[1], tree[2], tree[3])
    >>> toytree.distance.get_mrca(tree, 1, 2, 3)
    """
    node_sets = []

    # find every idx on way up to the root, and add the nidx itself
    for node in nodes:
        idx = node.idx if isinstance(node, toytree.Node) else node
        nset = set((i.idx for i in tree[idx]._iter_ancestors()))
        nset.add(idx)
        node_sets.append(nset)

    # bad set of node idxs
    if not node_sets:
        raise ToytreeError(f"No common ancestor of {nodes}")

    # get the lowest idx shared
    mrca = min(set.intersection(*node_sets))
    return tree[mrca]

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
            node = tree[idx]
            if topology_only:
                dist += sum(1 for i in node._iter_ancestors(mrca.up))
            else:
                dist += sum(i.dist for i in node._iter_ancestors(mrca.up))
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
    tree: 'toytree.ToyTree', 
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
    inodes = np.arange(tree.nnodes)
    dists = pd.DataFrame(
        columns=inodes,
        index=inodes,
        data=np.zeros((inodes.size, inodes.size)),
        dtype=int if topology_only else float,
    )
    for nodepair in itertools.permutations(inodes, 2):
        idx, jdx = nodepair
        dist = get_node_distance(tree, idx, jdx, topology_only)
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


if __name__ == "__main__":

    import toytree
    TREE = toytree.rtree.unittree(10, seed=123)
    print(TREE.draw())
    print(get_node_distance_matrix(TREE, True))
