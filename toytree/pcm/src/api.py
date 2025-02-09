#!/usr/bin/env python

"""DEPRECATED

Phylogenetic comparative methods functions made accessible at
:mod:`toytree.pcm` as a subpackage-level API.
"""

from typing import List, Optional
import pandas as pd
import numpy as np

from toytree.pcm.src.utils import get_vcv_matrix_from_tree
# from toytree.pcm.src.discrete_markov_model_sim import 
# from toytree.pcm.src.discrete_markov_model_sim import (
#     DiscreteMarkovModelSim,
#     DiscreteMarkovModelQMatrix,
# )


__all__ = [
    "get_vcv_from_tree",
    "get_qmatrix",
    "simulate_discrete_markov_data",
    "simulate_discrete_markov_data_on_tree",
]


def get_qmatrix_er(nstates: int, rate: float):
    pass

def get_qmatrix_sym(nstates: int, rates: List[float]):
    pass

def get_qmatrix_ard(nstates: int, rates: List[float]):
    pass


def get_instaneous_transition_rate_matrix(
    nstates: int,
    rates: List[float],
    ) -> pd.DataFrame:
    """Get an instantaneous transition rate matrix (Q matrix) from

    Parameters
    ----------
    nstates: int
        The number of states in the transition rate model.

    Returns
    -------
    pandas.DataFrame
        An instaneous transition rate matrix (Q matrix).

    Examples
    --------
    >>> # get a Q-matrix under a 3-state 'Equal-Rates' model
    >>> qmatrix = toytree.pcm.get_instaneous_transition_rate_matrix(3, 1e-3)
    """
    matrix = DiscreteMarkovModelQMatrix(nstates)
    qmat = matrix.get_rate_matrix(rates)
    return qmat


def simulate_discrete_markov_data(
    tree: 'ToyTree',
    qmatrix: np.ndarray,
    nsims: int = 1,
    ancestral_state: Optional[np.ndarray] = None,
    seed: Optional[int] = None,
    ) -> pd.DataFrame:
    """Return a DataFrame with simulated discrete trait values.

    The index (rows) are tip names and columns are the indices of
    nsims replicate simulations. Trait values for internal nodes 
    are not returned (see :func:`simulate_discrete_markov_data_on_tree`).
    Results can be treated like observed data, which is typically only
    available for tip nodes.

    Parameters
    ----------
    tree: toytree.ToyTree
        An input ToyTree on the edges of which the trait will be simulated.
    qmatrix: numpy.ndarray
        An instantaneous transition rate matrix between N states.
    nsims: int
        The number of replicate simulations to perform.
    seed: Optional[int]
        The numpy random number generator seed to use.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=100, seed=123)
    >>> qmatrix = toytree.pcm.get_transition_rate_matrix(3, 1e-3)
    >>> data = toytree.pcm.simulate_discrete_markov_states(tree, qmatrix)

    See Also
    --------
    :func:`simulate_discrete_markov_data_on_tree`
        Return a list of ToyTree instances with simulated data 
        assigned to a feature named 'discrete' on every node.
    """
    model = DiscreteMarkovModelSim(tree, qmatrix, nsims, ancestral_state, seed)
    return pd.DataFrame(
        index=tree.get_tip_labels(), data=model._get_state_array().T)


def simulate_discrete_markov_data_on_tree(
    tree: 'ToyTree',
    qmatrix: np.ndarray,
    nsims: int = 1,
    ancestral_state: Optional[np.ndarray] = None,
    seed: int = None,
    ) -> List['ToyTree']:
    """Return a list of ToyTrees instance (or list of ToyTree instances) with
    simulated states assigned to every node of the tree.

    Parameters
    ----------
    tree:
        An input Toytree on the edges of which a trait will be simulated.
    qmatrix:
        An instantaneous transition rate matrix (Q matrix)
    nsims: int
        The number of replicates simulations to run.
    ancestral_state:
        ...
    seed: Optional[int]
        ...

    Returns
    -------
    Union[Tree, List[ToyTree]]
        One or more ToyTrees with a feature "discrete" assigned with
        a value to every node of the tree.

    Example
    -------
    >>> tree = toytree.rtree.unittree(ntips=10, treeheight=100, seed=123)
    >>> qmatrix =
    >>> tree = toytree.pcm.simulate_discrete_markov_states_on_tree()
    """
    model = DiscreteMarkovModelSim(tree, qmatrix, nsims, ancestral_state, seed)
    return model._get_state_tree()



if __name__ == "__main__":

    import toytree
    TREE = toytree.rtree.unittree(10, treeheight=100, seed=123)

    # use a hand-made matrix
    ALPHA = 0.001
    BETA = 0.002
    QMATRIX = np.array([
        [-ALPHA, ALPHA],
        [BETA, -BETA],
    ])

    # or generate a symmetric matrix
    QMATRIX = DiscreteMarkovModelQMatrix(nstates=3).get_rate_matrix(5e-3)

    # show matrix and simulate
    print(QMATRIX)
    print(toytree.pcm.simulate_discrete_markov_data(TREE, QMATRIX, nsims=3))
    simtree = simulate_discrete_markov_data_on_tree(TREE, QMATRIX, nsims=1)
    print(simtree[0].get_node_data("discrete"))
