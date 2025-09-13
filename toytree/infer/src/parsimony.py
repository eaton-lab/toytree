#!/usr/bin/env python

"""Calculate parsimony score of a tree topology given data.

TODO
----
- support DNA IUPAC models where ambiguous states are automatically
expanded.
- support non DNA (arbitrary multistate including binary) data.
- vectorize to be faster.
- vectorize RI/CI to apply over trait matrix

JIT-compiled version
---------------------
- jit supports sets now, but they are being deprecated to introduce
a new numba typed.set, but which does not yet exist. So until it does
its not really worth spending time on...
- https://numba.pydata.org/numba-doc/dev/reference/pysupported.html#set

References
----------
- Xia, Xuhua. 2018. “Maximum Parsimony Method in Phylogenetics.”
  In Bioinformatics and the Cell: Modern Computational Approaches in
  Genomics, Proteomics and Transcriptomics, edited by Xuhua Xia,
  327–41. Cham: Springer International Publishing.
  https://doi.org/10.1007/978-3-319-90684-3_14.
- Fitch, Walter M. 1971. “Toward Defining the Course of Evolution:
  Minimum Change for a Specific Tree Topology.” Systematic Biology 20
  (4): 406–16. https://doi.org/10.1093/sysbio/20.4.406.

- Sankoff (1975)
- Felsenstein (2004)
- BioPython
- https://telliott99.blogspot.com/search/label/maximum%20likelihood
- https://telliott99.blogspot.com/2010/03/fitch-and-sankoff-algorithms-for.html
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from toytree.core import ToyTree

__all__ = [
    "consistency_and_retention_index",
]


# def get_parsimony_score(
#     tree: ToyTree,
#     data: ArrayLike,
#     weights: Optional[ArrayLike],
#     data_as_dna: bool = True,
# ):
#     """Return the parsimony score of a tree given a data matrix.

#     The parsimony score is calculated by performing a post-order
#     traversal on a rooted tree (if unrooted it will be arbitrarily
#     rooted, which has no effect on score) and setting the state of
#     internal nodes to be the set intersection of states at its
#     descendant Nodes. If no intersection exists, the union is instead
#     set and this counts as a 'change' event. If a weights matrix is
#     entered then this indicates the contribution of each type of
#     change towards the 'score' (Sankoff parsimony), else each change
#     counts as 1 (Fitch parsimony). If multiple states exist in the
#     data matrix the sum of scores of each state is returned.

#     Parameters
#     ----------
#     tree: ToyTree
#         A tree on which to calculate the parsimony score.
#     data: ArrayLike
#         A data matrix of shape (ntips, ntraits) containing discrete
#         values for one or more traits for each tip Node in idxorder.
#     weights: None or ArrayLike
#         The weights matrix must be square. If it is a dataframe then
#         the row and column names will be used, else they should be
#         ordered by state values alphanumerically (e.g., 0, 1, 2, 3 or
#         'A', 'C', 'G', 'T'). The diagonal must be zero, and
#         off-diagonal as float or int types.
#     data_as_dna: bool
#         If True then data values that are string types representing
#         DNA IUPAC ambiguity codes (e.g., RWMYSK) will be expanded to a
#         set of the two bases that they represent (e.g., W -> {A, T}).

#     Note
#     ----
#     This function uses numba jit-compilation for speed improvements.

#     References
#     ----------
#     - ...

#     Examples
#     --------
#     >>> ...
#     """
#     # get tree as an array of idxs in postorder traversal
#     traversal_order = np.array([i.idx for i in tree.traverse("postorder")])

#     # get data as a array of ints after expanding ambiguities
#     if data_as_dna:
#         pass
#     else:
#         pass

#     # calculate sum of scores and return
#     score = jit_compiled_fitch(
#         tree=traversal_order,
#         data=int_matrix,
#         weights=weights_matrix,
#     )
#     return score


class Parsimony:
    """Return a phylogenetic tree inferred by Maximum Parsimony.

    Examples
    ---------
    >>> toytree.set_log_level("DEBUG")  # print verbose information
    >>> data = ...
    >>> starting_tree = ... distance tree.
    >>> tool = Parsimony(data)
    >>> tool.get_score(tree=tree, )
    """
    def __init__(self, data: ...):
        self.data = data

    def get_score(self, tree):
        """Return parsimony score"""


    def _fitch_algorithm(self):
        """Implement the fitch algorithm.

        """

    def _sankoff_algorithm(self):
        """Implement the Sankoff algorithm.

        The strength of the Sankoff algorithm is that it allows a
        variety of cost matrices to be used. This is in principal
        closer to ML, where we would define a substitution model.
        Here the cost matrix is not inferred, but a priori defined
        by the user.

        """

    def _tree_move(self, method: str):
        """Return a ToyTree that is one 'move' from the current tree.

        >>> NNITreeSearcher(scorer)
        """
        pass


# class Fitch:
#     """Implementation of the Fitch parsimony algorithm."""
#     pass


# def _validate_against_bio():
#     """Compare against Bio implementation for validation"""
#     pass


def convert_trait_to_idx_dict(tree: ToyTree, trait: Dict[str, Any]) -> Dict[int, Any]:
    """
    """
    if isinstance(trait, str):
        trait = tree.get_node_data(trait).to_dict()
    else:
        try:
            trait = dict(trait)
        except Exception as exc:
            raise TypeError("trait input could not be cast to a dict.") from exc

    # if dict names are str cast to int idx labels
    if any(isinstance(i, str) for i in trait):
        trait = {tree[i].idx: j for (i, j) in trait.items()}
    return trait



def fitch_parsimony_score(tree: ToyTree, trait: Dict[int,Any]) -> int:
    """Return Fitch parsimony score given a tree and single trait.

    For didactic purposes this function will also store a feature named
    'fitch' to every Node which can be examined/visualized afterwards.

    Parameters
    ----------
    tree: ToyTree
        A tree on which to count state changes.
    trait: str | Dict | pd.Series
        A dict mapping tip node idx to a discrete character state.

    Returns
    -------
    int
        The minimum changes required for trait data to evolve on this tree.
    """
    # counter to keep track of change events
    nchanges = 0

    # iterate over Nodes in idxorder (postorder sorted) traversal
    for node in tree:

        # leaves are visited first, and converted to a set type
        if node.is_leaf():
            node.fitch = set((trait[node.idx],))

        # internal Nodes examine the sets of their children's states
        else:

            # check for shared (intersecting) states
            shared = set.intersection(*(i.fitch for i in node.children))

            # if any states are shared then ancestor inherits this state
            if shared:
                node.fitch = shared

            # if none shared, then store the union and increment counter
            else:
                node.fitch = set.union(*(i.fitch for i in node.children))
                nchanges += 1
    return nchanges


def consistency_and_retention_indices(tree: ToyTree, trait: Dict[str,Any], npermutations: int = 10_000, left_tailed: bool = False, rng: int = None) -> pd.Series:
    """Return the consistency (CI), retention (RI), and rescaled
    consistency index (RCI) for a discrete trait.

    The CI and RI compare the observed changes in a trait across a tree
    topology to the minimum and maximum changes as a measure of homoplasy.
    To assess significance, trait values are randomly permuted across
    the tips of the tree and the proportion of tests above or below the
    observed statistic is returned.

    If the observed CI > null (left-tailed=False) at p<0.05 it is
    evidence of phylogenetic signal; if observed CI < null (left-tailed
    True) at p<0.05 it is evidence of homplasy. If RI is high (1.0)
    there is no homoplasy; if ~0.5 half is due to shared ancestry; if
    0.0 it is as homoplasious as possible. The RCI rescales the CI
    for comparing characters on trees of different sizes or shapes.

    Parameters
    ----------
    tree:
        A ToyTree (only topology is used, rooting doesn't matter.)
    trait: str | Dict[str|int, Any] | pd.Series
        A feature name or trait values as a dict or Series mapping
        tip names or idx labels to discrete trait values.
    npermutations: int
        The number of permutations to test significance.
    left_tailed: bool
        If True the test statistic is left_tailed: it computes the N
        permutations <= the observed data, rather than the N >= the
        observed data.
    rng: None | int | np.random.RandomState
        Random seed for permutations.

    Example
    -------
    >>> # generate random tree, simulate 4-state traits, calculate CI
    >>> tree = toytree.rtree.unittree(ntips=40)
    >>> traits = tree.pcm.simulate_discrete_data(nstates=4, tips_only=True, nreplicates=10)
    >>> consistency_and_retention_indices(tree, traits.t0)

    References
    -----------
    - Fitch, Walter M. (1971) Systematic Biology 20 (4)
    - Klingenberg and Gidaszewski (2010) Systematic Biology 59 (3)
    """
    # get parsimony score
    trait = convert_trait_to_idx_dict(tree, trait)
    score = fitch_parsimony_score(tree, trait)

    # get CI and RI for trait
    nstates = len(set(trait.values()))
    min_changes = max(1, nstates - 1)
    max_changes = tree.ntips - 1
    ci = min_changes / score if score > 0 else 1.0
    ri = 1.0 if min_changes == max_changes else (max_changes - score) / (max_changes - min_changes)
    ri = max(0.0, min(1.0, ri))
    rci = ci * ri

    # get CI and RI for permutated traits
    rng = np.random.default_rng(rng)
    permuted_cis = np.zeros(npermutations)
    permuted_ris = np.zeros(npermutations)
    permuted_rcis = np.zeros(npermutations)
    permuted_score = np.zeros(npermutations)
    nsamp = len(trait)
    keys = list(trait)
    values = list(trait.values())
    for i in range(npermutations):
        ptrait = dict(zip(keys, rng.choice(values, size=nsamp, replace=False)))
        score_ = fitch_parsimony_score(tree, ptrait)
        ci_ = min_changes / score_ if score_ > 0 else 1.0
        ri_ = 1.0 if min_changes == max_changes else (max_changes - score_) / (max_changes - min_changes)
        ri_ = max(0.0, min(1.0, ri_))
        rci_ = ci_ * ri_
        permuted_cis[i] = ci_
        permuted_ris[i] = ri_
        permuted_rcis[i] = rci_
        permuted_score[i] = score_

    # number of tests > than observed
    if left_tailed:
        count_ci = np.sum(permuted_cis >= ci)
        count_ri = np.sum(permuted_ris >= ri)
        count_rci = np.sum(permuted_rcis >= rci)
    else:
        count_ci = np.sum(permuted_cis <= ci)
        count_ri = np.sum(permuted_ris <= ri)
        count_rci = np.sum(permuted_rcis <= rci)
    ci_pvalue = (count_ci + 1) / (npermutations + 1)
    ri_pvalue = (count_ri + 1) / (npermutations + 1)
    rci_pvalue = (count_rci + 1) / (npermutations + 1)

    # return as series
    return pd.Series({
        "CI": ci,
        "CI_permuted_mean": permuted_cis.mean(),
        "CI_p-value": ci_pvalue,
        "RI": ri,
        "RI_permuted_mean": permuted_ris.mean(),
        "RI_p-value": ri_pvalue,
        "RCI": rci,
        "RCI_permuted_mean": permuted_rcis.mean(),
        "RCI_p-value": rci_pvalue,
        "fitch_parsimony_score": score,
        "fitch_parsimony_score_permuted_mean": permuted_score.mean(),
        "npermutations": npermutations,
    })


if __name__ == "__main__":

    # test parsimony score and inference against Bio
    import toytree
    tree = toytree.rtree.unittree(40, treeheight=1000, seed=123)
    data = tree.pcm.simulate_discrete_data(nstates=4, tips_only=True, nreplicates=4)
    print(data)
    # print(fitch_parsimony_single(tree, data.t0))
    print(consistency_and_retention_indices(tree, data.t0))
