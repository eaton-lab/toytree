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
from loguru import logger
import numpy as np
import toytree


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


def one_nni(tree, 
        seed=None, 
        highlight=False, 
        force=(-1, -1),
        quiet=True,
       ) -> ToyTree:
    """Perfoms only ONE random swaping of two random subclades in a given tree
    
    
    Parameters
    ----------
    ...

    """
    
    # work in a copy of the tree
    tree = tree.copy()
    
    # for this version use only unrooted tree
    tree = tree.unroot()
    
    # create the random generator
    rng = np.random.default_rng(seed)
    
    
    # randomly select first subtree (any non-root Node)
    f_idx = rng.choice(tree.nnodes - 1)  
    if force[0] >= 0: f_idx = force[0] #overwrite random selection
    
    subtree_a = tree[f_idx]  

    
    # Check available nodes to select second subtree
    # It should follow the following statements
    available_nodes = (
        set(range(tree.nnodes - 1)) # set with all possible nodes but the root
        - set((i._idx for i in subtree_a._iter_descendants())) # remove descendants of subtree
        - set((i._idx for i in subtree_a._iter_sisters())) # remove sisters of subtree (to avoid uninformative interchange)
        - set((subtree_a._up._idx, )) # remove  parental of subtree (to avoid pick a subtree with subtree_a in there)
        - set((subtree_a._idx, )) # remove subtree node itself
    )
    
    
    
    # If the random subtree is very basal, no other options are available to swap subtrees
    if not available_nodes:
        if not quiet: print(f"No possible interchange if {subtree_a!r} is selected")
        return None
    else:
        if not quiet: print(f"Possible interchanges for {subtree_a!r} are: {available_nodes}")
    
    
    
    # randomly select second subtree to interchange
    s_idx = rng.choice(list(available_nodes))  # commented, I changed the code to h
    if force[1] >= 0: s_idx = force[1] #overwrite random selection

    subtree_b = tree[s_idx]


    if not quiet: print(f"Interchanging {subtree_a!r} with {subtree_b!r}")


    # set in memory the idx of both parents (parent of a = 1 and parent of b = 2)
    parent_1 = subtree_a._up.idx
    parent_2 = subtree_b._up.idx
    
    # remove swaping subtrees from the tree
    tree[parent_1]._remove_child(tree[subtree_a.idx])
    tree[parent_2]._remove_child(tree[subtree_b.idx])
    
    # add the subtrees in the new parents (a to 2 and b to 1)
    tree[parent_1]._add_child(tree[subtree_b.idx])
    tree[parent_2]._add_child(tree[subtree_a.idx])

    # call toytree update routine
    tree._update()


    # show subtrees swapped 
    if highlight:
        tree.style.edge_colors = ['black'] * tree.nnodes
        tree.style.node_colors = ['white'] * tree.nnodes
        tree.style.node_style.stroke_width = 1.5
        tree.style.node_sizes = 15
        tree.style.node_labels = "idx"
        tree.style.node_labels_style.font_size = 8
#         tree.style.node_labels_style._toyplot_anchor_shift = -12
#         tree.style.node_labels_style.baseline_shift = 9
        tree.style.tip_labels_style._toyplot_anchor_shift = -12
        tree.style.tip_labels_style.baseline_shift = 9



        for it, subtree in enumerate([subtree_a, subtree_b]):
            for node in subtree._iter_descendants():
                if node:
                    tree.style.edge_colors[node.idx] = toytree.color.COLORS2[it]
                    tree.style.node_colors[node.idx] = toytree.color.COLORS2[it]

    # remove lenghts
    tree.style.use_edge_lengths = False
        
    
    return tree


def get_all_neighbors_nni(tree,
                         node=None,
                         highlight=False, 
                         seed=None,
                         quiet=True,
                         ):
    """Given a tree performs multiple NNI to get all the neighbors
    given a node. If not is not provided, it is selected randomly.
    
    Parameters
    ----------
    ...

    """
    
    tree = tree.copy()
    tree = tree.unroot()
    
    if not quiet: print(f"There are {2 * (tree.ntips - 3)} expected nearest neighbors for the given tree")
    
    rng = np.random.default_rng(seed)
    
    
    # randomly select first subtree (any non-root Node)
    if node == None:
        f_idx = rng.choice(tree.nnodes - 1)  
    else:
        f_idx = node #use node specified by user
    
    subtree_a = tree[f_idx]
       
      
    # Check available nodes to select second subtree
    # It should follow the following statements
    available_nodes = (
        set(range(tree.nnodes - 1)) # set with all possible nodes but the root
        - set((i._idx for i in subtree_a._iter_descendants())) # remove descendants of subtree
        - set((i._idx for i in subtree_a._iter_sisters())) # remove sisters of subtree (to avoid uninformative interchange)
        - set((subtree_a._up._idx, )) # remove  parental of subtree (to avoid pick a subtree with subtree_a in there)
        - set((subtree_a._idx, )) # remove subtree node itself
    )
    
    neighbor_trees = []
    for available_node in available_nodes:
        neighbor_trees.append(one_nni(tree, force=(f_idx, available_node), highlight=highlight, quiet=True, seed=seed))
       
    return neighbor_trees


if __name__ == "__main__":

    # should be 15 rooted trees.
    toytree.set_log_level("INFO")
    TREE = toytree.rtree.unittree(5, seed=123)
    MTREE = move_nni(TREE, highlight=True)

    c0, _, _ = TREE.draw('s')
    c1, _, _ = MTREE.draw()
    toytree.utils.show([c0, c1], new=False)
