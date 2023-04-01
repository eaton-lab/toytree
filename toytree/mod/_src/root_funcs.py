#!/usr/bin/env python

"""Functions for finding/estimating the root of a tree

Methods
-------
- root_on_longest_edge(gene_tree)
- root_on_minimal_ancestor_deviations(...)
- root_on_minimal_duplication_loss_score(species_tree, gene_tree)

References
----------
76
77
78
"""

from typing import Optional
import itertools
import numpy as np
from loguru import logger
from toytree import ToyTree

logger = logger.bind(name="toytree")


def root_on_midpoint(tree: ToyTree, inplace: bool = False) -> ToyTree:
    """Return ToyTree rooted on midpoint of longest edge.

    Rooting on the "midpoint" assumes a clock-like evolutionary rate
    (i.e., branch lengths are equal to time) and may yield odd results
    when this assumption is violated. This algorithm calculates the
    pairwise path length between all tips in an unrooted tree and roots
    on the midpoint of the longest path.

    Parameters
    ----------
    tree: ToyTree
        Tree that will be (re-)rooted.
    inplace: bool
        If True then the input tree object is modified and returned,
        else a copy of the tree is modified and returned.

    References
    ----------
    - Farris, J. S. Estimating phylogenetic trees from distance
    matrices. Am. Nat. 106, 645–668 (1972).

    Example
    -------
    >>> ...
    """
    # get matrix of pairwise tip distances
    dmat = np.array(tree.distance.get_tip_distance_matrix())

    # get a pair of Nodes that span the max distance
    pairs = np.where(dmat == dmat.max())
    n0, n1 = pairs[0][0], pairs[1][0]

    # midpoint is half this distance
    dist_to_new_root = dmat[n0, n1] / 2.

    # going up this dist from one of the two Nodes will hit the
    # pseudo-root, but not for the other. Select the other.
    for idx in [n0, n1]:
        node = tree[idx]
        dist_below = 0.
        while 1:
            # this is the correct edge to root on
            if (node._dist + dist_below) >= dist_to_new_root:
                root_node = node
                root_node_dist = dist_to_new_root - dist_below
                break

            # cannot test any higher, restart from other tip Node.
            if node._up.is_root():
                break

            # check further up from this Node.
            node = node._up
            dist_below += node._dist

    # return tree or copy re-rooted
    tree = tree if inplace else tree.copy()
    return tree.root(root_node.idx, root_dist=root_node_dist)


def root_on_minimal_ancestor_deviations(
    tree: ToyTree,

    assign_rij_values_to_nodes: bool = False,
):
    """Return ToyTree rooted on edge that minimizes ancestor deviations.

    The minimal ancestor deviation (MAD) rooting method attempts to
    accommodate the effect of rate heterogeneity on branch lengths when
    rooting a tree by branch length information. This is done by using
    pairwise topological and metric information in unrooted trees. It
    assumes that branch lengths are additive and that tips (OTUs) are
    contemporaneous in time (i.e., tip height variation results from
    rate heterogeneity). This method evaluates the deviations of the
    global midpoint root position from each pairwise midpoint rooting
    position and minimizes it.

    Parameters
    ----------
    tree: ToyTree
        A tree with branch lengths on which to infer a MAD rooting.
    ...
    assign_rij_values_to_nodes: bool
        If True the returned tree will include a feature 'rij' on every
        Node with a float score of the root-mean-square of its pairwise
        relative deviations (rij). Downstream analysis can treat these
        values as root probabilities and integrate over alternative
        hypotheses (i.e., use a 'root neighborhood' approach sensu
        Tria et al 2017).

    Reference
    ---------
    - Tria, F., Landan, G. & Dagan, T. Phylogenetic rooting using
    minimal ancestor deviation. Nat Ecol Evol 1, 0193 (2017).
    https://doi.org/10.1038/s41559-017-0193
    """
    # do not allow polytomies.
    assert tree.is_bifurcating(), (
        "tree contains polytomies, first resolve manually or with "
        "`tree.mod.resolve_polytomies()`.")

    # get matrix of pairwise tip distances on the current tree
    dmat = np.array(tree.distance.get_node_distance_matrix())

    # iterate over all possible placements of the root
    for ridx in range(tree.nnodes - 1):

        # iterate over pairs of tips
        for tidx1, tidx2 in itertools.combinations(range(tree.ntips), 2):

            # pairwise path distance
            dij = dmat[tidx1, tidx2]

            # expected distance to ancestor under midpoint criterion
            dij_mid = dij / 2.

            # dai and daj: distance from putative ancestor (a) to each tip
            dai = dmat[ridx, tidx1]
            daj = dmat[ridx, tidx2]

            # measure the relative deviation
            r_ija = abs(((2 * dai) / dij_mid) - 1)
            r_jia = abs(((2 * daj) / dij_mid) - 1)

            # root-mean-square of the pairwise relative deviations
            # ...

            # minimization equation to search all positions on a branch
            # ...


    # alpha = ancestor node of a tip-pair induced by a root position.
    # ...

    # deviation between the tip-pair's midpoint and ancestor nodes.
    # ...


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("DEBUG")

    tree = toytree.rtree.unittree(6, seed=123)
    tree = tree.root("r0")
    tree.treenode.draw_ascii()
    print(root_on_midpoint(tree).get_node_data())
    # root_on_midpoint(tree)._draw_browser()
