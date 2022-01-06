#!/usr/env/bin python

"""Tree distance metrics for measuring differences between trees.

Tree distance methods decompose trees into sets of bipartitions or 
quartets, and use one of several methods for measuring differences
based on these sets, or additional features of the sets.

bipartition = {0, 1} | {2, 3, 4}
quartets = {0, 1} | {2, 3}; {0, 1} | {2, 4}; {0, 1} | {3, 4}, 

These methods are written to enable fast pairwise comparison of 
two trees, or many trees, as well as comparison of two or more trees
to a consensus. Methods for comparing multilple trees will 
cache edge sets in a dictionary. This can lead to high memory load 
for extremely large tree sets.

References
----------
- https://en.wikipedia.org/wiki/Robinson%E2%80%93Foulds_metric
- Robinson, D.F. and Foulds, L.R. (1981) "Comparison of phylogenetic
  trees". Mathematical Biosciences. 53 (1–2): 131–147. 
  doi:10.1016/0025-5564(81)90043-2.
- Smith, Martin R. (2020). "Information theoretic Generalized 
  Robinson-Foulds metrics for comparing phylogenetic trees". 
  Bioinformatics. 36 (20): 5007–5013. doi:10.1093/bioinformatics/btaa614.
- Mercè Llabrés, Francesc Rosselló, and Gabriel Valiente (2021)
  "The Generalized Robinson-Foulds Distance for Phylogenetic Trees"
  Journal of Computational Biology. http://doi.org/10.1089/cmb.2021.0342
- Sand, A, Holt, M., Johansen, J., Brodal, G., Mailund, T., Pedersen, C., 
  (2014) "tqDist: a library for computing the quartet and triplet 
  distances between binary or general trees", Bioinformatics, Volume 
  30, 14, 2079–2080, https://doi.org/10.1093/bioinformatics/btu157.
- Brodal 2013
- Estabrook 1985
- Holt 2014
- Sand 2014
- https://cran.r-project.org/web/packages/TreeDist/vignettes/Robinson-Foulds.html

Authors
-------
- Deren Eaton, Patrick McKenzie, Scarlet Ming-sha Au

Examples
--------
>>> t0 = ...
>>> t1 = ...
>>> dist = t0.distance.get_treedist(t1, method="rfi", normalize=True)
>>> dist = t0.distance.get_treedist_rf(t1)
>>> dist = t0.distance.get_treedist_rfi(t1)
>>> dist = t0.distance.get_treedist_rfg(t1)
>>> dist = t0.distance.get_treedist_qrt(t1)
"""

from typing import Set, TypeVar, Tuple
import itertools
from functools import cache
from scipy.special import factorial2

import pandas as pd
import numpy as np
from toytree.utils import ToytreeError


ToyTree = TypeVar("ToyTree")


####################################################
## Get distance metric from bipartition sets
####################################################

def _get_rf_distance(
    set1: Set, set2: Set, normalize: bool=True) -> float:
    """Return RF distance between two bipartition sets.
    
    The Robinson-Foulds distance is a normalized count of the 
    bipartitions induced by one tree, but not the other tree, i.e.,
    it is the symmetric difference between two bipart sets divided
    by the total number of (internal) bipartitions in both sets.

    Parameters
    ----------
    set1: set
        A set of bipartitions in tree1 (e.g., tree1._iter_bipartitions)
    set2: set
        A set of bipartitions in tree2 (e.g., tree2._iter_bipartitions)
    normalize: bool
        Normalize score by the total number of splits present.
    """
    # get symmetric difference of bipartitions sets
    sym_diff = set1 ^ set2

    # normalize by the total number of internal edges.
    # bipart sets are ordered so element 0 will be len==1 if singleton.
    if normalize:
        nsplits1 = sum(1 for i in set1 if len(i[0]) > 1)
        nsplits2 = sum(1 for i in set2 if len(i[0]) > 1)
        return len(sym_diff) / (nsplits1 + nsplits2)
    return len(sym_diff)

def _get_rf_distance_information_corrected(
    set1: Set, set2: Set, normalize: bool=True) -> float:
    """Return the information-corrected Robinson-Foulds distance (rfi).

    This distance measure is the sum of of the phylogenetic information
    of edges that are different between two trees, where information
    is calculated as the probability that a randomly sampled binary 
    tree of the same size contains the split. Splits that
    contain less information (e.g., a cherry vs a deep split) are more
    likely to arise by chance, and thus contribute less to the metric.

    Parameters
    ----------
    normalize: bool or str
        Normalize score relative to the phylogenetic info present in
        one or both subtrees...

        For the imb-bal tree example it seems like Union gives the 
        answer matching to MS, but for the text trees example it 
        seems that min is correct...

        True implements "min".
        - "min": normalize by N splits in least resolved tree.
        - "avg": normalize by avg N splits in the two trees.
        - "max": normalize by N splits in most resolved tree.        

    References
    ----------
    - Martin Smith: https://cran.r-project.org/web/packages/TreeDist/vignettes/information.html
    """
    # get total phylo info from the union of splits
    sinfo = sum(_get_split_phylo_info(s) for s in set1 | set2)

    # get sum of phylo info on the shared splits
    shared = set1 & set2
    dist = sum(_get_split_phylo_info(s) for s in shared)

    # distance = (total phylo info) - (shared phylo info)
    # normalization = distance / (... options). The default normalizer
    # in rfi is sum of phyinfo in both trees independently, following
    # the default in TreeDist.
    if normalize:
        norm1 = sum(_get_split_phylo_info(s) for s in set1)
        norm2 = sum(_get_split_phylo_info(s) for s in set2)
        # default normalization (True)
        if normalize in ["sum", True]:
            norm = sum((norm1, norm2))
        elif normalize == "max":
            norm = max(norm1, norm2)
        elif normalize == "avg":
            norm = (norm1 + norm2) / 2.
        elif normalize == "min":
            norm = min(norm1, norm2)
        return (sinfo - dist) / norm
    return sinfo - dist

####################################################################
## Get phylogenetic info from bipartition or pair of bipartitions
####################################################################

@cache
def _get_split_phylo_info(
    split: Tuple[Tuple,Tuple]) -> float:
    """Return the phylogenetic info of a split sensu Martin Smith 2020.

    Phy Info is the prob that a randomly sampled binary tree of 
    size X contains the split S. It is used in rf-info and returned
    in units of bits using a log base 2.

    The split AB|CDEF occurs in 15/105 of the possible resolutions 
    of a six leaf tree, so the prob of seeing it is P(S1) = 15/105,
    and its information content is h(S1) = -log_2(15/105) = 2.81.
    """
    size_a = len(split[0])
    size_b = len(split[1])
    return _get_split_phylo_info_from_sizes(size_a, size_b)

@cache
def _get_split_phylo_info_from_sizes(
    size_a: int, size_b:int) -> float:
    """Cache to return fast phylo info for any (size, size) split."""
    size_x = size_a + size_b
    return -np.log2(
        factorial2(2 * size_a - 3)
        * factorial2(2 * size_b - 3)
        / factorial2(2 * size_x - 5)
    )

@cache
def _get_shared_phylo_info(
    split1: Tuple[Tuple,Tuple],
    split2: Tuple[Tuple,Tuple],
    ) -> float:
    """
    From input bipartitions A1|B1 and A2|B2 are arranged such that 
    A1 is a superset of A2. If not possible then their shared phylo
    info is zero. If they are the same then it is Pphy(S1). 
    
    References
    ----------
    - Martin Smith (2020) Bioinformatics.
    - https://ms609.github.io/TreeDist/reference/TreeDistance.html
    """
    if split1 == split2:
        return _get_split_phylo_info(split1)
    if not split1 & split2:
        return 0

    # align such that A2 c A1, and B2 c B1.
    # if split1.
    size_a1 = len(split1[0])
    size_b1 = len(split1[1])
    size_a2 = len(split2[0])
    size_b2 = len(split2[1])
    return _get_shared_phylo_info_from_sizes(size_a1, size_b1, size_a2, size_b2)

@cache
def _get_shared_phylo_info_from_sizes(
    size_a1: int, size_b1:int, size_a2: int, size_b2: int) -> float:
    """Cache to return fast shared phy info for sized splits."""
    size_x = size_a1 + size_a2 + size_b1 + size_b2
    return -np.log2(
        factorial2(2 * (size_b1 + 1) - 5)
        * factorial2(2 * (size_a1 + 1) - 5)
        * factorial2(2 * (size_a1 - size_a2 + 2) - 5)
        / factorial2(2 * size_x - 5)
    )

####################################################################
## Get matching of bipartitions for ...
####################################################################

def _get_split_matching(set1: Set, set2: Set) -> float:
    """

    An optimal matching can be found by building a table of pairwise
    similarity scores among all bipartitions and then solving a 
    **linear assignment problem**. Similarity score can be measured
    by the *shared phylogenetic info* algorithm of Martin Smith.
    
    References
    ----------
    - https://medium.com/@rajneeshtiwari_22870/linear-assignment-problem-in-metric-learning-for-computer-vision-eba7d637c5d4
    """


def _get_rf_generalized():
    """Return generalized ...

    Finds the best "matching" between splits in two sets that are not 
    required to be identical.

    Even when using information content for Robinson–Foulds the 
    distances become saturated quickly. The generalized RF method
    (Böcker, Canzar, & Klau, 2013; Nye, Liò, & Gilks, 2006) 
    incorporates information from similar but non-identical splits.

    https://cran.r-project.org/web/packages/TreeDist/vignettes/Robinson-Foulds.html
    """

def _get_clustering_info_distance():
    """TODO"""

def _get_prop_intersect_over_union(set1: Set, set2: Set) -> float:
    """Return the proportion of intersecting sets among two trees.

    The proportion intersecting is measured as the len of the 
    intersection of sets 1 and 2 divided by the len of their union. 
    The sets can be different sizes if the trees do not share the 
    same tips, or have different number of internal Nodes resolved.

    `dist = len(s1 & s2) / len(s1 | s2)`

    Example
    -------
    >>> set1 = set(tree1._iter_quartets())
    >>> set2 = set(tree2._iter_quartets())    
    >>> print(_get_prop_intersect_over_union(set1, set2))
    """
    return len(set1 & set2) / len(set1 | set2)

def _get_prop_intersect_over_set1(set1: Set, set2: Set) -> float:
    """Return the proportion of intersecting sets among two trees.

    The proportion intersecting is measured as the len of the 
    intersection of sets 1 and 2 divided by the len of set 1. The 
    sets can be different sizes if the trees do not share the same 
    tips, or have different number of internal Nodes resolved.

    `dist = len(s1 & s2) / len(s1)`

    Example
    -------
    >>> set1 = set(tree1._iter_quartets())
    >>> set2 = set(tree2._iter_quartets())    
    >>> print(_get_prop_intersect_over_set1(set1, set2))
    """
    return len(set1 & set2) / len(set1)


##############################################################
##
##  PUBLIC METHODS
##
##############################################################

def get_treedist(
    tree1: ToyTree, 
    tree2: ToyTree, 
    method: str="rf",
    normalize: bool=False,
    ) -> float:
    """Return a tree distance metric for two trees.
    
    A tree distance metric is larger when two trees are more differnt,
    and smaller when they are more similar. This function provides a 
    general interface to multiple tree distance metrics which measure
    differences in different ways.

    Parameters
    ----------
    tree1: ToyTree
        An input ToyTree to compare to tree2.
    tree2: ToyTree
        An input ToyTree to compare to tree1.
    method: str
        A distance metric from the following supported options:
        - "rf": RobinsonFoulds (Robinson & Foulds)
        - "rfi": RobinsonFoulds-information-corrected (...)
        - "rfj": RobinsonFoulds-Jaccard (Bocker et al. 2013)
        - "rfg": RobinsonFoulds-generalized (...)
        - "qrt": Quartet divergence (Estabrook et al. 1985)
    normalize: bool
        Normalize distance score. Each method has a different default
        normalization method based on the input trees.
    """
    if method[0].lower() == "q":
        set1 = set(tree1._iter_quartets())
        set2 = set(tree2._iter_quartets())
        return _get_prop_intersect_over_set1(set1, set2)
    if method.lower() == "rf":
        set1 = set(tree1._iter_bipartitions())
        set2 = set(tree2._iter_bipartitions())
        return _get_rf_distance(set1, set2, normalize=normalize)
    if method.lower() == "rfi":
        set1 = set(tree1._iter_bipartitions())
        set2 = set(tree2._iter_bipartitions())
        return _get_rf_distance_information_corrected(set1, set2, normalize=normalize)
    raise ToytreeError("method not recognized")

def get_treedist_matrix(
    *trees: ToyTree, 
    method: str="rf", 
    normalize: bool=True,
    ) -> pd.DataFrame:
    """Return ...

    This is a generalizatino of `get_treedist` that is faster for 
    comparing many trees because it caches the induced sets for
    each tree for comparing to other trees.

    TODO: Not completed...
    """
    raise NotImplementedError("work in progress...")
    #
    trees = list(*trees)
    assert len(trees) > 1, "must be >1 trees."
    arr = np.zeros((len(trees), len(trees)), dtype=float)

    # get set method
    if method[0].lower() == "q":
        getter = lambda x: set(x._iter_quartets())
    elif method[0].lower() == "r":
        getter = lambda x: set(x._iter_bipartitions())

    # iterate over pairs of trees in upper triangle
    tidxs = range(len(trees))
    set_cache = {}
    for idx1, idx2 in itertools.combinations(tidxs, 2):
        tr1 = trees[idx1]
        tr2 = trees[idx2]
        if tr1 not in set_cache:
            set1 = getter(tr1)
            set_cache[tr1] = set1
        else:
            set1 = set_cache[tr1]
        if tr2 not in set_cache:
            set2 = getter(tr2)
            set_cache[tr2] = set2
        else:
            set2 = set_cache[tr2]

        # get distance
        arr[idx1, idx2] = _get_prop_intersect_over_set1(set1, set2)
        arr[idx2, idx1] = _get_prop_intersect_over_set1(set1, set2)        
    return arr

# def get_average_dist(*trees: ToyTree, method: str) -> float:
#     """Return the average distance among multiple input trees.
#     """

# def get_distance_to_consensus(*trees: ToyTree, method: str) -> pd.Series:
#     """
#     """
#     ctree = toytree.mtree(list(trees)).get_consensus_tree()
#     dists = [get_treedist(ctree, i, method=method) for i in trees]

##############################################################
##
##  VALIDATION FUNCTIONS FOR COMPARING TO R LIBRARY
##
##############################################################

def _test_with_treedist_r(
    tree1: ToyTree,
    tree2: ToyTree,
    method: str,
    normalize: bool,
    ) -> float:
    """Return distance calculated with R's TreeDist library.

    This is used only for validation/testing internally only. Users
    are not expected to have R or treedist installed, and no
    checks are performed. This is not used in unittests.
    """
    import subprocess
    import tempfile

    # get TreeDist function
    method = method.lower()
    if method == "rf":
        func = "RobinsonFoulds"
    elif method == "rfi":
        func = "InfoRobinsonFoulds"
    elif method == "rfg":
        func = "GeneralizedRobinsonFoulds"
    elif method == "clust":
        func = "ClusteringInfoDist"
    else:
        raise NotImplementedError("could do, but didn't yet..")

    # write R script to a tmpfile
    script = "\n".join([
        "library(TreeDist)",
        "t1 <- ape::read.tree(text='{}')".format(tree1.write(None, None, None)),
        "t2 <- ape::read.tree(text='{}')".format(tree2.write(None, None, None)),
        "dist <- {}(t1, t2, normalize={})".format(func, str(normalize).upper()),
        "print(dist)"
    ])

    with tempfile.NamedTemporaryFile(mode='w', encoding="utf-8") as tmp:
        tmp.write(script)
        tmp.flush()

        # run Rscript on the tempfile and catch stdout
        cmd = ["Rscript", "--vanilla", tmp.name]
        args = {'args': cmd, 'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT}
        with subprocess.Popen(**args, encoding='utf-8') as proc:
            out, _ = proc.communicate()
    return float(out.split()[-1])


def _validate(tree1, tree2):
    """Return dataframe with results for toytree and TreeDist"""
    algorithms = ["rf", "rfi"]
    algorithms += [i + "-norm" for i in algorithms]
    data = pd.DataFrame(
        index=algorithms,
        columns=["toytree", "TreeDist"],
        data=0,
    )

    for algo in algorithms:
        norm = "-norm" in algo
        aname = algo.replace("-norm", "")
        toy = get_treedist(tree1, tree2, method=aname, normalize=norm)
        trd = _test_with_treedist_r(tree1, tree2, aname, norm)
        data.loc[algo] = toy, trd
    return data


if __name__ == "__main__":

    import toytree
    tre1 = toytree.rtree.baltree(7)
    tre2 = toytree.rtree.imbtree(7)
    print("\n tre1-tre2")
    print(_validate(tre1, tre2))

    n1 = "(1, (2, (3, (4, (5, (6, (7, 8)))))));"
    n2 = "(1, (2, (3, (4, (5, (7, (6, 8)))))));"
    n3 = "(1, (2, (3, (5, (4, (6, (7, 8)))))));"
    n4 = "(1, (2, (3, 4, 5, (6, (7, 8)))));"
    t1 = toytree.tree(n1)
    t2 = toytree.tree(n2)    
    t3 = toytree.tree(n3)
    t4 = toytree.tree(n4)    

    print("\n t1-2")
    print(_validate(t1, t2))

    print("\n t1-3")
    print(_validate(t1, t3))

    print("\n t2-4")
    print(_validate(t2, t4))
