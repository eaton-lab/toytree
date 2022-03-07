#!/usr/bin/env python

"""Tree moves used in heuristic tree search algorithms.

Tree 'moves' (perturbations) are used to search tree space and 
usually applied with an optimality criterion to find a best scoring
tree under either parsimony or maximum likelihood hill-climbing 
algorithms.

UNDER DEVELOPMENT
-----------------
- Moves in tree space (SPR, TBR, NNI).
- rooted tree moves need to iterate over placements of the root?
- unrooted tree moves ...

See also eSPR and eTBR moves used in Bayesian phylogenetics. These
modify the probability of proposed pruning points by updating a
'distance' parameter as part of the MCMC process. For example in
mrbayes. Not implemented here.
"""

from typing import Optional, TypeVar, Iterator
from loguru import logger
import numpy as np
import toytree
from toytree.utils import ToytreeError


logger = logger.bind(name="toytree")
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
    tree: ToyTree
        The tree to be modified by a tree move.
    seed: int or None
        Seed for numpy random number generator.
    inplace: bool
        If True the tree is modified in place, else a copy is returned.
    highlight: bool
        If True the .style dict of the returned ToyTree will be
        modified to show the edges that were involved in the tree
        move if drawn without a tree_style argument.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=8, seed=123)
    >>> new_tree = toytree.mod.move_nni(tree, highlight=True)
    >>> tree.draw();
    >>> new_tree.draw();
    """
    tree = tree if inplace else tree.copy()
    rng = np.random.default_rng(seed)

    # randomly select a subtree (any non-root Node)
    sidx = rng.choice(tree.nnodes - 1)
    subtree = tree[sidx]

    # get list of Nodes (edges) where subtree can be inserted. This
    # cannot be root, or a desc on the subtree Node, or the subtree itself.
    edges = (
        set(range(tree.nnodes)) -
        set((i._idx for i in subtree._iter_descendants())) -
        set((i._idx for i in subtree._iter_sisters())) -
        set((subtree._up._idx, )) -
        set((subtree._idx, ))
    )

    # sample an edge by its descendant Node
    new_sister = tree[rng.choice(list(edges))]
    # logger.info(f"SPR: {sidx} -> {new_sister.idx}; options={edges}")

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

    # if old root is now a singleton b/c new_sister is one of its children
    if len(tree.treenode.children) == 1:
        tree.treenode = tree.treenode.children[0]
        oldroot = tree.treenode._up
        tree.treenode._up = None
        del oldroot

    # if new_sister is now the root.
    elif new_sister == tree.treenode:
        tree.treenode = new_node
    tree._update()

    # optional: color edges of the subtree that was moved.
    if highlight:
        tree.style.edge_colors = ['black'] * tree.nnodes
        tree.style.node_colors = ['white'] * tree.nnodes
        tree.style.node_style.stroke_width = 1.5
        tree.style.node_sizes = 8
        tree.style.node_labels = "idx"
        tree.style.node_labels_style.font_size = 12
        tree.style.node_labels_style._toyplot_anchor_shift = -9
        tree.style.node_labels_style.baseline_shift = 7.5
        tree.style.use_edge_lengths = False

        # tree.get_mrca_node(*tips)
        for node in subtree._iter_descendants():
            tree.style.edge_colors[node.idx] = toytree.color.COLORS2[3]
            tree.style.node_colors[node.idx] = toytree.color.COLORS2[3]
        tree.style.node_colors[new_node.idx] = toytree.color.COLORS2[3]
    return tree


def move_nni(
    tree: ToyTree,
    idx1: Optional[int]=None,
    idx2: Optional[int]=None,    
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
    tree: ToyTree
        The tree to be modified by a tree move.
    idx1: int or None
        Node index of the first clade to be swapped with another. If
        None then it is randomly sampled.
    idx2: int or None
        Node index of the second clade to be swapped with another. If
        None then it is randomly sampled given limitations of idx1.
    seed: int or None
        Seed for numpy random number generator.
    inplace: bool
        If True the tree is modified in place, else a copy is returned.
    highlight: bool
        If True the .style dict of the returned ToyTree will be
        modified to show the edges that were involved in the tree
        move if drawn without a tree_style argument.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=8, seed=123)
    >>> new_tree = toytree.mod.move_nni(tree, highlight=True)
    >>> tree.draw();
    >>> new_tree.draw();
    """
    tree = tree if inplace else tree.copy()
    rng = np.random.default_rng(seed)

    # randomly select a subtree (any non-root Node)
    if idx1 is None:
        idx1 = rng.choice(tree.nnodes - 1)
    node1 = tree[idx1]

    # get list of Nodes (edges) where subtree can be inserted. This
    # cannot be root, or a desc on the subtree Node, or the subtree itself.
    edges = (
        set(range(tree.nnodes - 1)) -
        set((i._idx for i in node1._iter_descendants())) -
        set((i._idx for i in node1._iter_sisters())) -
        set((i._idx for i in node1._iter_ancestors())) -
        set((node1._idx, ))
    )

    # sample an edge by its descendant Node
    if idx2 is None:
        idx2 = rng.choice(list(edges))
    node2 = tree[idx2]

    # raise error if user-entered pair is invalid
    if idx2 not in edges:
        raise ToytreeError(
            f"invalid NNI move: idx2 not within valid pairs from idx1: {edges}")

    # debugging
    logger.info(f"NNI: {idx1} -> {idx2}; options={edges}")

    # re-attach nodes and update
    parent_1 = node1._up.idx
    parent_2 = node2._up.idx
    tree[parent_1]._remove_child(tree[node1.idx])
    tree[parent_2]._remove_child(tree[node2.idx])
    tree[parent_1]._add_child(tree[node2.idx])
    tree[parent_2]._add_child(tree[node1.idx])
    tree._update()

    # optional: color edges of the subtree that was moved.
    if highlight:
        tree.style.edge_colors = ['black'] * tree.nnodes
        tree.style.node_colors = ['white'] * tree.nnodes
        tree.style.node_style.stroke_width = 1.5
        tree.style.node_sizes = 8
        tree.style.node_labels = "idx"
        tree.style.node_labels_style.font_size = 12
        tree.style.node_labels_style._toyplot_anchor_shift = -9
        tree.style.node_labels_style.baseline_shift = 7.5
        tree.style.use_edge_lengths = False

        # tree.get_mrca_node(*tips)
        tree.style.node_colors[node1.idx] = toytree.color.COLORS2[0]
        for node in node1._iter_descendants():
            tree.style.edge_colors[node.idx] = toytree.color.COLORS2[0]
            tree.style.node_colors[node.idx] = toytree.color.COLORS2[0]
        tree.style.node_colors[node2.idx] = toytree.color.COLORS2[3]
        for node in node2._iter_descendants():
            tree.style.edge_colors[node.idx] = toytree.color.COLORS2[3]
            tree.style.node_colors[node.idx] = toytree.color.COLORS2[3]
    return tree


def move_nni_generator(
    tree: ToyTree,
    seed: Optional[int]=None,
    highlight: bool=False,
    ) -> Iterator[ToyTree]:
    """Return an infinite generator over sequential NNI moves.
    
    Parameters
    ----------
    ...

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10, seed=123)
    >>> nni_gen = toytree.mod.move_nni_generator(tree)
    >>> niters = 0
    >>> score = np.inf
    >>> while niters < 1000:
    >>>     test_tree = next(nni_gen)
    >>>     test_score = next(nni_gen).draw();
    >>>     if test_score < score:
    >>>         score = test_score
    >>>         best_tree = test_tree
    >>>     niters += 1
    >>> best_tree.draw()
    """
    rng = np.random.default_rng(seed)
    while 1:
        tree = move_nni(tree, seed=rng.integers(2**32), highlight=highlight)
        yield tree


if __name__ == "__main__":

    # should be 15 rooted trees.
    toytree.set_log_level("INFO")
    TREE = toytree.rtree.unittree(15, seed=123)
    MTREE = move_nni(TREE, highlight=True)

    c0, _, _ = TREE.draw('s')
    c1, _, _ = MTREE.draw()
    toytree.utils.show([c0, c1], new=False)
