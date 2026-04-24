#!/usr/bin/env python

"""Calculate Fitch parsimony scores and related homoplasy indices.

TODO
----
- support DNA IUPAC models where ambiguous states are automatically
expanded.
- support ambiguity-aware state models and character matrices.
- vectorize to be faster.
- vectorize RI/CI to apply over trait matrix

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from toytree.core import ToyTree

__all__ = [
    "consistency_and_retention_indices",
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


# class Parsimony:
#     """Return a phylogenetic tree inferred by Maximum Parsimony.

#     Examples
#     --------
#     >>> toytree.set_log_level("DEBUG")  # print verbose information
#     >>> data = ...
#     >>> starting_tree = ... distance tree.
#     >>> tool = Parsimony(data)
#     >>> tool.get_score(tree=tree, )
#     """

#     def __init__(self, data: ...):
#         self.data = data

#     def get_score(self, tree):
#         """Return parsimony score."""

#     def _fitch_algorithm(self):
#         """Implement the fitch algorithm."""

#     def _sankoff_algorithm(self):
#         """Implement the Sankoff algorithm.

#         The strength of the Sankoff algorithm is that it allows a
#         variety of cost matrices to be used. This is in principal
#         closer to ML, where we would define a substitution model.
#         Here the cost matrix is not inferred, but a priori defined
#         by the user.

#         """

#     def _tree_move(self, method: str):
#         """Return a ToyTree that is one 'move' from the current tree.

#         >>> NNITreeSearcher(scorer)
#         """
#         pass


# class Fitch:
#     """Implementation of the Fitch parsimony algorithm."""
#     pass


# def _validate_against_bio():
#     """Compare against Bio implementation for validation"""
#     pass


_MISSING = object()
_PARSIMONY_ROWS = ("fitch_parsimony_score", "CI", "RI", "RCI")


def convert_trait_to_idx_dict(
    tree: ToyTree,
    trait: str | Mapping[Any, Any] | pd.Series,
) -> dict[int, Any]:
    """Return a complete tip-indexed trait mapping for parsimony utilities.

    Parameters
    ----------
    tree: ToyTree
        Tree whose tips define the expected trait mapping.
    trait: str | Mapping | pd.Series
        A feature name on the tree or a mapping from tip selectors to
        discrete states. Selectors may be tip idx labels, tip names, or
        tip ``Node`` objects.

    Returns
    -------
    dict[int, Any]
        Discrete trait states keyed by tip idx.

    Raises
    ------
    TypeError
        If ``trait`` cannot be interpreted as a mapping of discrete states.
    ValueError
        If any tip states are missing, ambiguous selectors match multiple
        nodes, internal nodes are supplied, or any state values are missing
        or unhashable.
    """
    if isinstance(trait, str):
        series = tree.get_tip_data(trait, missing=_MISSING)
        missing = [int(idx) for idx, value in series.items() if value is _MISSING]
        if missing:
            raise ValueError(
                "trait feature is missing values for one or more tips: "
                f"{missing[:5]}"
            )
        normalized = {int(idx): value for idx, value in series.items()}
    else:
        try:
            mapping = dict(trait)
        except Exception as exc:
            raise TypeError("trait input could not be cast to a dict.") from exc

        normalized: dict[int, Any] = {}
        for query, value in mapping.items():
            nodes = tree.get_nodes(query)
            if len(nodes) != 1:
                raise ValueError(
                    "trait selectors must identify exactly one tip node. "
                    f"Selector {query!r} matched {len(nodes)} nodes."
                )
            node = nodes[0]
            if not node.is_leaf():
                raise ValueError(
                    "trait mappings must be defined on tips only. "
                    f"Selector {query!r} resolved to internal node {node.idx}."
                )
            normalized[node.idx] = value

        expected = {node.idx for node in tree[: tree.ntips]}
        missing = sorted(expected - set(normalized))
        if missing:
            raise ValueError(
                "trait input is missing values for one or more tips: " f"{missing[:5]}"
            )

    for idx, value in normalized.items():
        is_missing = value is _MISSING
        if not is_missing:
            try:
                missing_value = pd.isna(value)
            except Exception:
                missing_value = False
            if isinstance(missing_value, (np.ndarray, pd.Series)):
                missing_value = bool(np.all(missing_value))
            is_missing = bool(missing_value)
        if is_missing:
            raise ValueError(f"trait value for tip {idx} is missing.")
        try:
            hash(value)
        except TypeError as exc:
            raise ValueError(
                "trait values must be discrete, hashable states. "
                f"Tip {idx} has unsupported value {value!r}."
            ) from exc
    return normalized


def _get_parsimony_step_bounds(trait: Mapping[int, Any]) -> tuple[int, int]:
    """Return the minimum and maximum possible steps for one character."""
    states = list(trait.values())
    counts = pd.Series(states, dtype=object).value_counts()
    min_changes = max(0, int(counts.size) - 1)
    max_changes = len(states) - int(counts.max())
    return min_changes, max_changes


def _get_ci_ri_rci(
    score: int,
    min_changes: int,
    max_changes: int,
) -> tuple[float, float, float]:
    """Return CI, RI, and RCI for one observed parsimony score."""
    ci = min_changes / score if score > 0 else 1.0
    ri = (
        1.0
        if min_changes == max_changes
        else (max_changes - score) / (max_changes - min_changes)
    )
    ri = max(0.0, min(1.0, float(ri)))
    return float(ci), ri, float(ci * ri)


def _permutation_pvalues(
    observed: float,
    null: np.ndarray,
) -> tuple[float, float]:
    """Return one-sided permutation p-values for greater/less alternatives."""
    p_greater = (np.sum(null >= observed) + 1) / (null.size + 1)
    p_less = (np.sum(null <= observed) + 1) / (null.size + 1)
    return float(p_greater), float(p_less)


def fitch_parsimony_score(
    tree: ToyTree,
    trait: str | Mapping[Any, Any] | pd.Series,
) -> int:
    """Return the Fitch parsimony score for one unordered discrete trait.

    For didactic purposes this function will also store a feature named
    'fitch' to every Node which can be examined/visualized afterwards.

    Parameters
    ----------
    tree: ToyTree
        A tree on which to count state changes. Only topology matters;
        rooting does not affect the score.
    trait: str | Mapping | pd.Series
        A feature name on the tree or a mapping from tip selectors to a
        discrete character state. Selectors may be tip idx labels, tip
        names, or tip ``Node`` objects.

    Returns
    -------
    int
        The minimum changes required for trait data to evolve on this tree.

    Notes
    -----
    This implementation currently assumes a single unordered discrete
    character on the tips. It annotates each node with a temporary
    ``fitch`` attribute containing the reconstructed state set.
    """
    trait = convert_trait_to_idx_dict(tree, trait)

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


def consistency_and_retention_indices(
    tree: ToyTree,
    trait: str | Mapping[Any, Any] | pd.Series,
    npermutations: int = 10_000,
    rng: None | int | np.random.Generator = None,
) -> pd.DataFrame:
    """Return parsimony indices and permutation tests for one trait.

    This function summarizes four related quantities for a single
    unordered discrete character on the tips of a tree:

    - Fitch parsimony score ``s``: the observed minimum number of
      state changes on the tree.
    - Consistency index ``CI = m / s``: the fraction of observed
      changes explained by the minimum possible number of changes.
      Lower values indicate more homoplasy.
    - Retention index ``RI = (g - s) / (g - m)``: the proportion of
      the character's extra steps that are still retained as synapomorphy
      rather than homoplasy. Here ``m`` is the minimum possible number
      of steps for the observed set of states and ``g`` is the maximum
      possible number of steps for the observed tip-state frequencies.
    - Rescaled consistency index ``RCI = CI * RI``: a size-adjusted
      combination of CI and RI that is often more comparable across
      characters and trees than CI alone.

    To assess whether the observed statistic is unusually high or low,
    the observed tip states are permuted across the same tip labels while
    preserving the state counts. The returned table includes p-values for
    two one-sided alternatives:

    - ``p_value_greater``: p-value for the alternative that the observed
      statistic is greater than the permuted null expectation.
    - ``p_value_less``: p-value for the alternative that the observed
      statistic is less than the permuted null expectation.

    For ``CI``, ``RI``, and ``RCI``, unusually large values are generally
    interpreted as stronger phylogenetic structure and unusually small
    values as greater homoplasy. For the Fitch score, the direction is
    reversed: unusually small scores imply stronger phylogenetic structure.

    Parameters
    ----------
    tree: ToyTree
        A tree on which to evaluate one tip-mapped discrete character.
        Only topology matters; rooting does not affect these indices.
    trait: str | Mapping | pd.Series
        A feature name on the tree or a mapping from tip selectors to
        discrete trait values. Selectors may be tip idx labels, tip
        names, or tip ``Node`` objects.
    npermutations: int
        Number of tip-state permutations used to build the null
        distribution for each statistic.
    rng: None | int | np.random.Generator
        Random seed or generator used for permutations.

    Returns
    -------
    pd.DataFrame
        A table indexed by statistic name with columns:

        - ``observed``
        - ``null_mean``
        - ``p_value_greater``
        - ``p_value_less``
        - ``signal_tail``

        The table has rows for ``fitch_parsimony_score``, ``CI``, ``RI``,
        and ``RCI``. Metadata about the permutation test are stored in
        ``DataFrame.attrs``.

    Examples
    --------
    >>> # generate random tree, simulate 4-state traits, calculate CI
    >>> tree = toytree.rtree.unittree(ntips=40)
    >>> trait = tree.pcm.simulate_discrete_trait(nstates=4, tips_only=True)
    >>> consistency_and_retention_indices(tree, trait)

    References
    ----------
    - Fitch, Walter M. (1971) Systematic Biology 20 (4)
    - Farris, James S. (1989) Cladistics 5 (4)
    - Klingenberg and Gidaszewski (2010) Systematic Biology 59 (3)
    """
    if int(npermutations) < 1:
        raise ValueError("npermutations must be >= 1.")
    npermutations = int(npermutations)

    generator = (
        rng if isinstance(rng, np.random.Generator) else np.random.default_rng(rng)
    )

    trait = convert_trait_to_idx_dict(tree, trait)
    score = fitch_parsimony_score(tree, trait)
    min_changes, max_changes = _get_parsimony_step_bounds(trait)
    ci, ri, rci = _get_ci_ri_rci(score, min_changes, max_changes)

    permuted_scores = np.zeros(npermutations, dtype=float)
    permuted_cis = np.zeros(npermutations, dtype=float)
    permuted_ris = np.zeros(npermutations, dtype=float)
    permuted_rcis = np.zeros(npermutations, dtype=float)
    keys = list(trait)
    values = np.array(list(trait.values()), dtype=object)
    for i in range(npermutations):
        ptrait = dict(zip(keys, generator.permutation(values)))
        score_ = fitch_parsimony_score(tree, ptrait)
        ci_, ri_, rci_ = _get_ci_ri_rci(score_, min_changes, max_changes)
        permuted_cis[i] = ci_
        permuted_ris[i] = ri_
        permuted_rcis[i] = rci_
        permuted_scores[i] = score_

    rows = {
        "fitch_parsimony_score": {
            "observed": float(score),
            "null_mean": float(permuted_scores.mean()),
            "signal_tail": "less",
        },
        "CI": {
            "observed": ci,
            "null_mean": float(permuted_cis.mean()),
            "signal_tail": "greater",
        },
        "RI": {
            "observed": ri,
            "null_mean": float(permuted_ris.mean()),
            "signal_tail": "greater",
        },
        "RCI": {
            "observed": rci,
            "null_mean": float(permuted_rcis.mean()),
            "signal_tail": "greater",
        },
    }
    null_map = {
        "fitch_parsimony_score": permuted_scores,
        "CI": permuted_cis,
        "RI": permuted_ris,
        "RCI": permuted_rcis,
    }
    for name in _PARSIMONY_ROWS:
        p_greater, p_less = _permutation_pvalues(rows[name]["observed"], null_map[name])
        rows[name]["p_value_greater"] = p_greater
        rows[name]["p_value_less"] = p_less

    result = pd.DataFrame.from_dict(rows, orient="index")[
        ["observed", "null_mean", "p_value_greater", "p_value_less", "signal_tail"]
    ]
    result.index.name = "statistic"
    result.attrs["npermutations"] = npermutations
    result.attrs["null_model"] = "tip_state_permutation_preserving_state_counts"
    return result


if __name__ == "__main__":
    # test parsimony score and inference against Bio
    import toytree

    tree = toytree.rtree.unittree(40, treeheight=1000, seed=123)
    data = tree.pcm.simulate_discrete_trait(nstates=4, tips_only=True)
    print(data)
    print(consistency_and_retention_indices(tree, data))
