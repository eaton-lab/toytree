#!/usr/bin/env python

"""Simulate univariate continuous traits on trees under BM, OU, or EB models.

The univariate simulators in this module now simulate a single trait at a time
and return a :class:`pandas.Series`. Regime-specific simulations are supported
by passing a categorical regime trait and a dictionary mapping regime states to
model parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Literal, Mapping, Sequence, TypeAlias

import numpy as np
import pandas as pd

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.sim._continuous_sim_shared import (
    _coerce_regime_labels,
    _get_time_from_root,
)
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = [
    "simulate_continuous_trait",
]

BMParams: TypeAlias = float
OUParams: TypeAlias = tuple[float, float]
EBParams: TypeAlias = tuple[float, float]
SingleModelParams: TypeAlias = BMParams | OUParams | EBParams
RegimeModelParams: TypeAlias = Mapping[str, BMParams | OUParams | EBParams]
ModelParams: TypeAlias = SingleModelParams | RegimeModelParams


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
            var = (
                model.sigma2
                * (1.0 - np.exp(-2.0 * model.alpha * t))
                / (2.0 * model.alpha)
            )
    else:
        mean = float(parent_value)
        if model.r == 0.0:
            var = model.sigma2 * t
        else:
            var = (
                model.sigma2
                * (np.exp(model.r * child_time) - np.exp(model.r * parent_time))
                / model.r
            )
    var = max(float(var), 0.0)
    std = float(np.sqrt(var))
    return float(rng.normal(loc=mean, scale=std))


def _simulate_increment_univariate_params(
    mtype: ContinuousModelType,
    sigma2: float,
    alpha: float,
    r: float,
    optimum: float,
    parent_value: float,
    branch_length: float,
    parent_time: float,
    child_time: float,
    rng: np.random.Generator,
) -> float:
    """Sample child value on a branch for one trait from scalar params."""
    model = ContinuousModel(
        mtype=mtype,
        sigma2=sigma2,
        alpha=alpha,
        r=r,
        optimum=optimum,
    )
    return _simulate_increment_univariate(
        model=model,
        parent_value=parent_value,
        branch_length=branch_length,
        parent_time=parent_time,
        child_time=child_time,
        rng=rng,
    )


def _coerce_scalar_root_state(root_state: float | None) -> float:
    """Return a scalar root state for univariate simulations."""
    if root_state is None:
        return 0.0
    if np.isscalar(root_state):
        return float(root_state)
    raise ToytreeError("root_state must be a scalar float or None.")


def _coerce_bm_regime_params(
    tree: ToyTree,
    params: BMParams | Mapping[str, BMParams],
    regime: str | pd.Series | None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-node scalar BM parameters (sigma2) and regime labels."""
    labels = _coerce_regime_labels(tree, regime)
    sigma2_by_node = np.full(tree.nnodes, np.nan, dtype=float)
    if isinstance(params, Mapping):
        pmap = {str(k): float(v) for k, v in params.items()}
        if not pmap:
            raise ToytreeError("params mapping must define at least one regime state.")
        for key, val in pmap.items():
            if val <= 0:
                raise ToytreeError(
                    f"BM params values must be > 0. Invalid value for regime {key!r}."
                )
        if regime is None:
            raise ToytreeError("regime is required when params is a dict.")
        for node in tree[:-1]:
            raw = labels[node.idx]
            if pd.isna(raw):
                raise ToytreeError(
                    "regime labels must be present on all non-root nodes "
                    "when params is a dict."
                )
            sval = str(raw)
            if sval not in pmap:
                raise ToytreeError(
                    f"params is missing a value for regime state {sval!r}."
                )
            sigma2_by_node[node.idx] = pmap[sval]
        sigma2_by_node[tree.treenode.idx] = float(next(iter(pmap.values())))
        return sigma2_by_node, labels

    if not np.isscalar(params):
        raise ToytreeError("BM params must be a float or dict[str, float].")
    sigma2 = float(params)
    if sigma2 <= 0:
        raise ToytreeError("BM params (sigma2) must be > 0.")
    sigma2_by_node[:] = sigma2
    return sigma2_by_node, labels


def _coerce_pair(value: object, *, model: str) -> tuple[float, float]:
    """Return a validated 2-tuple of floats for OU/EB params."""
    if not isinstance(value, (tuple, list, np.ndarray)):
        raise ToytreeError(
            f"{model} params must be a tuple[float, float] or regime dict."
        )
    arr = np.asarray(list(value), dtype=float)
    if arr.size != 2:
        raise ToytreeError(f"{model} params tuples must have length 2.")
    return float(arr[0]), float(arr[1])


def _coerce_ou_regime_params(
    tree: ToyTree,
    params: OUParams | Mapping[str, OUParams],
    regime: str | pd.Series | None,
    root_state: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return per-node OU arrays (sigma2, alpha, optimum)."""
    labels = _coerce_regime_labels(tree, regime)
    sigma2_by_node = np.full(tree.nnodes, np.nan, dtype=float)
    alpha_by_node = np.full(tree.nnodes, np.nan, dtype=float)
    optimum_by_node = np.full(tree.nnodes, float(root_state), dtype=float)

    if isinstance(params, Mapping):
        if regime is None:
            raise ToytreeError("regime is required when params is a dict.")
        pmap = {str(k): _coerce_pair(v, model="OU") for k, v in params.items()}
        if not pmap:
            raise ToytreeError("params mapping must define at least one regime state.")
        for key, (sigma2, alpha) in pmap.items():
            if sigma2 <= 0 or alpha < 0:
                raise ToytreeError(
                    f"OU params for regime {key!r} must satisfy sigma2>0 and alpha>=0."
                )
        for node in tree[:-1]:
            raw = labels[node.idx]
            if pd.isna(raw):
                raise ToytreeError(
                    "regime labels must be present on all non-root nodes "
                    "when params is a dict."
                )
            sval = str(raw)
            if sval not in pmap:
                raise ToytreeError(
                    f"params is missing a value for regime state {sval!r}."
                )
            sigma2_by_node[node.idx], alpha_by_node[node.idx] = pmap[sval]
        sigma2_by_node[tree.treenode.idx], alpha_by_node[tree.treenode.idx] = next(
            iter(pmap.values())
        )
        return sigma2_by_node, alpha_by_node, optimum_by_node

    sigma2, alpha = _coerce_pair(params, model="OU")
    if sigma2 <= 0 or alpha < 0:
        raise ToytreeError("OU params must satisfy sigma2>0 and alpha>=0.")
    sigma2_by_node[:] = sigma2
    alpha_by_node[:] = alpha
    return sigma2_by_node, alpha_by_node, optimum_by_node


def _coerce_eb_regime_params(
    tree: ToyTree,
    params: EBParams | Mapping[str, EBParams],
    regime: str | pd.Series | None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-node EB arrays (sigma2, r)."""
    labels = _coerce_regime_labels(tree, regime)
    sigma2_by_node = np.full(tree.nnodes, np.nan, dtype=float)
    r_by_node = np.full(tree.nnodes, np.nan, dtype=float)

    if isinstance(params, Mapping):
        if regime is None:
            raise ToytreeError("regime is required when params is a dict.")
        pmap = {str(k): _coerce_pair(v, model="EB") for k, v in params.items()}
        if not pmap:
            raise ToytreeError("params mapping must define at least one regime state.")
        for key, (sigma2, rval) in pmap.items():
            if sigma2 <= 0 or not np.isfinite(rval):
                raise ToytreeError(
                    f"EB params for regime {key!r} must satisfy sigma2>0 and finite r."
                )
        for node in tree[:-1]:
            raw = labels[node.idx]
            if pd.isna(raw):
                raise ToytreeError(
                    "regime labels must be present on all non-root nodes "
                    "when params is a dict."
                )
            sval = str(raw)
            if sval not in pmap:
                raise ToytreeError(
                    f"params is missing a value for regime state {sval!r}."
                )
            sigma2_by_node[node.idx], r_by_node[node.idx] = pmap[sval]
        sigma2_by_node[tree.treenode.idx], r_by_node[tree.treenode.idx] = next(
            iter(pmap.values())
        )
        return sigma2_by_node, r_by_node

    sigma2, rval = _coerce_pair(params, model="EB")
    if sigma2 <= 0 or not np.isfinite(rval):
        raise ToytreeError("EB params must satisfy sigma2>0 and finite r.")
    sigma2_by_node[:] = sigma2
    r_by_node[:] = rval
    return sigma2_by_node, r_by_node


def _simulate_continuous_single_trait(
    tree: ToyTree,
    *,
    model_type: ContinuousModelType,
    sigma2_by_node: np.ndarray,
    alpha_by_node: np.ndarray,
    r_by_node: np.ndarray,
    optimum_by_node: np.ndarray,
    root_state: float,
    name: str,
    tips_only: bool,
    inplace: bool,
    seed: int | np.random.Generator | None,
) -> pd.Series:
    """Simulate one continuous trait and optionally write it to the tree."""
    simulator = ContinuousTraitRegimeSimulator(
        tree=tree,
        model_type=model_type,
        sigma2_by_node=sigma2_by_node.reshape(tree.nnodes, 1),
        alpha_by_node=alpha_by_node.reshape(tree.nnodes, 1),
        r_by_node=r_by_node.reshape(tree.nnodes, 1),
        optimum_by_node=optimum_by_node.reshape(tree.nnodes, 1),
        root_state=np.asarray([float(root_state)], dtype=float),
        seed=seed,
    )
    arr = simulator.run(nreplicates=1)[:, 0, 0]
    series = pd.Series(arr, index=range(tree.nnodes), name=name, dtype=float)
    if tips_only:
        series = series.iloc[: tree.ntips].copy()
    if inplace:
        # Preserve full-tree feature coverage even when only tips are returned.
        tree.set_node_data(name, dict(series.dropna()), default=np.nan, inplace=True)
    return series


@dataclass
class ContinuousTraitRegimeSimulator:
    """Simulator for independent continuous traits with per-edge regimes."""

    tree: ToyTree
    model_type: ContinuousModelType
    sigma2_by_node: np.ndarray
    alpha_by_node: np.ndarray
    r_by_node: np.ndarray
    optimum_by_node: np.ndarray
    root_state: np.ndarray
    seed: int | np.random.Generator | None = None

    def __post_init__(self):
        self.rng = np.random.default_rng(self.seed)
        self.times = _get_time_from_root(self.tree)
        self.ntraits = int(self.root_state.size)

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
            for tidx in range(self.ntraits):
                # Use the parameter row for this child node, which is how
                # regime-painted branches are represented internally.
                arr[nidx, tidx] = _simulate_increment_univariate_params(
                    mtype=self.model_type,
                    sigma2=float(self.sigma2_by_node[nidx, tidx]),
                    alpha=float(self.alpha_by_node[nidx, tidx]),
                    r=float(self.r_by_node[nidx, tidx]),
                    optimum=float(self.optimum_by_node[nidx, tidx]),
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
# fmt: off
def simulate_continuous_trait(
    tree: ToyTree,
    model: Literal["bm", "ou", "eb"] = "bm",
    params: ModelParams = 1.0,
    root_state: float | None = None,
    name: str = "X",
    tips_only: bool = False,
    regime: str | pd.Series | None = None,
    inplace: bool = False,
    seed: int | np.random.Generator | None = None,
) -> pd.Series:
    # fmt: on
    """Simulate one continuous trait under BM, OU, or EB models.

    This is the unified univariate continuous-trait simulator in ``toytree``.
    It supports three common models of trait evolution:

    - ``"bm"`` (Brownian motion): a random walk in which variance accumulates
      linearly with branch length. ``params`` is ``sigma2``.
    - ``"ou"`` (Ornstein-Uhlenbeck): Brownian motion with attraction toward an
      optimum. In this simplified API, the optimum is set to ``root_state``.
      ``params`` is ``(sigma2, alpha)``.
    - ``"eb"`` (early burst): branchwise variance is scaled through time by
      parameter ``r`` (e.g., accelerating or decelerating evolutionary rates).
      ``params`` is ``(sigma2, r)``.

    Regime-specific simulation ("Brownie"-style) is enabled by passing a
    dict-valued ``params`` and a categorical ``regime`` trait. Regime labels
    are stored on nodes, but apply to the edge entering each node (child-node
    keyed edge regimes). Every regime state used on non-root nodes must be
    present in the ``params`` dict.

    Parameters
    ----------
    tree : ToyTree
        Tree on which trait values are simulated.
    model : {"bm", "ou", "eb"}
        Continuous-trait model to simulate.
    params :
        float | tuple[float, float] | dict[str, float] |
        dict[str, tuple[float, float]], default=1.0
        Model parameters. Expected values depend on ``model``. Invalid shapes
        (e.g., tuple for ``bm`` or scalar for ``ou``/``eb``) raise an error.
        This signature is represented by the module-level ``ModelParams``
        type alias.
    root_state : float | None, default=None
        Root state for the simulated trait. If None, the root state is ``0.0``.
        For ``model='ou'``, the OU optimum is set internally to this same value.
    name : str, default="X"
        Feature name used for the returned Series and for inplace storage on
        the tree when ``inplace=True``.
    tips_only : bool, default=False
        If True, return (and optionally store) only tip values.
    regime : str | pandas.Series | None, default=None
        Categorical regime trait used when ``params`` is a dict. If a string, it
        is interpreted as a node feature on ``tree``. If a Series, it may be
        indexed by node idx or unique node names.
    inplace : bool, default=False
        If True, store simulated values as a node feature on ``tree`` and still
        return the simulated Series.
    seed : int | numpy.random.Generator | None, default=None
        Seed or random-number generator.

    Returns
    -------
    pandas.Series
        Simulated trait values indexed by node idx (or by tip idx rows only if
        ``tips_only=True``).

    Raises
    ------
    ToytreeError
        If ``model`` is invalid, if ``params`` values are incompatible with the
        selected model, or if regime-specific parameters fail validation.

    Examples
    --------
    >>> tre = toytree.rtree.bdtree(30, seed=123)
    >>> x = tre.pcm.simulate_continuous_trait("bm", params=1.0, name="X", seed=1)
    >>> x.head()
    >>> x_ou = tre.pcm.simulate_continuous_trait("ou", params=(1.0, 0.5), seed=2)
    >>> tre.set_node_data("reg", {0: "fast", 1: "slow"}, inplace=True)
    >>> x_reg = tre.pcm.simulate_continuous_trait(
    ...     "bm", params={"fast": 2.0, "slow": 0.5}, regime="reg", seed=3
    ... )
    >>> x2 = tre.pcm.simulate_continuous_trait("eb", params=(1.0, -0.5), inplace=True)
    """
    mkey = str(model).lower()
    root = _coerce_scalar_root_state(root_state)
    name = str(name)
    if not name.strip():
        raise ToytreeError("name must be a non-empty string.")

    # Dispatch to model-specific parameter coercers so each model enforces its
    # own parameter shape and value constraints before simulation.
    if mkey == "bm":
        sigma2_by_node, _ = _coerce_bm_regime_params(tree, params=params, regime=regime)
        alpha_by_node = np.zeros(tree.nnodes, dtype=float)
        r_by_node = np.zeros(tree.nnodes, dtype=float)
        optimum_by_node = np.zeros(tree.nnodes, dtype=float)
        model_type = ContinuousModelType.BM
    elif mkey == "ou":
        sigma2_by_node, alpha_by_node, optimum_by_node = _coerce_ou_regime_params(
            tree, params=params, regime=regime, root_state=root
        )
        r_by_node = np.zeros(tree.nnodes, dtype=float)
        model_type = ContinuousModelType.OU
    elif mkey == "eb":
        sigma2_by_node, r_by_node = _coerce_eb_regime_params(
            tree, params=params, regime=regime
        )
        alpha_by_node = np.zeros(tree.nnodes, dtype=float)
        optimum_by_node = np.zeros(tree.nnodes, dtype=float)
        model_type = ContinuousModelType.EB
    else:
        raise ToytreeError("model must be one of: 'bm', 'ou', 'eb'.")

    return _simulate_continuous_single_trait(
        tree=tree,
        model_type=model_type,
        sigma2_by_node=sigma2_by_node,
        alpha_by_node=alpha_by_node,
        r_by_node=r_by_node,
        optimum_by_node=optimum_by_node,
        root_state=root,
        name=name,
        tips_only=tips_only,
        inplace=inplace,
        seed=seed,
    )
