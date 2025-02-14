#!/usr/env/bin python

"""Tree distance metrics for measuring differences between trees.

Tree distance methods decompose trees into sets of bipartitions or
quartets, and use one of several methods for measuring differences
based on these sets, or additional features of the sets.

bipartition = {0, 1} | {2, 3, 4}
quartets = {0, 1} | {2, 3}; {0, 1} | {2, 4}; {0, 1} | {3, 4},

Authors
-------
- Deren Eaton, Scarlet Ming-sha Au

Note
----
If there was a real need for speed with tree distance functions
they could be easily sped up by adding jit decorators to various
set comparison functions, but this has not been done yet.

TODO: clean up references
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
- Meila M (2007). “Comparing clusterings-an information based
  distance.” _Journal of Multivariate Analysis_, *98*(5), 873-895.
  doi: 10.1016/j.jmva.2006.11.013 (URL:
  https://doi.org/10.1016/j.jmva.2006.11.013).
"""

from typing import Set, Callable, Union, Iterator, Tuple, Optional

from loguru import logger
import numpy as np
import pandas as pd
from toytree.distance._src.treedist_utils import (
    _get_split_phylo_info,
    get_trees_nye_dist,
    get_trees_matching_split_dist,
    get_trees_matching_split_info_dist,
    get_trees_shared_phylo_info_dist,
    get_trees_mutual_clust_info_dist,
    get_trees_shared_phylo_info_dist_from_biparts,
    get_trees_mutual_clust_info_dist_from_biparts,
)
from toytree import ToyTree
from toytree.core.apis import TreeDistanceAPI, add_subpackage_method
from toytree.utils import ToytreeError

logger = logger.bind(name="toytree")


TIPS_IDENTICAL = "Treedist methods require that trees share identical tip names."


# put functions here to have then exposed to 'distance' subpackage API
__all__ = [
    "get_treedist_rf",
    "get_treedist_rfi",
    "get_treedist_rfg_ms",
    "get_treedist_rfg_msi",
    "get_treedist_rfg_spi",
    "get_treedist_rfg_mci",
]


###################################################################
# Get distance metrics from bipartition sets and additional info
###################################################################

def _get_rf_distance(
    set1: Set, set2: Set, normalize: bool = True,
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
    set1: Set, set2: Set, normalize: bool = True,
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

    The Robinson-Foulds distance is a normalized count of the
    bipartitions induced by one tree, but not the other tree, i.e.,
    it is the symmetric difference between two bipart sets divided
    by the total number of (internal) bipartitions in both sets.
    Larger values indicate that two trees are more different.

    Parameters:
        tree1: ToyTree
            An input ToyTree to compare to tree2.
        tree2: ToyTree
            An input ToyTree to compare to tree1.
        normalize: bool
            Normalize distance score by the total number of splits in
            both trees (the max number of possible differences).

    Examples:
        >>> t0 = toytree.rtree.unittree(ntips=10, seed=123)
        >>> t1 = toytree.rtree.unittree(ntips=10, seed=321)
        >>> t0.distance.get_treedist_rf(t1, normalize=False)
        ...
        >>> t0.distance.get_treedist_rf(t1, normalize=True)
        ...

    References:
        1. Robinson, D.F. and Foulds, L.R. (1981) "Comparison of phylogenetic
        trees". Mathematical Biosciences. 53 (1–2): 131–147.
        doi:10.1016/0025-5564(81)90043-2.
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
    """Return the information-corrected Robinson-Foulds distance (rfi).

    This distance measure is the sum of of the phylogenetic information
    of edges that are different between two trees, where information
    is calculated as the probability that a randomly sampled binary
    tree of the same size contains the split. Splits that contain less
    information (e.g., a cherry vs a deep split) are more likely to
    arise by chance, and thus contribute less to the metric.

    Parameters
    ----------
    tree1: ToyTree
        A ToyTree to compare to tree2.
    tree2: ToyTree
        A ToyTree to compare to tree1.
    normalize: bool
        Normalize score relative to the sum of phylogenetic info
        present in both subtrees.

    References
    ----------
    - Martin Smith: https://cran.r-project.org/web/packages/TreeDist/vignettes/information.html
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    set1 = set(tree1.iter_bipartitions(type=frozenset, sort=True))
    set2 = set(tree2.iter_bipartitions(type=frozenset, sort=True))
    return _get_rf_distance_information_corrected(set1, set2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_ms(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = True,
) -> float:
    """Return the Matching Split Distance.

    Parameters
    ----------
    tree1: ToyTree
        A ToyTree to compare to tree2.
    tree2: ToyTree
        A ToyTree to compare to tree1.
    normalize: bool
        Normalize score relative to the sum of phylogenetic info
        present in both subtrees.

    References
    ----------
    - Bogdanowicz & Giaro (2012)
    """
    return get_trees_matching_split_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_msi(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = True,
) -> float:
    """Return the Matching Split Information Distance.

    Parameters
    ----------
    tree1: ToyTree
        A ToyTree to compare to tree2.
    tree2: ToyTree
        A ToyTree to compare to tree1.
    normalize: bool
        Normalize score relative to the sum of phylogenetic info
        present in both subtrees.

    References
    ----------
    - Bogdanowicz & Giaro (2012)
    - Martin Smith (2020)
    """
    return get_trees_mutual_clust_info_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_spi(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = False,
) -> float:
    """Return generalized Robinson-Foulds Distance between two trees
    based on Shared Phylogenetic Information (SPI).

    Generalized Robinson–Foulds distances calculate tree similarity by
    finding an optimal matching of splits between two trees, even
    among non-identical splits, on which to compute shared information.
    Here the 'shared phylogenetic information' metric is used to
    meausure the information that two trees hold in common, following
    Martin Smith (2020).

    Parameters
    ----------

    See Also
    --------

    References
    ----------
    - Smith, Martin R. (2020). "Information theoretic Generalized
      Robinson-Foulds metrics for comparing phylogenetic trees".
      Bioinformatics. 36 (20): 5007–5013. doi:10.1093/bioinformatics/btaa614.
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    return get_trees_shared_phylo_info_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_mci(
    tree1: ToyTree,
    tree2: ToyTree,
    normalize: bool = False,
) -> float:
    """Return generalized Robinson-Foulds Distance between two trees
    based on Mutual Clustering Information (MCI).

    Generalized Robinson–Foulds distances calculate tree similarity by
    finding an optimal matching of splits between two trees, even
    among non-identical splits, on which to compute shared information.
    Here the 'mutual clustering information' metric is used to
    meausure the information that two trees hold in common.

    This is the recommended metric for tree comparisons by Martin
    Smith (2020).

    Parameters
    ----------
    tree1: ToyTree
        A tree that will be compared to the second.
    tree2: ToyTree
        A tree that will be compared to the first.
    normalize: bool
        ...

    See Also
    --------

    References
    ----------
    - https://cran.r-project.org/web/packages/TreeDist/vignettes/Robinson-Foulds.html
    """
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels()), TIPS_IDENTICAL
    return get_trees_mutual_clust_info_dist(tree1, tree2, normalize)


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_rfg_jac(
    tree1: ToyTree,
    tree2: ToyTree,
    k=1,
    allow_conflict: bool = True,
    normalize: bool = False,
) -> float:
    """Return generalized Robinson-Foulds Distance between two trees
    based on Nye Similarity metric.

    The Jaccard Robinson Foulds distance is a Generalized
    Robinson-Foulds metric based on the tree comparison method of
    Nye et al. (2006), and extended by Böcker et al. (2013).

    An optimal matching of bipartitions is found between two trees
    where pair scores represent the size of the largest split that is
    consistent with both them, normalized against the Jaccard index.

    Parameters
    ----------
    k: int
        An arbitrary exponent to which to raise the Jaccard Index. The
        Nye metric uses k=1; as k increases to infinity the metric
        converges on the standard RF metric.
    allow_conflict: bool
        If True conflicting splits that be paired, else they are given
        a score of zero.
    normalize: bool
        If True the score is normalized by the ...

    Notes
    -----

    See Also
    --------
    `toytree.distance.visualize_matching`

    Examples
    --------
    >>> tree1 = toytree.rtree.unittree(10, seed=123)
    >>> tree2 = toytree.rtree.unittree(10, seed=321)
    >>> tree1.distance.get_treedist_rfg_jac(tree2)   # ...
    >>> tree1.distance.get_treedist_rfg_jac(tree2, k=2)   # ...
    >>> tree1.distance.get_treedist_rfg_jac(tree2, k=2, allow_conflict=False)  # ...

    References
    ----------
    - Nye et al. (2006)
    - Böcker et al. 2013)
    - https://ms609.github.io/TreeDist/reference/JaccardRobinsonFoulds.html
    """
    raise NotImplementedError("TODO")


def get_treedist_kf_branch_score(
    tree1: ToyTree,
    tree2: ToyTree,
) -> float:
    """Return the Kune-Felsenstein metric...

    The Branch Score Distance of Kuhner and Felsenstein (1994) compares
    two trees using information of their branch lengths. It finds all
    bipartitions in the tree, and their branch lengths, as well as all
    possible alternative bipartitions that are not in the tree, which
    are assigned branch lenghts of zero.

    Reference
    ---------
    - Kuhner, M. K. and Felsenstein, J. (1994) Simulation comparison of
      phylogeny algorithms under equal and unequal evolutionary rates.
      Molecular Biology and Evolution, 11, 459–468.
    """
    raise NotImplementedError("TODO")
    utree = tree.unroot()
    iter_biparts = tree.iter_bipartitions(include_singleton_partitions=True)
    for node, bipart in zip(tree, iter_biparts):
        if node._up.is_root():
            "add dist to ..."
        print((node, node.up), node._dist, bipart)


def get_treedist_matrix(
    *trees: ToyTree,
    metric: Callable,
    normalize: bool = True,
    **kwargs,
) -> pd.DataFrame:
    """Return ...

    This is a generalization of `get_treedist_x` methods that
    arranges results for multiple tree comparisons into a dataframe.

    Parameters
    ----------

    Examples
    --------
    >>> tree1 = toytree.rtree.unittree(ntips=10, seed=123)
    >>> tree2 = toytree.rtree.unittree(ntips=10, seed=321)
    >>> ...
    """
    raise NotImplementedError("TODO")


##############################################################
#
#  NORMALIZATION
#
##############################################################

def _expected_variation(
    tree1: ToyTree,
    tree2: ToyTree,
    metric: str,
    nsamples: int = 1e+4,
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

    data['estimate'] = reps.mean()
    data['stdev'] = reps.std()
    data['stderr'] = data.stdev / np.sqrt(nsamples)
    data['nsamples'] = nsamples
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


##############################################################
#
#  VALIDATION FUNCTIONS FOR COMPARING TO R LIBRARY
#
#  TODO: move this to a test/ directory
##############################################################

def _test_with_treedist_r(
    tree1: ToyTree,
    tree2: ToyTree,
    method: str = "rf",
    normalize: bool = True,
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
    elif method == "rfg_spi":
        func = "PhylogeneticInfoDistance"
    elif method == "rfg_mci":
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
        # log the error
        try:
            out = float(out.split()[-1])
        except (ValueError, IndexError):
            logger.error(out)
    return out


def _validate(tree1, tree2):
    """Return dataframe with results for toytree and TreeDist"""
    algorithms = {
        "rf": get_treedist_rf,
        "rfi": get_treedist_rfi,
        "rfg_spi": get_treedist_rfg_spi,
        "rfg_mci": get_treedist_rfg_mci,
        # "qrt": get_treedist_qrt,
    }
    anames = list(algorithms) + [i + "-norm" for i in algorithms]
    data = pd.DataFrame(
        index=anames,
        columns=["toytree", "TreeDist"],
        data=0,
    )

    for algo, func in algorithms.items():
        for norm in (True, False):
            toy = func(tree1, tree2, normalize=norm)
            trd = _test_with_treedist_r(tree1, tree2, algo, norm)
            aname = algo + "-norm" if norm else algo
            data.loc[aname] = toy, trd
    return data


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
