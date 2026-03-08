#!/usr/bin/env python

"""Distance-based tree inference."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Iterator

import numpy as np
import pandas as pd

from toytree.utils import ToytreeError

if TYPE_CHECKING:
    from toytree import ToyTree

Array = np.ndarray | pd.DataFrame

__all__ = ["neighbor_joining_tree"]


def _coerce_and_validate_distance_matrix(
    data: Array,
) -> tuple[np.ndarray, list[object]]:  # noqa: E501
    """Coerce and validate input distance matrix and return matrix plus labels."""
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise ToytreeError("distance matrix must be 2-dimensional.")
    if arr.shape[0] != arr.shape[1]:
        raise ToytreeError("distance matrix must be square.")
    if arr.shape[0] < 3:
        raise ToytreeError("neighbor-joining requires at least 3 taxa.")
    if not np.isfinite(arr).all():
        raise ToytreeError("distance matrix must contain only finite values.")
    if np.any(arr < 0):
        raise ToytreeError("distance matrix cannot contain negative distances.")
    if not np.allclose(np.diag(arr), 0.0):
        raise ToytreeError("distance matrix diagonal must be all zeros.")
    if not np.allclose(arr, arr.T):
        raise ToytreeError("distance matrix must be symmetric.")

    if isinstance(data, pd.DataFrame):
        if list(data.index) != list(data.columns):
            raise ToytreeError(
                "DataFrame distance matrix must have identical index/columns."
            )
        labels = list(data.index)
    else:
        labels = list(range(arr.shape[0]))

    return arr, labels


def neighbor_joining_tree(data: Array) -> ToyTree:
    """Return a tree inferred by neighbor-joining from a distance matrix.

    Neighbor-joining (NJ) is a distance-based agglomerative method that does
    not assume a strict molecular clock. This function validates the input
    matrix, applies NJ, and returns an unrooted ``ToyTree``.

    Parameters
    ----------
    data : numpy.ndarray or pandas.DataFrame
        Symmetric distance matrix of shape ``(n, n)``.
        If a DataFrame is provided, index and columns must match.
        Matrices must be finite, non-negative, and have a zero diagonal.
        At least 3 taxa are required.

    Returns
    -------
    ToyTree
        An unrooted tree inferred by neighbor-joining.

    Raises
    ------
    ToytreeError
        If `data` is not a valid distance matrix (non-square, non-symmetric,
        non-finite values, negative distances, non-zero diagonal, fewer than
        three taxa, or mismatched DataFrame index/columns).

    Notes
    -----
    If DataFrame labels are duplicated, labels cannot map uniquely to tips.
    In that case, this function falls back to integer tip names
    ``0..n-1`` and prints a warning to stderr.

    Examples
    --------
    >>> names = [
    ...     "dog", "bear", "raccoon", "weasel",
    ...     "seal", "sea lion", "cat", "monkey",
    ... ]
    >>> data = pd.DataFrame(
    ...     index=names,
    ...     columns=names,
    ...     data=np.array([
    ...         [0, 32, 48, 51, 50, 48, 98, 148],
    ...         [32, 0, 26, 34, 29, 33, 84, 136],
    ...         [48, 26, 0, 42, 44, 44, 92, 152],
    ...         [51, 34, 42, 0, 44, 38, 86, 142],
    ...         [50, 29, 44, 44, 0, 24, 89, 142],
    ...         [48, 33, 44, 38, 24, 0, 90, 142],
    ...         [98, 84, 92, 86, 89, 90, 0, 148],
    ...         [148, 136, 152, 142, 142, 142, 148, 0],
    ...     ]),
    ... )
    >>> tree = neighbor_joining_tree(data)
    >>> tree = tree.mod.root_on_minimal_ancestor_deviation()
    """
    import toytree

    arr, index = _coerce_and_validate_distance_matrix(data)

    # Duplicate labels cannot map cleanly to distinct tips, so fallback to
    # integer labels while preserving deterministic matrix row order.
    if len(index) != len(set(index)):
        print(
            "WARNING: duplicate labels found in distance matrix; "
            "using integer labels for neighbor-joining tree.",
            file=sys.stderr,
        )
        index = list(range(arr.shape[0]))

    # dict to store Nodes, starting with tips.
    nodes = {i: toytree.Node(name=i) for i in index}

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

    # convert treenode to a ToyTree
    tree = toytree.ToyTree(node_j)

    # collapse polytomies (zero-dist) edges
    to_collapse = [i for i in tree[tree.ntips : -1] if i._dist == 0]
    if to_collapse:
        toytree.mod.remove_nodes(tree, *to_collapse, inplace=True)
    return tree


def iter_nj_algorithm(arr: np.ndarray) -> Iterator[tuple[int, int, float, float]]:
    """Yield node indices and branch lengths from neighbor-joining updates.

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
        np.fill_diagonal(c_arr, np.inf)
        i, j = [i[0] for i in np.where(c_arr == c_arr.min())]

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
        new_arr[: new_dim - 1, :][:, : new_dim - 1] = arr[mask, :][:, mask]
        new_arr[-1, :-1] = new_arr[:-1, -1] = (arr[i] + arr[j] - arr[i, j])[mask] / 2.0
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
        data=np.array(
            [
                [0, 32, 48, 51, 50, 48, 98, 148],
                [32, 0, 26, 34, 29, 33, 84, 136],
                [48, 26, 0, 42, 44, 44, 92, 152],
                [51, 34, 42, 0, 44, 38, 86, 142],
                [50, 29, 44, 44, 0, 24, 89, 142],
                [48, 33, 44, 38, 24, 0, 90, 142],
                [98, 84, 92, 86, 89, 90, 0, 148],
                [148, 136, 152, 142, 142, 142, 148, 0],
            ]
        ),
    )

    # run tree inference and draw it.
    tree = neighbor_joining_tree(data)

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

    help(neighbor_joining_tree)
