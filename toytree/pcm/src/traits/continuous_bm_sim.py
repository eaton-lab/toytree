#!/usr/bin/env python

"""Simulate continuous traits on trees under BM, OU, or EB models.

This module provides simulation utilities for continuous trait evolution
on phylogenies. The primary API is `simulate_continuous_bm`, which
supports univariate Brownian motion (BM), Ornstein-Uhlenbeck (OU), and
early-burst (EB) models with optional replicate simulation and in-place
storage on `ToyTree` nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Mapping, Sequence

import numpy as np
import pandas as pd

from toytree import ToyTree
from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.utils import ToytreeError

__all__ = [
    "simulate_continuous_bm",
    "simulate_continuous_multivariate_bm",
]


class ContinuousModelType(Enum):
    """Supported univariate continuous-trait simulation models."""

    BM = "BM"
    OU = "OU"
    EB = "EB"


@dataclass
class ContinuousModel:
    """Container for one-trait continuous model parameters."""

    mtype: ContinuousModelType
    sigma2: float
    alpha: float = 0.0
    r: float = 0.0
    optimum: float = 0.0

    def __post_init__(self):
        if isinstance(self.mtype, ContinuousModelType):
            pass
        else:
            self.mtype = ContinuousModelType(str(self.mtype).upper())
        self.sigma2 = float(self.sigma2)
        self.alpha = float(self.alpha)
        self.r = float(self.r)
        self.optimum = float(self.optimum)
        if self.sigma2 <= 0:
            raise ToytreeError("sigma2 must be > 0.")
        if self.alpha < 0:
            raise ToytreeError("alpha must be >= 0.")


def _coerce_model_vector(
    x,
    ntraits: int,
    names: list[str],
    default: float | None = None,
    param_name: str = "parameter",
) -> np.ndarray:
    """Coerce scalar/sequence/mapping parameter to float vector."""
    if x is None:
        if default is None:
            raise ToytreeError(f"{param_name} is required for this model.")
        return np.repeat(float(default), ntraits).astype(float)
    if np.isscalar(x):
        return np.repeat(float(x), ntraits).astype(float)
    if isinstance(x, Mapping):
        vals = []
        for name in names:
            if name not in x:
                if default is None:
                    raise ToytreeError(
                        f"{param_name} mapping is missing trait name '{name}'."
                    )
                vals.append(float(default))
            else:
                vals.append(float(x[name]))
        return np.asarray(vals, dtype=float)
    arr = np.asarray(list(x), dtype=float)
    if arr.size != ntraits:
        raise ToytreeError(
            f"{param_name} length must match number of traits ({ntraits})."
        )
    return arr


def _coerce_sigma2_and_names(
    sigma2: float | Sequence[float] | Mapping[str, float],
) -> tuple[np.ndarray, list[str]]:
    """Coerce sigma2 input and derive trait names."""
    if isinstance(sigma2, Mapping):
        names = [str(i) for i in sigma2.keys()]
        vals = np.asarray(list(sigma2.values()), dtype=float)
    elif np.isscalar(sigma2):
        names = ["t0"]
        vals = np.asarray([sigma2], dtype=float)
    else:
        vals = np.asarray(list(sigma2), dtype=float)
        names = [f"t{i}" for i in range(vals.size)]
    if vals.size == 0:
        raise ToytreeError("sigma2 must define at least one trait.")
    if np.any(vals <= 0):
        raise ToytreeError("sigma2 values must all be > 0.")
    return vals, names


def _coerce_root_state(
    root_state,
    ntraits: int,
    names: list[str],
) -> np.ndarray:
    """Coerce root state to float vector of ntraits."""
    if root_state is None:
        return np.zeros(ntraits, dtype=float)
    if np.isscalar(root_state):
        return np.repeat(float(root_state), ntraits).astype(float)
    if isinstance(root_state, Mapping):
        vals = []
        for name in names:
            if name not in root_state:
                raise ToytreeError(
                    f"root_state mapping is missing trait name '{name}'."
                )
            vals.append(float(root_state[name]))
        return np.asarray(vals, dtype=float)
    arr = np.asarray(list(root_state), dtype=float)
    if arr.size != ntraits:
        raise ToytreeError("root_state length must match number of traits.")
    return arr


def _get_time_from_root(tree: ToyTree) -> np.ndarray:
    """Return absolute time from root to each node."""
    times = np.zeros(tree.nnodes, dtype=float)
    root = tree.treenode
    times[root.idx] = 0.0
    for node in tree[::-1][1:]:
        pidx = node.up.idx
        times[node.idx] = times[pidx] + float(node.dist)
    return times


def _simulate_increment_univariate(
    model: ContinuousModel,
    parent_value: float,
    branch_length: float,
    parent_time: float,
    child_time: float,
    rng: np.random.Generator,
) -> float:
    """Sample child value on a branch for one trait."""
    t = float(branch_length)
    if t <= 0:
        return float(parent_value)
    if model.mtype == ContinuousModelType.BM:
        mean = float(parent_value)
        var = model.sigma2 * t
    elif model.mtype == ContinuousModelType.OU:
        e = np.exp(-model.alpha * t)
        mean = model.optimum + (float(parent_value) - model.optimum) * e
        if model.alpha == 0.0:
            var = model.sigma2 * t
        else:
            var = model.sigma2 * (1.0 - np.exp(-2.0 * model.alpha * t)) / (2.0 * model.alpha)
    else:
        mean = float(parent_value)
        if model.r == 0.0:
            var = model.sigma2 * t
        else:
            var = model.sigma2 * (np.exp(model.r * child_time) - np.exp(model.r * parent_time)) / model.r
    var = max(float(var), 0.0)
    std = float(np.sqrt(var))
    return float(rng.normal(loc=mean, scale=std))


@dataclass
class ContinuousTraitSimulator:
    """Simulator for one or more independent continuous traits."""

    tree: ToyTree
    models: list[ContinuousModel]
    root_state: np.ndarray
    seed: int | np.random.Generator | None = None

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)
        self.times = _get_time_from_root(self.tree)
        self.ntraits = len(self.models)

    def _run_once(self) -> np.ndarray:
        arr = np.zeros((self.tree.nnodes, self.ntraits), dtype=float)
        ridx = self.tree.treenode.idx
        arr[ridx, :] = self.root_state
        for node in self.tree[::-1][1:]:
            nidx = node.idx
            pidx = node.up.idx
            t = float(node.dist)
            tp = float(self.times[pidx])
            tc = float(self.times[nidx])
            for tidx, model in enumerate(self.models):
                arr[nidx, tidx] = _simulate_increment_univariate(
                    model=model,
                    parent_value=float(arr[pidx, tidx]),
                    branch_length=t,
                    parent_time=tp,
                    child_time=tc,
                    rng=self.rng,
                )
        return arr

    def run(self, nreplicates: int) -> np.ndarray:
        out = np.zeros((self.tree.nnodes, self.ntraits, nreplicates), dtype=float)
        for ridx in range(nreplicates):
            out[:, :, ridx] = self._run_once()
        return out


@add_subpackage_method(PhyloCompAPI)
def simulate_continuous_bm(
    tree: ToyTree,
    sigma2: float | Sequence[float] | Mapping[str, float] = 1.0,
    model: Literal["BM", "OU", "EB"] = "BM",
    root_state: float | Sequence[float] | Mapping[str, float] | None = None,
    alpha: float | Sequence[float] | Mapping[str, float] | None = None,
    r: float | Sequence[float] | Mapping[str, float] | None = None,
    optimum: float | Sequence[float] | Mapping[str, float] | None = None,
    nreplicates: int = 1,
    trait_name: str | None = None,
    tips_only: bool = False,
    inplace: bool = False,
    seed: int | np.random.Generator | None = None,
) -> pd.Series | pd.DataFrame | None:
    """Simulate one or more continuous traits under BM, OU, or EB models.

    Parameters
    ----------
    tree : ToyTree
        Tree on which trait values are simulated.
    sigma2 : float | Sequence[float] | Mapping[str, float], default=1.0
        Evolutionary rate parameter(s). A scalar simulates one trait. A sequence
        or mapping simulates multiple independent traits.
    model : Literal["BM", "OU", "EB"], default="BM"
        Continuous trait model to simulate.
    root_state : float | Sequence[float] | Mapping[str, float] | None, default=None
        Root state(s) for each trait. If None, root states are 0. If a mapping is
        provided it must contain keys for each trait name.
    alpha : float | Sequence[float] | Mapping[str, float] | None, default=None
        OU strength parameter(s). Used only when ``model="OU"``. If None, values
        default to 0 (BM-equivalent OU).
    r : float | Sequence[float] | Mapping[str, float] | None, default=None
        EB rate-change parameter(s). Used only when ``model="EB"``. If None,
        values default to 0 (BM-equivalent EB).
    optimum : float | Sequence[float] | Mapping[str, float] | None, default=None
        OU optimum value(s). If None, optimum defaults to ``root_state`` for each
        trait.
    nreplicates : int, default=1
        Number of replicate simulations. Values < 1 are coerced to 1.
    trait_name : str | None, default=None
        Base name for a single simulated trait. If ``nreplicates > 1`` columns are
        named ``{trait_name}_0``, ``{trait_name}_1``, etc.
    tips_only : bool, default=False
        If True, only tip-node values are returned or stored.
    inplace : bool, default=False
        If True, store simulated values as node features on ``tree`` and return
        None.
    seed : int | numpy.random.Generator | None, default=None
        Seed or random-number generator.

    Returns
    -------
    pandas.Series | pandas.DataFrame | None
        Returns a Series for one trait and one replicate, a DataFrame otherwise,
        or None when ``inplace=True``.

    Raises
    ------
    ToytreeError
        If parameters are invalid (e.g., mismatched lengths, non-positive
        ``sigma2`` values, invalid model, or conflicting naming inputs).

    Notes
    -----
    The previous aliases ``rates`` and ``root_states`` are not supported. Use
    ``sigma2`` and ``root_state``.

    Examples
    --------
    >>> tre = toytree.rtree.bdtree(30, seed=123)
    >>> tre.pcm.simulate_continuous_bm(sigma2=1.0, trait_name="X", inplace=True)
    >>> canvas, axes, mark = tre.draw();
    >>> tre.annotate.add_node_markers(axes, size=("X", 4, 12), mask=False,)
    """
    # Normalize basic simulation settings.
    nreplicates = max(1, int(nreplicates))
    model_type = ContinuousModelType(str(model).upper())

    # Coerce trait-level parameters to aligned vectors.
    sigma2_vec, names = _coerce_sigma2_and_names(sigma2)
    ntraits = sigma2_vec.size
    root_vec = _coerce_root_state(root_state, ntraits, names)

    if trait_name is not None and ntraits > 1:
        raise ToytreeError("trait_name can only be used when simulating one trait.")

    alpha_vec = _coerce_model_vector(
        alpha, ntraits, names, default=0.0, param_name="alpha"
    )
    r_vec = _coerce_model_vector(r, ntraits, names, default=0.0, param_name="r")
    opt_default = root_vec
    if optimum is None:
        opt_vec = opt_default.astype(float)
    else:
        opt_vec = _coerce_model_vector(
            optimum, ntraits, names, default=0.0, param_name="optimum"
        )

    # Build model objects and run trait simulation engine.
    models = [
        ContinuousModel(
            mtype=model_type,
            sigma2=float(sigma2_vec[i]),
            alpha=float(alpha_vec[i]),
            r=float(r_vec[i]),
            optimum=float(opt_vec[i]),
        )
        for i in range(ntraits)
    ]
    simulator = ContinuousTraitSimulator(
        tree=tree,
        models=models,
        root_state=root_vec,
        seed=seed,
    )
    values = simulator.run(nreplicates=nreplicates)

    # Flatten (node x trait x replicate) to a tabular output with deterministic naming.
    colnames: list[str] = []
    if ntraits == 1 and trait_name is not None:
        base = trait_name
    elif ntraits == 1:
        base = names[0]
    else:
        base = ""

    data_cols = []
    for ridx in range(nreplicates):
        for tidx in range(ntraits):
            if ntraits == 1:
                cname = base if nreplicates == 1 else f"{base}_{ridx}"
            else:
                tname = names[tidx]
                cname = tname if nreplicates == 1 else f"{tname}_{ridx}"
            colnames.append(cname)
            data_cols.append(values[:, tidx, ridx])

    df = pd.DataFrame(
        np.column_stack(data_cols),
        index=range(tree.nnodes),
        columns=colnames,
    )
    # Optionally reduce to tips only (common empirical-data shape).
    if tips_only:
        df = df.iloc[: tree.ntips]

    # Dispatch output mode: Series/DataFrame return vs in-place storage.
    if ntraits == 1 and nreplicates == 1:
        series = df.iloc[:, 0].copy()
        if not inplace:
            return series
        mapping = dict(series.dropna())
        tree.set_node_data(series.name, mapping, default=np.nan, inplace=True)
        return None

    if not inplace:
        return df
    for feature in df.columns:
        mapping = dict(df[feature].dropna())
        tree.set_node_data(feature, mapping, default=np.nan, inplace=True)
    return None


@add_subpackage_method(PhyloCompAPI)
def simulate_continuous_multivariate_bm(
    tree: ToyTree,
    sigma: np.ndarray | pd.DataFrame,
    root_state: Sequence[float] | Mapping[str, float] | None = None,
    nreplicates: int = 1,
    trait_names: Sequence[str] | None = None,
    tips_only: bool = False,
    inplace: bool = False,
    seed: int | np.random.Generator | None = None,
) -> pd.DataFrame | None:
    """Simulate correlated continuous traits under multivariate BM."""
    # Validate covariance-matrix and shape constraints.
    nreplicates = max(1, int(nreplicates))
    sigma_arr = np.asarray(sigma, dtype=float)
    if sigma_arr.ndim != 2 or sigma_arr.shape[0] != sigma_arr.shape[1]:
        raise ToytreeError("sigma must be a square covariance matrix.")
    if not np.allclose(sigma_arr, sigma_arr.T, atol=1e-12, rtol=1e-10):
        raise ToytreeError("sigma must be symmetric.")
    evals = np.linalg.eigvalsh(sigma_arr)
    if np.any(evals < -1e-10):
        raise ToytreeError("sigma must be positive semidefinite.")

    # Normalize output feature names and root-state vector.
    ntraits = sigma_arr.shape[0]
    if trait_names is None:
        trait_names = [f"t{i}" for i in range(ntraits)]
    else:
        trait_names = [str(i) for i in trait_names]
        if len(trait_names) != ntraits:
            raise ToytreeError("trait_names length must match sigma dimension.")

    if root_state is None:
        root_vec = np.zeros(ntraits, dtype=float)
    elif isinstance(root_state, Mapping):
        root_vec = np.array([float(root_state[i]) for i in trait_names], dtype=float)
    else:
        root_vec = np.asarray(list(root_state), dtype=float)
        if root_vec.size != ntraits:
            raise ToytreeError("root_state length must match sigma dimension.")

    # Simulate branch-wise MVN increments down the tree for each replicate.
    rng = np.random.default_rng(seed)
    ridx = tree.treenode.idx
    arr = np.zeros((tree.nnodes, ntraits, nreplicates), dtype=float)
    for rep in range(nreplicates):
        arr[ridx, :, rep] = root_vec
        for node in tree[::-1][1:]:
            pidx = node.up.idx
            nidx = node.idx
            t = float(node.dist)
            if t <= 0:
                arr[nidx, :, rep] = arr[pidx, :, rep]
                continue
            delta = rng.multivariate_normal(
                mean=np.zeros(ntraits, dtype=float),
                cov=sigma_arr * t,
            )
            arr[nidx, :, rep] = arr[pidx, :, rep] + delta

    # Assemble final table and apply optional in-place storage.
    colnames = []
    cols = []
    for rep in range(nreplicates):
        for tidx, name in enumerate(trait_names):
            colnames.append(name if nreplicates == 1 else f"{name}_r{rep}")
            cols.append(arr[:, tidx, rep])
    df = pd.DataFrame(
        np.column_stack(cols),
        index=range(tree.nnodes),
        columns=colnames,
    )
    if tips_only:
        df = df.iloc[: tree.ntips]
    if not inplace:
        return df
    for feature in df.columns:
        mapping = dict(df[feature].dropna())
        tree.set_node_data(feature, mapping, default=np.nan, inplace=True)
    return None
