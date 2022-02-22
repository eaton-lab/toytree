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

def move_nni_unrooted():
    raise NotImplementedError("TODO")

def iter_spr_rooted(tree: ToyTree):
    """Return a generator that will visit all trees within one SPR
    move of the current tree.

    The returned set of trees does not visit the original tree.

    NOT YET WORKING/TESTED (you can help!)

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, seed=123)
    >>> spr_trees = iter_spr_unrooted(tree)
    >>> logliks = [func(stre) for stre in spr_trees]
    """
    # just iter over each possible subtree and each possible placement,
    # right? But some are redundant? Try it out...
    # raise NotImplementedError("TODO")
    raise NotImplementedError("TODO")
    edges = tree.get_edges()
    nedges = edges[edges[:, 0] != tree.treenode.idx]

    # iterate over rows of edge matrix
    for eidx in range(nedges.shape[0]):
        nnidx = nedges[eidx, 1]
        tips = tree.get_tip_labels(nnidx)
        print(nnidx, tips)

        # iterate over possible edges to place this subtree (not orig edge)
        _sub1 = tree.drop_tips(tips)
        for nidx in range(1, _sub1.nnodes):
            if nidx in [tree.treenode.idx, nnidx]:
                continue

            # toytrees
            sub0 = tree.prune(tips)
            sub1 = tree.drop_tips(tips)
            node = sub1[nidx]

            new = toytree.Node(name="spr", dist=node.dist / 2)
            node.up.children.append(new)
            node.up.children.remove(node)
            node.up = new
            new.children.append(node)
            new.children.append(sub0.treenode)
            sub0.up = new
            yield toytree.ToyTree(sub1.treenode)

def move_spr_unrooted(tree: ToyTree, seed:Optional[int]=None):
    """Return an unrooted ToyTree after one SPR move to input tree.

    Select one edge randomly from the tree and split on that edge to
    create two subtrees. Attach one of the subtrees (e.g., the
    smaller one) randomly to the larger tree to create a new node.
    """
    # ensure tree is unrooted
    if tree.is_rooted():
        tree = tree.unroot()

    # seed generator
    rng = np.random.default_rng(seed)

    # select a random edge
    nidx = rng.integers(tree.nnodes - 1)

    # get subtree below this edge
    sub0 = tree.prune(tree.get_tip_labels(nidx))

    # get subtree with sub0 removed
    sub1 = tree.drop_tips(tree.get_tip_labels(nidx))

    # randomly select an edge on sub1 to add sub0 back to
    nidx = rng.choice(range(1, sub1.nnodes))
    node = sub1[nidx]

    # randomly select a point on the branch to add new node
    if len(sub0) == 1:
        sub0 = sub0.treenode.children[0]
    else:
        sub0 = sub0.treenode
        # node.up.children.append(sub0)

    new = toytree.Node(name="spr", dist=rng.uniform(node.dist))
    node.up.children.append(new)
    node.up.children.remove(node)
    node.up = new
    new.children.append(node)
    new.children.append(sub0)
    sub0.up = new

    tree = toytree.ToyTree(sub1.treenode)
    return tree


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



def move_spr_rooted(
    tree: ToyTree,
    seed: Optional[int]=None,
    inplace: bool=False,
    ) -> ToyTree:
    """Return a rooted ToyTree one SPR move from the current tree.

    Performs a subtree pruning and regrafting move on the input tree.
    Selects one edge randomly from the tree and splits on that edge
    to create two subtrees, then attaches one of the subtrees (the
    smaller one) randomly to the larger tree to create a new node.

    This implementation is super slow, should not use prune and
    drop_tips since these require an update call.
    """
    # seed generator
    rng = np.random.default_rng(seed)

    # randomly select one edge that is not leading to the root
    edges = tree.get_edges()
    nedges = edges[edges[:, 0] != tree.treenode.idx]
    nidx = nedges[rng.integers(nedges.shape[0]), 0]
    tips = tree.get_tip_labels(nidx)

    # get subtree below selected edge
    # TODO: much faster methods would avoid prune and drop calls.
    sub0 = tree.prune(tips)

    # get subtree with sub0 clade removed
    sub1 = tree.drop_tips(tips)

    # randomly select an edge on sub1 to add sub0 back to
    # TODO, what is this selecting? why 1:?
    nidx = rng.choice(sub1.get_nodes()[1:])
    node = sub1[nidx]

    # randomly select a point on the branch to add new node
    new = toytree.Node(name="spr", dist=rng.uniform(node.dist))
    node.up.children.append(new)
    node.up.children.remove(node)
    node.up = new
    new.children.append(node)
    new.children.append(sub0.treenode)
    sub0.up = new

    tree = toytree.ToyTree(sub1.treenode)
    return tree

def _move_spr_rooted_fast(tree:toytree.ToyTree, seed:Optional[int]=None):
    """Faster implementation that avoids ToyTree coords updates.

    Returns an rooted ToyTree where one subtree pruning and
    regrafting move has been performed from the input tree.

    Select one edge randomly from the tree and split on that edge to
    create two subtrees. Attach one of the subtrees (e.g., the
    smaller one) randomly to the larger tree to create a new node.
    """
    # seed generator
    rng = np.random.default_rng(seed)

    # randomly select one edge that is not leading to the root
    edges = tree.get_edges()
    nedges = edges[edges[:, 0] != tree.treenode.idx]
    nidx = nedges[rng.integers(nedges.shape[0]), 0]
    tips = tree.get_tip_labels(nidx)

    # get subtree below selected edge
    tree1 = tree.treenode._clone()
    tree1.prune(tips)

    # get subtree with sub0 clade removed
    tree2 = tree.treenode._clone()
    tree2.prune([i for i in tree.get_tip_labels() if i not in tips])

    # randomly select a non-root node on sub1
    node = rng.choice(list(tree2.iter_descendants()))

    # randomly select a point on the branch to add new node
    new = toytree.Node(name="spr", dist=rng.uniform(node.dist))
    node.up.children.append(new)
    node.up.children.remove(node)
    node.up = new
    new.children.append(node)
    new.children.append(tree1)
    tree1.up = new

    tree = toytree.core.tree.ToyTree(tree2)
    return tree


if __name__ == "__main__":

    # should be 15 rooted trees.
    TREE = toytree.rtree.unittree(4, seed=123)
    print(TREE)
    NEW = iter_spr_rooted(TREE)
    for i in NEW:
        print(i)
