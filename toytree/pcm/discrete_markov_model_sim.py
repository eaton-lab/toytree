#!/usr/bin/env python

"""
Discrete State Markov Model Simulator. 
Some code from ipcoal (McKenzie and Eaton 2020).
"""

from typing import List, Optional, Union, Dict, Any

import pandas as pd
import numpy as np
from scipy.linalg import expm
from toytree import ToyTree


class DiscreteMarkovModelQMatrix:
    """
    Returns a Q matrix under a model (ER, SYM, ...) for n states...
    TODO: more than ER
    """
    def __init__(
        self,
        nstates: int = 2,
        state_frequencies: Optional[Union[List,np.ndarray]] = None,
        ):

        assert nstates > 1, "discrete model must have >1 state"
        self.nstates = nstates
        self.state_frequencies = (
            state_frequencies if state_frequencies is not None 
            else np.repeat(1 / nstates, nstates)
        )



    def get_rate_matrix(self, scalar:float=1.):
        """
        Returns the normalized instantaneous rate matrix (Q) 
        optionally transformed by a scalar
        """
        # make non-normalized matrix (source sink)
        sfreqs = np.matrix(self.state_frequencies)
        ones = np.matrix(np.ones(sfreqs.size)).T
        non_normal_qmat = np.array(ones * sfreqs)
        for idx in range(ones.size):
            rowsum = non_normal_qmat[idx].sum()
            non_normal_qmat[idx, idx] = -(rowsum - non_normal_qmat[idx, idx])

        # full matrix scaling factor
        scaling = [
            non_normal_qmat[i][i] * self.state_frequencies[i]
            for i in range(self.nstates)
        ]
        scaling = -1 / np.sum(scaling)

        # get adjusted rate matrix
        qmatrix = non_normal_qmat * scaling * scalar
        return qmatrix



class DiscreteMarkovModelSim:
    """
    Simulate a discrete n-state character model on a phylogenetic tree
    to get states assigned to every node. Input requires a Q matrix
    (instantaneous transition rate matrix) that can be estimtated from
    tip states using DiscreteMarkovModelFit.

    Examples:
    ---------
    import toytree
    tree = toytree.rtree.unittree(10)
    qmatrix = [[-0.7, 0.3], [0.5, -0.5]]
    data = tree.pcm.simulate_discrete_markov_model(qmatrix, nsims=100)
    print(data)

    See also:
    ---------
    ...

    References:
    -----------
    ...
    """
    def __init__(
        self, 
        tree: ToyTree,
        qmatrix: Union[np.ndarray, pd.DataFrame],
        nsims: int = 1,
        ancestral_state: Optional[Any] = None,
        seed: int = None,
        ):

        # store input args
        self.rng = np.random.default_rng(seed)
        self.nsims = nsims
        self.tree = tree
        self.qmatrix = np.array(qmatrix)
        self.nstates = self.qmatrix.shape[0]
        self.ancestral_state = (
            ancestral_state if ancestral_state is not None
            else self.rng.choice(range(self.nstates), size=nsims)
        )

        # arg type checks
        assert self.nstates >= 2, "discrete model must have >1 states"
        assert self.ancestral_state.size == self.nsims, (
            "ancestral_state must be length nsims (set for every sim")
        assert np.allclose(self.qmatrix.sum(axis=1), 0), (
            f"rows of the Q matrix must sum to zero: {self.qmatrix.sum(axis=1)}")


    def get_state_array(self) -> np.ndarray:
        """
        Rates are returned in units of changes per unit branch length, 
        and so should be interpreted in the context of whether blens
        are in units of years, mya, substitutions, etc.
        """
        data = np.zeros((self.nsims, self.tree.ntips), dtype=int)
        for sim in range(self.nsims):
            trait = {self.tree.treenode.idx: self.ancestral_state[sim]}
            for node in self.tree.treenode.traverse():
                if not node.is_root():
                    # probability of change over this length of branch
                    prob_mat = expm(node.dist * self.qmatrix)
                    # sample from probability matrix
                    trait[node.idx] = np.argmax(
                        np.random.multinomial(1, prob_mat[trait[node.up.idx]]))
            data[sim] = [trait[i] for i in range(self.tree.ntips)]
        return data


    def get_state_tree(self) -> List[ToyTree]:
        """
        Rates are returned in units of changes per unit branch length, 
        and so should be interpreted in the context of whether blens
        are in units of years, mya, substitutions, etc.
        """
        data = []
        for sim in range(self.nsims):
            trait = {self.tree.treenode.idx: self.ancestral_state[sim]}
            for node in self.tree.treenode.traverse():
                if not node.is_root():
                    # probability of change over this length of branch
                    prob_mat = expm(node.dist * self.qmatrix)
                    # sample from probability matrix
                    trait[node.idx] = np.argmax(
                        np.random.multinomial(1, prob_mat[trait[node.up.idx]]))
            ntre = self.tree.set_node_values(feature='discrete', mapping=trait)
            data.append(ntre)
        return data


def simulate_discrete_markov_states(
    tree: ToyTree, 
    qmatrix: np.ndarray, 
    nsims: int = 1,
    ancestral_state: Optional[np.ndarray] = None,
    seed: int = None,
    ) -> pd.DataFrame:
    """
    Returns a DataFrame with dimensions (ntips x nsims) with simulated
    discrete characters assigned to each tip name in each simulation.
    """
    model = DiscreteMarkovModelSim(tree, qmatrix, nsims, ancestral_state, seed)
    return pd.DataFrame(
        index=tree.get_tip_labels(), data=model.get_state_array().T)


def simulate_discrete_markov_states_on_tree(
    tree: ToyTree, 
    qmatrix: np.ndarray, 
    nsims: int = 1,
    ancestral_state: Optional[np.ndarray] = None,
    seed: int = None,
    ) -> List[ToyTree]:
    """
    Returns a ToyTree object (or list of ToyTree objects) with 
    simulated states assigned to every node of the tree.
    """
    model = DiscreteMarkovModelSim(tree, qmatrix, nsims, ancestral_state, seed)
    return model.get_state_tree()



if __name__ == "__main__":

    import toytree
    TREE = toytree.rtree.unittree(10, treeheight=100, seed=123)

    ALPHA = 0.001
    BETA = 0.001
    QMATRIX = np.array([
        [- ALPHA, ALPHA],
        [BETA, - BETA],
    ])
    QMATRIX = DiscreteMarkovModelQMatrix(nstates=2).get_rate_matrix(5e-3)
    print(QMATRIX)
    print(simulate_discrete_markov_states(TREE, QMATRIX, nsims=1))
    # print(simulate_discrete_markov_states_on_tree(TREE, QMATRIX, nsims=1))
