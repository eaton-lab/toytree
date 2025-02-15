#!/usr/bin/env python

"""Functions for finding/estimating the root of a tree

Methods
-------
- root_on_longest_edge(gene_tree)
- root_on_minimal_ancestor_deviations(...)
- root_on_minimal_duplication_loss_score(species_tree, gene_tree)

References
----------
- Farris, J. S. Estimating phylogenetic trees from distance matrices.
  Am. Nat. 106, 645–668 (1972).
- Tria, F., Landan, G. & Dagan, T. Phylogenetic rooting using
  minimal ancestor deviation. Nat Ecol Evol 1, 0193 (2017).
  https://doi.org/10.1038/s41559-017-0193
- ...
"""

from typing import TypeVar, Dict, Union, Optional, Sequence
import itertools
import numpy as np
from loguru import logger
from toytree import ToyTree, Node
from toytree.core.apis import TreeModAPI, add_subpackage_method
from toytree.utils import ToytreeError

Query = TypeVar("Query", str, int, Node)
logger = logger.bind(name="toytree")


__all__ = [
    "root_on_midpoint",
    "root_on_balanced_midpoint",    
    "root_on_minimal_ancestor_deviation",
]



@add_subpackage_method(TreeModAPI)
def root_on_balanced_midpoint(
    tree: ToyTree,
    inplace: bool = False,
    edge_features: Optional[Sequence[str]] = None,
    tolerance: float = 1e-6,
) -> ToyTree:
    """Return ToyTree rooted on the balanced midpoint.

    Rooting on the "balanced midpoint" assumes a clock-like evol. rate
    (i.e., branch lengths are equal to time) and may yield odd results
    when this assumption is violated. This algorithm minimizes the max
    distance to all other tips. It solves the "tree center" problem.

    Parameters
    ----------
    tree: ToyTree
        Tree that will be (re-)rooted.
    inplace: bool
        If True then the input tree object is modified and returned,
        else a copy of the tree is modified and returned.
    edge_features: Sequence[str]
        One or more Node features that should be treated as a feature
        of its edge, not the Node itself. On rooting, edge features
        are re-polarized, to apply to the correct Node. The 'dist'
        and 'support' features are always treated as edge features.
        Add additional edge features here. See docs for example.
    tolerance: float
        The minimum improvement used as a stopping criterion when
        optimizing the rooting position on the treenode edge.

    Example
    -------
    >>> tree = toytree.rtree.unittree(10).unroot()
    >>> rtree = tree.mod.root_on_balanced_midpoint()
    """
    # get matrix of pairwise node distances
    dmat = tree.distance.get_node_distance_matrix()

    # set dists between internal nodes to zero on an array copy
    nmat = dmat.copy()
    nmat[tree.ntips:, tree.ntips:] = 0.

    # get node idx's with smallest max dist to all other tips
    dists = np.max(dmat, axis=0)
    n0, n1 = dists.argsort()[:2]

    # going up this dist from one of the two Nodes will hit the
    # pseudo-root, but not for the other. Optimize position on other.
    rdists = {i: nmat[i].sum() for i in [n0, n1]}
    rpos = {i: 0 for i in [n0, n1]}
    for idx in [n0, n1]:
        node = tree[idx]
        idxs_d = set([i.idx for i in node.get_leaves()])
        idxs_u = set([i.idx for i in tree[:tree.ntips]]) - idxs_d

        # skip if node is root
        if node.is_root():
            continue

        # optimize position on the branch
        lmin = 0.
        lmax = node._dist
        while 1:

            # get dists to each side from the new position
            pos = lmin + (lmax - lmin) / 2.
            dists_d = nmat[idx][list(idxs_d)] + pos
            dists_u = nmat[idx][list(idxs_u)] - pos

            # minimize the mean dist to each side
            bias = np.max(dists_d) - np.max(dists_u)
            diff = abs(bias) - rdists[idx]

            # end if difference less than tolerance
            if abs(diff) < tolerance:
                break

            # if dist to down is greater, move down.
            if bias < 0:
                lmin = pos
            # if dist to up is greater, move up.
            else:
                lmax = pos
            rpos[idx] = pos
            rdists[idx] = abs(bias)

    # keep node with min dist
    root_node_idx = sorted(rdists, key=lambda x: rdists[x])[0]
    root_node_dist = rpos[root_node_idx]

    # return tree or copy re-rooted
    # tree = tree if inplace else tree.copy()
    tree = tree.root(
        root_node_idx,
        root_dist=root_node_dist,
        edge_features=edge_features,
        inplace=inplace,
    )
    return tree



@add_subpackage_method(TreeModAPI)
def root_on_midpoint(
    tree: ToyTree,
    inplace: bool = False,
    edge_features: Optional[Sequence[str]] = None,
) -> ToyTree:
    """Return ToyTree rooted on midpoint of longest edge.

    Rooting on the "midpoint" assumes a clock-like evolutionary rate
    (i.e., branch lengths are equal to time) and may yield odd results
    when this assumption is violated. This algorithm calculates the
    pairwise path length between all tips in an unrooted tree and roots
    on the midpoint of the longest path.

    Note
    ----
    This method performs less accurately than balanced midpoint rooting
    or minimal ancestor deviation rooting on highly imbalanced trees.

    Parameters
    ----------
    tree: ToyTree
        Tree that will be (re-)rooted.
    inplace: bool
        If True then the input tree object is modified and returned,
        else a copy of the tree is modified and returned.
    edge_features: Sequence[str]
        One or more Node features that should be treated as a feature
        of its edge, not the Node itself. On rooting, edge features
        are re-polarized, to apply to the correct Node. The 'dist'
        and 'support' features are always treated as edge features.
        Add additional edge features here. See docs for example.

    References
    ----------
    - Farris, J. S. Estimating phylogenetic trees from distance
    matrices. Am. Nat. 106, 645–668 (1972).

    Example
    -------
    >>> tree = toytree.rtree.unittree(10).unroot()
    >>> rtree = tree.mod.root_by_midpoint()
    """
    # get matrix of pairwise tip distances
    dmat = tree.distance.get_tip_distance_matrix()

    # get any pair of Nodes that span the max distance
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

            # add blen and check further up from this Node.
            dist_below += node._dist
            node = node._up

    # return tree or copy re-rooted
    # tree = tree if inplace else tree.copy()
    tree = tree.root(
        root_node.idx,
        root_dist=root_node_dist,
        edge_features=edge_features,
        inplace=inplace,
    )
    return tree


@add_subpackage_method(TreeModAPI)
def root_on_minimal_ancestor_deviation(
    tree: ToyTree,
    *query: Query,
    inplace: bool = False,
    return_stats: bool = False,
    min_dist: float = 1e-12,
    edge_features: Optional[Sequence[str]] = None,
) -> Union[ToyTree, Dict[ToyTree, Dict[str, float]]]:
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
    query: int, str or Node
        Optional. Select one or more Nodes by int idx label, str name,
        or Node object to specify a branch on which to root. By default
        this is left empty and the optimal rooting is returned. But if
        you wish to obtain a tree rooted on an alternative edge then
        this will still use the MAD algorithm to minimize ancestral
        deviations to find the optimal node position on that edge.
    inplace: bool
        If True return the input tree modified, else return a modified
        copy of the tree.
    return_stats: bool
        If True the returned value is a (ToyTree, Dict) instead of just
        a ToyTree and the Dict contains the 'root_ambiguity_index' and
        the coefficient of variation in MAD. Note: edge features MAD
        and MAD_root_prob are always set to Nodes of the returned tree.
    min_dist: float
        Zero length edges use a min_dist value of default=1e-12 to
        prevent division by zero errors.
    edge_features: Sequence[str]
        One or more Node features that should be treated as a feature
        of its edge, not the Node itself. On rooting, edge features
        are re-polarized, to apply to the correct Node. The 'dist'
        and 'support' features are always treated as edge features.
        Add additional edge features here. See docs for example.

    Note
    ----
    Returns a ToyTree with MAD and MAD_root_prob features mapped to each
    Node as an edge_feature. These represent the minimum ancestor
    deviations if the tree is rooted on each edge, and the relative
    probability that each is the correct root. If rooting is unknown
    then downstream analysis can integrate over alternative root
    hypotheses weighted by their probability.

    Compared to Tria et al's mad.py script this function yields
    identical results when edges are non-zero, but varies *slightly* in
    how zero-length branches affect results.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(4, seed=123).unroot()
    >>> tree.set_node_data('name', dict(zip(range(tree.nnodes), list("abcdCA"))), inplace=True)
    >>> tree.set_node_data('dist', {'b': 1, 'd': 4, 'C': 1}, default=3, inplace=True)
    >>> rtree, stats = root_on_minimal_ancestor_deviation(tree, return_stats=True)
    >>> rtree.draw('p', node_sizes=18, node_labels="MAD")
    >>> print(stats)

    Reference
    ---------
    - Tria, F., Landan, G. & Dagan, T. Phylogenetic rooting using
    minimal ancestor deviation. Nat Ecol Evol 1, 0193 (2017).
    https://doi.org/10.1038/s41559-017-0193
    """
    # tell user to resolve polytomies.
    assert tree.is_bifurcating(include_root=False), (
        "tree contains polytomies, first resolve manually or with "
        "`tree.mod.resolve_polytomies()`.")

    # get a copy of the tree and translatable query
    if query:
        query = tree.get_mrca_node(*query).get_leaf_names()
    tree = tree.unroot(inplace=inplace)

    # warn user about zero len edges
    zero_len_edges = sum(1 for i in tree[:-1] if i._dist < min_dist)
    if zero_len_edges:
        logger.warning(
            f"Using min_dist {min_dist} for {zero_len_edges} zero len edges in tree.")

    # get pairwise dist matrix w/ min_dist for zero len edges
    dmat = tree.distance.get_node_distance_matrix()
    dmat[dmat < min_dist] = min_dist
    dmat[np.diag_indices_from(dmat)] = 0.

    # store paths between pairs of tips, {(0, 2): [1, 5, 2]... }
    paths = {}
    for path in itertools.combinations(range(tree.ntips), 2):
        node_path = tree.distance.get_node_path(*path)
        paths[path] = [i.idx for i in node_path][1:-1]
        paths[path[::-1]] = paths[path][::-1]

    # get npairs and a dict to store the Rbranch statistics
    npairs = int((tree.ntips * (tree.ntips - 1)) / 2)
    rij_dict = {}

    # iterate over (idx, jdx) edges separating (seti, setj) tip sets.
    inodes = tree.iter_edges()
    ibiparts = tree.enum._iter_bipartition_sets(feature="idx", include_singleton_partitions=True)
    for (node_i, node_j), (seti, setj) in zip(inodes, ibiparts):

        # get .idx label of nodes idx,jdx representing the edge
        idx = node_i._idx
        jdx = node_j._idx
        dij = dmat[idx, jdx]

        # iterate over tips descended from the two clades split by the new root
        # and calculate rho as the relative position of root node on the edge.
        rho_top = 0
        rho_bot = 0
        for tipb in seti:
            for tipc in setj:
                dbc = dmat[tipb, tipc]
                dbi = dmat[tipb, idx]
                rho_top += (dbc - (2 * dbi)) * (dbc ** -2)
                rho_bot += (2 * dij) * (dbc ** -2)

        # the relative position of root on edge (idx, jdx) constrained in [0, 1]
        rho = rho_top / rho_bot
        rho_i = min(max(0, rho), 1)

        # distance from i or j to ancestor
        dio = dmat[idx, jdx] * rho_i
        # logger.debug(f"ij={idx, jdx}, dio={dio:.3g}, rho={rho:.3f} rho_i={rho_i} dij={dmat[idx, jdx]}")

        # get sum sq rel deviation for this rooting over all tip pairs
        relative_deviations = np.zeros(npairs)
        pidx = 0

        # iterate over pairs of tips both in seti
        for tipb, tipc in itertools.combinations(seti, 2):
            dbc = dmat[tipb, tipc]
            aidx = max(paths[(tipb, tipc)])
            dab = dmat[tipb, aidx]
            relative_deviations[pidx] = abs(((2 * dab) / dbc) - 1)
            pidx += 1

        # iterate over pairs of tips both in setj above jdx
        above_j = setj - set(i._idx for i in node_j.iter_descendants())
        for tipb, tipc in itertools.combinations(above_j, 2):
            dbc = dmat[tipb, tipc]
            aidx = min(paths[(tipb, tipc)], key=lambda x: dmat[jdx, x])
            dab = dmat[tipb, aidx]
            relative_deviations[pidx] = abs(((2 * dab) / dbc) - 1)
            pidx += 1

        # iterate over pairs of tips both in setj below jdx
        below_j = setj - above_j
        for tipb, tipc in itertools.combinations(below_j, 2):
            dbc = dmat[tipb, tipc]
            aidx = max(paths[(tipb, tipc)])
            dab = dmat[tipb, aidx]
            relative_deviations[pidx] = abs(((2 * dab) / dbc) - 1)
            pidx += 1

        # iterate over pairs of tips both in setj but split above and below jdx
        for tipb, tipc in itertools.product(below_j, above_j):
            dbc = dmat[tipb, tipc]
            aidx = jdx
            dab = dmat[tipb, aidx]
            relative_deviations[pidx] = abs(((2 * dab) / dbc) - 1)
            pidx += 1

        # iterate over pairs spanning the root (idx, jdx) split
        for tipb, tipc in itertools.product(seti, setj):
            dbc = dmat[tipb, tipc]
            aidx = idx
            dab = dmat[tipb, aidx] + dio
            relative_deviations[pidx] = abs(((2 * dab) / dbc) - 1)
            pidx += 1

        # make sum-squares into root-mean-square and save to rij_dict
        rbranch = np.sqrt(np.mean(relative_deviations ** 2))

        # warn user if rbranch exceeds 1.
        if rbranch > 1:
            constrained_rbranch = min(max(0, rbranch), 1)
            logger.warning(f"edge {idx, jdx} MAD={rbranch:.2f} outlier constrained to {constrained_rbranch:.0f}))")
            rbranch = constrained_rbranch
        # logger.info(f"edge {idx, jdx} rho={rho_i:.3f} R={rbranch:.4f}")
        rij_dict[(idx, jdx, rho_i)] = rbranch

    # root ambiguity index is ratio of best to second best
    r_sorted = sorted(rij_dict, key=lambda x: rij_dict[x])
    root_ambiguity_index = rij_dict[r_sorted[0]] / rij_dict[r_sorted[1]]

    # warn user if equally likely rootings
    if root_ambiguity_index == 1:
        logger.warning(
            ">1 optimal rootings exist. Check the 'MAD' and 'MAD_root_prob' "
            "features on the returned tree to examine alternative rootings.")

    # select node to root the tree on. Choose the optimal MAD edge.
    if not query:
        ridx, uidx, rho_i = r_sorted[0]
        logger.info(f"rooting on MAD edge {ridx, uidx} w/ optimized rho={rho_i:.2f}")

    # or, root on user-selected edge which may not be the optimal
    else:
        root_node = tree.get_mrca_node(*query)
        if root_node.is_root():
            raise ToytreeError(f"Cannot root on current root {root_node}, select another Node.")
        ridx = root_node._idx

        # find the rho value for this edge rooting
        for edge in r_sorted:
            if edge[0] == ridx:
                _, _, rho_i = edge
        logger.info(f"rooting on user-selected edge {ridx, root_node._up._idx} w/ optimized rho={rho_i:.2f}")

    # set values to Nodes
    root_probs = {}
    mads = {}
    summed = sum(1 - i for i in rij_dict.values())
    for edge, value in rij_dict.items():
        nidx, _, _ = edge
        mads[nidx] = value
        root_probs[nidx] = (1 - value) / summed
    tree.set_node_data("MAD", mads, inplace=True)
    tree.set_node_data("MAD_root_prob", root_probs, inplace=True)

    # add these features as edge features
    tree.edge_features = tree.edge_features | {"MAD", "MAD_root_prob"}

    # root the tree
    tree.root(
        ridx,
        root_dist=tree[ridx]._dist * rho_i,
        edge_features=edge_features,
        inplace=True,
    )

    # clock-likeness of inferred root position is described by the root
    # clock coefficient of variation on the new rooted tree. Note the
    # usage of ddof=1 to match the results of Tria et al.
    dmat = tree.distance.get_node_distance_matrix()
    dists = np.array([dmat[i, tree.treenode._idx] for i in range(tree.ntips)])
    root_clock_coefficient_of_variation = 100 * (dists.std(ddof=1) / dists.mean())
    stats = dict(
        minimal_ancestor_deviation=rij_dict[r_sorted[0]],
        root_ambiguity_index=root_ambiguity_index,
        root_clock_coefficient_of_variation=root_clock_coefficient_of_variation,
    )
    logger.info(f"stats={stats}")
    if return_stats:
        return tree, stats
    return tree


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("INFO")
    import numpy as np

    # tree = toytree.rtree.rtree(6, seed=123).unroot()
    tree = toytree.rtree.bdtree(6, seed=123).root("r1")
    # tree[5]._dist = 3.
    # tree = toytree.rtree.rtree(5, seed=123).mod.ladderize()#.unroot()
    # tree.set_node_data('dist', {4: 5, 7: 3}, inplace=True)
    # tree.set_node_data('name', {5: "X", 6: "Y", 7: "Z"}, inplace=True)
    # tree.treenode.draw_ascii()
    # tree.write("/tmp/test.tree")
    c1, _, _ = tree.draw()
    c2, _, _ = tree.mod.root_on_midpoint().draw()
    c3, _, _ = root_on_balanced_midpoint(tree).draw()    
    toytree.utils.show([c1, c2, c3], tmpdir="~")


    # test1 rtree 5-tips variable edgelens
    # tree = toytree.rtree.rtree(5, seed=123).unroot()
    # tree.set_node_data('name', {i: j for (i, j) in enumerate("abcdeXYR")}, inplace=True)
    # tree.set_node_data('dist', {'e': 5, 'Y': 3}, inplace=True)
    # tree.write("/tmp/test1.tree")
    # c1, a, m = tree.draw(ts='p', layout='r', node_hover=True)
    # rtree, stats = root_on_minimal_ancestor_deviation(tree, return_stats=True)
    # c2, a, m = rtree.draw(ts='p', layout='r', node_hover=True)
    # print(stats)
    # print(rtree.get_node_data())
    # toytree.utils.show([c1, c2])

    # test1 alt-rooting rtree 5-tips variable edgelens
    # tree = toytree.rtree.rtree(5, seed=123).unroot()
    # tree.set_node_data('name', {i: j for (i, j) in enumerate("abcdeXYR")}, inplace=True)
    # tree.set_node_data('dist', {'e': 5, 'Y': 3}, inplace=True)
    # tree.write("/tmp/test1.tree")
    # c1, a, m = tree.draw(ts='p', layout='r', node_hover=True)
    # rtree, stats = root_on_minimal_ancestor_deviation(tree, 'a', return_stats=True)
    # c2, a, m = rtree.draw(ts='p', layout='r', node_hover=True)
    # print(stats)
    # print(rtree.get_node_data())
    # toytree.utils.show([c1, c2])

    # test2
    # tree = toytree.rtree.rtree(5, seed=123).unroot()
    # tree.set_node_data('name', {i: j for (i, j) in enumerate("abcdeXYR")}, inplace=True)
    # tree.set_node_data('dist', {'e': 5, 'Y': 3, 'X': 10}, inplace=True)
    # tree.write("/tmp/test2.tree")
    # c1, a, m = tree.draw(ts='p', layout='r', node_hover=True)
    # rtree, stats = root_on_minimal_ancestor_deviation(tree, return_stats=True)
    # c2, a, m = rtree.draw(ts='p', layout='r', node_hover=True)
    # print(stats)
    # print(rtree.get_node_data())
    # toytree.utils.show([c1, c2])

    # test w/ polytomies
    # tree = toytree.rtree.rtree(10, seed=123).unroot()
    # tree.mod.collapse_nodes(1, 2, 12, 15, inplace=True)
    # tree.set_node_data('dist', {2: 5, 12: 3, 13: 10}, inplace=True)
    # tree.write("/tmp/test3.tree")
    # c1, a, m = tree.draw(ts='p', layout='r', node_hover=True)

    # tree = tree.mod.resolve_polytomies()
    # rtree, stats = root_on_minimal_ancestor_deviation(tree, return_stats=True)
    # c2, a, m = rtree.draw(ts='p', layout='r', node_hover=True)
    # print(stats)
    # print(rtree.get_node_data())
    # toytree.utils.show([c1, c2])
