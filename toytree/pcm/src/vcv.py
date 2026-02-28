#!/usr/bin/env python

"""Conversion of phylogeny to and from variance-covariance matrix.

TODO
-----
1. Allow other correlation structures besides Brownian motion.
2. Estimate covariance structure using statsmodels.

References
----------
- Garland, T. Jr. and Ives, A. R. (2000) Using the past to predict the
  present: confidence intervals for regression equations in phylogenetic
  comparative methods. American Naturalist, 155, 346-364.

"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Union

import numpy as np
import pandas as pd

from toytree.core.apis import PhyloCompAPI, add_subpackage_method

if TYPE_CHECKING:
    from toytree.core import ToyTree


__all__ = [
    "get_vcv_matrix_from_tree",
    "get_corr_matrix_from_tree",
    "get_distance_matrix_from_vcv_matrix",
    "get_tree_from_vcv_matrix",
]

# # Fit GLS model without fixing the covariance structure (let it estimate)
# gls_model_est = sm.GLS(y, X).fit()
# print(gls_model_est.summary())


@add_subpackage_method(PhyloCompAPI)
def get_vcv_matrix_from_tree(
    tree: ToyTree,
    df: bool = False,
) -> Union[np.ndarray, pd.DataFrame]:
    """Return the Brownian-motion variance-covariance matrix for tree tips.

    The returned matrix is ``(ntips, ntips)`` and describes the expected
    covariance structure among tip values under Brownian motion on the input
    tree. Off-diagonal entries are the shared path length from the root to the
    MRCA of each tip pair, and diagonal entries are root-to-tip path lengths.

    Parameters
    ----------
    tree : ToyTree
        Tree with edge lengths.
    df : bool, default=False
        If ``True``, return a labeled ``pandas.DataFrame`` with tip labels as
        both index and columns. If ``False``, return a ``numpy.ndarray``.

    Returns
    -------
    numpy.ndarray or pandas.DataFrame
        Tip-by-tip variance-covariance matrix in tree tip order. If ``df=True``,
        row and column labels are ``tree.get_tip_labels()``.

    Raises
    ------
    Exception
        Propagated from tree methods if the tree structure or edge lengths are
        invalid for distance calculations.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> vcv = tree.pcm.get_vcv_matrix_from_tree(df=True)
    >>> vcv.shape
    (5, 5)
    """
    # get node distance matrix
    dmat = tree.distance.get_node_distance_matrix()

    # fill vcv array with shared dists (mrca to root)
    vcv = np.zeros((tree.ntips, tree.ntips))
    for tip1, tip2 in itertools.combinations(range(tree.ntips), 2):
        # get mrca node and its dist to root (co-variances)
        mrca = tree.get_mrca_node(tip1, tip2)
        vcv[tip1, tip2] = dmat[mrca.idx, tree.treenode.idx]
        vcv[tip2, tip1] = vcv[tip1, tip2]

    # fill diagonal with each tips dist from the root
    for node in tree[: tree.ntips]:
        vcv[node._idx, node._idx] = dmat[node._idx, -1]

    # return as ndarray or dataframe
    if not df:
        return vcv

    # return as dataframe
    tlabels = tree.get_tip_labels()
    return pd.DataFrame(vcv, columns=tlabels, index=tlabels)


@add_subpackage_method(PhyloCompAPI)
def get_corr_matrix_from_tree(
    tree: ToyTree,
    df: bool = False,
) -> Union[np.ndarray, pd.DataFrame]:
    """Return the tip correlation matrix implied by the tree VCV matrix.

    This converts the Brownian-motion variance-covariance matrix to a
    correlation matrix by dividing each entry by the product of the
    corresponding tip standard deviations.

    Parameters
    ----------
    tree : ToyTree
        Tree with edge lengths.
    df : bool, default=False
        If ``True``, return a labeled ``pandas.DataFrame``. Otherwise return a
        ``numpy.ndarray``.

    Returns
    -------
    numpy.ndarray or pandas.DataFrame
        Tip-by-tip correlation matrix. Entries that should be zero by the VCV
        structure are explicitly set to ``0.0`` to avoid floating-point noise.

    Raises
    ------
    Exception
        Propagated from ``get_vcv_matrix_from_tree()`` or downstream numeric
        operations if the input tree is invalid.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> corr = tree.pcm.get_corr_matrix_from_tree(df=True)
    >>> corr.shape
    (5, 5)
    """
    vcv = get_vcv_matrix_from_tree(tree)
    diag_std = np.sqrt(np.diag(vcv))
    outer = np.outer(diag_std, diag_std)
    corr = vcv / outer
    # correct rounding point errors
    corr[vcv == 0] = 0.0
    if not df:
        return corr
    names = tree.get_tip_labels()
    return pd.DataFrame(corr, index=names, columns=names)


@add_subpackage_method(PhyloCompAPI)
def get_distance_matrix_from_vcv_matrix(
    vcv: Union[np.ndarray, pd.DataFrame],
) -> Union[np.ndarray, pd.DataFrame]:
    """Return a tip distance matrix derived from a VCV matrix.

    Distances are computed from a variance-covariance matrix ``V`` using
    ``d(i, j) = V[i, i] + V[j, j] - 2 * V[i, j]``. This corresponds to the
    pairwise path-length distance implied by the Brownian-motion VCV.

    Parameters
    ----------
    vcv : numpy.ndarray or pandas.DataFrame
        Square variance-covariance matrix. If a DataFrame is provided, its
        labels are preserved on the returned DataFrame.

    Returns
    -------
    numpy.ndarray or pandas.DataFrame
        Square pairwise distance matrix with the same shape as ``vcv``.

    Raises
    ------
    Exception
        Propagated if the input cannot be converted to an array or does not
        support the required indexing operations.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> vcv = tree.pcm.get_vcv_matrix_from_tree(df=True)
    >>> dmat = tree.pcm.get_distance_matrix_from_vcv_matrix(vcv)
    >>> dmat.shape
    (5, 5)
    """
    names = None
    if isinstance(vcv, pd.DataFrame):
        names = vcv.index
    vcv = np.array(vcv)
    dists = np.zeros_like(vcv)
    for i in range(dists.shape[0]):
        for j in range(dists.shape[0]):
            dists[i, j] = vcv[i, i] + vcv[j, j] - (2 * vcv[i, j])
    if names is not None:
        dists = pd.DataFrame(dists, index=names, columns=names)
    return dists


@add_subpackage_method(PhyloCompAPI)
def get_tree_from_vcv_matrix(vcv: Union[np.ndarray, pd.DataFrame]) -> ToyTree:
    """Return tree reconstructed from a variance-covariance matrix.

    This first converts the VCV, which represents unique and shared
    edge lengths, into a distance matrix by subtracting each element
    in the matrix by the max value in the matrix. Then neighbor
    joining is applied to the distance matrix. The returned tree
    is unrooted.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> vcv = get_vcv_matrix_from_tree(tree, df=True)
    >>> nj_tree = get_tree_from_vcv_matrix(vcv)

    Parameters
    ----------
    vcv: ArrayLike
        A variance-covariance matrix as a np.ndarray or pd.DataFrame.
    """
    dist_mat = get_distance_matrix_from_vcv_matrix(vcv)
    import toytree

    return toytree.infer.neighbor_joining_tree(dist_mat)


if __name__ == "__main__":
    import toytree

    tre = toytree.rtree.unittree(ntips=10, seed=123, treeheight=3)
    # print(tre.write())
    # dists = toytree.distance.get_tip_distance_matrix(tre, df=True)
    # print(dists)
    # vcv = get_covariance_matrix_from_tree(tre, df=True)
    vcv = get_vcv_matrix_from_tree(tre, df=True)
    print(vcv)
    corr = get_corr_matrix_from_tree(tre, df=True)
    print(corr)

    std_dev = np.sqrt(np.diag(vcv))
    cov_mat_scaled = corr * np.outer(std_dev, std_dev)
    print(cov_mat_scaled)

    # np.linalg.inv(vcv)
    # print(tre.get_tip_data())

    # ttt = get_tree_from_vcv(vcv)
    # print(ttt)
    tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    print(tree.get_node_data())
    print(tree.distance.get_tip_distance_matrix())
    vcv = get_vcv_matrix_from_tree(tree, df=True)
    corr = get_corr_matrix_from_tree(tree, df=True)
    dist = get_distance_matrix_from_vcv_matrix(vcv)
    # print(vcv)
    # print(corr)
    print(dist)

    tree = get_tree_from_vcv_matrix(vcv).mod.root_on_minimal_ancestor_deviation()
    print(tree.get_node_data())
    tree.treenode.draw_ascii()
