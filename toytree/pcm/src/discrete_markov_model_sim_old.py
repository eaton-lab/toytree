#!/usr/bin/env python

"""
Discrete State Markov Model Simulator. 

Some code from ipcoal (McKenzie and Eaton 2020).
"""

from typing import Optional, Union, List, Any
import pandas as pd
import numpy as np
import scipy.linalg


class QMatrixGenerator:
    """Generate a Q matrix under a number of models (ER, SYM, ARD).

    Returns a Q matrix under a model (ER, SYM, ARD) for n states 
    given user input for number of states, state_frequencies, and
    for the case of complex models (SYM with >2 states, or ARD), the
    relative rates as a matrix.

    Parameters
    ----------
    nstates: int
        The number of discrete Markov states.
    state_frequencies: 
        Equilibrium frequencies of states 0-n in order (should sum
        to one. 
    relative_rates: numpy.ndarray
        The relative transition rates between states as an array
        of size (nstates x nstates). Only relative differences among
        rates are relevant (will be auto-scaled). Values on the 
        diagonal are ignored. 

    Examples
    --------
    >>> # Generate an ER (equal-rates) normalized Q-matrix
    >>> qgen = DiscreteMarkovModelQMatrix(nstates=3)
    >>> qmatrix = qgen.get_rate_matrix()

    >>> # Generate an SYM (symmetric) normalized Q-matrix
    >>> qgen = DiscreteMarkovModelQMatrix(3, [0.1, 0.2, 0.3])
    >>> qmatrix = qgen.get_rate_matrix()

    >>> # Generate an ARD (all-rates-different) normalized Q-matrix
    >>> qgen = DiscreteMarkovModelQMatrix(3, [0.1, 0.2, 0.3])
    >>> qmatrix = qgen.get_rate_matrix()
    """
    def __init__(
        self,
        nstates: int=2,
        state_frequencies: Optional[Union[List,np.ndarray]]=None,
        ):
        assert nstates > 1, "discrete model must have >1 state"
        self.nstates = nstates
        self.state_frequencies = (
            state_frequencies if state_frequencies is not None 
            else np.repeat(1 / nstates, nstates)
        )

    def _get_relative_rates_er(self):
        """Return relative rates under the equal-rates model"""
        return np.repeat(1, self.nstates)

    def _get_relative_rates_sym(self, rates):
        """Return relative rates under the symmetric model"""
        nparams = (self.nstates * (self.nstates - 1)) / 2
        assert len(rates) == nparams, (
            f"the symmetric model with {self.nstates} should have "
            f"{nparams} rate parameters.")
        return np.repeat(1, self.nstates)

    def _get_non_normalized_qmatrix(self) -> np.ndarray:
        """Return the non-normalized instantaneous rate matrix.

        This matrix represents the nstates and their state frequencies
        before being normalized by a matrix scaling factor that will
        account for differences in state frequencies.

        Note
        ----
        This is not the Q-matrix you are looking for.

        Examples
        --------
        >>> qgen = DiscreteMarkovModelQMatrix(nstates=3)
        >>> qmatrix = qgen.get_non_normalized_qmatrix()
        [[-0.66666667  0.33333333  0.33333333]
         [ 0.33333333 -0.66666667  0.33333333]
         [ 0.33333333  0.33333333 -0.66666667]]

        >>> qgen = DiscreteMarkovModelQMatrix(3, [0.2, 0.4, 0.6])
        >>> qmatrix = qgen.get_non_normalized_qmatrix()
        [[-1.   0.4  0.6]
         [ 0.2 -0.8  0.6]
         [ 0.2  0.4 -0.6]]
        """
        # make non-normalized matrix (source sink)
        sfreqs = np.matrix(self.state_frequencies)
        ones = np.matrix(np.ones(sfreqs.size)).T
        non_normal_qmat = np.array(ones * sfreqs)
        for idx in range(ones.size):
            rowsum = non_normal_qmat[idx].sum()
            non_normal_qmat[idx, idx] = -(rowsum - non_normal_qmat[idx, idx])
        return non_normal_qmat

    def get_adjusted_rate_matrix(self, scalar: float=1.) -> np.ndarray:
        """Return the adjusted instantaneous rate matrix (Q).

        This is the Q-matrix that should be used in phylogenetic 
        comparative methods. It represents the expected instantaneous
        transition rates between nstates. It is calculated from the
        state frequencies ...

        Parameters
        ----------
        scalar: float
            Multiply the Q-matrix by a scalar to represent transition
            rates per unit of the scalar.

        Examples
        --------
        >>> qgen = DiscreteMarkovModelQMatrix(nstates=3)
        >>> qmatrix = qgen.get_adjusted_rate_matrix()
        [[-1.   0.5  0.5]
         [ 0.5 -1.   0.5]
         [ 0.5  0.5 -1. ]]

        >>> qgen = DiscreteMarkovModelQMatrix(3, [0.2, 0.4, 0.6])
        >>> qmatrix = qgen.get_adjusted_rate_matrix()
        [[-1.13636364  0.45454545  0.68181818]
         [ 0.22727273 -0.90909091  0.68181818]
         [ 0.22727273  0.45454545 -0.68181818]]
        """
        # get the non-normalized rate matrix
        non_normal_qmat = self._get_non_normalized_qmatrix()

        # get full matrix scaling factor
        scaling = [
            non_normal_qmat[i][i] * self.state_frequencies[i]
            for i in range(self.nstates)
        ]
        scaling = -1 / np.sum(scaling)

        # get adjusted rate matrix
        qmatrix = non_normal_qmat * scaling * scalar
        return qmatrix


class DiscreteMarkovModelSim:
    """Simulate a discrete n-state character on a phylogenetic tree.

    Input Q matrix (instantaneous transition rate matrix) can be 
    estimated from tip states using DiscreteMarkovModelFit.
    
    Parameters
    ----------
    tree
        ...
    qmatrix
        ...
    nsims
        ...

    Examples
    --------
    >>> import toytree
    >>> tree = toytree.rtree.unittree(10)
    >>> qmatrix = [[-0.7, 0.3], [0.5, -0.5]]
    >>> data = tree.pcm.simulate_discrete_markov_model(qmatrix, nsims=100)

    See also:
    ---------
    ...

    References:
    -----------
    ...
    """
    def __init__(
        self, 
        tree: 'toytree.ToyTree',
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

    def _get_state_array(self) -> np.ndarray:
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
                    prob_mat = scipy.linalg.expm(node.dist * self.qmatrix)
                    # sample from probability matrix
                    trait[node.idx] = np.argmax(
                        np.random.multinomial(1, prob_mat[trait[node.up.idx]]))
            data[sim] = [trait[i] for i in range(self.tree.ntips)]
        return data

    def _get_state_tree(self) -> List['toytree.ToyTree']:
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
                    prob_mat = scipy.linalg.expm(node.dist * self.qmatrix)
                    # sample from probability matrix
                    trait[node.idx] = np.argmax(
                        np.random.multinomial(1, prob_mat[trait[node.up.idx]]))
            ntre = self.tree.set_node_data(feature='discrete', mapping=trait)
            data.append(ntre)
        return data


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

    # equal rates model
    QGEN = QMatrixGenerator(nstates=3)
    print(QGEN.get_adjusted_rate_matrix(1))    
    # print(QGEN._get_non_normalized_qmatrix())

    QGEN = QMatrixGenerator(nstates=3, state_frequencies=[0.2, 0.4, 0.6])
    # print(QGEN._get_non_normalized_qmatrix())
    print(QGEN.get_adjusted_rate_matrix(1))

    print(QGEN.get_adjusted_rate_matrix(0.5))

    # or generate a symmetric matrix
    QGEN = QMatrixGenerator(nstates=3, state_frequencies=[0.25, 0.2, 0.15])
    print(QGEN._get_non_normalized_qmatrix())
    print(QGEN.get_adjusted_rate_matrix())

    QMATRIX = QGEN.get_adjusted_rate_matrix(5e-3)

    # show matrix and simulate
    print(QMATRIX)
    print(toytree.pcm.simulate_discrete_markov_data(TREE, QMATRIX, nsims=3))
    # print(toytree.pcm.simulate_discrete_markov_data_on_tree(TREE, QMATRIX, nsims=1))
