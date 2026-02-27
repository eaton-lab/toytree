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


def _validate_symmetric_pd(x: np.ndarray, param_name: str) -> np.ndarray:
    """Return a symmetric positive-definite matrix."""
    if not np.allclose(x, x.T, atol=1e-12, rtol=1e-10):
        raise ToytreeError(f"{param_name} must be symmetric.")
    try:
        np.linalg.cholesky(x)
    except np.linalg.LinAlgError as exc:
        raise ToytreeError(f"{param_name} must be positive definite.") from exc
    return x


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
        return [f"t{i}" for i in range(ntraits)]
    onames = [str(i) for i in names]
    if len(onames) != ntraits:
        raise ToytreeError("names length must match inferred trait dimension.")
    for name in onames:
        if not name.strip():
            raise ToytreeError("names must be non-empty strings.")
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
        rmat = _validate_symmetric_pd(_as_square_matrix(raw, "R matrix"), "R matrix")
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
    rmat = _validate_symmetric_pd(_as_square_matrix(raw[0], "R matrix"), "R matrix")
    if rmat.shape[0] != ntraits:
        raise ToytreeError("R matrix dimension must match inferred trait dimension.")

    if model_key == "ou":
        amat = _as_square_matrix(raw[1], "A matrix")
        if amat.shape != (ntraits, ntraits):
            raise ToytreeError("A matrix dimension must match R matrix.")
        if not np.all(np.isfinite(amat)):
            raise ToytreeError("A matrix entries must be finite.")
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


def _regularize_covariance(cov: np.ndarray) -> np.ndarray:
    """Return a numerically stable covariance matrix for MVN sampling."""
    sym = (cov + cov.T) / 2.0
    evals, evecs = np.linalg.eigh(sym)
    if np.min(evals) < -1e-8:
        raise ToytreeError("Computed covariance is not positive semidefinite.")
    evals = np.clip(evals, 1e-14, None)
    out = evecs @ np.diag(evals) @ evecs.T
    return (out + out.T) / 2.0


def _ou_covariance_full_matrix(
    rmat: np.ndarray,
    amat: np.ndarray,
    branch_length: float,
) -> np.ndarray:
    """Return OU transition covariance for full selection matrix A."""
    if branch_length <= 0:
        return np.zeros_like(rmat)
    if np.allclose(amat, 0.0):
        return rmat * branch_length
    ntraits = rmat.shape[0]
    eye = np.eye(ntraits, dtype=float)
    ksum = np.kron(eye, amat) + np.kron(amat, eye)
    exp_term = expm(-ksum * branch_length)
    vec_r = rmat.reshape(ntraits * ntraits, order="F")
    rhs = (np.eye(ntraits * ntraits, dtype=float) - exp_term) @ vec_r
    try:
        vec_cov = np.linalg.solve(ksum, rhs)
    except np.linalg.LinAlgError:
        vec_cov = np.linalg.lstsq(ksum, rhs, rcond=None)[0]
    cov = vec_cov.reshape((ntraits, ntraits), order="F")
    return _regularize_covariance(cov)


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
    with np.errstate(over="raise", divide="raise", invalid="raise"):
        try:
            ints = np.where(
                np.isclose(ksum, 0.0, atol=1e-14),
                dt,
                (np.exp(ksum * child_time) - np.exp(ksum * parent_time)) / ksum,
            )
        except FloatingPointError as exc:
            raise ToytreeError("EB covariance overflowed; reduce r values.") from exc
    return _regularize_covariance(rmat * ints)


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
    seed: int | np.random.Generator | None = None,
) -> pd.DataFrame:
    """Simulate multiple continuous traits under BM, OU, or EB models.

    This is the unified multivariate continuous-trait simulator in ``toytree``.
    It supports correlated trait evolution under three models:

    - ``"bm"`` (Brownian motion): trait vectors follow a multivariate random
      walk with covariance accumulation proportional to branch length.
    - ``"ou"`` (Ornstein-Uhlenbeck): Brownian diffusion with matrix-valued
      pull toward an optimum vector (here anchored to ``root_states``).
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
        Output trait names. If None, names are ``t0..t{M-1}``.
    tips_only : bool, default=False
        If True, return only tip rows.
    regime : str | pandas.Series | None, default=None
        Regime labels used when ``params`` is a dict. If a string, interpreted
        as a node feature on ``tree``. If a Series, may be indexed by node idx
        or unique node names.
    inplace : bool, default=False
        If True, write each simulated trait column to tree node data.
    seed : int | numpy.random.Generator | None, default=None
        Random seed or numpy Generator.

    Returns
    -------
    pandas.DataFrame
        Simulated trait matrix with one column per trait and node idx rows
        (or tip rows only if ``tips_only=True``).

    Raises
    ------
    ToytreeError
        If ``model`` is invalid, parameters are malformed, required regime
        information is missing, matrix constraints fail (e.g., symmetry / PD),
        or covariance calculations become numerically invalid.
    """
    model_key = str(model).lower()
    if model_key not in ("bm", "ou", "eb"):
        raise ToytreeError("model must be one of: 'bm', 'ou', 'eb'.")
    if params is None:
        raise ToytreeError("params is required.")

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

    rng = np.random.default_rng(seed)
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
            cov = _regularize_covariance(rmat * t)
            delta = rng.multivariate_normal(mean=zeros, cov=cov)
            arr[nidx] = arr[pidx] + delta
        elif model_key == "ou":
            amat = a_by_node[nidx]
            trans = expm(-amat * t)
            mean = root_vec + trans @ (arr[pidx] - root_vec)
            cov = _ou_covariance_full_matrix(rmat, amat, t)
            arr[nidx] = rng.multivariate_normal(mean=mean, cov=cov)
        else:
            rvec = rv_by_node[nidx]
            cov = _eb_covariance_multivariate(rmat, rvec, parent_time, child_time)
            delta = rng.multivariate_normal(mean=zeros, cov=cov)
            arr[nidx] = arr[pidx] + delta

    out = pd.DataFrame(arr, index=range(tree.nnodes), columns=onames)
    if tips_only:
        out = out.iloc[: tree.ntips].copy()
    if inplace:
        for feature in out.columns:
            tree.set_node_data(
                feature,
                dict(out[feature].dropna()),
                default=np.nan,
                inplace=True,
            )
    return out
