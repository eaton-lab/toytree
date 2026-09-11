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
from typing import TYPE_CHECKING, Literal, Mapping, TypeAlias

import numpy as np
import pandas as pd

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.sim._continuous_sim_shared import (
    _coerce_regime_labels,
    _get_time_from_root,
)
from toytree.pcm.src.sim._utils import (
    RNGSeed,
    get_rng,
    make_node_series,
    validate_bool,
    validate_feature_name,
    validate_finite_float,
    validate_tree_for_simulation,
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
    """Sample one child value from validated scalar model parameters."""
    t = float(branch_length)
    if t == 0.0:
        return float(parent_value)
    if mtype == ContinuousModelType.BM:
        mean = float(parent_value)
        var = sigma2 * t
    elif mtype == ContinuousModelType.OU:
        e = np.exp(-alpha * t)
        mean = optimum + (float(parent_value) - optimum) * e
        if alpha == 0.0:
            var = sigma2 * t
        else:
            var = sigma2 * (-np.expm1(-2.0 * alpha * t)) / (2.0 * alpha)
    else:
        mean = float(parent_value)
        if r == 0.0:
            var = sigma2 * t
        else:
            var = (
                sigma2
                * np.exp(r * parent_time)
                * np.expm1(r * (child_time - parent_time))
                / r
            )
    var = max(float(var), 0.0)
    if var == 0.0:
        return float(mean)
    return float(rng.normal(loc=mean, scale=np.sqrt(var)))


def _coerce_scalar_root_state(root_state: float | None) -> float:
    """Return a scalar root state for univariate simulations."""
    if root_state is None:
        return 0.0
    if np.isscalar(root_state):
        return validate_finite_float(root_state, "root_state")
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
            if not np.isfinite(val) or val < 0:
                raise ToytreeError(
                    "BM params values must be finite and >= 0. "
                    f"Invalid value for regime {key!r}."
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
    if not np.isfinite(sigma2) or sigma2 < 0:
        raise ToytreeError("BM params (sigma2) must be finite and >= 0.")
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
    optimum: float | Mapping[str, float] | None,
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
            if (
                not np.isfinite(sigma2)
                or sigma2 < 0
                or not np.isfinite(alpha)
                or alpha < 0
            ):
                raise ToytreeError(
                    f"OU params for regime {key!r} must contain finite values "
                    "with sigma2>=0 and alpha>=0."
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
    else:
        sigma2, alpha = _coerce_pair(params, model="OU")
        if not np.isfinite(sigma2) or sigma2 < 0 or not np.isfinite(alpha) or alpha < 0:
            raise ToytreeError(
                "OU params must contain finite values with sigma2>=0 and alpha>=0."
            )
        sigma2_by_node[:] = sigma2
        alpha_by_node[:] = alpha

    if optimum is None:
        optimum_by_node[:] = root_state
    elif isinstance(optimum, Mapping):
        if regime is None:
            raise ToytreeError("regime is required when optimum is a dict.")
        omap = {
            str(key): validate_finite_float(value, "optimum")
            for key, value in optimum.items()
        }
        if not omap:
            raise ToytreeError("optimum mapping must define at least one regime state.")
        for node in tree[:-1]:
            raw = labels[node.idx]
            if pd.isna(raw):
                raise ToytreeError(
                    "regime labels must be present on all non-root nodes when "
                    "optimum is a dict."
                )
            state = str(raw)
            if state not in omap:
                raise ToytreeError(
                    f"optimum is missing a value for regime state {state!r}."
                )
            optimum_by_node[node.idx] = omap[state]
        optimum_by_node[tree.treenode.idx] = float(next(iter(omap.values())))
    else:
        optimum_by_node[:] = validate_finite_float(optimum, "optimum")
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
            if sigma2 < 0 or not np.isfinite(sigma2) or not np.isfinite(rval):
                raise ToytreeError(
                    f"EB params for regime {key!r} must satisfy finite sigma2>=0 "
                    "and finite r."
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
    if sigma2 < 0 or not np.isfinite(sigma2) or not np.isfinite(rval):
        raise ToytreeError("EB params must satisfy finite sigma2>=0 and finite r.")
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
    seed: RNGSeed,
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
    return make_node_series(
        tree,
        arr,
        name=name,
        tips_only=tips_only,
        inplace=inplace,
        dtype=float,
    )


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
    seed: RNGSeed = None

    def __post_init__(self):
        self.rng = get_rng(self.seed)
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
    seed: RNGSeed = None,
    *,
    optimum: float | Mapping[str, float] | None = None,
) -> pd.Series:
    # fmt: on
    """Simulate one continuous trait under BM, OU, or EB models.

    This is the unified univariate continuous-trait simulator in ``toytree``.
    It supports three common models of trait evolution:

    - ``"bm"`` (Brownian motion): a random walk in which variance accumulates
      linearly with branch length. ``params`` is ``sigma2``.
    - ``"ou"`` (Ornstein-Uhlenbeck): Brownian motion with attraction toward an
      optimum. ``params`` is ``(sigma2, alpha)`` and ``optimum`` defaults to
      ``root_state``.
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
        For ``model='ou'``, the OU optimum defaults to this same value.
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
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place.
        Integer and SeedSequence inputs initialize a new Generator.
    optimum : float, Mapping[str, float], or None, keyword-only
        OU optimum. If None, use ``root_state``. A scalar applies to every
        edge. A mapping supplies child-edge optima by regime label and requires
        ``regime``. This argument is invalid for BM and EB.

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
    >>> tre = toytree.rtree.birth_death_conditioned_tree(30, crown_age=1.0, seed=123)
    >>> x = tre.pcm.simulate_continuous_trait("bm", params=1.0, name="X", seed=1)
    >>> x.head()
    >>> x_ou = tre.pcm.simulate_continuous_trait("ou", params=(1.0, 0.5), seed=2)
    >>> tre.set_node_data("reg", {0: "fast", 1: "slow"}, inplace=True)
    >>> x_reg = tre.pcm.simulate_continuous_trait(
    ...     "bm", params={"fast": 2.0, "slow": 0.5}, regime="reg", seed=3
    ... )
    >>> x2 = tre.pcm.simulate_continuous_trait("eb", params=(1.0, -0.5), inplace=True)
    """
    tree = validate_tree_for_simulation(tree)
    tips_only = validate_bool(tips_only, "tips_only")
    inplace = validate_bool(inplace, "inplace")
    mkey = str(model).lower()
    root = _coerce_scalar_root_state(root_state)
    name = validate_feature_name(name)
    rng = get_rng(seed)
    if mkey != "ou" and optimum is not None:
        raise ToytreeError("optimum is only valid when model='ou'.")

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
            tree,
            params=params,
            regime=regime,
            root_state=root,
            optimum=optimum,
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
        seed=rng,
    )
