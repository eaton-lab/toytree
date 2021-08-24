#!/usr/bin/env python

"""
Discrete State Markov Model Simulator. 

References
----------
Yang...
"""

from typing import Optional, List, Any
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
import scipy.linalg


@dataclass
class MarkovModel:
    """Generate a Q-matrix under ER, SYM, or ARD models.
    
    This is intended primarily for internal use by toytree.pcm.

    Examples
    --------
    >>> model = MarkovModel(3, "ARD")
    >>> print(model.qmatrix)
    """
    nstates: int
    model: str
    rate: float=1.0
    relative_rates: Optional[np.ndarray]=None
    state_frequencies: Optional[np.ndarray]=None
    seed: Optional[int]=None

    rng: np.random.Generator = field(init=False, repr=False)
    transition_matrix: np.ndarray = field(init=False)
    qmatrix: np.ndarray = field(init=False)

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)
        self.model = self.model.upper()
        assert self.model in ("ER", "SYM", "ARD"), (
            "model must be one of 'ER', 'SYM', 'ARD'")
        self._check_rates()
        self._check_freqs()
        self._set_transition_matrix()
        self._set_qmatrix()

    def _check_rates(self):
        """Checks the relative rates matrix given model and nstates.

        If a user entered the matrix it is checked to be appropriate
        given the model type. If no matrix is entered then a random
        matrix is generated that is appropriate for the model type.

        Examples
        --------
        >>> MarkovModel(2, "ER").relative_rates
        [[0, 1],[1, 0]]        
        """
        # user entered rate matrix
        rates = self.relative_rates
        if rates is None:
            if self.model == "SYM":
                rates = np.random.uniform(0.5, 2, (self.nstates, self.nstates))
                rates[0, 1] = 1
                lower = np.tril_indices_from(rates)
                upper = np.tril_indices_from(rates)[::-1]
                rates[lower] = rates[upper]
            elif self.model == "ARD":
                rates = np.random.uniform(0.5, 2, (self.nstates, self.nstates))
                rates[0, 1] = 1
            else:
                rates = np.ones((self.nstates, self.nstates))
            # report the sampled rates
            np.fill_diagonal(rates, 0)
        else:
            rates = np.array(rates)
            # check if singular for ER model
            if self.model == "ER":
                if rates.size == 1:
                    rates = (np.repeat(rates, self.nstates * self.nstates)
                        .reshape((self.nstates, self.nstates)))
                assert len(set(rates[rates != 0])) == 1, (
                    "all rates should be equal in ER model. See SYM model.")
            # check if symmetric for SYM models
            elif self.model == "SYM":
                assert np.allclose(rates, rates.T, rtol=1e-5, atol=1e-8), (
                    "rates should be symmetric in SYM model. See ARD model.")
            # check shape
            assert rates.shape == (self.nstates, self.nstates), (
                f"given nstates={self.nstates} the rates matrix should "
                f"be shape ({self.nstates}, {self.nstates}).")
            np.fill_diagonal(rates, 0)
        self.relative_rates = rates

    def _check_freqs(self):
        """Checks stationary frequencies array given model and nstates.

        Entered values are checked for correct size and that they 
        sum to one. If no values are entered then a uniform frequency
        of the correct size is sampled for ER, or a random sample that
        sums to one is sampled for SYM and ARD.

        Examples
        --------
        >>> MarkovModel(3, "ER").state_frequencies
        [1/3, 1/3, 1/3]
        """
        freqs = self.state_frequencies
        if freqs is None:
            if self.model in ("SYM", "ARD"):
                freqs = np.random.uniform(0.5, 2, self.nstates)
                freqs /= freqs.sum()
            else:
                freqs = np.repeat(1.0 / self.nstates, self.nstates)
        else:
            freqs = np.array(freqs)
            if self.model in ("SYM", "ARD"):
                assert freqs.size == self.nstates, (
                    f"states_frequencies should be len={self.nstates}.")
            else:
                fixed = np.repeat(1.0 / self.nstates, self.nstates)
                assert np.allclose(freqs, fixed), (
                    f"ER model with nstates={self.nstates} has fixed state "
                    f"frequences: {fixed}. See SYM or ARD models.")
                freqs = fixed
        assert np.allclose(sum(freqs), 1.0), (
            f"state_frequencies must sum to 1. You entered: {freqs}")
        self.state_frequencies = freqs

    def _set_transition_matrix(self):
        """Sets the transition probabilities (freqs.T x rates).

        Examples
        --------
        >>> MarkovModel(3, "ER").transition_matrix
        [[0, 1/3, 1/3, 1/3]
         [1/3, 0, 1/3, 1/3]
         [1/3, 1/3, 0, 1/3]
         [1/3, 1/3, 1/3, 0]]
        """
        # matrix multiply and set diagonal back to zero.
        sfreq_mat = np.eye(self.nstates) * self.state_frequencies
        trans_mat = np.matmul(sfreq_mat, self.relative_rates)
        np.fill_diagonal(trans_mat, 0)

        # divide by scaling factor (largest rowsum excluding diagonal)
        scaling = np.sum(trans_mat, axis=1).max()
        trans_mat /= scaling

        # fill diagonals to sum to 1
        for idx in range(trans_mat.shape[0]):
            trans_mat[idx, idx] = abs(1 - trans_mat[idx].sum())
        self.transition_matrix = self.rate * trans_mat

    def _set_qmatrix(self):
        """Set a instantaneous transition probability matrix (Q).

        This matrix is the probability of transitioning from one
        state to another in a single unit of time. The rates are
        normalized by a matrix scaling factor, calculated as the max
        rowsum of the state_frequencies matrix x rates_matrix. 
        >>> T = (rates_matrix * state_frequencies) * rate / scaling
        >>> Q = (set T diagonal so rows sum to 0.)

        Parameters
        ----------
        rate: float
            A scalar by which the Q-matrix will be multipled to act
            as a unit scaler. Example, rate=1e-6 would mean that a 1 
            in the relatives rates matrix represents 1 change per 
            million edge length units on a tree.
        rates_matrix: numpy.ndarray
            The relative transition rates between states as an array 
            of size (nstates x nstates). Values on the diagonal are 
            ignored. Only relative differences matter. See rate.
        state_frequencies: numpy.ndarray
            Equilibrium frequencies of states 0-n in order (must sum
            to one. 

        Examples
        --------
        >>> MarkovModel(nstates=3, model="ER").qmatrix
        [[-1, 1/3, 1/3, 1/3]
         [1/3, -1, 1/3, 1/3]
         [1/3, 1/3, -1, 1/3]
         [1/3, 1/3, 1/3, -1]]        
        """
        self.qmatrix = self.transition_matrix - (self.rate * np.eye(self.nstates))

    def get_transition_probability_matrix(self, time: float) -> np.ndarray:
        """Return a transition probability matrix for a length of time.

        This represents the probability that over the length of time
        a character starting in one state will transition to another:
        >>> T = (rates_matrix * state_frequencies) / scaling_factor
        >>> Q = (set diagonal of T to sum rows to 0)
        >>> P(t) = expm(Q * rate * time)

        Parameters
        ----------
        time: float
            Length of time over which state transitions can occur. 
            Note that the rates in the rate_matrix should correspond
            to the same units as time (i.e. transitions / unit time).

        Examples
        --------
        >>> mod = MarkovModel(nstates=3, model="ER")
        >>> mod.get_transition_probability_matrix(time=1.)
        [[0.44769785 0.18410072 0.18410072 0.18410072]
         [0.18410072 0.44769785 0.18410072 0.18410072]
         [0.18410072 0.18410072 0.44769785 0.18410072]
         [0.18410072 0.18410072 0.18410072 0.44769785]]

        Over zero amount of time no change is expected:
        >>> mod.get_transition_probability_matrix(time=0)        
        [[1. 0. 0. 0.]
         [0. 1. 0. 0.]
         [0. 0. 1. 0.]
         [0. 0. 0. 1.]]        

        Over very long time scales transition probabilities will match
        the state_frequencies (1 / nstates for ER model):
        >>> mod.get_transition_probability_matrix(time=1000)
        [[0.25 0.25 0.25 0.25]
         [0.25 0.25 0.25 0.25]
         [0.25 0.25 0.25 0.25]
         [0.25 0.25 0.25 0.25]]
        """
        return scipy.linalg.expm(self.qmatrix * time)

    # def _repr_html_(self):
    #     """Return a html representation of the Markov model.
    #     TODO: return multiple tables?
    #     """


@dataclass
class DiscreteMarkovSimulator:
    """Simulate a discrete trait on a tree given a Q-matrix.
    
    This is intended primarily for internal use by toytree.pcm, 
    with the user-facing functions available from factory functions
    like :meth:`simulate_discrete_data`. This takes as input a 
    ToyTree and MarkModel instances
    """
    tree: 'toytree.ToyTree'
    model: MarkovModel
    root_state: Optional[int]=None
    seed: Optional[int]=None
    rng: np.random.Generator = field(init=False)

    def __post_init__(self):
        self.tree = self.tree.copy()
        self.rng = np.random.default_rng(self.seed)
        self.root_state = (
            self.root_state if self.root_state is not None else
            self.rng.multinomial(1, self.model.state_frequencies).argmax()
        )

    def _edge_sim(self, state, time) -> int:
        """Return the state at end of this time given starting state."""
        prob = scipy.linalg.expm(self.model.qmatrix * time)
        return self.rng.multinomial(1, prob[state]).argmax()

    def _traversal_sim(self, name="trait"):
        """Traverse tree from root to tips simulating trait."""
        self.tree.treenode.add_feature(name, self.root_state)
        for node in self.tree.treenode.traverse():
            if not node.is_root():
                parent_state = getattr(node.up, name)
                state = self._edge_sim(parent_state, node.dist)
                node.add_feature(name, state)

    def get_single_trait(self) -> pd.Series:
        """Return a Series with simulated integer data, node idx 
        labels as the index, and name = 'trait'."""
        self._traversal_sim()
        return self.tree.get_node_data("trait")

    def get_multiple_traits(self, replicates: int) -> pd.DataFrame:
        """Return a DataFrame with simulated integer data, node idx 
        labels as the index, and columns labeled as t0-t{nstates}.
        """
        reps = []
        for idx in range(replicates):
            self._traversal_sim(f"t{idx}")
            reps.append(self.tree.get_node_data(f"t{idx}"))
        return pd.concat(reps, axis=1)


####################################################################
# API Exposed functions
####################################################################
def get_markov_model(
    nstates: int,
    model: str="ER",
    rate: float=1.0,
    relative_rates: Optional[np.ndarray]=None,
    state_frequencies: Optional[np.ndarray]=None,
    seed: Optional[int]=None,
    ) -> MarkovModel:
    """Return a parameterized MarkovModel instance.
    
    The MarkovModel class is used to get an instantaneous transition
    rate matrix (Q) for calculating the probabilities of transitions
    between discrete character states in a Markov model. This 
    is used primarily for didactic purposes, and is also used 
    internally in functions such as :meth:`~toytree.pcm.simulate_discrete_data`.
    
    It checks that the user input for rates and state_frequencies
    if valid given the model type and number of states, and can 
    return random valid paramterizations for each model type. 

    Parameters
    ----------
    nstates: int
        The number of states to simulate. States will be names as 
        integers 0-nstates, unless you use `state_names` to rename.
    model: str
        The Markov model name ("ER", "SYM", or "ARD"). This is used
        to either sample random valid parameters for a model of the 
        specified type, or to check that user-entered value are valid.
    rate: float
        A scalar by which the Q-matrix will be multipled to act
        as a unit scaler. Example, rate=1e-6 would mean that a 1 
        in the relatives rates matrix represents 1 change per 
        million edge length units on a tree.
    relative_rates: Optional[numpy.ndarray]
        The relative transition rates between states as an array 
        of size (nstates x nstates). Values on the diagonal are 
        ignored. Only relative differences matter. See rate.
    state_frequencies: Optional[numpy.ndarray]
        Equilibrium frequencies of states 0-n in order (must sum
        to one. 
    seed: Optional[int]
        Integer seed for numpy random number generator.

    Returns
    -------
    MarkovModel
        A parameterized MarkovModel class instance. The parameters
        of Markov model can be accessed from this instance from its
        attributes `.qmatrix`, `.state_frequencies`, etc.

    Examples
    --------
    >>> print(toytree.pcm.get_markov_model(nstates=3, model="ER"))
    >>> print(toytree.pcm.get_markov_model(nstates=3, model="SYM"))
    >>> print(toytree.pcm.get_markov_model(nstates=3, model="ARD")
    """
    model = MarkovModel(
        model=model, 
        nstates=nstates, 
        rate=rate,
        relative_rates=relative_rates,
        state_frequencies=state_frequencies,
        seed=seed,
    )
    return model

def simulate_discrete_data(
    tree: 'ToyTree',
    nstates: int,
    model: str="ER",
    rate: float=1.0,
    relative_rates: Optional[np.ndarray]=None,
    state_frequencies: Optional[np.ndarray]=None,
    seed: Optional[int]=None,
    root_state: Optional[int]=None,
    nreplicates: int=0,
    tips_only: bool=False,
    state_names: Optional[List[Any]]=None,
    ) -> pd.Series:
    """Return trait values simulated under a discrete Markov model.

    The number of states and model type can be entered without any
    parameters to the Markov model (e.g., relative rates and/or 
    state_frequencies) to generate a random set of parameters that
    are valid under the specified model. Or, if parameters are entered
    then they are checked for validity with the specified model type,
    and then used to parameterize the Markov model simulation.

    Parameters
    ----------
    tree: toytree.ToyTree
        The tree on which to simulate the trait, usually ultrametric.
    nstates: int
        The number of states to simulate. States will be names as 
        integers 0-nstates, unless you use `state_names` to rename.
    model: str
        The Markov model name ("ER", "SYM", or "ARD"). This is used
        to either sample random valid parameters for a model of the 
        specified type, or to check that user-entered value are valid.
    rate: float
        A scalar by which the Q-matrix will be multipled to act
        as a unit scaler. Example, rate=1e-6 would mean that a 1 
        in the relatives rates matrix represents 1 change per 
        million edge length units on a tree.
    relative_rates: Optional[numpy.ndarray]
        The relative transition rates between states as an array 
        of size (nstates x nstates). Values on the diagonal are 
        ignored. Only relative differences matter. See rate.
    state_frequencies: Optional[numpy.ndarray]
        Equilibrium frequencies of states 0-n in order (must sum
        to one. 
    seed: Optional[int]
        Integer seed for numpy random number generator.
    root_state: Optional[int]
        The state at the root node (start of simulation). If None a
        state is randomly selected based on 
    nreplicates: int
        If nreplicates is > 0 then the returned object is a DataFrame
        with replicate numbers as columns labels, otherwise a single
        Series is returned.
    tips_only: bool
        If True then values are only returned for tip nodes, instead
        of all nodes in a tree. This is often the case for empirical
        data, where states are only known for the tips.
    state_names: Optional[List[Any]]
        Simulated states will be substituted with the ordered values
        in this list to replace states 0-nstates.

    Returns
    -------
    pandas.Series or pandas.DataFrame:
        ...

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> toytree.pcm.simulate_discrete_data(tree, 2, "ER")
    0    1
    1    0
    2    1
    3    0
    4    0
    5    0
    Name: trait, dtype: int64

    >>> toytree.pcm.simulate_discrete_data(
    >>>     tree=tree, nstates=2, model="ARD", 
    >>>     rate=0.1, 
    >>>     relative_rates=[[0, 2], [1, 0]], 
    >>>     state_frequencies=[0.4, 0.6],
    >>>     nreplicates=5,
    >>>     tips_only=True,
    >>>     state_names=["A", "B"],
    >>> )
        t0  t1  t2  t3  t4
    0   A   B   A   A   B
    1   B   B   A   B   B
    2   A   B   B   A   B
    3   A   B   B   B   B
    4   B   B   A   B   B
    ...
    """
    model = MarkovModel(
        model=model, 
        nstates=nstates, 
        rate=rate,
        relative_rates=relative_rates,
        state_frequencies=state_frequencies,
    )
    simulator = DiscreteMarkovSimulator(
        tree=tree,
        model=model,
        root_state=root_state,
        seed=seed,
    )

    # get DataFrame or Series result
    if nreplicates:
        traits = simulator.get_multiple_traits(nreplicates)
    else:
        traits = simulator.get_single_trait()

    # subsample to return only tips
    if tips_only:
        traits = traits.loc[:tree.ntips]

    # rename data from numeric to user defined
    if state_names is not None:
        for idx, value in enumerate(state_names):
            traits.replace(to_replace=idx, value=value, inplace=True)
    return traits

# def draw_markov_model():
#     """Returns a toyplot graph representation of a Markov model.
#     """
#     # c, a, m = toyplot.graph()
#     # return c, a, m


if __name__ == "__main__":

    import toytree

    # get a single tree with trait values
    tre = toytree.rtree.unittree(10, treeheight=10, seed=123)
    data = simulate_discrete_data(
        tree=tre, 
        nstates=3, model="SYM", state_frequencies=[0.1, 0.3, 0.6],
        tips_only=True,
        root_state=0,
        nreplicates=10,
        state_names=['a', 'b', 'c'],
    )
    print(data)

    # get many trees with traits simulated
    # ...


    # get a dataframe of tip or node traits
    # ...


    # get an array of many replicate sim data
    # ...