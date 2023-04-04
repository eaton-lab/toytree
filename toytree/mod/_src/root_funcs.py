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
"""

from typing import TypeVar, Tuple, Dict, Union, List
import itertools
from functools import cache
import numpy as np
from loguru import logger
from toytree.utils import ToytreeError
from toytree.distance import get_node_path, get_node_distance_matrix

ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
Query = TypeVar("Query", str, int, Node)
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
    dmat = tree.distance.get_tip_distance_matrix()

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


def root_on_minimal_ancestor_deviation(
    tree: ToyTree,
    *query: Query,
    inplace: bool = False,
    return_stats: bool = False,
    min_dist: float = 1e-12,
) -> Union[ToyTree, Tuple[ToyTree, Dict[str, float]]]:
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

    Note
    ----
    Returns a ToyTree with MAD and MAD_root_prob features mapped to each
    Node as an edge_feature. These represent the minimum ancestor
    deviations if the tree is rooted on each edge, and the relative
    probability that each is the correct root. If rooting is unknown
    then downstream analysis can integrate over alternative root
    hypotheses in a 'root neighborhood' approach sensu Tria et al 2017).

    Examples
    --------
    >>> tree = toytree.rtree.unittree(4, seed=123).unroot()
    >>> tree.set_node_data('name', dict(zip(range(tree.nnodes), list("abcdCA"))), inplace=True)
    >>> tree.set_node_data('dist', {'b': 1, 'd': 4, 'C': 1}, default=3, inplace=True)
    >>> rtree, stats = root_on_minimal_ancestor_deviation(tree)
    >>> rtree.draw('p', node_sizes=18, node_labels="MAD")
    >>> print(stats)

    Reference
    ---------
    - Tria, F., Landan, G. & Dagan, T. Phylogenetic rooting using
    minimal ancestor deviation. Nat Ecol Evol 1, 0193 (2017).
    https://doi.org/10.1038/s41559-017-0193
    """
    # do not allow polytomies.
    assert tree.is_bifurcating(include_root=False), (
        "tree contains polytomies, first resolve manually or with "
        "`tree.mod.resolve_polytomies()`.")

    # do not allow zero length branches, set to 1e-9 and warn.
    dist_set_to_min = 0
    for node in tree[:-1]:
        if not node._dist:
            node._dist = min_dist
            dist_set_to_min += 1
    if dist_set_to_min:
        logger.warning(
            f"Zero length edges not allowed. Set {dist_set_to_min} edges to dist=1e-9")

    # get matrix of pairwise tip distances on the current tree
    dmat = get_node_distance_matrix(tree)
    npairs = int((tree.ntips * (tree.ntips - 1)) / 2)

    # store paths between pairs of tips
    paths = {}
    for path in itertools.combinations(range(tree.ntips), 2):
        # paths[path] = get_node_path(tree, *path)[1:-1]
        node_path = get_node_path(tree, *path)
        paths[path] = [i.idx for i in node_path]
    # logger.debug(f"paths between tips: {paths}")

    # store rij values
    rij_dict = {}

    # iterate over all possible placements of the root as bipartions/edges
    for seti, setj in tree.iter_bipartitions(feature='idx', include_singleton_partitions=True):

        # get the Node idx of the nodes on either side of this edge
        node_i = tree.get_mrca_node(*seti)
        if node_i.up:
            node_j = node_i.up
        else:
            node_i = tree.get_mrca_node(*setj)
            node_j = node_j.up
            # order seti, setj so that (node_i, node_j) are always sorted by idx
            seti, setj = setj, seti
        idx = node_i.idx
        jdx = node_j.idx
        # logger.debug(f"seti={[tree[i].name for i in seti]}, setj={[tree[i].name for i in setj]}")

        # iterate over tips descended from the two clades split by the new root
        # and calculate rho as the relative position of root node on the edge.
        rho_top = 0
        rho_bot = 0
        for bdx in seti:
            for cdx in setj:
                dbc = dmat[bdx, cdx]
                dbi = dmat[bdx, idx]
                dij = dmat[idx, jdx]
                rho_top += (dbc - (2 * dbi)) * (dbc ** -2)
                rho_bot += (2 * dij) * (dbc ** -2)
                # logger.debug(
                #     f"i={tree[idx].name}, j={tree[jdx].name}, "
                #     f"b={tree[bdx].name}, c={tree[cdx].name}, "
                #     f"dbc={dbc:.1f}, dbi={dbi:.1f}, dij={dij:.1f}"
                # )

        # the relative position of root on edge (i, j)
        rho = rho_top / rho_bot
        rho_i = min(max(0, rho), 1)

        # distance from i or j to ancestor
        dio = dmat[idx, jdx] * rho_i
        djo = dmat[idx, jdx] * (1 - rho_i)
        # logger.debug(
        #     f"root on {tree[idx].name, tree[jdx].name}, "
        #     f"rho=({rho_i:.2f}, dio={dio:.2f}, djo={djo:.2f})"
        # )

        # calculate the rij for this branch as the root-mean-square of
        # the relative deviations over all tip pairs.
        # deviations = np.zeros(npairs)
        iter_pairs = itertools.combinations(range(tree.ntips), 2)
        sum_sq_dev = 0.
        # iterate over all pairs of tips given this rooting
        for pidx, (tidx1, tidx2) in enumerate(iter_pairs):

            # pairwise path distance between these 2 tips
            dij = dmat[tidx1, tidx2]

            # dai and daj: distance from putative ancestor (a) to each tip
            # alpha is the new root for tip pairs in different sets, else
            # it is an internal Node.
            if tidx1 in seti:
                # in diff sets
                if tidx2 in setj:
                    dai = dmat[tidx1, idx] + dio
                    # daj = dmat[tidx2, jdx] + djo
                    # alpha = 'r'
                # both are in seti
                else:
                    # get Node closest to i on path between a, b
                    # dists_to_i = [dmat[i, idx] for i in path]
                    # min_idx = np.argmin(dists_to_i)
                    # aidx = path[min_idx]

                    # path = paths[(tidx1, tidx2)][1:-1]
                    # aidx = min(((i, dmat[j, idx]) for i, j in enumerate(path)), key=lambda x: x[1])[0]
                    # aidx = path[aidx]
                    # aidx
                    # dai = dmat[tidx1, aidx]
                    # logger.info(list(paths.keys()))

                    # set(path).intersection()
                    # path = paths[(tidx1, tidx2)]
                    # anode = _get_ancestor_node(path, idx, dmat)
                    # dai = dmat[tidx1, anode.idx]

                    aidx = max(paths[(tidx1, tidx2)])
                    dai = dmat[tidx1, aidx]

                    # logger.warning(f"{x}, {anode}")

                    # daj = dmat[tidx2, aidx]
                    # alpha = tree[aidx].name
            else:
                # both are in setj
                if tidx2 in setj:
                    # get Node closest to j on path between a, b. This can be
                    # found by the Node idx label on the path closest to jidx.
                    if tidx1 < jdx:
                        # both are below, mrca is max idx
                        if tidx2 < jdx:
                            aidx = max(paths[(tidx1, tidx2)])
                        # tidx1 is below but tidx2 is above, mrca is jdx
                        else:
                            aidx = jdx
                    # both are above, get idx on path closets to jidx
                    else:
                        aidx = min(paths[(tidx1, tidx2)], key=lambda x: jdx - x)
                        aidx = jdx

                    dai = dmat[tidx2, aidx]
                    # logger.warning(f"{tidx1} {tidx2} {idx}-{jdx}| path={[i.idx for i in paths[(tidx1, tidx2)]]} | correct={anode.idx}")

                else:
                    # in diff sets
                    dai = dmat[tidx1, jdx] + djo
                    # daj = dmat[tidx2, idx] + dio
                    # alpha = 'r'

            # measure the relative deviation. Note, zero-length branches
            # will cause a division by zero here.
            r_ij_a = abs(((2 * dai) / dij) - 1)
            # r_ji_a = abs(((2 * daj) / dij) - 1)
            dev = r_ij_a  # + r_ji_a
            sum_sq_dev += dev ** 2
            # logger.debug(
            #     f"tips={tree[tidx1].name, tree[tidx2].name, alpha}    "
            #     f"dij={dij:.1f}    "
            #     f"dai={dai:.1f}    "
            #     f"daj={daj:.1f}    "
            #     f"ria={r_ij_a:.1f}    "
            #     f"rja={r_ji_a:.1f}    "
            #     f"dev={dev:.3f}"
            # )

        rbranch = np.sqrt((sum_sq_dev) / npairs)
        rij_dict[(idx, jdx, rho_i)] = rbranch
        # logger.info(f"rbranch {idx, jdx} {tree[idx].name, tree[jdx].name} = {rbranch:.3f}")

    # summarize
    # for key, val in rij_dict.items():
        # logger.debug(f"{key}: {val:.4f}")

    # root ambiguity index is ratio of best to second best
    edges_sort = sorted(rij_dict, key=lambda x: rij_dict[x])
    root_ambiguity_index = rij_dict[edges_sort[0]] / rij_dict[edges_sort[1]]

    # select node to root the tree on. Choose the optimal MAD edge.
    if not query:
        left, right, rho_i = edges_sort[0]
        root_node = min(left, right)
        logger.info(f"rooting on optimal MAD Node ({root_node}) w/ rho={rho_i:.2f}")
    # or, root on user-selected edge which may not be the optimal
    else:
        root_node = tree.get_mrca_node(*query).idx
        if root_node.is_root():
            raise ToytreeError(f"Cannot root on current root {root_node}, select another Node.")
        for edge in edges_sort:
            if edge[0] == root_node:
                _, _, rho_i = edge
        logger.info(f"rooting on user-selected Node ({root_node}) w/ rho={rho_i:.2f}")

    # set values on nodes
    root_probs = {}
    mads = {}
    summed = sum(1 - i for i in rij_dict.values())
    for edge, value in rij_dict.items():
        left, right, _ = edge
        if left > right:
            node = right
        else:
            node = left
        mads[node] = value
        if value > 1:
            logger.warning(f"Node {node} MAD > 1 ({value}))")
        # logger.debug(f"Node {node} MAD = ({value}) ({left}, {right})")
        root_probs[node] = (1 - value) / summed
    tree.set_node_data("MAD", mads, inplace=True)
    tree.set_node_data("MAD_root_prob", root_probs, inplace=True)

    # print(tree.features)
    # logger.info(f"\n{tree.get_node_data()}")

    # get a tree copy that will be modified by min-dist and 
    tree = tree if inplace else tree.copy()

    # re-root the tree
    tree.root(
        root_node,
        root_dist=tree[root_node]._dist * rho_i,
        edge_features=["MAD", "MAD_root_prob"],
        inplace=True,
    )

    # clock-likeness of inferred root position is described by the root
    # clock coefficient of variation on the new rooted tree. Note the
    # usage of ddof=1 to match the results of Tria et al.
    dmat = tree.distance.get_node_distance_matrix()
    dists = np.array([dmat[i, tree.treenode._idx] for i in range(tree.ntips)])
    root_clock_coefficient_of_variation = 100 * (dists.std(ddof=1) / dists.mean())
    stats = dict(
        minimal_ancestor_deviation=min(rij_dict.values()),
        root_ambiguity_index=root_ambiguity_index,
        root_clock_coefficient_of_variation=root_clock_coefficient_of_variation,
    )
    logger.info(f"stats={stats}")
    if return_stats:
        return tree, stats
    return tree


# @cache
def _get_ancestor_node(path: Tuple[Node], ridx: int, dist_matrix: np.ndarray) -> Node:
    """Return the mrca of two Nodes given a new tree rooting.

    This uses a distance matrix to find the common ancestor of two
    Nodes given a new root Node idx (ridx) is specified. This is used
    in MAD rooting for a speed boost.
    """
    dist = 1e15
    last = None
    for node in path:
        newdist = dist_matrix[node.idx, ridx]
        if newdist > dist:
            # logger.warning(f"---{[i.idx for i in path]} {ridx}")
            return last
        dist = newdist
        last = node
    # logger.warning(f"{[i.idx for i in path]} {ridx}")
    # never got better, first node was best.
    return path[0]


if __name__ == "__main__":

    import toytree
    toytree.set_log_level("INFO")

    # tree = toytree.rtree.unittree(6, seed=123).unroot()
    # tree = toytree.rtree.rtree(5, seed=123).mod.ladderize().unroot()
    # tree.set_node_data('dist', {4: 5, 7: 3}, inplace=True)
    # tree.set_node_data('name', {5: "X", 6: "Y", 7: "Z"}, inplace=True)
    # tree.treenode.draw_ascii()

    # tree = toytree.rtree.rtree(5, seed=123).mod.ladderize().unroot()
    # tree.set_node_data('name', dict(zip(range(tree.nnodes), list("abcdeXYR"))), inplace=True)
    # tree.set_node_data('dist', {'e': 5, 'Y': 3}, inplace=True)
    # tree.treenode.draw_ascii()
    # tree = tree.root("r0")
    # tree.treenode.draw_ascii()
    # print(root_on_midpoint(tree).get_node_data())
    # root_on_midpoint(tree)._draw_browser()

    # tree = toytree.rtree.rtree(10, seed=123).unroot()
    # tree._draw_browser(ts='p', layout='r', node_hover=True)
    # rtree = tree.root(12, root_dist =tree[12]._dist * 0.89)
    # rtree._draw_browser(ts='p', layout='r', node_hover=True)
    tree = toytree.tree("/home/deren/Desktop/KOG0007.faa.aln.nwk").unroot()
    rtree = root_on_minimal_ancestor_deviation(tree)
    # print(stats)
    canvas, *x = toytree.mtree([tree, rtree]).draw(
        # ts='r', layout='r', scale_bar=True, node_labels="name",
        ts='s', height=700,
        node_sizes=18,
        # edge_colors=("MAD", "BlueRed"),
    )
    toytree.utils.show(canvas)
    print(rtree.get_node_data())
    # rtree._draw_browser(ts='s', layout='r')
    # print(rtree.get_node_data())

    # handle root Node (some problem is causing R > 1.)
    # ktree = toytree.tree("/home/deren/Desktop/KOG0007.faa.aln.nwk").unroot()
    # tre = toytree.mod.root_on_minimal_ancestor_deviation(ktree)
    # print(tre.get_node_data())
