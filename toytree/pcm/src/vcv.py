#!/usr/bin/env python

"""Conversion of phylogeny to and from variance-covariance matrix.

TODO
-----
1. Allow other correlation structures besides Brownian motion.
2. Estimate covariance structure using statsmodels.

References
-----------
- Garland, T. Jr. and Ives, A. R. (2000) Using the past to predict the
  present: confidence intervals for regression equations in phylogenetic
  comparative methods. American Naturalist, 155, 346-364.

"""

from typing import Union
import itertools
import numpy as np
import pandas as pd
import toytree
from toytree import ToyTree
from toytree.core.apis import add_subpackage_method, PhyloCompAPI


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
    """Return a variance-covariance matrix (DataFrame) from a ToyTree.

    The VCV represents the sum lengths of shared edges between
    pairs of samples as covariances (off-diagonals) and sum
    root-to-tip edge lengths of each sample as variances (diagonals)
    This matrix is often useful as it provides the expected variances
    and covariances of a continuous trait evolving on a tree under
    Brownian motion.

    Parameters
    ----------
    tree: toytree.ToyTree
        A tree on which to compute the VCV.
    df: bool
        True returns pandas DataFrame, else returns numpy ndarray.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> vcv = get_vcv_matrix_from_tree(tree, df=True)
    >>> #      r0   r1   r2   r3   r4
    >>> # r0  3.0  2.0  1.0  0.0  0.0
    >>> # r1  2.0  3.0  1.0  0.0  0.0
    >>> # r2  1.0  1.0  3.0  0.0  0.0
    >>> # r3  0.0  0.0  0.0  3.0  1.0
    >>> # r4  0.0  0.0  0.0  1.0  3.0
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
    for node in tree[:tree.ntips]:
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
    r"""Return a correlation matrix (DataFrame) from a ToyTree.

    The correlation matrix is computed from the variance-covariance
    matrix. The relationship between the VCV (C) and the correlation
    matrix (R) is:
    $$ R_{ij} = \frac{C_{ij}}{\sqrt{C_{ii} * C_{jj}}} $$

    Parameters
    ----------
    tree: toytree.ToyTree
        A tree on which to compute the correlation matrix.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> corr = get_corr_matrix_from_tree(tree, df=True)
    >>> #           r0        r1        r2        r3        r4
    >>> # r0  1.000000  0.666667  0.333333  0.000000  0.000000
    >>> # r1  0.666667  1.000000  0.333333  0.000000  0.000000
    >>> # r2  0.333333  0.333333  1.000000  0.000000  0.000000
    >>> # r3  0.000000  0.000000  0.000000  1.000000  0.333333
    >>> # r4  0.000000  0.000000  0.000000  0.333333  1.000000
    """
    vcv = get_vcv_matrix_from_tree(tree)
    diag_std = np.sqrt(np.diag(vcv))
    outer = np.outer(diag_std, diag_std)
    corr = vcv / outer
    # correct rounding point errors
    corr[vcv == 0] = 0.
    if not df:
        return corr
    names = tree.get_tip_labels()
    return pd.DataFrame(corr, index=names, columns=names)


# @add_subpackage_method(PhyloCompAPI)
def get_distance_matrix_from_vcv_matrix(vcv: Union[np.ndarray, pd.DataFrame]) -> Union[np.ndarray, pd.DataFrame]:
    """Returns the Euclidean distance between tips from a VCV matrix.

    The Euclidean distance is computed as:
        V[i, i] + V[j, j] - (2 * V[i, j])
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


# @add_subpackage_method(PhyloCompAPI)
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
    return toytree.infer.infer_neighbor_joining_tree(dist_mat)


if __name__ == "__main__":

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
