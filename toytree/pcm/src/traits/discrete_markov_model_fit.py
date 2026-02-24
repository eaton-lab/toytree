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
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.optimize import minimize

# from loguru import logger
from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.traits.aic_table import ModelResult
from toytree.pcm.src.traits.discrete_markov_model_sim import MarkovModel
from toytree.utils import ToytreeError

__all__ = [
    # "FitMarkovModelResult",
    # "DiscreteMarkovModelFit",
    "fit_discrete_markov_model",
    "infer_ancestral_states_discrete_ctmc",
]


@dataclass
class FitMarkovModelResult(ModelResult):
    """Container for fitted parameters and likelihood results."""

    nstates: int
    model: str
    relative_rates: np.ndarray
    state_frequencies: np.ndarray
    qmatrix: np.ndarray
    log_likelihood: float
    nparams: int
    fixed_rates: Optional[np.ndarray] = None
    fixed_state_frequencies: Optional[np.ndarray] = None

    def __repr__(self) -> str:
        def _fmt_arr(arr: Optional[np.ndarray]) -> str:
            if arr is None:
                return "None"
            arr = np.asarray(arr)
            if arr.ndim == 1:
                preview = ", ".join(f"{v:.4g}" for v in arr[:4])
                tail = "..." if arr.size > 4 else ""
                return f"[{preview}{tail}]"
            shape = "x".join(str(i) for i in arr.shape)
            return f"<array {shape}>"

        return (
            "FitMarkovModelResult(\n"
            f"  model={self.model}, nstates={self.nstates}, nparams={self.nparams}\n"
            f"  log_likelihood={self.log_likelihood:.6g}\n"
            f"  state_frequencies={_fmt_arr(self.state_frequencies)}\n"
            f"  relative_rates={_fmt_arr(self.relative_rates)}\n"
            f"  qmatrix={_fmt_arr(self.qmatrix)}\n"
            f"  fixed_rates={_fmt_arr(self.fixed_rates)}\n"
            f"  fixed_state_frequencies={_fmt_arr(self.fixed_state_frequencies)}\n"
            ")"
        )


class DiscreteMarkovModelFit:
    """Fit a discrete Markov model (ER, SYM, ARD) using ML.

    The model uses the same reversible parameterization as the simulator
    (see :class:`MarkovModel`) and computes likelihoods using
    Felsenstein's pruning algorithm on a fixed tree.

    Parameters
    ----------
    tree: ToyTree
        Tree with branch lengths in the same time units as rates.
    data: str or pandas.Series
        A single trait as a feature name on the tree, or a Series.
        Values are categorical states or NaN for missing.
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
        Scalar applied to Q construction only in fixed-rate workflows
        (i.e., when fixed_rates specifies at least one fixed
        off-diagonal entry). For free-rate fitting this must be 1.0.
    """

    def __init__(
        self,
        tree,
        data: Union[str, pd.Series],
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
        if self.data.shape[0] != self.tree.nnodes:
            raise ToytreeError("data must be tree.nnodes in size")
        self.state_labels, self.state_map = self._build_state_map()
        self._validate_nstates()

        self.fixed_rates = self._coerce_fixed_rates(fixed_rates)
        self._validate_rate_scalar_usage()
        self.fixed_state_frequencies = self._coerce_fixed_frequencies(
            fixed_state_frequencies
        )
        self.root_prior = self._coerce_root_prior(root_prior)
        self.tip_states = self._encode_tip_states()
        self.state_names = self._build_state_names()
        self._rate_param_info = self._build_rate_parameterization()
        self._freq_param_info = self._build_frequency_parameterization()

    def _coerce_data(self, data: Union[str, pd.Series]) -> pd.Series:
        """Ensure data are a single-trait Series in node index order."""
        if isinstance(data, str):
            series = self.tree.get_node_data(data, missing=float("nan"))
        elif isinstance(data, pd.Series):
            series = data.copy()
        else:
            raise ToytreeError("data must be a feature name (str) or pandas Series")

        # Accept all-node or tip-only series and expand to all nodes.
        mapping = dict(series.dropna())
        mapping = expand_node_mapping(self.tree, mapping)
        arr = np.full(self.tree.nnodes, np.nan, dtype=object)
        for node, value in mapping.items():
            arr[node._idx] = value
        name = series.name if series.name is not None else "trait"
        return pd.Series(arr, index=range(self.tree.nnodes), name=name)

    def _build_state_map(self) -> Tuple[List[object], Dict[object, int]]:
        """Build a map from observed categorical states to integer indices."""
        observed = pd.unique(self.data.values)
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
            raise ToytreeError(f"nstates={self.nstates} is less than observed states")

    def _coerce_fixed_rates(self, fixed_rates: Optional[np.ndarray]) -> np.ndarray:
        """Normalize fixed rate matrix and validate shape."""
        if fixed_rates is None:
            fixed_rates = np.full((self.nstates, self.nstates), np.nan)
        fixed_rates = np.array(fixed_rates, dtype=float)
        if fixed_rates.shape != (self.nstates, self.nstates):
            raise ToytreeError("fixed_rates must be shape (nstates, nstates)")
        np.fill_diagonal(fixed_rates, 0.0)
        if self.model in {"ER", "SYM"}:
            # Symmetric models require each mirrored pair to be specified
            # together (both fixed or both NaN), and fixed values must match.
            for i in range(self.nstates):
                for j in range(i + 1, self.nstates):
                    a = fixed_rates[i, j]
                    b = fixed_rates[j, i]
                    a_nan = np.isnan(a)
                    b_nan = np.isnan(b)
                    if a_nan != b_nan:
                        raise ToytreeError(
                            "fixed_rates must specify symmetric pairs for ER "
                            "and SYM models (both directions fixed or both NaN)"
                        )
                    if (not a_nan) and (not np.isclose(a, b, rtol=1e-5, atol=1e-8)):
                        raise ToytreeError(
                            "fixed_rates must be symmetric for ER and SYM models"
                        )
        return fixed_rates

    def _validate_rate_scalar_usage(self) -> None:
        """Allow non-default rate_scalar only when at least one rate is fixed."""
        if np.isclose(self.rate_scalar, 1.0):
            return
        offdiag = ~np.eye(self.nstates, dtype=bool)
        has_fixed_rate = np.any(~np.isnan(self.fixed_rates[offdiag]))
        if not has_fixed_rate:
            raise ToytreeError(
                "rate_scalar is only allowed in fixed-rate workflows. "
                "Set fixed_rates with at least one fixed off-diagonal entry, "
                "or use rate_scalar=1.0."
            )

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
        return tip_states.astype(float).to_numpy()

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
            return {
                "mode": "fixed",
                "values": np.repeat(1.0 / self.nstates, self.nstates),
            }
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

    def _build_qmatrix(
        self, params: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
        node_states = self.tip_states

        for node in self.tree.treenode.traverse("postorder"):
            node_lik = np.ones(nstates)
            if not node.is_leaf():
                for child in node.children:
                    prob = expm(qmatrix * child.dist)
                    child_lik = prob @ likelihoods[child]
                    node_lik *= child_lik

            state = node_states[node._idx]
            if not np.isnan(state):
                mask = np.zeros(nstates)
                mask[int(state)] = 1.0
                node_lik *= mask
            likelihoods[node] = node_lik
        return likelihoods

    def _pruning_likelihood(self, qmatrix: np.ndarray, freqs: np.ndarray) -> float:
        """Compute likelihood with pruning algorithm."""
        likelihoods = self._compute_conditional_likelihoods(qmatrix)

        root = self.tree.treenode
        prior = self.root_prior if self.root_prior is not None else freqs
        root_lik = likelihoods[root]
        return float((root_lik * prior).sum())

    def _compute_node_posteriors(
        self, qmatrix: np.ndarray, freqs: np.ndarray
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Return posterior state probabilities and inferred states per node."""
        likelihoods = self._compute_conditional_likelihoods(qmatrix)
        nstates = self.nstates

        prior = self.root_prior if self.root_prior is not None else freqs
        up: Dict[object, np.ndarray] = {}
        up[self.tree.treenode] = prior.copy()

        for node in self.tree.treenode.traverse("preorder"):
            if node.is_leaf():
                continue
            for child in node.children:
                sibling_product = np.ones(nstates)
                for sibling in node.children:
                    if sibling is child:
                        continue
                    prob_sib = expm(qmatrix * sibling.dist)
                    sib_lik = prob_sib @ likelihoods[sibling]
                    sibling_product *= sib_lik
                prob_child = expm(qmatrix * child.dist)
                parent_weight = up[node] * sibling_product
                up[child] = parent_weight @ prob_child

        nnodes = self.tree.nnodes
        posterior = np.zeros((nnodes, nstates))
        for node in self.tree.treenode.traverse("preorder"):
            node_idx = node._idx
            node_post = up[node] * likelihoods[node]
            node_post /= node_post.sum()
            posterior[node_idx] = node_post

        prob_df = pd.DataFrame(
            posterior,
            index=range(nnodes),
            columns=self.state_names,
        )
        state_df = pd.DataFrame(
            np.array(self.state_names, dtype=object)[posterior.argmax(axis=1)],
            index=range(nnodes),
            columns=["state"],
        )
        return prob_df, state_df

    def _neg_log_likelihood(self, params: np.ndarray) -> float:
        """Negative log-likelihood for optimizer."""
        qmatrix, _, freqs = self._build_qmatrix(params)
        lik = np.clip(self._pruning_likelihood(qmatrix, freqs), 1e-300, None)
        return -float(np.log(lik))

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


@add_subpackage_method(PhyloCompAPI)
def fit_discrete_markov_model(
    tree,
    data: Union[str, pd.Series],
    nstates: int,
    model: str,
    fixed_rates: Optional[np.ndarray] = None,
    fixed_state_frequencies: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
) -> FitMarkovModelResult:
    """Fit a discrete Markov model for one trait.

    Notes
    -----
    The internal model scale parameter is intentionally not exposed in this
    user-facing wrapper. For advanced fixed-rate workflows that require direct
    control over the CTMC scale, instantiate `DiscreteMarkovModelFit` directly.
    """
    fitter = DiscreteMarkovModelFit(
        tree=tree,
        data=data,
        nstates=nstates,
        model=model,
        fixed_rates=fixed_rates,
        fixed_state_frequencies=fixed_state_frequencies,
        root_prior=root_prior,
    )
    return fitter.fit(compute_posteriors=False)


@add_subpackage_method(PhyloCompAPI)
def infer_ancestral_states_discrete_ctmc(
    tree,
    data: Union[str, pd.Series],
    nstates: int,
    model: str,
    fixed_rates: Optional[np.ndarray] = None,
    fixed_state_frequencies: Optional[np.ndarray] = None,
    root_prior: Optional[np.ndarray] = None,
    inplace: bool = False,
) -> Dict[str, object]:
    """Infer ancestral discrete trait states under a CTMC model.

    This function fits a discrete-state CTMC model and computes posterior
    state probabilities for all nodes on a tree. Observations can be provided
    for tip nodes only (typical empirical data) or for a mixture of tips and
    internal nodes. Any non-missing internal-node observations are treated as
    hard constraints during pruning (e.g., fossil assignments), which can
    affect both fitted parameters and ancestral reconstructions.

    Parameters
    ----------
    tree : ToyTree
        Tree on which to fit the model and infer ancestral states.
    data : str | pd.Series
        Trait observations as either a node feature name on ``tree`` or a
        pandas Series. The Series may contain values for all nodes or tips
        only. If only tips are provided, internal nodes are filled with NaN.
        Observed states must be all ``int`` or all ``str`` (booleans are not
        allowed and mixed types are rejected).
    nstates : int
        Total number of states in the CTMC model (including potentially
        unobserved states).
    model : str
        Rate model parameterization. Supported values are ``"ER"``, ``"SYM"``,
        and ``"ARD"``.
    fixed_rates : np.ndarray | None
        Optional ``(nstates, nstates)`` relative-rate matrix with numeric
        values for fixed entries and ``np.nan`` for free entries. Diagonal
        entries are ignored and set to zero. For ``ER`` and ``SYM`` models,
        mirrored off-diagonal entries must be specified symmetrically.
    fixed_state_frequencies : np.ndarray | None
        Optional stationary state frequencies vector of length ``nstates``.
    root_prior : np.ndarray | None
        Optional root-state prior probability vector of length ``nstates``.
        If None, stationary frequencies are used.
    inplace : bool
        If True, write inferred states and posterior tuples to the input tree
        as node features. If False, the input tree is not modified.

    Returns
    -------
    dict[str, object]
        Dictionary with keys:

        - ``"model_fit"``: fitted ``FitMarkovModelResult``.
        - ``"data"``: ``pd.DataFrame`` indexed by numeric node idx labels.

        The dataframe contains:

        - ``"{trait}_anc"``: maximum-posterior inferred state label per node.
        - ``"{trait}_anc_posterior"``: posterior probabilities per node as a
          tuple ordered by the fitted model state labels.

    Raises
    ------
    ToytreeError
        If ``data`` is not a feature name or pandas Series, if trait states are
        not all discrete ``int`` or ``str`` values, if state types are mixed,
        or if model-fitting inputs are invalid.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(8, seed=123)
    >>> data = toytree.pcm.simulate_discrete_data(
    ...     tree=tree, nstates=3, model="ER", tips_only=True, seed=123
    ... )
    >>> tree = tree.set_node_data("X", dict(data), default=np.nan, inplace=False)
    >>> out = tree.pcm.infer_ancestral_states_discrete_ctmc(
    ...     "X", nstates=3, model="ARD"
    ... )
    >>> out["data"].head()
    """

    def _coerce_series_to_all_nodes(series: pd.Series) -> pd.Series:
        mapping = dict(series)
        mapping = expand_node_mapping(tree, mapping)
        arr = np.full(tree.nnodes, np.nan, dtype=object)
        for node, value in mapping.items():
            arr[node._idx] = value
        name = series.name if series.name is not None else "trait"
        return pd.Series(arr, index=range(tree.nnodes), name=name)

    trait_name = None
    if isinstance(data, str):
        trait_name = data
        series = tree.get_node_data(data, missing=float("nan"))
        data = _coerce_series_to_all_nodes(series)
    elif isinstance(data, pd.Series):
        trait_name = data.name
        data = _coerce_series_to_all_nodes(data)
    else:
        raise ToytreeError("data must be a feature name (str) or pandas Series")
    if not trait_name:
        trait_name = "trait"

    observed = pd.Series(data).dropna().unique().tolist()
    if observed:
        valid_types = (int, np.integer, str)
        if not all(
            isinstance(v, valid_types) and not isinstance(v, bool) for v in observed
        ):
            raise ToytreeError("trait states must be int or str")
        types = {type(v) for v in observed}
        if len(types) > 1:
            raise ToytreeError("trait states must be all int or all str (no mixing)")

    fitter = DiscreteMarkovModelFit(
        tree=tree,
        data=data,
        nstates=nstates,
        model=model,
        fixed_rates=fixed_rates,
        fixed_state_frequencies=fixed_state_frequencies,
        root_prior=root_prior,
    )
    result = fitter.fit(compute_posteriors=False)
    node_probs, node_states = fitter._compute_node_posteriors(
        result.qmatrix, result.state_frequencies
    )
    probs_by_node = node_probs.to_numpy()
    if inplace:
        prob_mapping = {i: tuple(probs_by_node[i]) for i in range(tree.nnodes)}
        state_mapping = node_states["state"].to_dict()
        tree.set_node_data(
            feature=f"{trait_name}_anc_posterior",
            data=prob_mapping,
            inplace=True,
        )
        tree.set_node_data(
            feature=f"{trait_name}_anc",
            data=state_mapping,
            inplace=True,
        )

    df = pd.DataFrame(index=range(tree.nnodes))
    df[f"{trait_name}_anc"] = node_states["state"]
    df[f"{trait_name}_anc_posterior"] = [tuple(row) for row in node_probs.to_numpy()]
    return {
        "model_fit": result,
        "data": df,
    }
