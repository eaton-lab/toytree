#!/usr/bin/env python

"""Infer a tree from a distance matrix using UPGMA clustering.

"""

import sys
import numpy as np
import pandas as pd
import toytree


__all__ = ["upgma_tree"]


def upgma_tree(data: pd.DataFrame | np.ndarray) -> toytree.ToyTree:
    """Return a ToyTree inferred by UPGMA from a distance matrix.

    Unweighted Pair Group Method with Arithmetic Mean (UPGMA) is a
    hierarchical clustering algorithm used for inferring phylogenetic
    trees from a distance matrix. It assumes a molecular clock (i.e.,
    all lineages evolve at a constant rate) and constructs an
    ultrametric tree where all leaves are equidistant from the root.

    Parameters
    ----------
    data: pd.DataFrame | np.ndarray
        An input dataframe or array representing a symmetric distance
        matrix. If no labels are provided (e.g., array) then tips are
        named by their row index.

    Examples
    --------
    >>> # random tree -> dist matrix -> UPGMA tree
    >>> tree = toytree.rtree.unittree(ntips=8, seed=123)
    >>> dist = tree.distance.get_tip_distance_matrix()
    >>> ntree = toytree.infer.upgma_tree(dist)
    """
    # convert data to an array for faster processing.
    arr = np.array(data, dtype=float)

    # get names index from df or arr, do not allow replicate names
    index = data.index if isinstance(data, pd.DataFrame) else range(data.shape[0])
    if len(index) != len(set(index)):
        print("identical names found in data, using int indices for upgma tree", file=sys.stderr)
        index = range(data.shape[0])

    # store tip Nodes, and add ntips attribute.
    nodes = {}
    for name in index:
        node = toytree.Node(name=name, dist=0)
        node._ntips = 1
        nodes[name] = node

    # loop to cluster and reduce matrix until only 1 sample left.
    while arr.shape[0] > 1:

        # get ordered names from nodes dict
        names = list(nodes.keys())

        # get index (i,j) of min_dist on off-diagonal (selects first one if tied)
        np.fill_diagonal(arr, np.inf)
        min_dist = np.min(arr)
        idxs = [i[0] for i in np.where(arr == min_dist)]

        # create new interior Node
        new_name = f"i-{arr.shape[0]}"
        inode = toytree.Node(name=new_name, dist=0)
        nodes[new_name] = inode

        # connect i,j to new Node with equal branch lengths
        for idx in idxs:
            name = names[idx]
            node = nodes[name]
            node._dist = (min_dist / 2) - node._height
            inode._add_child(node)

        # set height of new Node to be used by its parent to find dist.
        inode._height = node._height + node._dist

        # count n leaves descended from new Node
        inode._ntips = sum(i._ntips for i in inode._children)

        # update the distance matrix to remove i,j and add new Node.
        new_dim = arr.shape[0] - 1
        new_arr = np.zeros(shape=(new_dim, new_dim))

        # index of rows to keep
        nidxs = [i for i in range(arr.shape[0]) if i not in idxs]

        # fill kept rows into the new_arr
        new_arr[:new_dim - 1, :][:, :new_dim - 1] = arr[nidxs, :][:, nidxs]

        # remove i,j from nodes, and get ntips of each.
        nti = nodes.pop(names[idxs[0]])._ntips
        ntj = nodes.pop(names[idxs[1]])._ntips

        # get avg distance of new Node to every other Node.
        diks = arr[idxs[0], nidxs]
        djks = arr[idxs[1], nidxs]
        wdiks = (nti / (nti + ntj)) * diks
        wdjks = (ntj / (nti + ntj)) * djks
        avg_dists = wdiks + wdjks
        new_arr[-1, :-1] = avg_dists
        new_arr[:-1, -1] = avg_dists

        # advance internal node name counter
        arr = new_arr

    # convert treenode to a ToyTree
    tree = toytree.ToyTree(nodes[new_name])

    # collapse polytomies (zero-dist) edges
    to_collapse = [i for i in tree[tree.ntips:-1] if i._dist == 0]
    if to_collapse:
        toytree.mod.remove_nodes(tree, *to_collapse, inplace=True)
    return tree


if __name__ == "__main__":

    # example from Felsenstein
    # DATA = pd.DataFrame(
    #     index=["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"],
    #     columns=["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"],
    #     data=np.array([
    #         [0, 32, 48, 51, 50, 48, 98, 148],
    #         [32, 0, 26, 34, 29, 33, 84, 136],
    #         [48, 26, 0, 42, 44, 44, 92, 152],
    #         [51, 34, 42, 0, 44, 38, 86, 142],
    #         [50, 29, 44, 44, 0, 24, 89, 142],
    #         [48, 33, 44, 38, 24, 0, 90, 142],
    #         [98, 84, 92, 86, 89, 90, 0, 148],
    #         [148, 136, 152, 142, 142, 142, 148, 0],
    #     ])
    # )

    # # show the distance matrix
    # # print(DATA)
    # TREE = infer_upgma_tree(DATA)
    # DIST = [f"{i:.2f}" for i in TREE.get_node_data('dist')]
    # TREE._draw_browser(
    #     ts='n',
    #     scale_bar=True,
    #     node_labels=DIST,
    #     node_sizes=15,
    #     node_mask=False,
    #     node_markers="r2x1",
    #     width=400, height=400,
    #     tip_labels_style={"anchor-shift": 20,},
    #     tmpdir="~",
    # )

    # toytree.set_log_level("DEBUG")

    DATA = pd.DataFrame(
        index=list("abcde"),
        columns=list("abcde"),
        data=np.array([
            [0.0, 2.0, 2.0, 3.0, 3.0],
            [2.0, 0.0, 0.5, 3.0, 3.0],
            [2.0, 0.5, 0.0, 3.0, 3.0],
            [3.0, 3.0, 3.0, 0.0, 0.0],
            [3.0, 3.0, 3.0, 0.0, 0.0],
        ])
    )

    TREE = upgma_tree(DATA)
    DIST = [f"{i:.2f}" for i in TREE.get_node_data('dist')]
    TREE._draw_browser(
        ts='n',
        scale_bar=True,
        # node_labels=DIST,
        node_labels="name",
        node_sizes=15,
        node_mask=False,
        node_markers="r2x1",
        width=400, height=400,
        tip_labels_style={"anchor-shift": 20,},
        tmpdir="~",
    )