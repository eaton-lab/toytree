#!/usr/bin/env python

"""Simulate finite-state traits under continuous-time Markov chains.

The public API constructs direct-Q equal-rates (ER), symmetric-rates (SYM),
and all-rates-different (ARD) models and simulates states from the root toward
the tips. Root probabilities are kept separate from the transition-rate
parameterization.
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
from toytree.pcm.src.sim._utils import (
    RNGSeed,
    get_rng,
    make_node_series,
    validate_bool,
    validate_feature_name,
    validate_nonnegative_float,
    validate_positive_int,
    validate_state_labels,
    validate_tree_for_simulation,
)
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
    return prior / prior.sum()


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
    seed: RNGSeed = None
    """: Random-number source used if relative_rates is None."""

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
        self.rng = get_rng(self.seed)
        self.nstates = validate_positive_int(self.nstates, "nstates")
        if self.nstates < 2:
            raise ToytreeError("nstates must be at least 2.")
        if not isinstance(self.mtype, ModelType):
            try:
                self.mtype = ModelType(str(self.mtype).upper())
            except ValueError as exc:
                raise ToytreeError("model must be one of: 'ER', 'SYM', 'ARD'.") from exc
        self.rate_scalar = validate_nonnegative_float(self.rate_scalar, "rate_scalar")
        self._check_rates()
        self._set_transition_matrix()
        self.state_frequencies = get_stationary_frequencies(self.qmatrix)
        entered_prior = _coerce_root_prior(self.root_prior, self.nstates)
        if entered_prior is None:
            if self.state_frequencies is None:
                if self.mtype in (ModelType.ER, ModelType.SYM):
                    # Uniform frequencies are stationary under every symmetric
                    # Q, including reducible boundary cases where the
                    # stationary distribution is not unique.
                    entered_prior = np.full(self.nstates, 1.0 / self.nstates)
                else:
                    raise ToytreeError(
                        "root_prior is required when Q has no unique stationary "
                        "distribution"
                    )
            else:
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
            try:
                rates = np.asarray(rates, dtype=float)
            except (TypeError, ValueError) as exc:
                raise ToytreeError(
                    "relative_rates must contain numeric values."
                ) from exc
            if self.mtype == ModelType.ER and rates.size == 1:
                rates = np.full(
                    (self.nstates, self.nstates), float(rates.reshape(-1)[0])
                )
            if rates.shape != (self.nstates, self.nstates):
                raise ToytreeError(
                    f"given nstates={self.nstates}, relative_rates must have "
                    f"shape ({self.nstates}, {self.nstates})."
                )
            rates = rates.copy()
            np.fill_diagonal(rates, 0)
        rates = np.asarray(rates, dtype=float)
        offdiag = ~np.eye(self.nstates, dtype=bool)
        if np.any(~np.isfinite(rates[offdiag])) or np.any(rates[offdiag] < 0.0):
            raise ToytreeError(
                "relative_rates must contain finite non-negative off-diagonal values"
            )
        if self.mtype == ModelType.ER:
            values = rates[offdiag]
            if not np.allclose(values, values[0], rtol=1e-5, atol=1e-8):
                raise ToytreeError(
                    "all off-diagonal rates must be equal in an ER model; "
                    "use SYM or ARD for unequal rates."
                )
        elif self.mtype == ModelType.SYM and not np.allclose(
            rates, rates.T, rtol=1e-5, atol=1e-8
        ):
            raise ToytreeError(
                "relative_rates must be symmetric in a SYM model; use ARD "
                "for directional rates."
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
        time = validate_nonnegative_float(time, "time")
        if time == 0.0:
            return np.eye(self.nstates, dtype=float)
        probability = scipy.linalg.expm(self.qmatrix * time)
        # Remove only floating-point artifacts from the matrix exponential.
        probability[np.abs(probability) < 1e-15] = 0.0
        probability = np.clip(probability, 0.0, 1.0)
        probability /= probability.sum(axis=1, keepdims=True)
        return probability

    def __repr__(self):
        """Return a str representation of the Markov model."""
        return f"MarkovModel(nstates={self.nstates}, model={self.mtype.name})"


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
    seed: RNGSeed = None
    """: ..."""
    rng: np.random.Generator = field(init=False)
    """: ..."""

    def __post_init__(self):
        self.tree = validate_tree_for_simulation(self.tree)
        self.rng = get_rng(self.seed)

    def _edge_sim(self, state: int, time: float) -> int:
        """Return the state at end of this time given starting state."""
        prob = scipy.linalg.expm(self.model.qmatrix * time)
        return int(self.rng.choice(self.model.nstates, p=prob[state]))

    def _traversal_sim(self) -> np.ndarray:
        """Traverse tree from root to tips simulating trait."""
        arr = np.zeros(self.tree.nnodes, dtype=np.int64)

        # MarkovModel resolves a missing root prior to the stationary
        # distribution during construction.
        arr[-1] = self.rng.choice(self.model.nstates, p=self.model.root_prior)

        # traverse down tree simulating traits
        for node in self.tree[::-1][1:]:
            parent_state = arr[node.up._idx]
            state = self._edge_sim(parent_state, node._dist)
            arr[node._idx] = state
        return arr

    def run(self) -> np.ndarray:
        """Return one simulated realization indexed by node idx."""
        return self._traversal_sim()


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
    return validate_state_labels(state_names, nstates)


####################################################################
# API Exposed functions
####################################################################
def get_markov_model(
    nstates: int,
    model: str = "ER",
    rate_scalar: float = 1.0,
    relative_rates: float | np.ndarray | None = None,
    root_prior: Optional[np.ndarray] = None,
    seed: RNGSeed = None,
) -> MarkovModel:
    """Return a validated ER, SYM, or ARD continuous-time Markov model.

    Off-diagonal entries of the instantaneous rate matrix are defined as
    ``q_ij = rate_scalar * relative_rates[i, j]`` and diagonal entries are
    set to the negative row sums. The returned object can calculate
    ``P(t) = expm(Q*t)`` and is the model used by
    :meth:`~toytree.pcm.simulate_discrete_trait`.

    Parameters
    ----------
    nstates : int
        Number of modeled states. States are ordered internally as integer
        indices from ``0`` through ``nstates - 1`` and at least two states are
        required.
    model : {"ER", "SYM", "ARD"}, default="ER"
        Constraint on off-diagonal relative rates. ER requires one shared
        rate, SYM requires ``r_ij = r_ji``, and ARD permits every direction to
        differ. Names are case-insensitive.
    rate_scalar : float, default=1.0
        Finite nonnegative multiplier applied to every off-diagonal relative
        rate. Its units are transitions per tree branch-length unit. A value
        of zero produces a no-transition model.
    relative_rates : numpy.ndarray | None, default=None
        Numeric ``(nstates, nstates)`` matrix in state-index order. Diagonal
        values are ignored; off-diagonal values must be finite, nonnegative,
        and satisfy ``model``. A scalar or one-element array is also accepted
        for ER and expanded to every off-diagonal entry. If None, ER uses
        ones, whereas valid SYM and ARD rates are sampled from the supplied
        random-number stream.
    root_prior : numpy.ndarray | None, default=None
        Root-state probability vector in state-index order. It affects root
        sampling but does not alter Q. If None, use Q's unique stationary
        distribution. Reducible ER/SYM models use a canonical uniform prior;
        reducible ARD models require an explicit prior.
    seed : int | numpy.random.Generator | numpy.random.SeedSequence | None
        Random-number source used for any sampled parameters. A supplied
        Generator is consumed in place; integers and SeedSequences initialize
        a new Generator. The seed has no effect when no parameters are sampled.

    Returns
    -------
    MarkovModel
        Parameterized model. Important attributes include ``qmatrix``,
        ``relative_rates``, ``root_prior``, and ``state_frequencies``.

    Raises
    ------
    ToytreeError
        If a parameter is malformed, rates violate the requested model, a
        probability vector is invalid, or reducible ARD lacks a root prior.

    Examples
    --------
    >>> print(toytree.pcm.get_markov_model(nstates=3, model="ER"))
    >>> print(toytree.pcm.get_markov_model(nstates=3, model="SYM"))
    >>> print(toytree.pcm.get_markov_model(nstates=3, model="ARD", seed=123))
    """
    return MarkovModel(
        mtype=str(model).upper(),
        nstates=nstates,
        rate_scalar=rate_scalar,
        relative_rates=relative_rates,
        root_prior=root_prior,
        seed=seed,
    )


@add_subpackage_method(PhyloCompAPI)
def simulate_discrete_trait(
    tree: ToyTree,
    nstates: int,
    model: str = "ER",
    relative_rates: float | np.ndarray | None = None,
    root_prior: Optional[np.ndarray] = None,
    rate_scalar: float = 1.0,
    tips_only: bool = False,
    name: str = "X",
    state_names: Sequence[Any] | None = None,
    seed: RNGSeed = None,
    inplace: bool = False,
) -> pd.Series:
    """Return trait values simulated under a discrete Markov model.

    State histories are generated from the root toward the tips using
    ``P(t) = expm(Q*t)`` on each edge. Parameters may be supplied explicitly;
    otherwise ER uses unit relative rates and SYM/ARD sample valid relative
    rates from the same random stream used for state evolution.

    Parameters
    ----------
    tree : toytree.ToyTree
        Tree on which to simulate. It need not be ultrametric. Edge lengths
        must be finite and nonnegative and must use units reciprocal to the
        transition-rate units.
    nstates : int
        The number of states to simulate. By default, states are labeled
        ``"A"``, ``"B"``, ``"C"``, ... for small state spaces and fall back
        to numeric strings for larger ``nstates``.
    model : {"ER", "SYM", "ARD"}, default="ER"
        Constraint on the off-diagonal rates; names are case-insensitive.
        ER shares one rate, SYM shares a rate for each unordered state pair,
        and ARD permits every directional rate to differ.
    relative_rates : numpy.ndarray | None, default=None
        Finite nonnegative ``(nstates, nstates)`` matrix in ``state_names``
        order. Diagonal values are ignored. A scalar/one-element value is
        accepted for ER. If None, ER uses ones and SYM/ARD sample valid rates.
    root_prior : numpy.ndarray | None, default=None
        Root-state probabilities in ``state_names`` order. The supplied prior
        affects only root sampling, not Q or its stationary frequencies. If
        None, the root is sampled from Q's unique stationary distribution.
        Reducible ER/SYM models instead use a canonical uniform prior, whereas
        reducible ARD requires this argument. A one-hot vector fixes the root.
    rate_scalar : float, default=1.0
        Finite nonnegative multiplier in transitions per branch-length unit.
        For example, if tree edges are in years, ``1e-6`` means that a unit
        relative rate corresponds to one expected transition per million
        years. Zero produces no transitions.
    tips_only : bool, default=False
        If True values are only returned for tip Nodes, else values are
        returned for all Nodes in the tree.
    name : str, default="X"
        Name for the returned Series and for inplace storage on the tree when
        ``inplace=True``.
    state_names : Sequence[str] | Sequence[int] | None, default=None
        Labels to substitute for simulated integer state indices in the
        entered order. If None, defaults are uppercase single-letter labels
        for ``nstates <= 26`` and numeric strings otherwise.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place;
        sampled model parameters and trait evolution use one continuous random
        stream. Integer and SeedSequence inputs initialize a new Generator.
    inplace : bool, default=False
        If True, simulated trait data are also written to the input tree as
        node features. The simulated Series is still returned.

    Returns
    -------
    pandas.Series
        Simulated trait values indexed by numeric node idx, or tip idx only if
        ``tips_only=True``. Metadata on the Series records the state order, Q,
        and root prior so direct input to ``fit_discrete_ctmc`` preserves ARD
        directionality.

    Raises
    ------
    ToytreeError
        If the tree or any model/output/random-number parameter is invalid.

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
    tree = validate_tree_for_simulation(tree)
    nstates = validate_positive_int(nstates, "nstates")
    if nstates < 2:
        raise ToytreeError("nstates must be at least 2.")
    tips_only = validate_bool(tips_only, "tips_only")
    inplace = validate_bool(inplace, "inplace")
    name = validate_feature_name(name)
    labels = _coerce_state_names(state_names, nstates)
    rng = get_rng(seed)
    model = MarkovModel(
        mtype=str(model).upper(),
        nstates=nstates,
        relative_rates=relative_rates,
        root_prior=root_prior,
        rate_scalar=rate_scalar,
        seed=rng,
    )
    simulator = DiscreteMarkovSimulator(
        tree=tree,
        model=model,
        seed=rng,
    )
    indices = simulator.run()
    values = np.asarray(labels, dtype=object)[indices]
    traits = make_node_series(
        tree,
        values,
        name=name,
        tips_only=tips_only,
        inplace=inplace,
        dtype=object,
    )
    # Preserve the complete state-space order even when a realized sample does
    # not contain every state. ``fit_discrete_ctmc`` reads this metadata from a
    # directly supplied Series; ``state_names=`` remains available after data
    # have been copied through formats that do not retain pandas attrs.
    traits.attrs["state_names"] = tuple(labels)
    traits.attrs["model"] = model.mtype.value
    traits.attrs["qmatrix"] = tuple(tuple(row) for row in model.qmatrix)
    traits.attrs["root_prior"] = tuple(model.root_prior)
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
