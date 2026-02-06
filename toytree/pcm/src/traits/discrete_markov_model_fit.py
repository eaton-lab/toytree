#!/usr/bin/env python

"""Fit discrete Markov models to traits using maximum likelihood.

This module provides a compact, fully working implementation of
Felsenstein's pruning algorithm for discrete-state traits under
continuous-time Markov models. It aligns with the simulator's
parameterization where off-diagonal rates follow:

    q_ij = rate_scalar * r_ij * pi_j

with r_ij representing relative rates and pi_j the stationary
frequencies. Diagonal elements are set so each row sums to zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.optimize import minimize

from toytree.utils import ToytreeError
from toytree.pcm.src.traits.discrete_markov_model_sim import MarkovModel


@dataclass
class FitMarkovModelResult:
    """Container for fitted parameters and likelihood results."""

    nstates: int
    model: str
    relative_rates: np.ndarray
    state_frequencies: np.ndarray
    qmatrix: np.ndarray
    log_likelihood: float
    fixed_rates: Optional[np.ndarray] = None
    fixed_state_frequencies: Optional[np.ndarray] = None
    nparams: int = 0


class DiscreteMarkovModelFit:
    """Fit a discrete Markov model (ER, SYM, ARD) using ML.

    The model uses the same reversible parameterization as the simulator
    (see :class:`MarkovModel`) and computes likelihoods using
    Felsenstein's pruning algorithm on a fixed tree.

    Parameters
    ----------
    tree: ToyTree
        Tree with branch lengths in the same time units as rates.
    data: pandas.Series or pandas.DataFrame
        Tip data. Index must match tip labels. Each column is treated
        as a replicate. Values are categorical states or NaN for missing.
    nstates: int
        Number of discrete states (must be >= the number observed).
    model: str
        One of "ER", "SYM", "ARD".
    fixed_rates: Optional[np.ndarray]
        Optional (nstates x nstates) matrix of fixed off-diagonal rates.
        Use np.nan for entries to estimate. Diagonal is ignored.
    fixed_state_frequencies: Optional[np.ndarray]
        Optional fixed stationary frequencies (length nstates).
    root_prior: Optional[np.ndarray]
        Optional prior for the root state. If None, uses stationary
        frequencies for the model.
    rate_scalar: float
        Scalar applied to the relative rates during Q construction.
    """

    def __init__(
        self,
        tree,
        data: Union[pd.Series, pd.DataFrame],
        nstates: int,
        model: str,
        fixed_rates: Optional[np.ndarray] = None,
        fixed_state_frequencies: Optional[np.ndarray] = None,
        root_prior: Optional[np.ndarray] = None,
        rate_scalar: float = 1.0,
    ) -> None:
        self.tree = tree
        self.data = self._coerce_data(data)
        self.model = model.upper()
        self.nstates = nstates
        self.rate_scalar = rate_scalar

        if self.model not in {"ER", "SYM", "ARD"}:
            raise ToytreeError("model must be one of 'ER', 'SYM', 'ARD'")

        self.tip_labels = self.tree.get_tip_labels()
        self._validate_data_index()
        self.state_labels, self.state_map = self._build_state_map()
        self._validate_nstates()

        self.fixed_rates = self._coerce_fixed_rates(fixed_rates)
        self.fixed_state_frequencies = self._coerce_fixed_frequencies(
            fixed_state_frequencies
        )
        self.root_prior = self._coerce_root_prior(root_prior)

        self.tip_states = self._encode_tip_states()
        self.nreplicates = self.tip_states.shape[1]

        self.state_names = self._build_state_names()
        self._rate_param_info = self._build_rate_parameterization()
        self._freq_param_info = self._build_frequency_parameterization()

    def _coerce_data(self, data: Union[pd.Series, pd.DataFrame]) -> pd.DataFrame:
        """Ensure data are in a DataFrame with replicate columns."""
        if isinstance(data, pd.Series):
            data = data.to_frame()
        if not isinstance(data, pd.DataFrame):
            raise ToytreeError("data must be a pandas Series or DataFrame")
        return data.copy()

    def _validate_data_index(self) -> None:
        """Ensure data index matches tree tip labels."""
        if set(self.data.index) != set(self.tip_labels):
            raise ToytreeError(
                "data index must contain the same tip labels as the tree"
            )
        self.data = self.data.loc[self.tip_labels]

    def _build_state_map(self) -> Tuple[List[object], Dict[object, int]]:
        """Build a map from observed categorical states to integer indices."""
        observed = pd.unique(self.data.values.ravel())
        observed = [val for val in observed if pd.notna(val)]
        state_labels = sorted(observed)
        state_map = {state: idx for idx, state in enumerate(state_labels)}
        return state_labels, state_map

    def _build_state_names(self) -> List[object]:
        """Return state labels for all nstates (including unobserved)."""
        names = list(self.state_labels)
        if len(names) < self.nstates:
            names.extend(range(len(names), self.nstates))
        return names

    def _validate_nstates(self) -> None:
        """Ensure nstates is consistent with observed states."""
        if self.nstates < len(self.state_map):
            raise ToytreeError(
                f"nstates={self.nstates} is less than observed states"
            )

    def _coerce_fixed_rates(self, fixed_rates: Optional[np.ndarray]) -> np.ndarray:
        """Normalize fixed rate matrix and validate shape."""
        if fixed_rates is None:
            fixed_rates = np.full((self.nstates, self.nstates), np.nan)
        fixed_rates = np.array(fixed_rates, dtype=float)
        if fixed_rates.shape != (self.nstates, self.nstates):
            raise ToytreeError(
                "fixed_rates must be shape (nstates, nstates)"
            )
        np.fill_diagonal(fixed_rates, 0.0)
        if self.model in {"ER", "SYM"}:
            mask = ~np.isnan(fixed_rates) & ~np.isnan(fixed_rates.T)
            if mask.any() and not np.allclose(
                fixed_rates[mask], fixed_rates.T[mask], rtol=1e-5, atol=1e-8
            ):
                raise ToytreeError(
                    "fixed_rates must be symmetric for ER and SYM models"
                )
        return fixed_rates

    def _coerce_fixed_frequencies(
        self, fixed_state_frequencies: Optional[np.ndarray]
    ) -> Optional[np.ndarray]:
        """Validate optional fixed stationary frequencies."""
        if fixed_state_frequencies is None:
            return None
        fixed_state_frequencies = np.array(fixed_state_frequencies, dtype=float)
        if fixed_state_frequencies.shape != (self.nstates,):
            raise ToytreeError("fixed_state_frequencies must have length nstates")
        if not np.isclose(fixed_state_frequencies.sum(), 1.0):
            raise ToytreeError("fixed_state_frequencies must sum to 1")
        return fixed_state_frequencies

    def _coerce_root_prior(
        self, root_prior: Optional[np.ndarray]
    ) -> Optional[np.ndarray]:
        """Validate optional root prior vector."""
        if root_prior is None:
            return None
        root_prior = np.array(root_prior, dtype=float)
        if root_prior.shape != (self.nstates,):
            raise ToytreeError("root_prior must have length nstates")
        if not np.isclose(root_prior.sum(), 1.0):
            raise ToytreeError("root_prior must sum to 1")
        return root_prior

    def _encode_tip_states(self) -> np.ndarray:
        """Convert tip data to integer state codes with NaN for missing."""
        tip_states = self.data.copy()
        for state, idx in self.state_map.items():
            tip_states[tip_states == state] = idx
        tip_states = tip_states.astype(float).to_numpy()
        return tip_states

    def _build_rate_parameterization(self) -> Dict[str, object]:
        """Determine which rate parameters are fixed or free."""
        k = self.nstates
        free_positions: List[Tuple[int, int]] = []
        fixed_values: Dict[Tuple[int, int], float] = {}

        if self.model == "ER":
            fixed_vals = self.fixed_rates[~np.eye(k, dtype=bool)]
            fixed_vals = fixed_vals[~np.isnan(fixed_vals)]
            if fixed_vals.size > 0:
                if not np.allclose(fixed_vals, fixed_vals[0]):
                    raise ToytreeError("ER model requires a single shared rate")
                return {"mode": "er-fixed", "value": float(fixed_vals[0])}
            return {"mode": "er-free"}

        if self.model == "SYM":
            for i in range(k):
                for j in range(i + 1, k):
                    if np.isnan(self.fixed_rates[i, j]):
                        free_positions.append((i, j))
                    else:
                        fixed_values[(i, j)] = self.fixed_rates[i, j]
            return {"mode": "sym", "free": free_positions, "fixed": fixed_values}

        for i in range(k):
            for j in range(k):
                if i == j:
                    continue
                if np.isnan(self.fixed_rates[i, j]):
                    free_positions.append((i, j))
                else:
                    fixed_values[(i, j)] = self.fixed_rates[i, j]
        return {"mode": "ard", "free": free_positions, "fixed": fixed_values}

    def _build_frequency_parameterization(self) -> Dict[str, object]:
        """Determine how stationary frequencies are handled."""
        if self.model == "ER":
            return {"mode": "fixed", "values": np.repeat(1.0 / self.nstates, self.nstates)}
        if self.fixed_state_frequencies is not None:
            return {"mode": "fixed", "values": self.fixed_state_frequencies}
        return {"mode": "free"}

    def _params_to_rates(self, params: np.ndarray) -> np.ndarray:
        """Construct relative rates from the parameter vector."""
        k = self.nstates
        rates = np.zeros((k, k))
        info = self._rate_param_info

        if info["mode"] == "er-fixed":
            rates[:] = info["value"]
            np.fill_diagonal(rates, 0.0)
            return rates

        if info["mode"] == "er-free":
            rate = float(np.exp(params[0]))
            rates[:] = rate
            np.fill_diagonal(rates, 0.0)
            return rates

        offset = 0
        if info["mode"] == "sym":
            for idx, (i, j) in enumerate(info["free"]):
                rates[i, j] = np.exp(params[idx])
                rates[j, i] = rates[i, j]
            for (i, j), value in info["fixed"].items():
                rates[i, j] = value
                rates[j, i] = value
            np.fill_diagonal(rates, 0.0)
            return rates

        # ARD
        for idx, (i, j) in enumerate(info["free"]):
            rates[i, j] = np.exp(params[idx])
        for (i, j), value in info["fixed"].items():
            rates[i, j] = value
        np.fill_diagonal(rates, 0.0)
        return rates

    def _params_to_frequencies(self, params: np.ndarray, offset: int) -> np.ndarray:
        """Construct stationary frequencies from the parameter vector."""
        info = self._freq_param_info
        if info["mode"] == "fixed":
            return info["values"]
        raw = np.zeros(self.nstates)
        raw[: self.nstates - 1] = params[offset : offset + self.nstates - 1]
        raw[self.nstates - 1] = 0.0
        weights = np.exp(raw)
        return weights / weights.sum()

    def _parameter_count(self) -> int:
        """Return number of free parameters in the model."""
        rate_info = self._rate_param_info
        freq_info = self._freq_param_info

        if rate_info["mode"] == "er-fixed":
            rate_params = 0
        elif rate_info["mode"] == "er-free":
            rate_params = 1
        else:
            rate_params = len(rate_info["free"])

        freq_params = 0
        if freq_info["mode"] == "free":
            freq_params = self.nstates - 1
        return rate_params + freq_params

    def _split_params(self, params: np.ndarray) -> Tuple[np.ndarray, int]:
        """Return parameters for rates and the offset for frequencies."""
        rate_info = self._rate_param_info
        if rate_info["mode"] == "er-free":
            return params[:1], 1
        if rate_info["mode"] == "er-fixed":
            return np.empty(0), 0
        return params[: len(rate_info["free"])], len(rate_info["free"])

    def _build_qmatrix(self, params: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Construct Q matrix plus relative rates and frequencies."""
        rate_params, offset = self._split_params(params)
        rates = self._params_to_rates(rate_params)
        freqs = self._params_to_frequencies(params, offset)
        model = MarkovModel(
            nstates=self.nstates,
            mtype=self.model,
            relative_rates=rates,
            state_frequencies=freqs,
            rate_scalar=self.rate_scalar,
        )
        return model.qmatrix, rates, freqs

    def _compute_conditional_likelihoods(
        self, qmatrix: np.ndarray
    ) -> Dict[object, np.ndarray]:
        """Compute conditional likelihoods at every node."""
        likelihoods: Dict[object, np.ndarray] = {}
        nstates = self.nstates

        for node in self.tree.treenode.traverse("postorder"):
            if node.is_leaf():
                tip_index = self.tip_labels.index(node.name)
                tip_obs = self.tip_states[tip_index]
                arr = np.ones((self.nreplicates, nstates))
                for rep_idx, obs in enumerate(tip_obs):
                    if np.isnan(obs):
                        continue
                    arr[rep_idx, :] = 0.0
                    arr[rep_idx, int(obs)] = 1.0
                likelihoods[node] = arr
                continue

            # start with ones and multiply in each child's conditional likelihood
            node_lik = np.ones((self.nreplicates, nstates))
            for child in node.children:
                prob = expm(qmatrix * child.dist)
                child_lik = likelihoods[child] @ prob.T
                node_lik *= child_lik
            likelihoods[node] = node_lik
        return likelihoods

    def _pruning_likelihood(self, qmatrix: np.ndarray, freqs: np.ndarray) -> np.ndarray:
        """Compute per-replicate likelihoods with pruning algorithm."""
        likelihoods = self._compute_conditional_likelihoods(qmatrix)

        root = self.tree.treenode
        prior = self.root_prior if self.root_prior is not None else freqs
        root_lik = likelihoods[root]
        return (root_lik * prior).sum(axis=1)

    def _compute_node_posteriors(
        self, qmatrix: np.ndarray, freqs: np.ndarray
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Return posterior state probabilities and inferred states per node."""
        likelihoods = self._compute_conditional_likelihoods(qmatrix)
        nstates = self.nstates
        nrep = self.nreplicates

        prior = self.root_prior if self.root_prior is not None else freqs
        up: Dict[object, np.ndarray] = {}
        up[self.tree.treenode] = np.tile(prior, (nrep, 1))

        for node in self.tree.treenode.traverse("preorder"):
            if node.is_leaf():
                continue
            for child in node.children:
                sibling_product = np.ones((nrep, nstates))
                for sibling in node.children:
                    if sibling is child:
                        continue
                    prob_sib = expm(qmatrix * sibling.dist)
                    sib_lik = likelihoods[sibling] @ prob_sib.T
                    sibling_product *= sib_lik
                prob_child = expm(qmatrix * child.dist)
                parent_weight = up[node] * sibling_product
                up[child] = parent_weight @ prob_child

        nnodes = self.tree.nnodes
        posterior = np.zeros((nnodes, nrep, nstates))
        for node in self.tree.treenode.traverse("preorder"):
            node_idx = node._idx
            node_post = up[node] * likelihoods[node]
            node_post /= node_post.sum(axis=1, keepdims=True)
            posterior[node_idx] = node_post

        if nrep == 1:
            prob_df = pd.DataFrame(
                posterior[:, 0, :],
                index=range(nnodes),
                columns=self.state_names,
            )
            state_df = pd.DataFrame(
                np.array(self.state_names, dtype=object)[posterior[:, 0, :].argmax(axis=1)],
                index=range(nnodes),
                columns=["state"],
            )
            return prob_df, state_df

        columns = pd.MultiIndex.from_product(
            [range(nrep), self.state_names], names=["replicate", "state"]
        )
        prob_df = pd.DataFrame(
            posterior.reshape(nnodes, nrep * nstates),
            index=range(nnodes),
            columns=columns,
        )
        state_arr = np.array(self.state_names, dtype=object)[
            posterior.argmax(axis=2)
        ]
        state_df = pd.DataFrame(state_arr, index=range(nnodes), columns=range(nrep))
        return prob_df, state_df

    def _neg_log_likelihood(self, params: np.ndarray) -> float:
        """Negative log-likelihood for optimizer."""
        qmatrix, _, freqs = self._build_qmatrix(params)
        liks = self._pruning_likelihood(qmatrix, freqs)
        liks = np.clip(liks, 1e-300, None)
        return -np.log(liks).sum()

    def fit(self, compute_posteriors: bool = False) -> FitMarkovModelResult:
        """Fit the model parameters with ML and return a result object.

        Parameters
        ----------
        compute_posteriors: bool
            If True, compute node posterior probabilities and inferred
            states during fitting. This is not required for fitting the
            model parameters alone.
        """
        nparams = self._parameter_count()
        if nparams == 0:
            params = np.empty(0)
            qmatrix, rates, freqs = self._build_qmatrix(params)
            log_likelihood = -self._neg_log_likelihood(params)
            return FitMarkovModelResult(
                nstates=self.nstates,
                model=self.model,
                relative_rates=rates,
                state_frequencies=freqs,
                qmatrix=qmatrix,
                log_likelihood=log_likelihood,
                fixed_rates=self.fixed_rates,
                fixed_state_frequencies=self.fixed_state_frequencies,
                nparams=0,
            )

        start = np.zeros(nparams)
        result = minimize(self._neg_log_likelihood, start, method="L-BFGS-B")
        qmatrix, rates, freqs = self._build_qmatrix(result.x)
        return FitMarkovModelResult(
            nstates=self.nstates,
            model=self.model,
            relative_rates=rates,
            state_frequencies=freqs,
            qmatrix=qmatrix,
            log_likelihood=-result.fun,
            fixed_rates=self.fixed_rates,
            fixed_state_frequencies=self.fixed_state_frequencies,
            nparams=nparams,
        )


def fit_discrete_markov_model(
    tree,
    data: Union[pd.Series, pd.DataFrame],
    nstates: int,
    model: str,
    fixed_rates: Optional[np.ndarray] = None,
    fixed_state_frequencies: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
    rate_scalar: float = 1.0,
) -> FitMarkovModelResult:
    """Convenience wrapper to fit a discrete Markov model."""
    fitter = DiscreteMarkovModelFit(
        tree=tree,
        data=data,
        nstates=nstates,
        model=model,
        fixed_rates=fixed_rates,
        fixed_state_frequencies=fixed_state_frequencies,
        root_prior=root_prior,
        rate_scalar=rate_scalar,
    )
    return fitter.fit(compute_posteriors=False)


def infer_ancestral_states_discrete_mk(
    tree,
    data: Union[pd.Series, pd.DataFrame],
    nstates: int,
    model: str,
    fixed_rates: Optional[np.ndarray] = None,
    fixed_state_frequencies: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
    rate_scalar: float = 1.0,
    inplace: bool = False,
) -> Union[Tuple[FitMarkovModelResult, pd.DataFrame, pd.DataFrame], object]:
    """Infer ancestral states and return node-level posterior probabilities.

    Parameters
    ----------
    inplace: bool
        If True, store posterior probabilities on tree nodes and return the tree.
        Each node receives a tuple of length nstates with state probabilities.
        If False, return the fitted model result plus probability/state tables.
    """
    fitter = DiscreteMarkovModelFit(
        tree=tree,
        data=data,
        nstates=nstates,
        model=model,
        fixed_rates=fixed_rates,
        fixed_state_frequencies=fixed_state_frequencies,
        root_prior=root_prior,
        rate_scalar=rate_scalar,
    )
    result = fitter.fit(compute_posteriors=False)
    node_probs, node_states = fitter._compute_node_posteriors(
        result.qmatrix, result.state_frequencies
    )
    if inplace:
        tree = tree.copy()
        probs_by_node = node_probs.to_numpy()
        for node in tree.treenode.traverse("preorder"):
            node_probs_tuple = tuple(probs_by_node[node._idx])
            node.add_feature("discrete_state_probabilities", node_probs_tuple)
        return tree
    return result, node_probs, node_states


__all__ = [
    "FitMarkovModelResult",
    "DiscreteMarkovModelFit",
    "fit_discrete_markov_model",
    "infer_ancestral_states_discrete_mk",
]
