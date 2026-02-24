#!/usr/env/bin python

"""Tree distance metrics for comparing phylogenetic tree topologies.

This module implements split- (bipartition-) based tree distance metrics
exposed through ``ToyTree.distance`` and module-level helpers. Implemented
methods include the Robinson-Foulds (RF) distance and several generalized
Robinson-Foulds variants that compare trees using split matching and
information-based scores.

Most public functions require that the compared trees share identical tip
labels. Core matching and information calculations are delegated to helper
functions in :mod:`toytree.distance._src.treedist_utils`.

Tree distance methods are often described using either bipartitions (splits)
or quartets. A split is the bipartition induced by an edge (for example,
``{0, 1} | {2, 3, 4}``), whereas quartets summarize induced relationships for
4-taxon subsets. This module currently emphasizes split-based metrics; some
additional distance interfaces in this file remain placeholders.

Notes
-----
Some metrics spend most of their time in set operations and split-matching
steps. The current implementation prioritizes correctness and readability.
Compiled / JIT-accelerated variants could improve performance in the future.

References
----------
- Robinson, D. F., & Foulds, L. R. (1981). Comparison of phylogenetic trees.
  *Mathematical Biosciences*, 53(1-2), 131-147.
  https://doi.org/10.1016/0025-5564(81)90043-2
- Smith, M. R. (2020). Information theoretic Generalized Robinson-Foulds
  metrics for comparing phylogenetic trees. *Bioinformatics*, 36(20),
  5007-5013. https://doi.org/10.1093/bioinformatics/btaa614
- Llabrés, M., Rosselló, F., & Valiente, G. (2021). The Generalized
  Robinson-Foulds Distance for Phylogenetic Trees. *Journal of Computational
  Biology*. https://doi.org/10.1089/cmb.2021.0342
- Sand, A., Holt, M. K., Johansen, J., Brodal, G. S., Mailund, T., &
  Pedersen, C. N. S. (2014). tqDist: a library for computing the quartet and
  triplet distances between binary or general trees. *Bioinformatics*,
  30(14), 2079-2080. https://doi.org/10.1093/bioinformatics/btu157
- Meila, M. (2007). Comparing clusterings—an information based distance.
  *Journal of Multivariate Analysis*, 98(5), 873-895.
  https://doi.org/10.1016/j.jmva.2006.11.013
- TreeDist vignette (Robinson-Foulds metrics):
  https://cran.r-project.org/web/packages/TreeDist/vignettes/Robinson-Foulds.html
- TreeDist vignette (information-based metrics):
  https://cran.r-project.org/web/packages/TreeDist/vignettes/information.html
- Robinson-Foulds metric overview (background):
  https://en.wikipedia.org/wiki/Robinson%E2%80%93Foulds_metric
"""

from typing import Callable, Iterator, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

from toytree import ToyTree, ToytreeError
from toytree.core.apis import TreeDistanceAPI, add_subpackage_method
from toytree.distance._src.treedist_utils import (
    _get_split_phylo_info,
    get_trees_matching_split_dist,
    get_trees_matching_split_info_dist,
    get_trees_mutual_clust_info_dist,
    get_trees_mutual_clust_info_dist_from_biparts,
    get_trees_shared_phylo_info_dist,
    get_trees_shared_phylo_info_dist_from_biparts,
)

TIPS_IDENTICAL = "Treedist methods require that trees share identical tip names."


# put functions here to have then exposed to 'distance' subpackage API
__all__ = [
    "get_treedist_rf",
    "get_treedist_rfi",
    "get_treedist_rfg_ms",
    "get_treedist_rfg_msi",
    "get_treedist_rfg_spi",
    "get_treedist_rfg_mci",
    "get_treedist_kf_branch_score",
]


###################################################################
# Get distance metrics from bipartition sets and additional info
###################################################################


def _get_rf_distance(
    set1: Set,
    set2: Set,
    normalize: bool = True,
) -> float:
    """Return RF distance between two bipartition sets.

    The Robinson-Foulds distance is a normalized count of the
    bipartitions induced by one tree, but not the other tree, i.e.,
    it is the symmetric difference between two bipart sets divided
    by the total number of (internal) bipartitions in both sets.

    Parameters
    ----------
    set1: set
        A set of bipartitions in tree1 (e.g., tree1.iter_bipartitions)
    set2: set
        A set of bipartitions in tree2 (e.g., tree2.iter_bipartitions)
    normalize: bool
        Normalize distance score by the total number of splits in
        both trees (the max number of possible differences).
    """
    # get symmetric difference of bipartitions sets
    sym_diff = set1 ^ set2
    score = len(sym_diff)

    # normalize by the total number of internal edges.
    if normalize:
        return score / sum(len(i) for i in (set1, set2))
    return score


def _get_rf_distance_information_corrected(
    set1: Set,
    set2: Set,
    normalize: bool = True,
) -> float:
    """Return the information-corrected Robinson-Foulds distance (rfi).

    This distance measure is the sum of of the phylogenetic information
    of edges that are different between two trees, where information
    is calculated as the probability that a randomly sampled binary
    tree of the same size contains the split. Splits that contain
    less information (e.g., a cherry vs a deep split) are more likely
    to arise by chance, and thus contribute less to the metric.

    See Also
    --------
    - `get_treedist_rf`

    References
    ----------
    - Martin Smith: https://cran.r-project.org/web/packages/TreeDist/vignettes/information.html
    """
    # get total phylo info from the union of splits
    total_info = sum(_get_split_phylo_info(s) for s in set1 | set2)

    # get sum of phylo info on the shared splits
    shared = set1 & set2
    shared_info = sum(_get_split_phylo_info(s) for s in shared)

    # distance = (total phylo info) - (shared phylo info)
    # normalization = distance / (... options). The default normalizer
    # in rfi is sum of phyinfo in both trees independently, following
    # the default in TreeDist.
    if normalize:
        # default normalization (True)
        norm1 = sum(_get_split_phylo_info(s) for s in set1)
        norm2 = sum(_get_split_phylo_info(s) for s in set2)
        if normalize in ["sum", True]:
            return (total_info - shared_info) / sum((norm1, norm2))
        # other options (min, max, avg, )
        # elif normalize == "max":
        #     norm = max(norm1, norm2)
        # elif normalize == "avg":
        #     norm = (norm1 + norm2) / 2.
        # elif normalize == "min":
        #     norm = min(norm1, norm2)
    return total_info - shared_info


def _get_unrooted_bipartition_length_map(tree: ToyTree) -> dict:
    """Return branch lengths keyed by canonical unrooted bipartitions."""
    utree = tree if not tree.is_rooted() else tree.unroot()
    biparts = utree.iter_bipartitions(
        feature="name",
        include_singleton_partitions=True,
        type=tuple,
        sort=True,
    )
    data = {}
    # iter_bipartitions() yields one split per non-root node in idx order.
    # On an unrooted tree this aligns with utree[:-1], which stores edge lengths.
    for node, bipart in zip(utree[:-1], biparts):
        data[bipart] = float(node.dist)
    return data


##############################################################
#
#  PUBLIC METHODS
#
##############################################################


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rf(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: Union[bool, int, Callable] = False,
) -> float:
    """Return the Robinson-Foulds (RF) distance between two trees.

    The RF distance measures topological disagreement as the symmetric
    difference between the sets of internal bipartitions (splits) induced by
    two trees. Larger values indicate greater topological difference.

    This implementation compares canonical split sets generated with
    ``iter_bipartitions(type=frozenset, sort=True)`` and requires the two trees
    to share identical tip labels.

    Parameters
    ----------
    tree1 : ToyTree
        First tree to compare.
    tree2 : ToyTree
        Second tree to compare.
    normalize : bool, default=False
        If ``True``, divide the RF count by the total number of internal splits
        across both trees (the denominator used by this implementation). If
        ``False``, return the raw symmetric-difference count.

    Returns
    -------
    float
        The RF distance. This is an integer-valued count when
        ``normalize=False`` and a normalized score when ``normalize=True``.

    Raises
    ------
    AssertionError
        If the two trees do not share identical tip labels.

    Examples
    --------
    >>> t1 = toytree.tree("((a,b),(c,d));")
    >>> t2 = toytree.tree("((a,c),(b,d));")
    >>> t1.distance.get_treedist_rf(t2, normalize=False)
    2.0
    >>> t1.distance.get_treedist_rf(t2, normalize=True)
    1.0

    References
    ----------
    Robinson, D. F., & Foulds, L. R. (1981). Comparison of phylogenetic
    trees. *Mathematical Biosciences*, 53(1-2), 131-147.
    https://doi.org/10.1016/0025-5564(81)90043-2
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    set1 = set(tree1.iter_bipartitions(type=frozenset, sort=True))
    set2 = set(tree2.iter_bipartitions(type=frozenset, sort=True))
    return _get_rf_distance(set1, set2, normalize=normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfi(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = False,
) -> float:
    """Return the information-corrected Robinson-Foulds distance (RFI).

    The RFI distance is an RF-like split distance that weights disagreement by
    the phylogenetic information content of splits. Splits that are more likely
    to occur by chance (for example, some shallow splits) contribute less than
    more informative splits.

    This implementation computes information-weighted disagreement from the
    union and intersection of canonical split sets generated with
    ``iter_bipartitions(type=frozenset, sort=True)`` and requires the two trees
    to share identical tip labels.

    Parameters
    ----------
    tree1 : ToyTree
        First tree to compare.
    tree2 : ToyTree
        Second tree to compare.
    normalize : bool, default=False
        If ``True``, divide by the sum of phylogenetic information in the split
        sets of both trees (the default ``"sum"`` normalization used by this
        implementation). If ``False``, return the raw information-weighted
        disagreement.

    Returns
    -------
    float
        The information-corrected Robinson-Foulds distance.

    Raises
    ------
    AssertionError
        If the two trees do not share identical tip labels.

    Examples
    --------
    >>> t1 = toytree.tree("((a,b),(c,d));")
    >>> t2 = toytree.tree("((a,c),(b,d));")
    >>> round(t1.distance.get_treedist_rfi(t2, normalize=False), 6)
    3.169925
    >>> t1.distance.get_treedist_rfi(t2, normalize=True)
    1.0

    References
    ----------
    Smith, M. R. (2020). Information theoretic Generalized Robinson-Foulds
    metrics for comparing phylogenetic trees. *Bioinformatics*, 36(20),
    5007-5013. https://doi.org/10.1093/bioinformatics/btaa614

    TreeDist information vignette:
    https://cran.r-project.org/web/packages/TreeDist/vignettes/information.html
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    set1 = set(tree1.iter_bipartitions(type=frozenset, sort=True))
    set2 = set(tree2.iter_bipartitions(type=frozenset, sort=True))
    return _get_rf_distance_information_corrected(set1, set2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_ms(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = False,
) -> float:
    """Return the Matching Split Distance (MS).

    The Matching Split Distance is a generalized Robinson-Foulds-style metric
    that compares trees by optimally matching splits between trees, rather than
    counting only exact split matches and mismatches. This wrapper delegates to
    :func:`toytree.distance._src.treedist_utils.get_trees_matching_split_dist`.

    Parameters
    ----------
    tree1 : ToyTree
        First tree to compare.
    tree2 : ToyTree
        Second tree to compare.
    normalize : bool, default=False
        Normalization flag passed to the underlying implementation. Only
        ``False`` is currently supported; ``True`` raises ``ToytreeError``.

    Returns
    -------
    float
        The raw matching split distance.

    Raises
    ------
    ToytreeError
        If ``normalize=True`` is requested (currently unsupported by the
        underlying matching-split implementation).

    Examples
    --------
    >>> t1 = toytree.tree("((a,b),(c,d));")
    >>> t2 = toytree.tree("((a,c),(b,d));")
    >>> t1.distance.get_treedist_rfg_ms(t2, normalize=False)
    2.0

    Notes
    -----
    The ``normalize`` argument is part of the public signature for API
    consistency with related tree-distance functions, but normalization is not
    currently implemented for this metric in the underlying routine.

    References
    ----------
    Bogdanowicz, D., & Giaro, K. (2012).
    """
    return get_trees_matching_split_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_msi(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = True,
) -> float:
    """Return the Matching Split Information distance (MSI).

    MSI is a generalized Robinson-Foulds-style metric that compares trees by
    optimally matching splits and then scoring disagreement using split
    information content. Relative to a count-based matching-split distance,
    mismatches involving more informative splits contribute more strongly.

    Parameters
    ----------
    tree1 : ToyTree
        First tree to compare.
    tree2 : ToyTree
        Second tree to compare.
    normalize : bool, default=True
        If ``True``, return the normalized MSI score from the underlying
        implementation. If ``False``, return the raw information-weighted
        distance.

    Returns
    -------
    float
        The matching split information distance (raw or normalized).

    Raises
    ------
    Exception
        Propagated validation errors from the underlying matching-split
        information implementation (for example, incompatible tree inputs).

    Examples
    --------
    >>> t1 = toytree.tree("((a,b),(c,d));")
    >>> t2 = toytree.tree("((a,c),(b,d));")
    >>> round(t1.distance.get_treedist_rfg_msi(t2, normalize=False), 6)
    3.169925
    >>> t1.distance.get_treedist_rfg_msi(t2, normalize=True)
    1.0

    Notes
    -----
    This metric supports normalization (unlike ``get_treedist_rfg_ms``), and
    ``normalize=True`` is the default.

    References
    ----------
    Bogdanowicz, D., & Giaro, K. (2012).

    Smith, M. R. (2020). Information theoretic Generalized Robinson-Foulds
    metrics for comparing phylogenetic trees. *Bioinformatics*, 36(20),
    5007-5013. https://doi.org/10.1093/bioinformatics/btaa614
    """
    return get_trees_matching_split_info_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_spi(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = False,
) -> float:
    """Return the Shared Phylogenetic Information distance (SPI).

    SPI is a generalized Robinson-Foulds-style metric that compares trees by
    optimally matching splits and scoring disagreement using shared
    phylogenetic information. Relative to count-based split metrics,
    disagreements involving more informative splits contribute more strongly.

    Parameters
    ----------
    tree1 : ToyTree
        First tree to compare.
    tree2 : ToyTree
        Second tree to compare.
    normalize : bool, default=False
        If ``True``, return the normalized SPI distance from the underlying
        implementation. If ``False``, return the raw SPI-based distance.

    Returns
    -------
    float
        The shared phylogenetic information distance (raw or normalized).

    Raises
    ------
    AssertionError
        If the two trees do not share identical tip labels.

    Examples
    --------
    >>> t1 = toytree.tree("((a,b),(c,d));")
    >>> t2 = toytree.tree("((a,c),(b,d));")
    >>> round(t1.distance.get_treedist_rfg_spi(t2, normalize=False), 6)
    3.169925
    >>> t1.distance.get_treedist_rfg_spi(t2, normalize=True)
    1.0

    Notes
    -----
    This metric supports normalization, but unlike ``get_treedist_rfg_msi`` the
    default for this wrapper is ``normalize=False``.

    References
    ----------
    Smith, M. R. (2020). Information theoretic Generalized Robinson-Foulds
    metrics for comparing phylogenetic trees. *Bioinformatics*, 36(20),
    5007-5013. https://doi.org/10.1093/bioinformatics/btaa614

    TreeDist information vignette:
    https://cran.r-project.org/web/packages/TreeDist/vignettes/information.html
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    return get_trees_shared_phylo_info_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_mci(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = False,
) -> float:
    """Return the Mutual Clustering Information distance (MCI).

    MCI is a generalized Robinson-Foulds-style metric that compares trees by
    optimally matching splits and scoring disagreement using a mutual
    clustering-information criterion. Relative to split-count metrics, it
    provides an information-theoretic view of topological difference.

    This wrapper delegates to
    :func:`toytree.distance._src.treedist_utils.get_trees_mutual_clust_info_dist`.

    Parameters
    ----------
    tree1 : ToyTree
        First tree to compare.
    tree2 : ToyTree
        Second tree to compare.
    normalize : bool, default=False
        If ``True``, return the normalized MCI distance from the underlying
        implementation. If ``False``, return the raw MCI-based distance.

    Returns
    -------
    float
        The mutual clustering information distance (raw or normalized).

    Raises
    ------
    AssertionError
        If the two trees do not share identical tip labels.

    Examples
    --------
    >>> t1 = toytree.tree("((a,b),(c,d));")
    >>> t2 = toytree.tree("((a,c),(b,d));")
    >>> t1.distance.get_treedist_rfg_mci(t2, normalize=False)
    2.0
    >>> t1.distance.get_treedist_rfg_mci(t2, normalize=True)
    1.0

    Notes
    -----
    This metric supports normalization, but the wrapper default is
    ``normalize=False``. TreeDist-related documentation often recommends MCI
    for general tree comparison use cases.

    References
    ----------
    Smith, M. R. (2020). Information theoretic Generalized Robinson-Foulds
    metrics for comparing phylogenetic trees. *Bioinformatics*, 36(20),
    5007-5013. https://doi.org/10.1093/bioinformatics/btaa614

    TreeDist Robinson-Foulds vignette:
    https://cran.r-project.org/web/packages/TreeDist/vignettes/Robinson-Foulds.html
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    return get_trees_mutual_clust_info_dist(tree1, tree2, normalize)


# @add_subpackage_method(TreeDistanceAPI)
# def get_treedist_rfg_jac(
#     tree1: ToyTree,
#     tree2: ToyTree,
#     k=1,
#     allow_conflict: bool = True,
#     normalize: bool = False,
# ) -> float:
#     """Return generalized Robinson-Foulds Distance between two trees
#     based on Nye Similarity metric.

#     The Jaccard Robinson Foulds distance is a Generalized
#     Robinson-Foulds metric based on the tree comparison method of
#     Nye et al. (2006), and extended by Böcker et al. (2013).

#     An optimal matching of bipartitions is found between two trees
#     where pair scores represent the size of the largest split that is
#     consistent with both them, normalized against the Jaccard index.

#     Parameters
#     ----------
#     k: int
#         An arbitrary exponent to which to raise the Jaccard Index. The
#         Nye metric uses k=1; as k increases to infinity the metric
#         converges on the standard RF metric.
#     allow_conflict: bool
#         If True conflicting splits that be paired, else they are given
#         a score of zero.
#     normalize: bool
#         If True the score is normalized by the ...

#     Notes
#     -----

#     See Also
#     --------
#     `toytree.distance.visualize_matching`

#     Examples
#     --------
#     >>> tree1 = toytree.rtree.unittree(10, seed=123)
#     >>> tree2 = toytree.rtree.unittree(10, seed=321)
#     >>> tree1.distance.get_treedist_rfg_jac(tree2)   # ...
#     >>> tree1.distance.get_treedist_rfg_jac(tree2, k=2)   # ...
#     >>> tree1.distance.get_treedist_rfg_jac(tree2, k=2, allow_conflict=False)  # ...

#     References
#     ----------
#     - Nye et al. (2006)
#     - Böcker et al. 2013)
#     - https://ms609.github.io/TreeDist/reference/JaccardRobinsonFoulds.html
#     """
#     raise NotImplementedError("TODO")


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_kf_branch_score(
    tree1: ToyTree,
    tree2: ToyTree,
) -> float:
    """Return the Kuhner-Felsenstein branch score distance.

    The Branch Score Distance of Kuhner and Felsenstein (1994) compares
    two trees using branch lengths on the union of their induced splits.
    Splits absent from one tree are assigned branch length 0, and the
    returned value is the square root of the summed squared branch-length
    differences across all splits.

    Trees are unrooted internally before comparison, so root placement
    alone does not affect the result. Terminal branches (singleton splits)
    are included.

    Parameters
    ----------
    tree1 : ToyTree
        A tree to compare to ``tree2``.
    tree2 : ToyTree
        A tree to compare to ``tree1``.

    Returns
    -------
    float
        The Kuhner-Felsenstein branch score distance.

    Raises
    ------
    AssertionError
        If the trees do not share identical tip labels.

    Examples
    --------
    >>> t1 = toytree.tree("((a:1,b:1):1,(c:1,d:1):1);")
    >>> t2 = toytree.tree("((a:1,b:2):1,(c:1,d:1):1);")
    >>> t1.distance.get_treedist_kf_branch_score(t2)
    1.0

    References
    ----------
    Kuhner, M. K., and Felsenstein, J. (1994). Simulation comparison of
    phylogeny algorithms under equal and unequal evolutionary rates.
    Molecular Biology and Evolution, 11, 459-468.
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    dists1 = _get_unrooted_bipartition_length_map(tree1)
    dists2 = _get_unrooted_bipartition_length_map(tree2)

    total = 0.0
    # Compare branch lengths across the union of splits, using zero for any
    # split missing from one tree (the standard branch-score definition).
    for split in set(dists1) | set(dists2):
        diff = dists1.get(split, 0.0) - dists2.get(split, 0.0)
        total += diff * diff
    return float(np.sqrt(total))


##############################################################
#
#  NORMALIZATION
#
##############################################################


def _expected_variation(
    tree1: ToyTree,
    tree2: ToyTree,
    metric: str,
    nsamples: int = 1e4,
    normalize: bool = False,
    seed: Optional[int] = None,
    **kwargs,
):
    """Return expected treedist metric between N random trees.

    For most tree distant metrics normalized values are expected to
    fall between 0-1, however, a distance of 1 will rarely be achieved
    since even two completely random trees are likely to still share
    some amount of information (splits, phylo info, clustering, etc.).
    Therefore, you can instead generate a null upper bound for the
    expected distance between random trees to use as a normalizer.

    Parameters
    ----------
    ...

    Examples
    --------
    >>> # get expected RFI distance between two N-tip trees.
    >>> tree1 = toytree.rtree.unittree(ntips=10, seed=123)
    >>> tree2 = toytree.rtree.unittree(ntips=10, seed=321)
    >>> expect = expected_variation(tree1, tree2, metric="rfg_spi")
    >>> print(expect)

    >>> # get Z-score to test if observation deviates from expectation
    >>> dist = tree1.distance.get_distance_rfi(tree2)
    >>> print(dist, (dist - expect.mean) / expect.std))
    """
    nsamples = int(nsamples)
    data = pd.Series(
        index=["estimate", "stdev", "stderr", "nsamples"],
        name=f"{metric}_distance",
        dtype=float,
    )

    # select function that takes bipart sets as input
    if metric == "rf":
        metric = _get_rf_distance
    elif metric == "rfi":
        metric = _get_rf_distance_information_corrected
    elif metric == "rfg_spi":
        metric = get_trees_shared_phylo_info_dist_from_biparts
    elif metric == "rfg_mcl":
        metric = get_trees_mutual_clust_info_dist_from_biparts
    else:
        raise ToytreeError("metric not recognized")

    # get bipartition table as ndarray, and array names
    biparts1 = set(tree1.iter_bipartitions())
    btable = tree2._get_bipartitions_table(include_singleton_partitions=False).values
    names = np.array(tree2.get_tip_labels())

    # for each sample assign randomized names to tree2 topology
    reps = np.zeros(shape=nsamples)
    rng = np.random.default_rng(seed)
    for idx in range(nsamples):
        # get splits when names are randomized
        biparts2 = set(_iter_random_biparts(btable, names, rng))
        reps[idx] = metric(biparts1, biparts2, normalize=normalize, **kwargs)

    data["estimate"] = reps.mean()
    data["stdev"] = reps.std()
    data["stderr"] = data.stdev / np.sqrt(nsamples)
    data["nsamples"] = nsamples
    return data


def _iter_random_biparts(
    btable,
    names,
    rng: Optional[np.random.Generator] = None,
) -> Iterator[Tuple[Tuple[str], Tuple[str]]]:
    """Return bipartitions for a topology w/ names randomized.

    This is used to calculate the expected variation in treedists for
    metrics that do not have an expected saturating distance, and so
    it is useful to ask how different two random trees are expected
    to be for a given ntips size.
    """
    np.random.shuffle(names)
    for idx in range(btable.shape[0]):
        mask0 = btable[idx].astype(bool)
        mask1 = np.invert(mask0)
        yield (tuple(names[mask0]), tuple(names[mask1]))


if __name__ == "__main__":
    import toytree

    t1 = toytree.rtree.baltree(10)
    t2 = toytree.rtree.imbtree(10)
    # print(_expected_variation(t1, t2, 'rf'))
    # print(_expected_variation(t1, t2, 'rfi'))

    # print("\n bal v imb")
    # print(_validate(t1, t2))

    t1 = toytree.tree("(1, (2, (3, (4, (5, (6, (7, 8)))))));")
    t2 = toytree.tree("(1, (2, (3, (4, (5, (7, (6, 8)))))));")
    t3 = toytree.tree("(1, (2, (3, (5, (4, (6, (7, 8)))))));")
    t4 = toytree.tree("(1, (2, (3, 4, 5, (6, (7, 8)))));")

    tree = toytree.tree("(((A:0.1,D:0.25):0.05,C:0.01):0.2,(B:0.3,E:0.8):0.2);")
    # get_treedist_kf_branch_score(tree)

    # print("\n t1-2")
    # print(_validate(t1, t2))

    # print("\n t1-3")
    # print(_validate(t1, t3))

    # print("\n t2-4")
    # print(_validate(t2, t4))

    # t1 = toytree.rtree.baltree(10, random_names=True)
    # t2 = toytree.rtree.imbtree(10, random_names=True)
    # print(get_treedist_rf(t1, t2, True))
    # print(_expected_variation(t1, t2, 'rf', normalize=True))
    # print(_expected_variation(t1, t2, 'rfi', normalize=True))
    # print(_expected_variation(t1, t2, 'rfg_spi', normalize=True))
    # print(_expected_variation(t1, t2, 'rfg_mcl', normalize=True))
    # print(_expected_variation(t1, t2, 'rfi'))
