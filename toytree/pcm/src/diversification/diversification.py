#!/usr/bin/env python

"""Functions for calculating diversification related statistics.

"""

from typing import Union, TypeVar
from itertools import combinations
import pandas as pd
import numpy as np
import toytree
from toytree.pcm.src.utils import calculate_posterior


ToyTree = TypeVar("ToyTree")
MultiTree = TypeVar("MultiTree")

__all__ = [
    "get_tip_level_diversification", 
    "get_equal_splits",
]


def _get_equal_splits(tree: ToyTree) -> pd.Series:
    """Return equal splits (ES) metric sensu Redding and Mooers 2006. 
    See :meth:`.get_equal_splits`
    """
    # store results
    data = pd.Series(name="ES", index=tree.get_tip_labels(), dtype=np.float64)

    # traverse up to root from each tip
    for node in tree:
        name = node.name
        divrate = 0
        j = 1
        while node.up:
            divrate += node.up.dist / (2 ** j)
            node = node.up
            j += 1
        data[name] = divrate
    return data    


def _get_tip_level_diversification(tree: ToyTree):
    """Return tip-level diversification rates sensu Jetz 2012. 
    See :meth:`.get_tip_level_diversification`
    """
    # ensure tree is a tree
    data = 1 / get_equal_splits(tree)
    data.name = "DR"
    return data


def get_equal_splits(
    trees: Union[ToyTree, MultiTree, str],
    njobs: int=1,
) -> pd.DataFrame:
    """Return equal splits (ES) metric sensu Redding and Mooers 2006.

    Parameters
    ----------
    trees: ToyTree, MultiTree, or newick file of one or more trees.
        One or more input trees.
    njobs: int
        Distribute N jobs in parallel using ProcessPoolExecutor.

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
    trees: Union[ToyTree, MultiTree, str],
    njobs: int=1,
    **kwargs,
) -> pd.DataFrame:
    """Return tip-level diversification rates sensu Jetz 2012.

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
    """
    if isinstance(trees, toytree.ToyTree):
        return _get_tip_level_diversification(trees, **kwargs)
    return calculate_posterior(
        _get_tip_level_diversification, trees, njobs, **kwargs)


def get_prob_dist_of_ntips(
    n_starting_tips: int=1,
    time: float=1,
    speciation_rate: float=0.5,
    extinction_rate: float=0.5,
    n_max_tips: int=500,
) -> np.ndarray:
    """Return probability distribution of a b-d model ending in ntips.

    References
    ----------
    - Harmon Chapter 10 (section 10.2)
    - Foote et al. (1999)
    """
    net_div = speciation_rate - extinction_rate
    rel_ext = extinction_rate / speciation_rate

    # the prob that any particular lineage has gone extinct before t
    def alpha(time):
        return (
            (rel_ext * ((np.exp(net_div) * time) - 1)) / 
            (np.exp(net_div) * time - rel_ext)
        )

    # ...
    def beta(time):
        return (
            (np.exp(net_div) * time - 1) /        
            (np.exp(net_div) * time - rel_ext)
        )

    # a simpler set of equations can be used when n_starting=1
    # p0t = alpha(0) ** n_starting_tips
    # pnt = (1 - alpha(t)) * (1 - beta(t)) * beta(t) ** ()

    # UNFINISHED...
    jvals = np.arange(1, min(n_starting_tips, n_max_tips))
    j_choose_n0 = sum(1 for i in combinations(range(n_starting_tips), j) if i)
    
    j_minus_one = sum(1 for i in combinations(range(n_max_tips - 1), j - 1) if i)
    aterm = alpha(time) ** (n_starting_tips - j)
    bterm = beta(time) ** (n_max_tips - j)
    sumprob += j_choose_n0 * j_minus_one * aterm * bterm * ((1 - alpha(time)) * (1 - beta(time)))**j
    pnt = None


def get_net_diversification_rate(
    ntips: int, 
    age: float, 
    stem: bool=True,
    relative_extinction_rate: float=0, 
) -> float:
    r"""
    
    $r_{stem} = \frac{ln(n)}{t_{stem}}$
    $r_{crown} = \frac{ln(n) - ln(2)}{t_{crown}}$

    Parameters
    ----------
    ntips: int
        The size of the clade.
    age: float
        The age of the clade.
    stem: bool
        True if age represents stem age, else False if crown age.
    relative_extinction_rate: float
        Estimate of (extinction rate / speciation rate).

    References
    ----------
    - Magallon and Sanderson (2001)
    - Harmon chapter 11
    """
    ext = relative_extinction_rate
    if stem:
        if relative_extinction_rate:
            return  np.log(ntips * (1 - ext) + ext) / age
        return np.log(ntips) / age
    if relative_extinction_rate:
        inner1 = (ntips * (1 - ext**2)) / 2
        inner2 = 2 * ext
        inner3a = (1 - ext)
        inner_inner = (ntips * ext**2) - (8 * ext) + (2 * ntips * ext) + ntips
        inner3b = np.sqrt(ntips * inner_inner)
        inner3 = (inner3a * inner3b) / 2
        return (np.log(inner1 + inner2 + inner3) - np.log(2)) / age
    return (np.log(ntips) - np.log(2)) / age


def get_birth_death_likelihood(
    tree: ToyTree,
    speciation_rate: float,
    extinction_rate: float,
    time_to_present: float,
    time_to_root: float,
    condition_on_tree_existence: bool=True,
) -> float:
    """...

    Example
    -------
    >>> # get edge lengths from a tree
    >>> edges = tree.get_node_data("dist")
    >>> get_birth_death_likelihood()

    References
    ----------
    - Harmon Chapter 11
    - Nee et al. (1994)
    - Maddison
    - Morlon et al. 2011
    - Stadler 2013a
    """
    if not extinction_rate:
        return (tree.ntips - 1) / sum(i.dist for i in tree)


    # final likelihood equation is Harmon 11.18 - 11.19
    lik = "..."
    # return lik / λ[1 − E(troot)]**2 


def fit_birth_death_model(
    tree: ToyTree,
):
    pass


if __name__ == "__main__":

    # tres = [toytree.rtree.unittree(10) for i in range(10)]
    # mtree = toytree.mtree(tres)
    # print(get_equal_splits(mtree, 2))
    # print(get_tip_level_diversification(mtree, 2))
    
    TREE = toytree.rtree.bdtree(ntips=100, b=0.5, d=0.5)
    MTREE = [TREE, TREE, TREE]
    print(get_tip_level_diversification(MTREE, njobs=10))