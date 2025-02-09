#!/usr/bin/env python

"""Relative evolutionary divergence

"""

from toytree import ToyTree
import numpy as np


__all__ = ["get_relative_evolutionary_divergence"]


def get_relative_evolutionary_divergence(tree: ToyTree, inplace: bool = False):
    """Returns a dict mapping Node idx to relative evolutionary divergence.
    
    RED interpolates the relative divergence of each node in a rooted tree by
    the average distance to the node's leafs, such that the root has a RED of
    0 and the leafs have a RED of 1.
    
    Parameters
    ----------
    tree: ToyTree
        A tree with edge lengths on which RED values will be computed.
    inplace: bool
        If True a tree is returned with data stored to Nodes as 
        feature "RED". Else a dict is returned.

    References
    ----------
    https://doi.org/10.1038/s41564-021-00918-8
    https://doi.org/10.48550/arXiv.1308.6333
    """
    # make sure the tree is rooted
    if not tree.is_rooted() :
        raise Exception("RED requires a rooted tree.")

    # store root to 0, tips to 1
    red = {tree.treenode.idx: 0}
    red.update({i: 1 for i in range(tree.ntips)})
    
    # get all-by-all node distance matrix
    mat = tree.distance.get_node_distance_matrix(topology_only=False)
    
    # preorder (parent then child) excluding root and tips
    for node in tree[-2: tree.ntips: -1]:
        
        # get parent's red value (P), and dist to parent (a)
        P = red[node.up.idx]
        a = mat[node.idx, node.up.idx]
        
        # get avg dist from this node to each of its leaves (b)
        b = np.mean([mat[node.idx, leaf.idx] for leaf in node.iter_leaves()])
        
        # integrety check in case of invalid branch lengths
        if a + b == 0:
            raise ValueError(f"node {node}: a == b == {a}")
        
        # store this nodes red value
        red[node.idx] = P + (a / (a + b)) * (1 - P)

    # return a tree with data set to nodes, or return the data in a dict
    if inplace:
        return tree.set_node_data("RED", red)
    else:
        return red


if __name__ == "__main__":

    import toytree
    tree = toytree.rtree.unittree(ntips=10, seed=123)
    # reds = tree.pcm.get_relative_evolutionary_divergence()
    reds = toytree.pcm.get_relative_evolutionary_divergence(tree)
    print(reds)