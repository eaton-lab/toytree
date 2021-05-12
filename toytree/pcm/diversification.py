#!/usr/bin/env python

"""
Functions for calculating diversification related statistics.

Includes:
---------
- 
"""

from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd


def calculate_equal_splits(tree):
    """
    Return DataFrame with equal splits (ES) measure sensu Redding and 
    Mooers 2006.

    Reference:
    ----------
    TODO:
    """
    # dataframe for storing results
    data = pd.DataFrame(columns=["ES"], index=tree.get_tip_labels())

    # traverse up to root from each tip
    for idx in range(tree.ntips):
        node = tree.idx_dict[idx]
        divrate = 0
        j = 1
        while node.up:
            divrate += node.up.dist / (2 ** j)
            node = node.up
            j += 1
        data.iloc[idx, 0] = divrate
    return data



def calculate_tip_level_diversification(tree):
    """
    Returns a dataframe with tip-level diversification rates
    sensu Jetz 2012.

    Reference:
    ----------
    TODO:
    """
    # ensure tree is a tree
    data = 1 / calculate_equal_splits(tree)
    data.columns = ["DR"]
    return data



def calculate_posterior_tip_level_diversification(treefile, njobs=1):
    """
    Returns a dataframe with tip-level diversification rates calculated
    across a set of trees. Calculations are parallelized with 
    multiprocessing and trees are read from file as as a generator to 
    reduce RAM usage. 

    To calculate for only a single tree see instead the ToyTree 
    function .pcm.calculate_tip_level_diversification()

    Parameters:
    -----------
    trees (multi-line newick file):
        A multi-line newick tree file. This can be processed very
        memory-efficiently by not reading the entire file at once.

    njobs (int):
        Distribute N jobs in parallel using ProcessPoolExecutor

    Returns:
    --------
    df (pandas.DataFrame):
        The raw DF based on branch lengths of the tree.

    Examples:
    ---------
    df = toytree.pcm.calculate_tip_level_diversification(file, njobs=20)
    """
    # load data and metadata from newick, toytree, or multitree
    if isinstance(trees, str) and os.path.exists(trees):
        with open(trees) as tree_generator:
            tre = toytree.tree(next(tree_generator))
            ntips = tre.ntips
            ntrees = sum(1 for i in tree_generator) + 1
            tiporder = tre.get_tip_labels()
        itertree = open(trees, 'r')
    elif isinstance(trees, toytree.core.toytree.ToyTree):
        itertree = iter([trees])
        ntrees = len(trees)
        ntips = trees.ntips
        tiporder = trees.get_tip_labels()
    elif isinstance(trees, toytree.core.multitree.MultiTree):
        itertree = iter(i for i in trees)
        ntrees = len(trees)
        ntips = trees.treelist[0].ntips
        tiporder = trees.treelist[0].get_tip_labels()
    else:
        raise IOError("problem with input: {}".format(trees))

    # array to store results 
    tarr = np.zeros((ntips, ntrees))

    # run non-parallel calculations
    if njobs == 1:
        for tidx, tree in enumerate(itertree):
            df = _calculate_DR(tree)
            tarr[:, tidx] = df.loc[tiporder, "DR"]

    # or, distribute jobs in parallel (py3 only)
    else:
        pool = ProcessPoolExecutor(njobs)
        treegen = iter(trees)
        rasyncs = {}

        # submit as many jobs as there are cores
        for job in range(njobs):
            tree = next(itertree)
            rasyncs[job] = pool.submit(
                calculate_DR,
                (tree),
            )

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
                tarr[:, tidx] = result.loc[tiporder, "DR"]
                tidx += 1
                del rasyncs[job]

                # append new job unless no jobs left
                try:
                    tree = next(itertree)
                    rasyncs[job] = pool.submit(
                        calculate_DR,
                        (tree),
                    )
                except StopIteration:
                    pass

            # wait for next check
            time.sleep(0.5)           

            # wait until all jobs finish
            if not rasyncs:
                break
        pool.shutdown()

    # close the file handle, if exists
    if hasattr(itertree, "close"):
        itertree.close()

    # calculate summary of DR across the distribution of trees.
    arr = pd.DataFrame(tarr, index=tiporder)
    df = pd.DataFrame({
        'mean': arr.mean(1),
        # 'harmMean': hmean(arr, axis=1),
        'median': arr.median(1),
        'std': arr.std(1),
        '2.5%': np.percentile(arr, 0.025, axis=1),
        '97.5%': np.percentile(arr, 0.975, axis=1),
        'min': arr.min(1),
        'max': arr.max(1),
    })
    return df
