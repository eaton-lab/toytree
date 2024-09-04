#!/usr/bin/env python

"""Submodule for quartet distance functions.

Authors: Deren Eaton and Scarlet Ming-sha Au

Computing Tree Similarity Metrics based on Quartets

All Tree Similarity Metrics based on Quartets revolve
around the following terms:

Q = Total possible quartets
S = Resolved in the same way between the two trees
D = Resolved differently between the two trees
R1 = Unresolved in tree 1, resolved in tree 2
R2 = Unresolved in tree 2, resolved in tree1
U = unresolved in both trees
N = S + D + R1 + R2 + U

Note
----
distance = 1 - similarity

References
----------
- Estabrook GF, McMorris FR, Meacham CA (1985). “Comparison of undirected
  phylogenetic trees based on subtrees of four evolutionary units.”
  Systematic Zoology, 34(2), 193--200. doi:10.2307/2413326 .
- ...
"""

from typing import Mapping
import itertools
import pandas as pd
import numpy as np
from toytree.core import ToyTree
from toytree.core.apis import TreeDistanceAPI, add_subpackage_method
import toytree


__all__ = [
    "get_treedist_quartets",
]


def get_quartet_resolutions_table(tree: ToyTree, df: bool = False) -> np.ndarray:
    """Return an array of quartet resolutions.

    The returned table can be an array of dataframe and is ordered
    alphanumerically by the names of the tips in the tree. If the tree
    has duplicate tip names an error will be raised.
    """
    snames = sorted(tree.get_tip_labels())
    assert len(snames) == len(set(snames)), "duplicate tip names are not allowed"

    # an empty array to enumerate all quartets and their resolutions
    ntips = toytree.enum.get_num_quartets(tree.ntips)
    arr = np.zeros(ntips, dtype=np.int_)

    # a dict to map {tipset: resolved} as {frozenset(abcd): tuple(abcd)}
    # note: this has a large memory usage for large trees.
    riter = tree.enum.iter_quartets(collapse=True, type=tuple, sort=True)
    rdict = {frozenset(i): i for i in riter}

    # iterator over tuples of sorted tip names: abcd, abce, abde
    iter_snames = itertools.combinations(snames, 4)
    for idx, qrt in enumerate(iter_snames):
        resolved = rdict.get(frozenset(qrt))
        if resolved:
            arr[idx] = qrt.index(resolved[1])

    # optionally return as df with index labels for debugging
    if df:
        return pd.Series(arr, index=list(itertools.combinations(snames, 4)))
    return arr


def get_quartet_comparison(tree1: ToyTree, tree2: ToyTree) -> Mapping[str, int]:
    """Return dict of quartet similarity/resolution data for two trees.

    This is used internally. Users should call `get_quartet_metrics`.
    """
    # require trees to share the same tips
    assert set(tree1.get_tip_labels()) == set(tree2.get_tip_labels())

    # get each quartet resolution array
    arr1 = get_quartet_resolutions_table(tree1)
    arr2 = get_quartet_resolutions_table(tree2)

    # stats dict
    data = {}

    # mask to select only quartes resolved in both trees
    mask = (arr1 != 0) & (arr2 != 0)

    # compute Q = total possible number of quartets
    data["Q"] = arr1.shape[0]

    # S = total number of quartets resolved in the same way in both trees
    data["S"] = sum(arr1[mask] == arr2[mask])

    # D = symmetric diff of resolved quartets
    data["D"] = sum(arr1[mask] != arr2[mask])

    # U = number of quartets unresolved in both trees
    data["U"] = sum((arr1 == 0) & (arr2 == 0))

    # R1 = number of quartets resolved in tree1, but unresolved in tree2
    data["R1"] = sum((arr1 != 0) & (arr2 == 0))

    # R2 = number of quartets resolved in tree2, but unresolved in tree1
    data["R2"] = sum((arr1 == 0) & (arr2 != 0))

    # N = S + D + R1 + R2 + U
    data["N"] = data["S"] + data["D"] + data["R1"] + data["R2"] + data["U"]
    return data


######################################################################
# COMPUTE METRICS GIVEN A DATA DICT WITH KEYS D, S, R1, R2, U, N, Q
# calculated in `get_quartet_comparison()`
######################################################################


def get_qrt_metric_do_not_conflict(data: Mapping[str, int]) -> float:
    return (data["S"] + data["R1"] + data["R2"] + data["U"]) / data["N"]


def get_qrt_metric_explicitly_agree(data: Mapping[str, int]) -> float:
    return data["S"] / data["N"]


def get_qrt_metric_strict_joint_assertions(data: Mapping[str, int]) -> float:
    return data["S"] / (data["S"] + data["D"])


def get_qrt_metric_semistrict_joint_assertions(data: Mapping[str, int]) -> float:
    return data["S"] / (data["S"] + data["D"] + data["U"])


def get_qrt_metric_steel_and_penny(data: Mapping[str, int]) -> float:
    return (data["S"] + data["U"]) / data["N"]


def get_qrt_metric_symmetric_difference(data: Mapping[str, int]) -> float:
    part1 = 2 * data["D"] + data["R1"] + data["R2"]
    part2 = (2 * data["D"]) + (2 * data["S"]) + data["R1"] + data["R2"]
    return 1 - (part1 / part2)


def get_qrt_metric_symmetric_divergence(data: Mapping[str, int]) -> float:
    return (2 * data["D"] + data["R1"] + data["R2"]) / data["N"]


def get_qrt_metric_similarity_to_reference(data: Mapping[str, int]) -> float:
    part1 = data["S"] + ((data["R1"] + data["R2"] + data["U"]) / 3)
    return part1 / data["Q"]


def get_qrt_metric_marczewski_steinhaus(data: Mapping[str, int]) -> float:
    part1 = (2 * data["D"]) + data["R1"] + data["R2"]
    part2 = (2 * data["D"]) + data["S"] + data["R1"] + data["R2"]
    return 1 - part1 / part2


QUARTET_METRICS = {
    "do_not_conflict": get_qrt_metric_do_not_conflict,
    "explicitly_agree": get_qrt_metric_explicitly_agree,
    "strict_joint_assertions": get_qrt_metric_strict_joint_assertions,
    "semistrict_joint_assertions": get_qrt_metric_semistrict_joint_assertions,
    "steel_and_penny": get_qrt_metric_steel_and_penny,
    "symmetric_difference": get_qrt_metric_symmetric_difference,
    "symmetric_divergence": get_qrt_metric_symmetric_divergence,
    "similarity_to_reference": get_qrt_metric_similarity_to_reference,
    "marczewski_steinhaus": get_qrt_metric_marczewski_steinhaus,
}

######################################################################
######################################################################
######################################################################


def get_quartet_metric(
    tree1: ToyTree,
    tree2: ToyTree,
    metric: str = None,
    similarity: bool = False,
) -> float:
    """Return a single quartet metric for two trees.

    Metrics
    -------
    ...

    Parameters
    ----------
    tree1: ToyTree
        A tree.
    tree1: ToyTree
        A tree with the same tip labels as tree1.
    metric: str or None
        A quartet metric (see 'Metrics' above) to compute.
    similarity: bool
        True returns similarity score, False returns a tree distance
        metric (1-similarity). Default is False.

    Example
    -------
    >>> tree1 = toytree.rtree.unittree(8, seed=123)
    >>> tree2 = toytree.rtree.unittree(8, seed=321)
    >>> get_quartet_metric(tree1, tree2)
    >>> # {'Q': 70, 'S': 70, 'D': 0, 'U': 0, 'R1': 0, 'R2': 0, 'N': 140}
    >>> get_quartet_metric(tree1, tree2, "steel_and_penny")
    >>> # 0.5
    """
    data = get_quartet_comparison(tree1, tree2)
    if metric is None:
        return data
    if metric in QUARTET_METRICS:
        value = QUARTET_METRICS[metric](data)
        if not similarity:
            value = 1 - value
        return value
    raise ValueError(
        f"metric {metric} not recognized, must be one of "
        f"{sorted(QUARTET_METRICS.keys())}.")


@add_subpackage_method(TreeDistanceAPI)
def get_treedist_quartets(
    tree1: ToyTree,
    tree2: ToyTree,
    similarity: bool = False,
) -> pd.Series:
    """Return a pd.Series with all quartet metrics for two trees.

    This returns all quartet metrics computed between two trees, since
    once quartets are enumerated and compared calculating the metrics
    is fast and simple.

    Parameters
    ----------
    tree1: ToyTree
        A tree.
    tree1: ToyTree
        A tree with the same tip labels as tree1.
    similarity: bool
        True returns similarity score, False returns a tree distance
        metric (1-similarity). Default is False.

    Examples
    --------
    >>> tree1 = toytree.rtree.unittree(8, seed=123)
    >>> tree2 = toytree.rtree.unittree(8, seed=123)
    >>> tree2.mod.collapse_nodes(10, 11, inplace=True)
    >>> get_treedist_quartet_metrics(tree1, tree2, similarity=False)
    >>> # Q                              70.000000
    >>> # S                              42.000000
    >>> # D                               0.000000
    >>> # U                               0.000000
    >>> # R1                             28.000000
    >>> # R2                              0.000000
    >>> # N                              70.000000
    >>> # do_not_conflict                 0.000000
    >>> # explicitly_agree                0.400000
    >>> # strict_joint_assertions         0.000000
    >>> # semistrict_joint_assertions     0.000000
    >>> # steel_and_penny                 0.400000
    >>> # symmetric_difference            0.250000
    >>> # symmetric_divergence            0.600000
    >>> # similarity_to_reference         0.266667
    >>> # marczewski_steinhaus            0.400000

    Quartet Data
    -------------
    ------------------------------------------
    | Q    | All possible quartets           |
    | S    | Resolved same in both trees     |
    | D    | Resolved diff between trees     |
    | U    | Unresolved in both trees        |
    | R1   | Unresolved in tree1 not tree2   |
    | R2   | Unresolved in tree2 not tree1   |
    | N    | S + D + U + R1 + R2             |
    ------------------------------------------

    Quartet Similarity Metrics
    --------------------------
    | name                    | compute               | reference   |
    --------------------------------------------------------------------------
    | DC: Do Not Conflict     | (S + R1 + R2 + U) / N | Estabrook et al. (1985) |
    | EA: Explicity Agree     | S / N                 | Estabrook et al. (1985) |
    | SJA: Strict Joint Assert| S / (S + D)           | Estabrook et al. (1985) |
    | SSJA: Semi-Strict ''    | S / (S + D + U)       | Estabrook et al. (1985) |
    | dQ: Steel and Penny     | (S + U) / N           | Steel and Penny (1993)  |
    | SD: Symmetric diff      | (2d + r1 + r2) / (2d + 2s + r1 + r2) | Day (1986) |
    | MS: Marczewski-Steinhaus| (2d + r1 + r2) / (2d + s + r1 + r2)| Marczewski and Steinhaus (1958) |
    | SV: Symmetric Divergence| (2d + r1 + r2) / N   | Smith 2019 |
    | S2R: Similarity to Ref  | (s + (r1 + r2 + u) / 3) / Q | Asher and Smith (2022) |
    --------------------------------------------------------------------------

    Reference
    ---------
    https://ms609.github.io/Quartet/reference/SimilarityMetrics.html
    """
    data = get_quartet_comparison(tree1, tree2)
    methods = list(data.keys()) + list(QUARTET_METRICS.keys())
    frame = pd.Series(index=methods, dtype=np.float64)
    for key, value in data.items():
        frame[key] = value
    for metric, method in QUARTET_METRICS.items():
        value = method(data)
        if not similarity:
            value = 1 - value
        frame[metric] = value
    return frame


if __name__ == "__main__":

    TREE1 = toytree.rtree.unittree(6, seed=123)
    TREE2 = toytree.rtree.unittree(6, seed=321)
    TREE2 = TREE2.mod.collapse_nodes(8)

    treedf1 = get_quartet_resolutions_table(TREE1, df=True)
    treedf2 = get_quartet_resolutions_table(TREE2, df=True)
    print(treedf2)

    data = get_quartet_comparison(TREE1, TREE2)
    print(data)

    # ...
    tree1 = toytree.rtree.unittree(8, seed=123)
    tree2 = toytree.rtree.unittree(8, seed=321)
    print(get_quartet_metric(tree1, tree2))
    print(get_quartet_metric(tree1, tree2, "steel_and_penny"))

    tree1 = toytree.rtree.unittree(8, seed=123)
    tree2 = toytree.rtree.unittree(8, seed=1233)
    tree2.mod.collapse_nodes(10, 11, inplace=True)
    print(get_treedist_quartets(tree1, tree2, similarity=False))
