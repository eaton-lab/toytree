#!/usr/bin/env python

"""Distance-based tree inference.

"""

from typing import Tuple, Iterator, Union, TypeVar
import numpy as np
import pandas as pd
import toytree


Array: TypeVar = Union[np.ndarray, pd.DataFrame]


def infer_neighbor_joining_tree(data: Array) -> toytree.ToyTree:
    """Return a ToyTree inferred by neighbor-joining from a distance matrix.

    Neighbor-joining is a clustering algorithm for building trees from
    a distance matrix. It does not assume a clock, and is guaranteed
    to recover the true tree if the distances reflect the distances
    among samples on the true tree.

    Parameters
    ----------
    data: pd.DataFrame
        A symmetric DataFrame with distances measured between samples.

    Example
    -------
    >>> # example from Felsenstein book
    >>> names = ["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"]
    >>> data = pd.DataFrame(
    >>>     index=names,
    >>>     columns=names,
    >>>     data=np.array([
    >>>         [0, 32, 48, 51, 50, 48, 98, 148],
    >>>         [32, 0, 26, 34, 29, 33, 84, 136],
    >>>         [48, 26, 0, 42, 44, 44, 92, 152],
    >>>         [51, 34, 42, 0, 44, 38, 86, 142],
    >>>         [50, 29, 44, 44, 0, 24, 89, 142],
    >>>         [48, 33, 44, 38, 24, 0, 90, 142],
    >>>         [98, 84, 92, 86, 89, 90, 0, 148],
    >>>         [148, 136, 152, 142, 142, 142, 148, 0],
    >>>     ])
    >>> )
    >>> # run tree inference, root, and draw it.
    >>> tree = infer_neighbor_joining_tree(data)
    >>> tree = tree.mod.root_on_minimal_ancestor_deviation()
    >>> tree.draw(scale_bar=True, node_sizes=5, tip_labels_align=True)
    """
    # store names if provided, else use numeric range
    if hasattr(data, "index"):
        names = data.index
    else:
        names = np.arange(data.shape[0])

    # store a copy of dataframe as an array that will be modified.
    arr = np.array(data).astype(float)

    # dict to store Nodes, starting with tips.
    nodes = {i: toytree.Node(name=i) for i in names}

    # iterate generator function to get next pair of Nodes to join.
    for i, j, v_i, v_j in iter_nj_algorithm(arr):

        # get ordered Node names from the nodes dict.
        names = list(nodes.keys())
        # print(f"{names[i]}\t{names[j]}\t{v_i:.3f}\t{v_j:.3f}")

        # get Nodes with i, j names and pop from dict
        node_i = nodes.pop(names[i])
        node_j = nodes.pop(names[j])

        # create new ancestral Node, store it in nodes, and connect.
        if nodes:
            new_name = f"{node_i.name}-{node_j.name}"
            node_a = toytree.Node(name=new_name)
            nodes[new_name] = node_a

            # connect i and j to it with edge lengths v_i and v_j
            node_i._dist = v_i
            node_j._dist = v_j
            node_a._add_child(node_i)
            node_a._add_child(node_j)

        # connect final pair of Nodes
        else:
            node_i._dist = v_i
            node_j._add_child(node_i)

    # return final ancestor Node as root of a ToyTree
    return toytree.ToyTree(node_j)


def iter_nj_algorithm(arr: Array) -> Iterator[Tuple[int, int, float, float]]:
    """Generator function to yield node indices and branch lengths.

    Each iteration of the neighbor-joining algorithm finds the pair
    of samples with the shortest average distance to all other
    samples. This generator yields the indices (i, j) of the pair given
    an input 2-D distance array, and the branch lengths (v_i, v_j) of
    each of these to their parent node.
    """
    # iterate and reduce matrix until all Nodes are joined
    while 1:

        # get neighbor values (u_i)
        uvals = arr.sum(axis=0) / (arr.shape[0] - 2)

        # get c_arr as d_ij - u_i - u_j
        c_arr = arr - uvals - np.expand_dims(uvals, 1)

        # mask diagonal and get (i,j) index of min off-diagonal value
        mask = np.ones(c_arr.shape, dtype=bool)
        np.fill_diagonal(mask, False)
        idxs, jdxs = np.where(c_arr == c_arr[mask].min())
        i = idxs[0]
        j = jdxs[0]

        # get branch lengths from i,j to new internal Node
        v_i = 0.5 * arr[i, j] + 0.5 * (uvals[i] - uvals[j])
        v_j = 0.5 * arr[i, j] + 0.5 * (uvals[j] - uvals[i])

        # yield the new Node info (i, j, v_i, v_j)
        yield i, j, v_i, v_j

        # update arr to remove i and j and insert ij ancestor dists.
        new_dim = arr.shape[0] - 1
        new_arr = np.zeros(shape=(new_dim, new_dim))
        mask = np.ones(arr.shape[0], dtype=bool)
        mask[[i, j]] = False
        new_arr[:new_dim - 1, :][:, :new_dim - 1] = arr[mask, :][:, mask]
        new_arr[-1, :-1] = new_arr[:-1, -1] = (arr[i] + arr[j] - arr[i, j])[mask] / 2.
        arr = new_arr

        # if new arr size is 2 yield final pair and end.
        if new_dim == 2:
            yield 0, 1, arr[0, 1], arr[0, 1]
            break


if __name__ == "__main__":

    # example from Felsenstein
    names = ["dog", "bear", "raccoon", "weasel", "seal", "sea lion", "cat", "monkey"]
    data = pd.DataFrame(
        index=names,
        columns=names,
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

    # run tree inference and draw it.
    tree = infer_neighbor_joining_tree(data)

    # roots on 'monkey'
    tree = tree.mod.root_on_minimal_ancestor_deviation()

    # plot with .dist values shown
    # DISTS = [f"{i:.2f}" for i in TREE.get_node_data('dist')]
    tree._draw_browser(
        scale_bar=True,
        node_sizes=5,
        tip_labels_align=True,
        tmpdir="~",
        # node_labels="dist",
        # node_labels_style={"anchor-shift": -15, "baseline-shift": -10},
        # node_mask=(0, 1, 1),
    )

    help(infer_neighbor_joining_tree)