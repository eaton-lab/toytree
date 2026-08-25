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

from __future__ import annotations

import string
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Sequence

import numpy as np
import pandas as pd
import scipy.linalg

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = [
    "get_markov_model",
    "simulate_discrete_trait",
]


def get_stationary_frequencies(qmatrix: np.ndarray) -> Optional[np.ndarray]:
    """Return the unique stationary distribution of Q, or None.

    A reducible CTMC can have more than one stationary distribution. In that
    case there is no model-implied default distribution for the root.
    """
    qmatrix = np.asarray(qmatrix, dtype=float)
    basis = scipy.linalg.null_space(qmatrix.T)
    if basis.shape[1] != 1:
        return None
    freqs = basis[:, 0]
    if freqs.sum() < 0.0:
        freqs = -freqs
    total = float(freqs.sum())
    if (not np.isfinite(total)) or np.isclose(total, 0.0):
        return None
    freqs = freqs / total
    tol = 1e-10
    if np.any(freqs < -tol):
        return None
    freqs = np.clip(freqs, 0.0, None)
    freqs /= freqs.sum()
    if not np.allclose(freqs @ qmatrix, 0.0, atol=1e-8, rtol=1e-8):
        return None
    return freqs


def _coerce_root_prior(
    root_prior: Optional[np.ndarray],
    nstates: int,
) -> Optional[np.ndarray]:
    """Return a validated root-state probability vector."""
    if root_prior is None:
        return None
    prior = np.asarray(root_prior, dtype=float)
    if prior.shape != (nstates,):
        raise ToytreeError("root_prior must have length nstates")
    if np.any(~np.isfinite(prior)) or np.any(prior < 0.0):
        raise ToytreeError("root_prior must contain finite non-negative values")
    if not np.isclose(prior.sum(), 1.0):
        raise ToytreeError("root_prior must sum to 1")
    return prior


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
    root_prior: Optional[np.ndarray] = None
    """: Root-state distribution. If None, use the stationary distribution."""
    rate_scalar: float = 1.0
    """: Rate scalar to multiple relative rates by."""
    seed: int | np.random.Generator | None = None
    """: Random seed used if relative_rates is None."""

    # attributes filled after init.
    rng: np.random.Generator = field(init=False, repr=False)
    """: Random number generator init with seed."""
    transition_matrix: np.ndarray = field(init=False)
    """: Instantaneous rate matrix (Q), retained for backward compatibility."""
    qmatrix: np.ndarray = field(init=False)
    """: Instantaneous rate matrix (Q)."""
    state_frequencies: Optional[np.ndarray] = field(init=False)
    """: Unique stationary distribution implied by Q, if one exists."""

    def __post_init__(self):
        self.rng = (
            self.seed
            if isinstance(self.seed, np.random.Generator)
            else np.random.default_rng(self.seed)
        )
        self.mtype = ModelType(str(self.mtype).upper())
        self._check_rates()
        self._set_transition_matrix()
        self.state_frequencies = get_stationary_frequencies(self.qmatrix)
        entered_prior = _coerce_root_prior(self.root_prior, self.nstates)
        if entered_prior is None:
            if self.state_frequencies is None:
                raise ToytreeError(
                    "root_prior is required when Q has no unique stationary "
                    "distribution"
                )
            entered_prior = self.state_frequencies.copy()
        self.root_prior = entered_prior

    def _check_rates(self):
        """Check the relative rates matrix given mtype and nstates.

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
                rates = self.rng.uniform(0.5, 2, (self.nstates, self.nstates))
                rates[0, 1] = 1
                lower = np.tril_indices_from(rates)
                upper = np.tril_indices_from(rates)[::-1]
                rates[lower] = rates[upper]
            elif self.mtype.name == "ARD":
                rates = self.rng.uniform(0.5, 2, (self.nstates, self.nstates))
                rates[0, 1] = 1
            else:
                rates = np.ones((self.nstates, self.nstates))
            np.fill_diagonal(rates, 0)

        # if user entered rates then check that they are valid.
        else:
            rates = np.array(rates, dtype=float)
            # check if singular for ER model
            if self.mtype.name == "ER":
                if rates.size == 1:
                    rates = np.repeat(rates, self.nstates * self.nstates).reshape(
                        (self.nstates, self.nstates)
                    )
                assert (
                    len(set(rates[rates != 0])) == 1
                ), "all rates should be equal in ER model. See SYM model."
            # check if symmetric for SYM models
            elif self.mtype.name == "SYM":
                assert np.allclose(
                    rates, rates.T, rtol=1e-5, atol=1e-8
                ), "rates should be symmetric in SYM model. See ARD model."
            # check shape
            assert rates.shape == (self.nstates, self.nstates), (
                f"given nstates={self.nstates} the rates matrix should "
                f"be shape ({self.nstates}, {self.nstates})."
            )
            np.fill_diagonal(rates, 0)
        rates = np.asarray(rates, dtype=float)
        offdiag = ~np.eye(self.nstates, dtype=bool)
        if np.any(~np.isfinite(rates[offdiag])) or np.any(rates[offdiag] < 0.0):
            raise ToytreeError(
                "relative_rates must contain finite non-negative off-diagonal values"
            )
        self.relative_rates = rates

    def _set_transition_matrix(self):
        """Set Q directly from the off-diagonal relative rates.

        Off-diagonal entries are q_ij = rate_scalar * r_ij. Diagonal entries
        are the negative row sums.

        Examples
        --------
        >>> MarkovModel(3, "ER").transition_matrix
        [[-2, 1, 1]
         [1, -2, 1]
         [1, 1, -2]]
        """
        if (not np.isfinite(self.rate_scalar)) or self.rate_scalar < 0.0:
            raise ToytreeError("rate_scalar must be finite and non-negative")
        trans_mat = np.asarray(self.relative_rates, dtype=float).copy()
        np.fill_diagonal(trans_mat, 0)
        trans_mat *= self.rate_scalar

        # set diagonals so rows sum to zero
        row_sums = trans_mat.sum(axis=1)
        np.fill_diagonal(trans_mat, -row_sums)
        # store the result on both names for clarity and compatibility
        # with callers that expect either attribute.
        self.transition_matrix = trans_mat
        self.qmatrix = trans_mat

    def get_transition_probability_matrix(self, time: float) -> np.ndarray:
        """Return a transition probability matrix for a length of time.

        This represents the probability that over the length of time
        a character starting in one state will transition to another:
        >>> Q_ij = rate_scalar * r_ij
        >>> Q_ii = -sum(Q_ij)
        >>> P(t) = expm(Q * time)

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
        [[0.57858629 0.21070686 0.21070686]
         [0.21070686 0.57858629 0.21070686]
         [0.21070686 0.21070686 0.57858629]]

        Over zero amount of time no change is expected:
        >>> mod.get_transition_probability_matrix(time=0)
        [[1. 0. 0.]
         [0. 1. 0.]
         [0. 0. 1.]]

        Over very long time scales transition probabilities will match
        the state_frequencies (1 / nstates for ER model):
        >>> mod.get_transition_probability_matrix(time=1000)
        [[0.33333333 0.33333333 0.33333333]
         [0.33333333 0.33333333 0.33333333]
         [0.33333333 0.33333333 0.33333333]]
        """
        return scipy.linalg.expm(self.qmatrix * time)

    # def _repr_html_(self):
    #     """Return a html representation of the Markov model.
    #     TODO: return multiple tables?
    #     """

    def __repr__(self):
        """Return a str representation of the Markov model."""
        return f"MarkovModel(nstates={self.nstates}, model={self.mtype.name})"
        # Debug repr expansion omitted for readability.


@dataclass
class DiscreteMarkovSimulator:
    """Simulate a discrete trait on a tree given a Q-matrix.

    This is intended primarily for internal use by toytree.pcm,
    with the user-facing functions available from factory functions
    like :meth:`simulate_discrete_trait`. This takes as input a
    ToyTree and MarkModel instances
    """

    tree: ToyTree
    """: ToyTree with edge lengths in units of ..."""
    model: MarkovModel
    """: MarkovModel object with parameterized Q matrix."""
    seed: int | np.random.Generator | None = None
    """: ..."""
    rng: np.random.Generator = field(init=False)
    """: ..."""

    def __post_init__(self):
        self.rng = (
            self.seed
            if isinstance(self.seed, np.random.Generator)
            else np.random.default_rng(self.seed)
        )

    def _edge_sim(self, state: int, time: float) -> int:
        """Return the state at end of this time given starting state."""
        prob = scipy.linalg.expm(self.model.qmatrix * time)
        return self.rng.multinomial(1, prob[state]).argmax()

    def _traversal_sim(self) -> np.ndarray:
        """Traverse tree from root to tips simulating trait."""
        arr = np.zeros(self.tree.nnodes, dtype=np.int64)

        # MarkovModel resolves a missing root prior to the stationary
        # distribution during construction.
        arr[-1] = self.rng.multinomial(1, self.model.root_prior).argmax()

        # traverse down tree simulating traits
        for node in self.tree[::-1][1:]:
            parent_state = arr[node.up._idx]
            state = self._edge_sim(parent_state, node._dist)
            arr[node._idx] = state
        return arr

    def run(self) -> np.ndarray:
        """Return one simulated realization indexed by node idx."""
        return self._traversal_sim()


def _coerce_trait_name(name: str) -> str:
    """Return a validated trait name."""
    name = str(name)
    if not name.strip():
        raise ToytreeError("name must be a non-empty string.")
    return name


def _default_state_names(nstates: int) -> list[str]:
    """Return default state labels for a discrete simulation."""
    if nstates <= len(string.ascii_uppercase):
        return list(string.ascii_uppercase[:nstates])
    return [str(i) for i in range(nstates)]


def _coerce_state_names(
    state_names: Sequence[Any] | None,
    nstates: int,
) -> list[Any]:
    """Return validated state labels for a discrete simulation."""
    if state_names is None:
        return _default_state_names(nstates)
    labels = list(state_names)
    if len(labels) != nstates:
        raise ToytreeError("state_names length must match nstates.")
    return labels


####################################################################
# API Exposed functions
####################################################################
def get_markov_model(
    nstates: int,
    model: str = "ER",
    rate_scalar: float = 1.0,
    relative_rates: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
    seed: int | np.random.Generator | None = None,
) -> MarkovModel:
    """Return a parameterized MarkovModel instance.

    The MarkovModel class is used to get an instantaneous transition
    rate matrix (Q) for calculating the probabilities of transitions
    between discrete character states in a Markov model. This
    is used primarily for didactic purposes, and is also used
    internally in functions such as :meth:`~toytree.pcm.simulate_discrete_trait`.

    It checks that the user input for rates and root_prior
    is valid given the model type and number of states, and can
    return random valid paramterizations for each model type.

    Parameters
    ----------
    nstates: int
        The number of modeled states, ordered internally as state indices
        ``0`` to ``nstates - 1``.
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
    root_prior: Optional[numpy.ndarray]
        Root-state probabilities in state-index order. This does not alter Q
        or its derived stationary frequencies. If None, the unique stationary
        distribution of Q is used.
    seed: int | numpy.random.Generator | None
        Seed or random-number generator used for any sampled parameters.

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
        root_prior=root_prior,
        seed=seed,
    )
    return model


@add_subpackage_method(PhyloCompAPI)
def simulate_discrete_trait(
    tree: ToyTree,
    nstates: int,
    model: str = "ER",
    relative_rates: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
    rate_scalar: Optional[float] = 1.0,
    tips_only: bool = False,
    name: str = "X",
    state_names: Sequence[Any] | None = None,
    seed: int | np.random.Generator | None = None,
    inplace: bool = False,
) -> pd.Series:
    """Return trait values simulated under a discrete Markov model.

    The number of states and model type can be entered without any
    parameters to the Markov model (e.g., relative rates and/or a
    root prior) to generate a random set of parameters that
    are valid under the specified model. Or, if parameters are entered
    then they are checked for validity with the specified model type,
    and then used to parameterize the Markov model simulation.

    Parameters
    ----------
    tree: toytree.ToyTree
        The tree on which to simulate the trait, usually ultrametric.
    nstates: int
        The number of states to simulate. By default, states are labeled
        ``"A"``, ``"B"``, ``"C"``, ... for small state spaces and fall back
        to numeric strings for larger ``nstates``.
    model: str
        The Markov model name ("ER", "SYM", or "ARD"). This is used
        to either sample random valid parameters for a model of the
        specified type, or to check that user-entered value are valid.
    relative_rates: Optional[numpy.ndarray]
        The relative transition rates between states as an array
        of size (nstates x nstates). Values on the diagonal are
        ignored. Only relative differences matter. See rate_scalar.
    root_prior: Optional[numpy.ndarray]
        Root-state probabilities in state-index order. The supplied prior
        affects only root sampling, not Q or its stationary frequencies. If
        None, the root is sampled from Q's unique stationary distribution.
        A one-hot vector fixes the root to one state.
    rate_scalar: float
        A scalar by which the Q-matrix will be multipled to act
        as a unit scaler. Example, rate=1e-6 would mean that a 1
        in the relatives rates matrix represents 1 change per
        million edge length units on a tree. Default=1 (no scaling)
    tips_only: bool
        If True values are only returned for tip Nodes, else values are
        returned for all Nodes in the tree.
    name : str, default="X"
        Name for the returned Series and for inplace storage on the tree when
        ``inplace=True``.
    state_names: Sequence[Any] | None
        Labels to substitute for simulated integer state indices in the
        entered order. If None, defaults are uppercase single-letter labels
        for ``nstates <= 26`` and numeric strings otherwise.
    seed : int | numpy.random.Generator | None
        Seed or random-number generator.
    inplace: bool
        If True, simulated trait data are also written to the input tree as
        node features. The simulated Series is still returned.

    Returns
    -------
    pandas.Series
        Simulated trait values indexed by node idx, or by tip idx rows only if
        ``tips_only=True``.

    Raises
    ------
    ToytreeError
        If ``name`` is blank or if ``state_names`` does not match ``nstates``.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(10)
    >>> x = toytree.pcm.simulate_discrete_trait(tree, 3, "ER")
    >>> x.name
    'X'
    >>> y = toytree.pcm.simulate_discrete_trait(
    ...     tree=tree,
    ...     nstates=3,
    ...     model="SYM",
    ...     name="ecotype",
    ...     state_names=["A", "B", "C"],
    ...     tips_only=True,
    ... )
    """
    name = _coerce_trait_name(name)
    labels = _coerce_state_names(state_names, nstates)
    model = MarkovModel(
        mtype=str(model).upper(),
        nstates=nstates,
        relative_rates=relative_rates,
        root_prior=root_prior,
        rate_scalar=rate_scalar,
        seed=seed,
    )
    simulator = DiscreteMarkovSimulator(
        tree=tree,
        model=model,
        seed=seed,
    )

    traits = pd.Series(
        simulator.run(), index=range(tree.nnodes), name=name, dtype=object
    )

    if tips_only:
        traits = traits.iloc[: tree.ntips].copy()

    # Convert integer state indices to user-facing categorical labels before
    # optionally storing the result on the tree.
    for idx, value in enumerate(labels):
        traits.replace(to_replace=idx, value=value, inplace=True)

    if inplace:
        tree.set_node_data(traits.name, traits, inplace=True, default=np.nan)
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
    data = simulate_discrete_trait(
        tree=tre,
        nstates=3,
        model="SYM",
        rate_scalar=1.0,
        root_prior=[0.1, 0.3, 0.6],
        tips_only=True,
        name="X",
        state_names=["A", "B", "C"],
    )
    print(data)

    model = get_markov_model(
        model="SYM",
        nstates=3,
        root_prior=[0.1, 0.2, 0.7],
        rate_scalar=0.1,
    )
    print(model)
    print(model.get_transition_probability_matrix(time=10))
