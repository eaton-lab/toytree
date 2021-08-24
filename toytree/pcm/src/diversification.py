#!/usr/bin/env python

"""
Functions for calculating diversification related statistics.
"""

from typing import Union
import pandas as pd
import toytree
from toytree.pcm.src.utils import calculate_posterior


def _get_equal_splits(tree):
    """Return DataFrame with equal splits (ES) metric sensu Redding 
    and Mooers 2006. See :meth:`.get_equal_splits`
    """
    # store results
    data = pd.Series(name="ES", index=tree.get_tip_labels(), dtype=float)

    # traverse up to root from each tip
    for idx in range(tree.ntips):
        node = tree.idx_dict[idx]
        divrate = 0
        j = 1
        while node.up:
            divrate += node.up.dist / (2 ** j)
            node = node.up
            j += 1
        data[idx] = divrate
    return data    

def _get_tip_level_diversification(tree):
    """Returns a DataFrame with tip-level diversification rates
    sensu Jetz 2012. See :meth:`.get_tip_level_diversification`
    """
    # ensure tree is a tree
    data = 1 / get_equal_splits(tree)
    data.name = "DR"
    return data

def get_equal_splits(
    trees: Union['ToyTree', 'MultiTree', str],
    njobs: int=1,
    ) -> pd.DataFrame:
    """Return DataFrame with equal splits (ES) metric sensu Redding 
    and Mooers 2006.

    Parameters
    ----------
    trees: ToyTree, MultiTree, or newick file of one or more trees.
        One or more input trees.
    njobs: int
        Distribute N jobs in parallel using ProcessPoolExecutor.
    **kwargs: dict
        A dictionary of arguments to the Callable function.

    Returns
    -------
    pandas.DataFrame or pandas.Series
        If multiple trees a DataFrame with posterior statistics is
        returned, else a Series with stats for a single tree.

    Reference
    ---------
    TODO
    """
    if isinstance(trees, toytree.ToyTree):
        return _get_equal_splits(trees)
    return calculate_posterior(_get_equal_splits, trees, njobs)

def get_tip_level_diversification(
    trees: Union['ToyTree', 'MultiTree', str],
    njobs: int=1,
    **kwargs,
    ) -> pd.DataFrame:
    """Return a DataFrame with tip-level diversification rates
    sensu Jetz 2012.

    Parameters
    ----------
    trees: ToyTree, MultiTree, or newick file of one or more trees.
        One or more input trees.
    njobs: int
        Distribute N jobs in parallel using ProcessPoolExecutor.
    **kwargs: dict
        A dictionary of arguments to the Callable function.

    Returns
    -------
    pandas.DataFrame or pandas.Series
        If multiple trees a DataFrame with posterior statistics is
        returned, else a Series with stats for a single tree.

    Reference
    ---------
    TODO
    """
    if isinstance(trees, toytree.ToyTree):
        return _get_tip_level_diversification(trees, **kwargs)
    return calculate_posterior(
        _get_tip_level_diversification, trees, njobs, **kwargs)


if __name__ == "__main__":

    tres = [toytree.rtree.unittree(10) for i in range(10)]
    mtree = toytree.mtree(tres)

    print(get_equal_splits(mtree, 2))
    print(get_tip_level_diversification(mtree, 2))
