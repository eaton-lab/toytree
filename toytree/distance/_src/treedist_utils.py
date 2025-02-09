#!/usr/bin/env python

"""Information-based generalized Robinson-Foulds distances

References
----------
- https://ms609.github.io/TreeDist/reference/TreeDistance.html
"""

from typing import Tuple, Sequence, Set

# FIXME: support backup method old Python does not support
# from functools import cache
import itertools

from loguru import logger
from scipy.special import factorial2
from scipy.optimize import linear_sum_assignment
import numpy as np
import pandas as pd
from toytree.utils import ToytreeError
from toytree import ToyTree
from toytree.core.apis import TreeDistanceAPI, add_subpackage_method

logger = logger.bind(name="toytree")

####################################################
# Size of Tree Space, Tree Combinatorics, used to calc shared phylo info
#
# >>> _get_n_unrooted_trees(5)  # 105
####################################################


def _get_n_unrooted_trees(size: int) -> int:
    """Return the number of possible unrooted trees for ntips=size."""
    return int(factorial2(2 * size - 5))


def _get_n_rooted_trees(size: int) -> int:
    """Return the number of possible rooted trees for ntips=size."""
    return int(factorial2(2 * size - 3))


def _get_n_trees_matching_split(size_a: int, size_b: int) -> int:
    """Return number of trees that could contain split of size (A, B)"""
    if size_a == 0:
        return _get_n_unrooted_trees(size_b)
    if size_b == 0:
        return _get_n_unrooted_trees(size_a)
    return factorial2(2 * size_a - 3) * factorial2(2 * size_b - 3)


def _get_n_trees_matching_two_splits(ntips: int, size_a1: int, size_a2: int) -> int:
    """Return N trees that could contain A1 and A2 where A1 is subset of A2.

    Based on 'TreesConsistentWithTwoSplits' from TreeDist.
    """
    small = min(size_a1, size_a2)
    large = max(size_a1, size_a2)

    # simple scenarios
    if small == 0:
        return _get_n_trees_matching_split(large, ntips - large)
    if large == ntips:
        return _get_n_trees_matching_split(small, ntips - small)

    # calculate matching
    n_overlap = large - small
    part1 = _get_n_rooted_trees(n_overlap + 1)
    part2 = _get_n_rooted_trees(small)
    part3 = _get_n_rooted_trees(ntips - large)
    return int(part1 * part2 * part3)


#################################################################
# Get matching split info for bipartitions
##################################################################

def _get_two_splits_matching_split_dist(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    """Return the number of elements that must be moved from one
    subset to another in order to make the two splits identical.
    """
    a1, b1 = (set(i) for i in split1)
    a2, b2 = (set(i) for i in split2)
    ntips = len(a1) + len(b1)
    return ntips - max(len(a1 & a2) + len(b1 & b2), len(a1 & b2) + len(b1 & a2))


#################################################################
# Get Nye similarity metric
##################################################################

def _get_two_splits_nye_similarity(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    """Return the Nye similarity metric for two splits.

    Considers the elements held in common between subsets of each
    split, and considers both possible alignments of subsets, returning
    only the alignment score of the best.
    """
    a1, b1 = (set(i) for i in split1)
    a2, b2 = (set(i) for i in split2)

    # get alignment score from subset scores and return max alignment
    subset_score_1 = _get_nye_score(a1, a2)
    subset_score_2 = _get_nye_score(b1, b2)
    ali_score_1 = min(subset_score_1, subset_score_2)
    subset_score_1 = _get_nye_score(a1, b2)
    subset_score_2 = _get_nye_score(a2, b1)
    ali_score_2 = min(subset_score_1, subset_score_2)
    return max(ali_score_1, ali_score_2)


def _get_nye_score(set1: Set, set2: Set) -> float:
    """Return the Nye score for two sets"""
    return len(set1 & set2) / len(set1 | set2)


def get_tree_splitwise_nye_similarity(tree: ToyTree) -> float:
    """Return the maximum phylogenetic information in a tree."""
    return sum(1 for i in tree.iter_bipartitions())


#################################################################
# Get phylogenetic info from bipartitions
#
# >>> _get_phylo_info(4, 5)                         # 6.42...
# >>> _get_split_phylo_info((0,1,2,3),(4,5,6,7,8))  # 6.42...
##################################################################

def _get_phylo_prob(size_a: int, size_b: int) -> float:
    """Return prob that binary tree of size X contains split A|B."""
    size_x = size_a + size_b
    trees_w_split = _get_n_trees_matching_split(size_a, size_b)
    return trees_w_split / _get_n_unrooted_trees(size_x)


# @cache
def _get_phylo_info(size_a: int, size_b: int) -> float:
    """Return information of phylo prob in units of bits."""
    if (size_a < 2) or (size_b < 2):
        return 0
    return -np.log2(_get_phylo_prob(size_a, size_b))


# @cache
def _get_split_phylo_info(split: Tuple[Tuple, Tuple]) -> float:
    """Return the phylogenetic info of a split sensu Martin Smith 2020.

    Phy Info is the prob that a randomly sampled binary tree of
    size X contains the split S. It is used in rf-info and returned
    in units of bits using a log base 2.

    The split AB|CDEF occurs in 15/105 of the possible resolutions
    of a six leaf tree, so the prob of seeing it is P(S1) = 15/105,
    and its information content is h(S1) = -log_2(15/105) = 2.81.
    """
    # uses cache func to get stored result for split sizes previously seen.
    return _get_phylo_info(len(split[0]), len(split[1]))


def get_tree_splitwise_phylo_info(tree: ToyTree) -> float:
    """Return the maximum phylogenetic information in a tree."""
    return sum(_get_split_phylo_info(i) for i in tree.iter_bipartitions())


####################################################
# Get phylogenetic info from PAIRS of bipartitions
#
# >>> set1 = (tuple("AB"), tuple("CDEF"))
# >>> set2 = (tuple("ABC"), tuple("DEF"))
# >>> _get_two_splits_shared_phylo_info(set1, set2)  # 1.222...
####################################################

def _get_subset_superset(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> Tuple[Tuple, Tuple]:
    """Return a bipart half (A1, A2) from each bipart so A1 is a
    subset of A2, else A2 will return empty.
    """
    # select smaller half of split1 and superset from split 2
    subset = set(split1[0])
    superset = [i for i in split2 if set(i).issuperset(subset)]
    superset = superset[0] if superset else ()
    if not superset:
        subset = set(split1[1])
        superset = [i for i in split2 if set(i).issuperset(subset)]
        superset = superset[0] if superset else ()
    return tuple(sorted(subset)), superset


def _get_phylo_prob_two_splits(ntips: int, size_a1: int, size_a2: int) -> float:
    """Return the prob two splits exist in a tree of size X tips"""
    ntrees = _get_n_trees_matching_two_splits(ntips, size_a1, size_a2)
    ntotal = _get_n_unrooted_trees(ntips)
    return ntrees / ntotal


# @cache
def _get_phylo_info_two_splits(ntips: int, size_a1: int, size_a2: int) -> float:
    """Return the phylo information in two splits matching in a tree"""
    return -np.log2(_get_phylo_prob_two_splits(ntips, size_a1, size_a2))


def _get_two_splits_shared_phylo_info(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    """Return the shared phylo info (spi) for two splits in a tree.

    if conflict:
        SPI = h_shared = 0
    else:
        SPI = h_shared = h(S1) + h(S2) - h(S1, S2)

    Examples
    --------
    >>> split1 = ((0, 1, 2), (3, 4, 5, 6, 7))
    >>> split2 = ((0, 1, 2, 3), (4, 5, 6, 7))
    >>> _get_two_splits_shared_phylo_info(split1, split1)  # 5.044
    >>> _get_two_splits_shared_phylo_info(split2, split2)  #
    """
    subset, superset = _get_subset_superset(split1, split2)
    if not superset:
        return 0
    ntips = len(split1[0]) + len(split1[1])
    hs1 = _get_split_phylo_info(split1)
    hs2 = _get_split_phylo_info(split2)
    # check: returns S1S2 = S1 when S1=S2
    hs12 = _get_phylo_info_two_splits(ntips, len(subset), len(superset))
    return (hs1 + hs2) - hs12


def _get_two_splits_different_phylo_info(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    """Return the shared phylo info (spi) for two splits in a tree.

    if conflict:
        SPI = h_shared = 0
    else:
        SPI = h_shared = h(S1) + h(S2) - h(S1, S2)
    """
    hs1 = _get_split_phylo_info(split1)
    hs2 = _get_split_phylo_info(split2)
    subset, superset = _get_subset_superset(split1, split2)
    if not superset:
        return hs1 + hs2
    ntips = len(split1[0]) + len(split1[1])
    hs12 = _get_phylo_info_two_splits(ntips, len(subset), len(superset))
    hshared = (hs1 + hs2) - hs12
    return hs12 - hshared


####################################################
# Information theoretic alternative to matching split dist
####################################################

def _get_two_splits_matching_split_phylo_info(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    """Return the phylogenetic information of matching splits.

    In the matching split distance, m represents a simple count of
    the number of shared taxa. An alternative is to measure the
    phylogenetic information content of the largest split consistent
    with S1 and S2:
    """
    a1, b1 = (set(i) for i in split1)
    a2, b2 = (set(i) for i in split2)
    info1 = _get_phylo_info(len(a1 & a2), len(b1 & b2))
    info2 = _get_phylo_info(len(a1 & b2), len(b1 & a2))
    return max(info1, info2)


####################################################
# Get clustering entropy of bipartitions
####################################################

# @cache
def _entropy(*prob: float) -> float:
    """Return sum of entropies where e = prob * log2(prob)"""
    return -sum(p * np.log2(p) if p else 0 for p in prob)


def _get_split_entropy(split: Tuple[Tuple, Tuple]) -> float:
    """Return the clustering entropy associated with a split S.

    If a split S = A|B, then PCl(A) denotes the probability that a
    randomly selected leaf belongs to A: `PCl(A) = |A| / |X|`.
    Entropy(S) = −PCl(A) * log(PCl(A)) − PCl(B) * log(PCl(B))
    """
    len_a, len_b = [len(i) for i in split]
    ntips = len_a + len_b
    return _entropy(len_a / ntips, len_b / ntips)


def get_tree_splitwise_entropy(tree: ToyTree) -> float:
    """Return the maximum entropy of a tree"""
    return sum(_get_split_entropy(i) for i in tree.iter_bipartitions())


####################################################
# Get clustering entropy from PAIRS of bipartitions
####################################################

def _get_two_splits_entropy(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> Tuple[float, float, float, float, float]:
    """Return entropy info for two splits.

    Returns h_1, h_2, h_joint, h_shared, h_dist
    """
    ntips = len(split1[0]) + len(split1[1])
    sets = [set(i) for i in (split1[0], split1[1], split2[0], split2[1])]
    overlaps = (i & j for (i, j) in itertools.combinations(sets, 2))
    overlaps = [i for i in overlaps if i]

    h_1 = _get_split_entropy(split1)
    h_2 = _get_split_entropy(split2)
    h_joint = _entropy(*[len(i) / ntips for i in overlaps])
    h_shared = h_1 + h_2 - h_joint
    h_dist = h_joint - h_shared
    return h_1, h_2, h_joint, h_shared, h_dist


def _get_two_splits_entropy_info(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    return _get_two_splits_entropy(split1, split2)[3]


def _get_two_splits_entropy_info_dist(
    split1: Tuple[Tuple, Tuple],
    split2: Tuple[Tuple, Tuple],
) -> float:
    return _get_two_splits_entropy(split1, split2)[4]


####################################################################
# Get matching of bipartitions based on split similarity scores,
# i.e., shared phylo info (spi) or mutual clustering info (msi)
####################################################################

def _get_split_matching(
    biparts1: Sequence[Tuple[Tuple, Tuple]],
    biparts2: Sequence[Tuple[Tuple, Tuple]],
    split_similarity_metric: str = "spi",
) -> float:
    """Return a paired similarity matrix and optimal matching.

    An optimal matching can be found by building a table of pairwise
    similarity scores among all bipartitions and then solving a
    **linear sum assignment problem**. Similarity scores are measured
    by the *shared phylogenetic info* algorithm of Martin Smith, and
    the linear assignment is performed by scipy using the Hungarian
    algorithm.

    Parameters
    ----------
    split_similarity_metric: str
        "spi": shared phylogenetic information.
        "mci": mutual clustering information.
        "msi": matching split phylogenetic information.
        "ms": matching split distance.

    References
    ----------
    - ...
    """
    # split similarity function
    if split_similarity_metric == "mci":
        _get_split_similarity = _get_two_splits_entropy_info
        maximize = True
    elif split_similarity_metric == "spi":
        _get_split_similarity = _get_two_splits_shared_phylo_info
        maximize = True
    elif split_similarity_metric == "ms":
        _get_split_similarity = _get_two_splits_matching_split_dist
        maximize = False
    elif split_similarity_metric == "msi":
        _get_split_similarity = _get_two_splits_matching_split_phylo_info
        maximize = True
    elif split_similarity_metric == "nye":
        _get_split_similarity = _get_two_splits_nye_similarity
        maximize = True
    else:
        raise ToytreeError(
            "split similarity metric must be in "
            "('mci', 'spi', 'ms', 'msi', 'nye')")

    # get partitions in their input order.
    nb1 = len(biparts1)
    nb2 = len(biparts2)

    # get matric of split similarity measures
    arr = np.zeros(shape=(nb1, nb2))
    for idx, bip1 in enumerate(biparts1):
        for jdx, bip2 in enumerate(biparts2):
            arr[idx, jdx] = _get_split_similarity(bip1, bip2)

    # get linear solution pairing splits
    indices = linear_sum_assignment(arr, maximize=maximize)
    return arr, indices


def _report_matching(
    tree1: ToyTree,
    tree2: ToyTree,
    split_similarity_metric: str = "spi",
) -> Tuple["Canvas", "Cartesian", "Mark"]:
    """View the matching of splits between two trees.

    This method is used only for testing/validation, and to learn
    about generalized RF distance methods.

    Returns
    -------
    A toyplot Canvas with 3 Cartesian axes: [Matrix] [Tree1] [Tree2].
    """
    # get the matching
    biparts1 = list(tree1.iter_bipartitions())
    biparts2 = list(tree2.iter_bipartitions())
    pairs, indices = _get_split_matching(biparts1, biparts2, split_similarity_metric)

    nb1 = len(biparts1)
    nb2 = len(biparts2)
    data = pd.DataFrame(
        pairs,
        index=range(tree1.ntips, tree1.ntips + nb1),
        columns=range(tree2.ntips, tree2.ntips + nb2),
    )
    print(f"\n# paired split scores labeled by Node idx\n{data}")

    # add size to align indices with Node labels
    # arr1 += nb1
    # arr2 += nb2
    print("\n# matched split indices, tip labels, and scores")
    for i, j in zip(*indices):
        bip1 = biparts1[i]
        bip1 = f"{','.join(bip1[0])}|{','.join(bip1[1])}"
        bip2 = biparts2[j]
        bip2 = f"{','.join(bip2[0])}|{','.join(bip2[1])}"
        score = pairs[i, j]
        if score:
            print(f"{i}\t{j}\t{bip1} => {bip2}\t{score:.3f}")
        else:
            print(f"{i}\t{j}\t{bip1} .. {bip2}\t{score:.3f}")


####################################################################
# Functions using matched bipartitions
# Reference: https://ms609.github.io/TreeDist/reference/TreeDistance.html
####################################################################

def get_trees_nye_similarity(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the Nye similarity between two trees.

    References
    ----------
    - Nye TMW, Liò P, Gilks WR (2006). “A novel algorithm and
    web-based tool for comparing two alternative phylogenetic trees.”
    Bioinformatics, 22(1), 117--119. doi: 10.1093/bioinformatics/bti720.
    """
    biparts1 = list(tree1.iter_bipartitions())
    biparts2 = list(tree2.iter_bipartitions())
    arr, indices = _get_split_matching(biparts1, biparts2, "nye")
    nye = arr[indices].sum()
    if normalize:
        ind_info = sum(get_tree_splitwise_nye_similarity(i) for i in (tree1, tree2))
        return nye / (ind_info / 2)
    return nye


def get_trees_nye_dist(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the Nye similarity distance between two trees.
    """
    nye = get_trees_nye_similarity(tree1, tree2, normalize=False)
    ind_info = sum(get_tree_splitwise_nye_similarity(i) for i in (tree1, tree2))
    if normalize:
        return (ind_info - (2 * nye)) / ind_info
    return ind_info - (2 * nye)


def get_trees_matching_split_dist(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the matching split distance between two trees.

    Distance is the number of elements that must be moved from one
    subset to another in order to make the two splits identical.
    """
    biparts1 = list(tree1.iter_bipartitions())
    biparts2 = list(tree2.iter_bipartitions())
    arr, indices = _get_split_matching(biparts1, biparts2, "ms")
    msd = arr[indices].sum()
    if normalize:
        logger.warning("no normalization method for matching split distance.")
    return msd


def get_trees_matching_split_info(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the matching split info distance between two trees.

    Matching uses the number of elements that must be moved from one
    subset to another in order to make the two splits identical, but,
    then the phylo info is returned for each match.
    """
    biparts1 = list(tree1.iter_bipartitions())
    biparts2 = list(tree2.iter_bipartitions())
    arr, indices = _get_split_matching(biparts1, biparts2, "msi")
    msi = arr[indices].sum()
    if normalize:
        ind_info = sum(get_tree_splitwise_phylo_info(i) for i in (tree1, tree2))
        return msi / (ind_info / 2)
    return msi


def get_trees_matching_split_info_dist(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the matching split info distance between two trees.

    Matching uses the number of elements that must be moved from one
    subset to another in order to make the two splits identical, but,
    then the phylo info is returned for each match.
    """
    msi = get_trees_matching_split_info(tree1, tree2, normalize=False)
    ind_info = sum(get_tree_splitwise_phylo_info(i) for i in (tree1, tree2))
    if normalize:
        return (ind_info - (2 * msi)) / ind_info
    return ind_info - (2 * msi)


def get_trees_shared_phylo_info(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return SPI score as sum of shared phylo info on matched splits.

    According to Martin Smith (2020):
    The SPI score measures how much the information shared between
    splits in a pair of trees narrows down the set of candidates
    that could be the ‘true’ tree, corresponding to the philosophy
    that phylogenetics seeks to reconstruct the single tree that
    accurately represents historical events.
    """
    biparts1 = list(tree1.iter_bipartitions())
    biparts2 = list(tree2.iter_bipartitions())
    arr, indices = _get_split_matching(biparts1, biparts2, "spi")
    spi = arr[indices].sum()
    if normalize:
        ind_info = sum(get_tree_splitwise_phylo_info(i) for i in (tree1, tree2))
        return spi / (ind_info / 2)
    return spi


def get_trees_shared_phylo_info_dist(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return difference in phylogenetic information betweern two trees.

    This is synonymous with the Phylogenetic Information Distance (pid)
    and thus synonymous with the function `get_treedist_pid`, although
    the latter has default of normalization=True.
    """
    spi = get_trees_shared_phylo_info(tree1, tree2, normalize=False)
    ind_info = sum(get_tree_splitwise_phylo_info(i) for i in (tree1, tree2))
    if normalize:
        if not ind_info:
            return 0.
        return (ind_info - (2 * spi)) / ind_info
    return ind_info - (2 * spi)


def get_trees_shared_phylo_info_dist_from_biparts(
    biparts1: Sequence[Tuple[Tuple, Tuple]],
    biparts2: Sequence[Tuple[Tuple, Tuple]],
    normalize: bool = False,
) -> float:
    """Return difference in phylogenetic information betweern two trees.

    This is synonymous with the Phylogenetic Information Distance (pid)
    and thus synonymous with the function `get_treedist_pid`, although
    the latter has default of normalization=True.
    """
    arr, indices = _get_split_matching(biparts1, biparts2, "spi")
    spi = arr[indices].sum()
    info1 = sum(_get_split_phylo_info(i) for i in biparts1)
    info2 = sum(_get_split_phylo_info(i) for i in biparts2)
    ind_info = info1 + info2
    if normalize:
        return (ind_info - (2 * spi)) / ind_info
    return ind_info - (2 * spi)


def get_trees_mutual_clust_info(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the mutual clustering information (cid).

    """
    biparts1 = list(tree1.iter_bipartitions())
    biparts2 = list(tree2.iter_bipartitions())
    arr, indices = _get_split_matching(biparts1, biparts2, "mci")
    mci = arr[indices].sum()
    if normalize:
        ind_info = sum(get_tree_splitwise_entropy(i) for i in (tree1, tree2))
        return mci / (ind_info / 2)
    return mci


@add_subpackage_method(TreeDistanceAPI)
def get_trees_mutual_clust_info_dist(
    tree1: ToyTree, tree2: ToyTree, normalize: bool = False,
) -> float:
    """Return the mutual clustering information distance (cid).

    """
    mci = get_trees_mutual_clust_info(tree1, tree2, normalize=False)
    ind_info = sum(get_tree_splitwise_entropy(i) for i in (tree1, tree2))
    if normalize:
        return (ind_info - (2 * mci)) / ind_info
    return ind_info - (2 * mci)


@add_subpackage_method(TreeDistanceAPI)
def get_trees_mutual_clust_info_dist_from_biparts(
    biparts1: Sequence[Tuple[Tuple, Tuple]],
    biparts2: Sequence[Tuple[Tuple, Tuple]],
    normalize: bool = False,
) -> float:
    """Return the mutual clustering information distance (cid).

    """
    arr, indices = _get_split_matching(biparts1, biparts2, "mci")
    mci = arr[indices].sum()
    info1 = sum(_get_split_entropy(b) for b in biparts1)
    info2 = sum(_get_split_entropy(b) for b in biparts2)
    ind_info = info1 + info2
    if normalize:
        return mci / (ind_info / 2)
    return mci


if __name__ == "__main__":

    import toytree

    # trees from ?TreeDist::SharedPhylogeneticInfo
    t1 = toytree.tree('((((a, b), c), d), (e, (f, (g, h))));')
    t2 = toytree.tree('(((a, b), (c, d)), ((e, f), (g, h)));')
    t3 = toytree.tree('((((h, b), c), d), (e, (f, (g, a))));')

    # t1 = toytree.tree('((A, B), ((C, (D, E)), (F, (G, (H, I)))));')
    # t2 = toytree.tree('((A, B), ((C, D, (E, I)), (F, (G, H))));')

    # phy info for a split:
    # print(_get_phylo_info(0, 0))


    # phy info for a tree (all splits): SplitWiseInfo(tree1) = 22.54
    print(get_tree_splitwise_phylo_info(t1)) # 22.54
    print(get_tree_splitwise_phylo_info(t2)) # 19.36

    print("MCI ", get_trees_mutual_clust_info(t1, t2)) # 3.03
    print("nMCI", get_trees_mutual_clust_info(t1, t2, True)) # 0.6908

    print("CID ", get_trees_mutual_clust_info_dist(t1, t2)) # 2.71
    print("nCID", get_trees_mutual_clust_info_dist(t1, t2, normalize=True)) # 0.3091

    print("MS ", get_trees_matching_split_dist(t1, t2)) # 6

    print("MSI ", get_trees_matching_split_info(t1, t2)) # 17.09
    print("nMSI", get_trees_matching_split_info(t1, t2, normalize=True)) # 0.815

    print("MSID ", get_trees_matching_split_info_dist(t1, t2)) # 7.72
    print("nMSID", get_trees_matching_split_info_dist(t1, t2, normalize=True)) # 0.185

    print("NYE ", get_trees_nye_similarity(t1, t2)) # 3.8
    print("nNYE ", get_trees_nye_similarity(t1, t2, normalize=True)) # 0.76

    print("NYED ", get_trees_nye_dist(t1, t2)) # 3.8
    print("nNYED ", get_trees_nye_dist(t1, t2, normalize=True)) # 0.76

    _report_matching(t1, t2, 'ms')

    # how similar are two trees? SharedPhylogeneticInfo(t1, t2) = 13.75
    # print(get_trees_phylo_info_shared(t1, t2), "shared")

    # how different are two trees? DifferentPhylogeneticInfo(t1, t2) = 14.40
    # print(get_trees_phylo_info_different(t1, t2, 1), "different")

    # _get_two_splits_shared_phylo_info()

    # PhylogeneticInfoDistance === DifferentPhylogeneticInfo
    # phy info diff for two trees: DifferentPhylogenetic Info
    # print(_get_split_matching(t1, t2, "mci"))
    # _visualize_matching(t1, t2)

    # split = set([range(60), range(60, 100)]) # 0.97 bits
    # split = set([range(50), range(50, 100)]) # 1 bits

    # split1 = set([range(60), range(60, 100)]) # 0.97 bits
    # split2 = set([range(0, 50), range(50, 100)]) # 1 bits
    # print(_get_entropy_distance(split1, split2))
    # print(_get_entropy_of_pair_split()  # 1.36 bits

    # t1 = toytree.rtree.unittree(6, seed=333)

    # for bipart in t1._iter_bipartitions():
    #     bip1 = ",".join(bipart[0])
    #     bip2 = ",".join(bipart[1])

    #     for dipart in t1._iter_bipartitions():
    #         dip1 = ",".join(dipart[0])
    #         dip2 = ",".join(dipart[1])

    #         e = _get_two_splits_entropy(bipart, dipart)
    #         print(
    #             f"{bip1}|{bip2} {_get_split_entropy(bipart):.2f} . "
    #             f"{dip1}|{dip2} {_get_split_entropy(dipart):.2f} . "
    #             f"{e[2]:.2f} {e[3]:.2f} {e[4]:.2f}"
            # )

    # t0 = toytree.tree('((a, b, c, d, e, f), (g, h, i, j));')
    # t1 = toytree.tree('((a, b, c, d, e, i, j), (g, h, f));')

    # b0 = t0._iter_bipartitions()
    # b1 = t1._iter_bipartitions()

    # for i in b0:
    #     for j in b1:
    #         print(i, j, _get_two_splits_matching_info(i, j))