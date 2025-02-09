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
from typing import Union, Callable
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import toytree
from toytree import ToyTree, MultiTree
from toytree.core.apis import add_subpackage_method, PhyloCompAPI


def calculate_posterior(
    function: Callable,
    trees: Union[str, ToyTree, MultiTree],
    njobs: int = 1,
    **kwargs,
) -> pd.DataFrame:
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
        itertree = iter(trees)
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
        njobs = min(njobs, len(trees))
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

    pass
