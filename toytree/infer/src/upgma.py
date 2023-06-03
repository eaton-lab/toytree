#!/usr/bin/env python

"""Infer a tree from a distance matrix using UPGMA clustering.

"""

import numpy as np
import pandas as pd
import toytree


def infer_upgma_tree(data: pd.DataFrame) -> toytree.ToyTree:
    """Return a ToyTree inferred by UPGMA from a distance matrix.

    Parameters
    ----------
    ...

    Examples
    --------
    >>> ...
    """
    # convert data to an array for faster processing.
    arr = np.array(data, dtype=float)

    # store tip Nodes, and add ntips attribute.
    nodes = {}
    for name in data.index:
        node = toytree.Node(name=name, dist=0)
        node._ntips = 1
        nodes[name] = node

    # loop to cluster and reduce matrix until only 1 sample left.
    while arr.shape[0] > 1:

        # get ordered names from nodes dict
        names = list(nodes.keys())

        # get index (i,j) of minvalue on off-diagonal.
        mask = np.ones(arr.shape, dtype=bool)
        np.fill_diagonal(mask, False)
        min_value = arr[mask].min()
        idxs = np.where(arr == min_value)[0]

        # create a new interior Node as ancestor of (i,j)
        new_name = f"internal-{arr.shape[0]}"
        new_node = toytree.Node(name=new_name, dist=0)
        nodes[new_name] = new_node

        # connect i,j to new Node with equal branch lengths
        for idx in idxs:
            name = names[idx]
            node = nodes[name]
            node._dist = (min_value / 2) - node._height
            new_node._add_child(node)

        # set height of new Node to be used by its parent to find dist.
        new_node._height = node._height + node._dist

        # count n leaves descended from new Node
        new_node._ntips = sum(i._ntips for i in new_node._children)

        # update the distance matrix to remove i,j and add new Node.
        new_dim = arr.shape[0] - 1
        new_arr = np.zeros(shape=(new_dim, new_dim))

        # index of rows to keep
        nidxs = [i for i in range(arr.shape[0]) if i not in idxs]

        # # fill kept rows into the new_arr
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

    # return the top-level Node as a ToyTree
    return toytree.ToyTree(nodes[new_name])


if __name__ == "__main__":

    # example from Felsenstein
    DATA = pd.DataFrame(
        index=["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"],
        columns=["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"],
        data=np.array([
            [0, 32, 48, 51, 50, 48, 98, 148],
            [32, 0, 26, 34, 29, 33, 84, 136],
            [48, 26, 0, 42, 44, 44, 92, 152],
            [51, 34, 42, 0, 44, 38, 86, 142],
            [50, 29, 44, 44, 0, 24, 89, 142],
            [48, 33, 44, 38, 24, 0, 90, 142],
            [98, 84, 92, 86, 89, 90, 0, 148],
            [148, 136, 152, 142, 142, 142, 148, 0],
        ])
    )

    # show the distance matrix
    # print(DATA)
    TREE = infer_upgma_tree(DATA)
    DIST = [f"{i:.2f}" for i in TREE.get_node_data('dist')]
    TREE._draw_browser(
        ts='n',
        scale_bar=True, 
        node_labels=DIST,
        node_sizes=15, 
        node_mask=False,
        node_markers="r2x1",
        width=400, height=400,
        tip_labels_style={"-toyplot-anchor-shift": 20, }
    )
