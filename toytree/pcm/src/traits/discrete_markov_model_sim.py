#!/usr/bin/env python

"""Discrete State Markov Model Simulator.

This module implements a discrete trait simulator based on a Markov
model. The root state is either randomly sampled, or assigned, and
transitions among states occur probabilistiically along the edges of
a phylogeny. Transition rates can be specified for models with
unequal transition rates.   

References
----------
- Yang...
"""

from typing import Optional, List, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import scipy.linalg
from toytree import ToyTree
from toytree.core.apis import add_subpackage_method, PhyloCompAPI

__all__ = [
    "get_markov_model",
    "simulate_discrete_data",
]


class ModelType(Enum):
    """Supported named Markov model types to be fit or simulated.

    This will raise an exception is user tries to enter a value not
    supported in this class.
    """
    ER = "ER"
    SYM = "SYM"
    ARD = "ARD"


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
    """: Number of possible character states."""
    mtype: ModelType
    """: Model type ("ER", "SYM", "ARD")."""
    relative_rates: Optional[np.ndarray] = None
    """: Relative transition rates. If not entered then values are
    sampled within model constraints given the random seed."""
    state_frequencies: Optional[np.ndarray] = None
    """: Equilibrium frequencies of the nstates."""
    rate_scalar: float = 1.0
    """: Rate scalar to multiple relative rates by."""
    seed: Optional[int] = None
    """: Random seed used if relative_rates is None."""

    # attributes filled after init.
    rng: np.random.Generator = field(init=False, repr=False)
    """: Random number generator init with seed."""
    transition_matrix: np.ndarray = field(init=False)
    """: Transition probability matrix (P)."""
    qmatrix: np.ndarray = field(init=False)
    """: Instantaneous rate matrix (Q)."""

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)
        self.mtype = ModelType(self.mtype)
        self._check_rates()
        self._check_freqs()
        self._set_transition_matrix()
        self._set_qmatrix()

    def _check_rates(self):
        """Checks the relative rates matrix given mtype and nstates.

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
        
        # if no user-entered rates then sample random rates constrained
        # by the model type.
        if rates is None:
            if self.mtype.name == "SYM":
                rates = np.random.uniform(0.5, 2, (self.nstates, self.nstates))
                rates[0, 1] = 1
                lower = np.tril_indices_from(rates)
                upper = np.tril_indices_from(rates)[::-1]
                rates[lower] = rates[upper]
            elif self.mtype.name == "ARD":
                rates = np.random.uniform(0.5, 2, (self.nstates, self.nstates))
                rates[0, 1] = 1
            else:
                rates = np.ones((self.nstates, self.nstates))
            np.fill_diagonal(rates, 0)
        
        # if user entered rates then check that they are valid.
        else:
            rates = np.array(rates)
            # check if singular for ER model
            if self.mtype.name == "ER":
                if rates.size == 1:
                    rates = (
                        np.repeat(rates, self.nstates * self.nstates)
                        .reshape((self.nstates, self.nstates))
                    )
                assert len(set(rates[rates != 0])) == 1, (
                    "all rates should be equal in ER model. See SYM model.")
            # check if symmetric for SYM models
            elif self.mtype.name == "SYM":
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
            if self.mtype.name in ("SYM", "ARD"):
                freqs = np.random.uniform(0.5, 2, self.nstates)
                freqs /= freqs.sum()
            else:
                freqs = np.repeat(1.0 / self.nstates, self.nstates)
        else:
            freqs = np.array(freqs)
            if self.mtype.name in ("SYM", "ARD"):
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
        self.transition_matrix = self.rate_scalar * trans_mat

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
        self.qmatrix = self.transition_matrix - (self.rate_scalar * np.eye(self.nstates))

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

    def __repr__(self):
        """Return a str representation of the Markov model."""
        return f"MarkovModel(nstates={self.nstates}, model={self.mtype.name})"
        # ,\nT matrix\n{self.transition_matrix}\nQ matrix\n{self.qmatrix}\nTransition Probabilities (t=1)\n{self.get_transition_probability_matrix(time=1)}"



@dataclass
class DiscreteMarkovSimulator:
    """Simulate a discrete trait on a tree given a Q-matrix.

    This is intended primarily for internal use by toytree.pcm,
    with the user-facing functions available from factory functions
    like :meth:`simulate_discrete_data`. This takes as input a
    ToyTree and MarkModel instances
    """
    tree: ToyTree
    """: ToyTree with edge lengths in units of ..."""
    model: MarkovModel
    """: MarkovModel object with parameterized Q matrix."""
    root_state: Optional[int] = None
    """: Integer character state at the root."""
    seed: Optional[int] = None
    """: ..."""
    rng: np.random.Generator = field(init=False)
    """: ..."""

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)

    def _edge_sim(self, state: int, time: float) -> int:
        """Return the state at end of this time given starting state."""
        prob = scipy.linalg.expm(self.model.qmatrix * time)
        return self.rng.multinomial(1, prob[state]).argmax()

    def _traversal_sim(self) -> np.ndarray:
        """Traverse tree from root to tips simulating trait."""
        arr = np.zeros(self.tree.nnodes, dtype=np.int64)
        # sample a random root state
        if self.root_state is None:
            arr[-1] = self.rng.multinomial(1, self.model.state_frequencies).argmax()
        else:
            arr[-1] = self.root_state

        # ...
        for node in self.tree[::-1][1:]:
            parent_state = arr[node.up._idx]
            state = self._edge_sim(parent_state, node._dist)
            arr[node._idx] = state
        return arr

    def run(self, nreplicates: int) -> pd.DataFrame:
        """Return a DataFrame with simulated discrete (integer) data.

        Node idx labels as index, and columns labeled t0-t{replicates}.
        """
        arr = np.zeros((self.tree.nnodes, nreplicates), dtype=np.int64)
        for ridx in range(nreplicates):
            arr[:, ridx] = self._traversal_sim()
        traits = [f"t{i}" for i in range(nreplicates)]
        return pd.DataFrame(data=arr, index=range(self.tree.nnodes), columns=traits)


####################################################################
# API Exposed functions
####################################################################
def get_markov_model(
    nstates: int,
    model: str = "ER",
    rate_scalar: float = 1.0,
    relative_rates: Optional[np.ndarray] = None,
    state_frequencies: Optional[np.ndarray] = None,
    seed: Optional[int] = None,
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
    rate_scalar: float
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
        mtype=str(model).upper(),
        nstates=nstates,
        rate_scalar=rate_scalar,
        relative_rates=relative_rates,
        state_frequencies=state_frequencies,
        seed=seed,
    )
    return model


@add_subpackage_method(PhyloCompAPI)
def simulate_discrete_data(
    tree: ToyTree,
    nstates: int,
    model: str = "ER",
    relative_rates: Optional[np.ndarray] = None,
    state_frequencies: Optional[np.ndarray] = None,
    root_state: Optional[int] = None,
    rate_scalar: Optional[float] = 1.0,
    nreplicates: int = 1,
    tips_only: bool = False,
    state_names: Optional[List[Any]] = None,
    seed: Optional[int] = None,
    inplace: bool = False,
) -> Union[pd.DataFrame, None]:
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
    relative_rates: Optional[numpy.ndarray]
        The relative transition rates between states as an array
        of size (nstates x nstates). Values on the diagonal are
        ignored. Only relative differences matter. See rate_scalar.
    state_frequencies: Optional[numpy.ndarray]
        Equilibrium frequencies of states 0-n in order (must sum
        to one.
    root_state: Optional[int]
        The state at the root node (start of simulation). If None a
        state is randomly uniformly sampled from nstates.
    rate_scalar: float
        A scalar by which the Q-matrix will be multipled to act
        as a unit scaler. Example, rate=1e-6 would mean that a 1
        in the relatives rates matrix represents 1 change per
        million edge length units on a tree. Default=1 (no scaling)
    seed: Optional[int]
        Integer seed for numpy random number generator.
    tips_only: bool
        If True values are only returned for tip Nodes, else values are
        returned for all Nodes in the tree.
    state_names: Optional[List[Any]]
        State names will be substituted for simulated discrete integer
        states in the entered order.
    nreplicates: int
        If nreplicates is > 0 then the returned object is a DataFrame
        with replicate numbers as columns labels, otherwise a single
        Series is returned.
    inplace: bool
        If False a DataFrame is returned, if True a ToyTree is returned
        with data stored to Nodes.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>>
    >>> # simulate a single trait
    >>> toytree.pcm.simulate_discrete_data(tree, 2, "ER")
    >>> # 0    1
    >>> # 1    0
    >>> # 2    1
    >>> # 3    0
    >>> # 4    0
    >>> # 5    0
    >>> # Name: trait, dtype: int64
    >>>
    >>> # simulate multiple replicate simulations
    >>> toytree.pcm.simulate_discrete_data(
    >>>     tree=tree, nstates=2, model="ARD",
    >>>     rate=0.1,
    >>>     relative_rates=[[0, 2], [1, 0]],
    >>>     state_frequencies=[0.4, 0.6],
    >>>     nreplicates=5,
    >>>     tips_only=True,
    >>>     state_names=["A", "B"],
    >>> )
    >>>
    >>> #     t0  t1  t2  t3  t4
    >>> # 0   A   B   A   A   B
    >>> # 1   B   B   A   B   B
    >>> # 2   A   B   B   A   B
    >>> # 3   A   B   B   B   B
    >>> # 4   B   B   A   B   B
    >>> # ...
    """
    model = MarkovModel(
        mtype=model,
        nstates=nstates,
        relative_rates=relative_rates,
        state_frequencies=state_frequencies,
        rate_scalar=rate_scalar,
    )
    simulator = DiscreteMarkovSimulator(
        tree=tree,
        model=model,
        root_state=root_state,
        seed=seed,
    )

    # get DataFrame or Series result
    traits = simulator.run(nreplicates)

    # subsample to return only tips
    if tips_only:
        traits = traits.iloc[:tree.ntips]

    # rename data from numeric to user defined
    if state_names is not None:
        for idx, value in enumerate(state_names):
            traits.replace(to_replace=idx, value=value, inplace=True)

    # store data to ToyTree or return as DataFrame
    if not inplace:
        return traits
    tree.set_node_data_from_dataframe(traits, inplace=True)
    return None


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
        nstates=3,
        model="SYM",
        rate_scalar=1.,
        state_frequencies=[0.1, 0.3, 0.6],
        tips_only=True,
        root_state=0,
        nreplicates=10,
        state_names=['a', 'b', 'c'],
    )
    # print(data.T)
    # data = simulate_discrete_data(tre, nstates=2, inplace=True)
    print(data)

    # get many trees with traits simulated
    # ...

    # get a dataframe of tip or node traits
    # ...

    # get an array of many replicate sim data
    # ...

    model = get_markov_model(model="SYM", nstates=3, state_frequencies=[0.1, 0.2, 0.7], rate_scalar=0.1)
    print(model)
    print(model.get_transition_probability_matrix(time=10))
