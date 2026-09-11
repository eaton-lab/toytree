#!/usr/bin/env python

"""Simulate multivariate continuous traits under BM, OU, or EB models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Mapping, Sequence, TypeAlias

import numpy as np
import pandas as pd
from scipy.linalg import expm

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.sim._continuous_sim_shared import (
    _coerce_regime_labels,
    _get_time_from_root,
)
from toytree.pcm.src.sim._utils import (
    RNGSeed,
    get_rng,
    make_node_dataframe,
    validate_bool,
    validate_feature_name,
    validate_tree_for_simulation,
)
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["simulate_multivariate_continuous_trait"]

BMParams: TypeAlias = np.ndarray
OUParams: TypeAlias = tuple[np.ndarray, np.ndarray]
EBParams: TypeAlias = tuple[np.ndarray, Sequence[float] | np.ndarray]
SingleModelParams: TypeAlias = BMParams | OUParams | EBParams
RegimeModelParams: TypeAlias = Mapping[str, SingleModelParams]
ModelParams: TypeAlias = SingleModelParams | RegimeModelParams


def _as_square_matrix(x: object, param_name: str) -> np.ndarray:
    """Return input as a float square matrix."""
    arr = np.asarray(x, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ToytreeError(f"{param_name} must be a square matrix.")
    if not np.all(np.isfinite(arr)):
        raise ToytreeError(f"{param_name} entries must be finite.")
    return arr


def _validate_symmetric_psd(x: np.ndarray, param_name: str) -> np.ndarray:
    """Return a symmetric positive-semidefinite matrix."""
    if not np.allclose(x, x.T, atol=1e-12, rtol=1e-10):
        raise ToytreeError(f"{param_name} must be symmetric.")
    sym = (x + x.T) / 2.0
    evals, evecs = np.linalg.eigh(sym)
    tol = 1e-10 * max(1.0, float(np.max(np.abs(evals))))
    if float(np.min(evals)) < -tol:
        raise ToytreeError(f"{param_name} must be positive semidefinite.")
    if np.any(evals < 0.0):
        sym = evecs @ np.diag(np.clip(evals, 0.0, None)) @ evecs.T
        sym = (sym + sym.T) / 2.0
    return sym


def _infer_ntraits_from_multivariate_params(
    model_key: str,
    params: object,
) -> int:
    """Infer trait dimensionality from the multivariate params input."""
    if isinstance(params, Mapping):
        if not params:
            raise ToytreeError("params mapping must define at least one regime.")
        first = next(iter(params.values()))
    else:
        first = params

    if model_key == "bm":
        return int(_as_square_matrix(first, "params").shape[0])
    if model_key in ("ou", "eb"):
        if not isinstance(first, (tuple, list, np.ndarray)):
            raise ToytreeError(f"{model_key.upper()} params must be a length-2 tuple.")
        if len(first) != 2:
            raise ToytreeError(f"{model_key.upper()} params must be length 2.")
        return int(_as_square_matrix(first[0], "R matrix").shape[0])
    raise ToytreeError("model must be one of: 'bm', 'ou', 'eb'.")


def _coerce_trait_names_for_multivariate(
    names: Sequence[str] | None,
    ntraits: int,
) -> list[str]:
    """Return validated trait names for multivariate outputs."""
    if names is None:
        return [f"X{i + 1}" for i in range(ntraits)]
    onames = [validate_feature_name(i, parameter="names entry") for i in names]
    if len(onames) != ntraits:
        raise ToytreeError("names length must match inferred trait dimension.")
    if len(set(onames)) != len(onames):
        raise ToytreeError("names must be unique.")
    return onames


def _coerce_root_states_for_multivariate(
    root_states: Sequence[float] | np.ndarray | None,
    ntraits: int,
) -> np.ndarray:
    """Return root-state vector of length ntraits."""
    if root_states is None:
        return np.zeros(ntraits, dtype=float)
    arr = np.asarray(list(root_states), dtype=float)
    if arr.size != ntraits:
        raise ToytreeError("root_states length must match inferred trait dimension.")
    if not np.all(np.isfinite(arr)):
        raise ToytreeError("root_states entries must be finite.")
    return arr


def _coerce_model_params_multivariate(
    model_key: str,
    raw: object,
    ntraits: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return validated (R, A, r) arrays for one regime or global params."""
    if model_key == "bm":
        rmat = _validate_symmetric_psd(_as_square_matrix(raw, "R matrix"), "R matrix")
        if rmat.shape[0] != ntraits:
            raise ToytreeError(
                "R matrix dimension must match inferred trait dimension."
            )
        return (
            rmat,
            np.zeros((ntraits, ntraits), dtype=float),
            np.zeros(ntraits, dtype=float),
        )

    if not isinstance(raw, (tuple, list, np.ndarray)):
        raise ToytreeError(f"{model_key.upper()} params must be a tuple of length 2.")
    if len(raw) != 2:
        raise ToytreeError(f"{model_key.upper()} params must be length 2.")
    rmat = _validate_symmetric_psd(_as_square_matrix(raw[0], "R matrix"), "R matrix")
    if rmat.shape[0] != ntraits:
        raise ToytreeError("R matrix dimension must match inferred trait dimension.")

    if model_key == "ou":
        amat = _as_square_matrix(raw[1], "A matrix")
        if amat.shape != (ntraits, ntraits):
            raise ToytreeError("A matrix dimension must match R matrix.")
        eigvals = np.linalg.eigvals(amat)
        if float(np.min(np.real(eigvals))) < -1e-10:
            raise ToytreeError(
                "A matrix must be stable: every eigenvalue must have a "
                "non-negative real part."
            )
        return rmat, amat, np.zeros(ntraits, dtype=float)

    rvec = np.asarray(list(raw[1]), dtype=float)
    if rvec.size != ntraits:
        raise ToytreeError("r vector length must match R matrix dimension.")
    if not np.all(np.isfinite(rvec)):
        raise ToytreeError("r vector entries must be finite.")
    return rmat, np.zeros((ntraits, ntraits), dtype=float), rvec


def _coerce_params_by_node_multivariate(
    tree: ToyTree,
    model_key: str,
    params: ModelParams,
    regime: str | pd.Series | None,
    ntraits: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return per-node (R, A, r) arrays keyed by child node idx."""
    r_by_node = np.zeros((tree.nnodes, ntraits, ntraits), dtype=float)
    a_by_node = np.zeros((tree.nnodes, ntraits, ntraits), dtype=float)
    rv_by_node = np.zeros((tree.nnodes, ntraits), dtype=float)

    if not isinstance(params, Mapping):
        rmat, amat, rvec = _coerce_model_params_multivariate(model_key, params, ntraits)
        r_by_node[:] = rmat
        a_by_node[:] = amat
        rv_by_node[:] = rvec
        return r_by_node, a_by_node, rv_by_node

    if regime is None:
        raise ToytreeError("regime is required when params is a dict.")
    pmap = {str(k): v for k, v in params.items()}
    if not pmap:
        raise ToytreeError("params mapping must define at least one regime.")
    labels = _coerce_regime_labels(tree, regime)
    coerced = {
        key: _coerce_model_params_multivariate(model_key, val, ntraits)
        for key, val in pmap.items()
    }

    for node in tree[:-1]:
        raw_label = labels[node.idx]
        if pd.isna(raw_label):
            raise ToytreeError(
                "regime labels must be present on all non-root nodes "
                "when params is a dict."
            )
        sval = str(raw_label)
        if sval not in coerced:
            raise ToytreeError(f"params is missing values for regime state {sval!r}.")
        rmat, amat, rvec = coerced[sval]
        r_by_node[node.idx] = rmat
        a_by_node[node.idx] = amat
        rv_by_node[node.idx] = rvec

    root_key = str(next(iter(pmap.keys())))
    rmat, amat, rvec = coerced[root_key]
    r_by_node[tree.treenode.idx] = rmat
    a_by_node[tree.treenode.idx] = amat
    rv_by_node[tree.treenode.idx] = rvec
    return r_by_node, a_by_node, rv_by_node


def _coerce_optima_by_node_multivariate(
    tree: ToyTree,
    optimum_states: Sequence[float]
    | np.ndarray
    | Mapping[str, Sequence[float] | np.ndarray]
    | None,
    regime: str | pd.Series | None,
    root_states: np.ndarray,
    ntraits: int,
) -> np.ndarray:
    """Return per-child-edge OU optimum vectors."""
    out = np.repeat(root_states[None, :], tree.nnodes, axis=0)
    if optimum_states is None:
        return out
    if not isinstance(optimum_states, Mapping):
        optimum = np.asarray(optimum_states, dtype=float)
        if optimum.shape != (ntraits,) or not np.all(np.isfinite(optimum)):
            raise ToytreeError(
                "optimum_states must contain one finite value per trait."
            )
        out[:] = optimum
        return out
    if regime is None:
        raise ToytreeError("regime is required when optimum_states is a dict.")
    if not optimum_states:
        raise ToytreeError("optimum_states mapping must define at least one regime.")
    omap: dict[str, np.ndarray] = {}
    for key, value in optimum_states.items():
        optimum = np.asarray(value, dtype=float)
        if optimum.shape != (ntraits,) or not np.all(np.isfinite(optimum)):
            raise ToytreeError(
                "each optimum_states value must contain one finite value per trait."
            )
        omap[str(key)] = optimum
    labels = _coerce_regime_labels(tree, regime)
    for node in tree[:-1]:
        raw_label = labels[node.idx]
        if pd.isna(raw_label):
            raise ToytreeError(
                "regime labels must be present on all non-root nodes when "
                "optimum_states is a dict."
            )
        state = str(raw_label)
        if state not in omap:
            raise ToytreeError(
                f"optimum_states is missing values for regime state {state!r}."
            )
        out[node.idx] = omap[state]
    out[tree.treenode.idx] = next(iter(omap.values()))
    return out


def _validate_computed_covariance(cov: np.ndarray) -> np.ndarray:
    """Return a symmetric PSD covariance without adding artificial variance."""
    sym = (cov + cov.T) / 2.0
    evals, evecs = np.linalg.eigh(sym)
    tol = 1e-9 * max(1.0, float(np.max(np.abs(evals))))
    if float(np.min(evals)) < -tol:
        raise ToytreeError("Computed covariance is not positive semidefinite.")
    if np.any(evals < 0.0):
        sym = evecs @ np.diag(np.clip(evals, 0.0, None)) @ evecs.T
        sym = (sym + sym.T) / 2.0
    return sym


def _ou_covariance_full_matrix(
    rmat: np.ndarray,
    amat: np.ndarray,
    branch_length: float,
) -> np.ndarray:
    """Return OU transition covariance for full selection matrix A."""
    if branch_length <= 0:
        return np.zeros_like(rmat)
    if np.count_nonzero(amat) == 0:
        return rmat * branch_length
    ntraits = rmat.shape[0]
    eye = np.eye(ntraits, dtype=float)
    ksum = np.kron(eye, amat) + np.kron(amat, eye)
    vec_r = rmat.reshape(ntraits * ntraits, order="F")
    # The augmented exponential evaluates int_0^t exp(-K s) vec(R) ds
    # directly. Unlike solving K vec(V) = (I-exp(-Kt)) vec(R), this remains
    # valid when A contains neutral (zero-eigenvalue) trait dimensions.
    nflat = ntraits * ntraits
    augmented = np.zeros((nflat + 1, nflat + 1), dtype=float)
    augmented[:nflat, :nflat] = -ksum
    augmented[:nflat, nflat] = vec_r
    vec_cov = expm(augmented * branch_length)[:nflat, nflat]
    cov = vec_cov.reshape((ntraits, ntraits), order="F")
    return _validate_computed_covariance(cov)


def _eb_covariance_multivariate(
    rmat: np.ndarray,
    rvec: np.ndarray,
    parent_time: float,
    child_time: float,
) -> np.ndarray:
    """Return EB branch covariance with per-trait rate scalars."""
    dt = child_time - parent_time
    if dt <= 0:
        return np.zeros_like(rmat)
    # Averages pairwise r terms so diagonals reduce to the univariate EB formula.
    ksum = (rvec[:, None] + rvec[None, :]) / 2.0
    mask_zero = np.isclose(ksum, 0.0, atol=1e-14)
    ints = np.full(ksum.shape, dt, dtype=float)
    with np.errstate(over="raise", divide="raise", invalid="raise"):
        try:
            # Use masked evaluation so zero-denominator entries are never
            # evaluated in the division branch under strict floating-point
            # error settings. This preserves the exact dt limit for ksum=0.
            nz = ~mask_zero
            if np.any(nz):
                k = ksum[nz]
                ints[nz] = (
                    np.exp(k * parent_time) * np.expm1(k * (child_time - parent_time))
                ) / k
        except FloatingPointError as exc:
            raise ToytreeError("EB covariance overflowed; reduce r values.") from exc
    if not np.all(np.isfinite(ints)):
        raise ToytreeError("EB covariance overflowed; reduce r values.")
    return _validate_computed_covariance(rmat * ints)


@add_subpackage_method(PhyloCompAPI)
def simulate_multivariate_continuous_trait(
    tree: ToyTree,
    model: Literal["bm", "ou", "eb"] = "bm",
    params: ModelParams | None = None,
    root_states: Sequence[float] | np.ndarray | None = None,
    names: Sequence[str] | None = None,
    tips_only: bool = False,
    regime: str | pd.Series | None = None,
    inplace: bool = False,
    seed: RNGSeed = None,
    *,
    optimum_states: Sequence[float]
    | np.ndarray
    | Mapping[str, Sequence[float] | np.ndarray]
    | None = None,
) -> pd.DataFrame:
    """Simulate multiple continuous traits under BM, OU, or EB models.

    This is the unified multivariate continuous-trait simulator in ``toytree``.
    It supports correlated trait evolution under three models:

    - ``"bm"`` (Brownian motion): trait vectors follow a multivariate random
      walk with covariance accumulation proportional to branch length.
    - ``"ou"`` (Ornstein-Uhlenbeck): Brownian diffusion with matrix-valued
      pull toward an optimum vector. The optimum defaults to ``root_states``.
    - ``"eb"`` (early burst): branchwise diffusion covariance is scaled through
      time by per-trait exponential rate parameters.

    Parameters
    ----------
    tree : ToyTree
        Tree on which trait values are simulated.
    model : {"bm", "ou", "eb"}, default="bm"
        Continuous-trait model to simulate.
    params : ModelParams | None, default=None
        Model parameters keyed to ``model``.
        For BM use an ``(M, M)`` rate matrix ``R`` or ``dict[regime, R]``.
        For OU use ``(R, A)`` or ``dict[regime, (R, A)]`` where ``A`` is
        an ``(M, M)`` selection matrix.
        For EB use ``(R, r)`` or ``dict[regime, (R, r)]`` where ``r`` is a
        length-``M`` vector of exponential rate-scaling parameters.
    root_states : Sequence[float] | np.ndarray | None, default=None
        Root-state vector of length ``M``. If None, defaults to zeros.
    names : Sequence[str] | None, default=None
        Output trait names. If None, names are ``X1..XM``.
    tips_only : bool, default=False
        If True, return only tip rows.
    regime : str | pandas.Series | None, default=None
        Regime labels used when ``params`` is a dict. If a string, interpreted
        as a node feature on ``tree``. If a Series, may be indexed by node idx
        or unique node names.
    inplace : bool, default=False
        If True, write each simulated trait column to tree node data.
    seed : int | numpy.random.Generator | None, default=None
        Random-number source. A supplied Generator is consumed in place.
        Integer and SeedSequence inputs initialize a new Generator.
    optimum_states : sequence, numpy.ndarray, mapping, or None, keyword-only
        OU optimum vector. If None, use ``root_states``. A single vector
        applies to every edge. A mapping supplies child-edge optima by regime
        label and requires ``regime``. Invalid for BM and EB.

    Returns
    -------
    pandas.DataFrame
        Simulated trait matrix with one column per trait and node idx rows
        (or tip rows only if ``tips_only=True``).

    Raises
    ------
    ToytreeError
        If ``model`` is invalid, parameters are malformed, required regime
        information is missing, matrix constraints fail (e.g., symmetry / PSD),
        or covariance calculations become numerically invalid.
    """
    tree = validate_tree_for_simulation(tree)
    tips_only = validate_bool(tips_only, "tips_only")
    inplace = validate_bool(inplace, "inplace")
    model_key = str(model).lower()
    if model_key not in ("bm", "ou", "eb"):
        raise ToytreeError("model must be one of: 'bm', 'ou', 'eb'.")
    if params is None:
        raise ToytreeError("params is required.")
    if model_key != "ou" and optimum_states is not None:
        raise ToytreeError("optimum_states is only valid when model='ou'.")

    ntraits = _infer_ntraits_from_multivariate_params(model_key, params)
    onames = _coerce_trait_names_for_multivariate(names, ntraits)
    root_vec = _coerce_root_states_for_multivariate(root_states, ntraits)
    r_by_node, a_by_node, rv_by_node = _coerce_params_by_node_multivariate(
        tree=tree,
        model_key=model_key,
        params=params,
        regime=regime,
        ntraits=ntraits,
    )
    optimum_by_node = _coerce_optima_by_node_multivariate(
        tree,
        optimum_states,
        regime,
        root_vec,
        ntraits,
    )

    rng = get_rng(seed)
    times = _get_time_from_root(tree)
    arr = np.zeros((tree.nnodes, ntraits), dtype=float)
    ridx = tree.treenode.idx
    arr[ridx, :] = root_vec
    zeros = np.zeros(ntraits, dtype=float)

    for node in tree[::-1][1:]:
        nidx = node.idx
        pidx = node.up.idx
        t = float(node.dist)
        if t <= 0:
            arr[nidx] = arr[pidx]
            continue
        parent_time = float(times[pidx])
        child_time = float(times[nidx])
        rmat = r_by_node[nidx]
        if model_key == "bm":
            cov = _validate_computed_covariance(rmat * t)
            delta = rng.multivariate_normal(mean=zeros, cov=cov, check_valid="raise")
            arr[nidx] = arr[pidx] + delta
        elif model_key == "ou":
            amat = a_by_node[nidx]
            trans = expm(-amat * t)
            optimum = optimum_by_node[nidx]
            mean = optimum + trans @ (arr[pidx] - optimum)
            cov = _ou_covariance_full_matrix(rmat, amat, t)
            arr[nidx] = rng.multivariate_normal(mean=mean, cov=cov, check_valid="raise")
        else:
            rvec = rv_by_node[nidx]
            cov = _eb_covariance_multivariate(rmat, rvec, parent_time, child_time)
            delta = rng.multivariate_normal(mean=zeros, cov=cov, check_valid="raise")
            arr[nidx] = arr[pidx] + delta

    return make_node_dataframe(
        tree,
        arr,
        names=onames,
        tips_only=tips_only,
        inplace=inplace,
    )
