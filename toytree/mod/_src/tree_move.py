#!/usr/bin/env python

"""

UNDER DEVELOPMENT:
------------------
rooted trees need to iterate over placements of the root?

Moves in tree space (SPR, TBR, NNI).

These functions are not optimized for speed sufficiently to be used in
phylogenetic analyses but rather are intended primarily for didactic
purposes.

Tree 'moves' (perturbations) are used to search tree space to
find optimal trees and used extensively in parsimony and maximum
likelihood hill-climbing algorithms.

See also eSPR and eTBR moves used in Bayesian phylogenetics. These
modify the probability of proposed pruning points by updating a
'distance' parameter as part of the MCMC process. For example in
mrbayes. Not implemented here.
"""

from typing import Optional, TypeVar
import numpy as np
import toytree.core.tree

ToyTree = TypeVar("ToyTree")

def move_spr(
    tree: ToyTree,
    seed: Optional[int]=None,
    inplace: bool=False,
    highlight: bool=False,
    ) -> ToyTree:
    """Return a rooted ToyTree one SPR move from the current tree.

    The returned tree will have a different topology from the starting
    tree, at an SPR distance of 1. It randomly samples a subtree to
    extract from the tree, and then reinserts the subtree at an edge
    that is not (1) one of its descendants; (2) its sister; (3) its
    parent; or (4) itself.

    Parameters
    ----------
    ...

    Examples
    --------
    >>> ...
    """
    tree = tree if inplace else tree.copy()
    rng = np.random.default_rng(seed)

    # randomly select a subtree (any non-root Node)
    sidx = rng.choice(tree.nnodes - 1)
    subtree = tree[sidx]
    tips = subtree.get_leaf_names()

    # get list of Nodes (edges) where subtree can be inserted. This
    # cannot be the root, or a descendant on the subtree Node, or the
    # subtree itself.
    edges = (
        set(range(tree.nnodes)) -
        set((i._idx for i in subtree._iter_descendants())) -
        set((i._idx for i in subtree._iter_sisters())) -
        set((subtree._up._idx, )) -
        set((subtree._idx, ))
    )

    # sample an edge by its descendant Node
    new_sister = tree[rng.choice(list(edges))]

    # connect subtree to new sister by inserting a new Node
    new_node = toytree.Node("new")
    new_node_parent = new_sister._up
    old_node = subtree._up
    old_node_parent = old_node._up
    new_node._up = new_node_parent
    new_node._children = (subtree, new_sister)

    # remove 12 and connect 11 to 14
    old_node._remove_child(subtree)
    if old_node_parent:
        old_node_parent._remove_child(old_node)
        for child in old_node._children:
            old_node_parent._add_child(child)
            child._dist += old_node._dist
    del old_node

    # connect subtree to tree
    subtree._up = new_node
    new_sister._up = new_node
    if new_node_parent:
        new_node_parent._remove_child(new_sister)
        new_node_parent._add_child(new_node)
    tree._update()

    # optional: color edges of the subtree that was moved.
    if highlight:
        tree.style.edge_colors = ['black'] * tree.nnodes
        descs = tree.get_mrca_node(*tips).get_descendants()
        for node in tree:
            if node in descs:
                tree.style.edge_colors[node.idx] = toytree.color.COLORS1[0]
    return tree


if __name__ == "__main__":

    # should be 15 rooted trees.
    TREE = toytree.rtree.unittree(4, seed=123)
    print(TREE._draw_browser())
    print(move_spr(TREE)._draw_browser())
