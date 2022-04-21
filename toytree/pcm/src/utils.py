#!/usr/bin/env python

"""General phylogenetic comparative methods utilities.

Note
----
Some of these functions may move to other modules as they are 
further developed.

References
----------
- Freckleton, R. P., Harvey, P. H. and M. Pagel, M. (2002)
  Phylogenetic analysis and comparative data: a test and review of
  evidence. _American Naturalist_, *160*, 712-726.
- Pagel, M. (1999) Inferring the historical patterns of biological
  evolution. _Nature_, *401*,877-884.
"""

import os
from typing import Union, Callable, TypeVar
from concurrent.futures import ProcessPoolExecutor
import itertools
import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
import toytree


ToyTree = TypeVar("ToyTree")
# MultiTree = TypeVar("MultiTree")


def get_vcv_matrix_from_tree(tree: ToyTree) -> pd.DataFrame:
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

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=5, seed=123, treeheight=3)
    >>> print(get_vcv_from_tree(tree))
    >>> #      r0     r1      r2      r3      r4
    >>> # r0  3.0     2.0     1.0     0.0     0.0
    >>> # r1  2.0     3.0     1.0     0.0     0.0
    >>> # r2  1.0     1.0     3.0     0.0     0.0
    >>> # r3  0.0     0.0     0.0     3.0     1.0
    >>> # r4  0.0     0.0     0.0     1.0     3.0
    """
    theight = tree.treenode.height
    vcv = np.zeros((tree.ntips,tree.ntips))
    for tip1, tip2 in itertools.combinations(range(tree.ntips), 2):
        node = tree.get_mrca_node(tip1, tip2)
        vcv[tip1, tip2] = theight - node.height
        vcv[tip2, tip1] = theight - node.height
    # fill diagonal with variances (tip-to-root distances)
    vcv[np.diag_indices_from(vcv)] = [
        tree.distance.get_node_distance(i, tree.treenode.idx) 
        for i in range(tree.ntips)
    ]
    tlabels = tree.get_tip_labels()

    # convert to correlation
    return pd.DataFrame(vcv, columns=tlabels, index=tlabels)

def get_corr_matrix_from_tree(tree: ToyTree) -> pd.DataFrame:
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
    >>> print(get_vcv_from_tree(tree))
    >>> #      r0     r1      r2      r3      r4
    >>> # r0  3.0     2.0     1.0     0.0     0.0
    >>> # r1  2.0     3.0     1.0     0.0     0.0
    >>> # r2  1.0     1.0     3.0     0.0     0.0
    >>> # r3  0.0     0.0     0.0     3.0     1.0
    >>> # r4  0.0     0.0     0.0     1.0     3.0
    """
    vcv = get_vcv_matrix_from_tree(tree)
    diag_std = np.sqrt(np.diag(vcv))
    outer = np.outer(diag_std, diag_std)
    corr = vcv / outer
    corr[vcv == 0] = 0
    return corr

def get_tree_from_vcv(vcv: ArrayLike) -> ToyTree:
    """Return tree reconstructed from a variance-covariance matrix.

    This first converts the VCV, which represents unique and shared
    edge lengths, into a distance matrix by subtracting each element
    in the matrix by the max value in the matrix. Then neighbor
    joining is applied to the distance matrix. The returned tree
    is unrooted.

    Parameters
    ----------
    vcv: ArrayLike
        A variance-covariance matrix as a np.ndarray or pd.DataFrame.
    """
    max_value = np.array(vcv).max()
    return toytree.infer.infer_neighbor_joining_tree(max_value - vcv)

def calculate_posterior(
    function: Callable,
    trees: Union[str, 'toytree.MultiTree', 'toytree.ToyTree'], 
    njobs: int=1,
    **kwargs,
    ):
    """Return a DataFrame with posterior of (metric) from a tree set.

    Calculations are parallelized and tree(s) can be loaded from a 
    flexible set of options. For super large files reading from a
    multi-line newick file is most memory-efficient.

    Parameters
    ----------
    function: Callable
        A function that takes a tree as input and returns a float 
        metric as a pandas.Series.
    trees: ToyTree, MultiTree, or newick file
        Flexible options to input/parse one or multiple trees.
    njobs: int
        Distribute N jobs in parallel using ProcessPoolExecutor
    **kwargs: dict
        A dictionary of arguments to the Callable function.

    Examples
    --------
    >>> ...
    """
    # load data and metadata from newick, toytree, or multitree
    if isinstance(trees, list):
        trees = toytree.mtree(trees)
    if isinstance(trees, str) and os.path.exists(trees):
        with open(trees) as tree_generator:
            tre = toytree.tree(next(tree_generator))
            ntips = tre.ntips
            ntrees = sum(1 for i in tree_generator) + 1
            tiporder = tre.get_tip_labels()
        itertree = open(trees, 'r')
    elif isinstance(trees, toytree.ToyTree):
        itertree = iter([trees])
        ntrees = len(trees)
        ntips = trees.ntips
        tiporder = trees.get_tip_labels()
    elif isinstance(trees, toytree.MultiTree):
        itertree = iter(i for i in trees)
        ntrees = len(trees)
        ntips = trees.treelist[0].ntips
        tiporder = trees.treelist[0].get_tip_labels()
    else:
        raise IOError(f"problem with input: {trees}")

    # array to store results 
    tarr = np.zeros((ntips, ntrees))

    # run non-parallel calculations
    if njobs == 1:
        for tidx, tree in enumerate(itertree):
            data = function(tree, **kwargs)
            tarr[:, tidx] = data[tiporder]

    # or, distribute jobs in parallel (py3 only)
    else:
        pool = ProcessPoolExecutor(njobs)
        rasyncs = {}

        # submit as many jobs as there are cores
        for job in range(njobs):
            tree = next(itertree)
            kwargs.update({"tree": tree})
            rasyncs[job] = pool.submit(function, **kwargs)

        # as each job finished submit a new one until none are left.
        # this allows avoiding loading all trees simultaneously.
        tidx = 0
        while 1:
            # get finished jobs
            finished = [i for i in rasyncs if rasyncs[i].done()]
    
            # store results and append new job to the engine
            for job in finished:

                # store result
                result = rasyncs[job].result()
                tarr[:, tidx] = result[tiporder]
                tidx += 1
                del rasyncs[job]

                # append new job unless no jobs left
                try:
                    tree = next(itertree)
                    kwargs.update({"tree": tree})
                    rasyncs[job] = pool.submit(function, **kwargs)
                except StopIteration:
                    pass

            # wait until all jobs finish
            if not rasyncs:
                break
        pool.shutdown()

    # close the file handle, if exists
    if hasattr(itertree, "close"):
        itertree.close()

    # calculate summary of DR across the distribution of trees.
    arr = pd.DataFrame(tarr, index=tiporder)
    data = pd.DataFrame({
        'mean': arr.mean(1),
        # 'harmMean': hmean(arr, axis=1),
        'median': arr.median(1),
        'std': arr.std(1),
        '2.5%': np.percentile(arr, 0.025, axis=1),
        '97.5%': np.percentile(arr, 0.975, axis=1),
        'min': arr.min(1),
        'max': arr.max(1),
    })
    return data


if __name__ == "__main__":

    tre = toytree.rtree.unittree(10, seed=123)
    print(get_vcv_matrix_from_tree(tre))
