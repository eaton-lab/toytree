#!/usr/bin/env python

"""Calculate parsimony score of a tree topology given data.

TODO
----
- support DNA IUPAC models where ambiguous states are automatically
expanded.
- support non DNA (arbitrary multistate including binary) data.
- vectorize to be faster.

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

from typing import TypeVar, Optional
from numpy.typing import ArrayLike

ToyTree = TypeVar("ToyTree")


def get_parsimony_score(
    tree: ToyTree,
    data: ArrayLike,
    weights: Optional[ArrayLike],
    data_as_dna: bool = True,
):
    """Return the parsimony score of a tree given a data matrix.

    The parsimony score is calculated by performing a post-order
    traversal on a rooted tree (if unrooted it will be arbitrarily
    rooted, which has no effect on score) and setting the state of
    internal nodes to be the set intersection of states at its
    descendant Nodes. If no intersection exists, the union is instead
    set and this counts as a 'change' event. If a weights matrix is
    entered then this indicates the contribution of each type of
    change towards the 'score' (Sankoff parsimony), else each change
    counts as 1 (Fitch parsimony). If multiple states exist in the
    data matrix the sum of scores of each state is returned.

    Parameters
    ----------
    tree: ToyTree
        A tree on which to calculate the parsimony score.
    data: ArrayLike
        A data matrix of shape (ntips, ntraits) containing discrete
        values for one or more traits for each tip Node in idxorder.
    weights: None or ArrayLike
        The weights matrix must be square. If it is a dataframe then
        the row and column names will be used, else they should be
        ordered by state values alphanumerically (e.g., 0, 1, 2, 3 or
        'A', 'C', 'G', 'T'). The diagonal must be zero, and
        off-diagonal as float or int types.
    data_as_dna: bool
        If True then data values that are string types representing
        DNA IUPAC ambiguity codes (e.g., RWMYSK) will be expanded to a
        set of the two bases that they represent (e.g., W -> {A, T}).

    Note
    ----
    This function uses numba jit-compilation for speed improvements.

    References
    ----------
    - ...

    Examples
    --------
    >>> ...
    """
    # get tree as an array of idxs in postorder traversal
    traversal_order = np.array([i.idx for i in tree.traverse("postorder")])

    # get data as a array of ints after expanding ambiguities
    if data_as_dna:
        pass
    else:
        pass

    # calculate sum of scores and return
    score = jit_compiled_fitch(
        tree=traversal_order,
        data=int_matrix,
        weights=weights_matrix,
    )
    return score


class Parsimony:
    """Infer a phylogenetic tree by Maximum Parsimony.

    Note
    ----
    The maximum parsimony algorithm does not infer rooted trees, i.e.,
    topologies re-rooted at any arbitrary edge will yield the same
    parsimony score.

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


class Fitch:
    """Implementation of the Fitch parsimony algorithm."""
    pass


def _validate_against_bio():
    """Compare against Bio implementation for validation"""
    pass


if __name__ == "__main__":

    # test parsimony score and inference against Bio
    import toytree
    tree = toytree.rtree.unittree(10, treeheight=1000, seed=123)
    # data = tree.pcm.simulate_discrete_markov_data("seqs", states=4, reps=10)

