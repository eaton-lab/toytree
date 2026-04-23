#!/usr/bin/env python

"""Gaussian node-state inference for pruning-based PGLS fits.

This module provides :func:`infer_node_states_pgls`, a convenience wrapper
that fits the pruning-based Gaussian PGLS model and then performs dense
Gaussian conditioning to infer/impute response states on tips and internal
nodes. The fitting step remains pruning-based; only the node-state conditioning
step uses dense covariance algebra in this phase.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Mapping

import numpy as np
import pandas as pd
from patsy import NAAction, PatsyError, build_design_matrices, dmatrices

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.phylolinalg.pgls import PCMPGLSPruningModel, _prepare_pgls_inputs
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["infer_node_states_pgls"]


def _scale_and_clamp_tree(tree: ToyTree, epsilon: float) -> ToyTree:
    """Return a root-height-scaled copy with clamped non-positive branch lengths."""
    work_tree = tree.mod.edges_scale_to_root_height(1.0)
    for node in work_tree:
        if node._dist <= 0:
            node._dist = float(epsilon)
    work_tree._update()
    return work_tree


def _get_unique_name_to_idx(tree: ToyTree) -> dict[str, int]:
    """Return a unique node-name map; raise if non-empty names are duplicated."""
    out: dict[str, int] = {}
    dups: set[str] = set()
    for node in tree:
        if not node.name:
            continue
        if node.name in out:
            dups.add(node.name)
        else:
            out[node.name] = node.idx
    if dups:
        raise ToytreeError(
            "Cannot align node-indexed data by name because tree node names are "
            f"not unique. Duplicates include: {sorted(dups)[:5]}"
        )
    return out


def _coerce_node_dataframe(tree: ToyTree, data: pd.DataFrame) -> pd.DataFrame:
    """Align a tip-only or full-node DataFrame to integer node idx labels."""
    if not isinstance(data, pd.DataFrame):
        raise ToytreeError("data must be a pandas DataFrame when provided.")
    if not data.index.is_unique:
        raise ToytreeError("data index must be unique.")

    nnodes = tree.nnodes
    idx = data.index
    frame = data.copy()
    is_int_index = isinstance(idx, pd.RangeIndex) or (
        hasattr(idx, "dtype") and np.issubdtype(idx.dtype, np.integer)
    )
    if is_int_index:
        vals = pd.Index(idx).astype(int)
        bad = [i for i in vals if i < 0 or i >= nnodes]
        if bad:
            raise ToytreeError("data index contains invalid node idx labels.")
        frame.index = vals
        return frame

    name_to_idx = _get_unique_name_to_idx(tree)
    try:
        new_index = [name_to_idx[str(i)] for i in idx]
    except KeyError as exc:
        raise ToytreeError(
            "Could not align data index to node names on the tree."
        ) from exc
    frame.index = pd.Index(new_index, dtype=int)
    return frame


def _validate_formula_complete_on_rows(formula: str, node_df: pd.DataFrame) -> None:
    """Raise if any provided rows have missing values in formula columns."""
    if node_df.empty:
        raise ToytreeError("data must include at least one row.")
    try:
        ymat, xmat = dmatrices(formula, data=node_df, return_type="dataframe")
    except PatsyError as exc:
        raise ToytreeError(
            "Invalid formula or data for infer_node_states_pgls: " f"{exc}"
        ) from exc
    if ymat.shape[0] != node_df.shape[0] or xmat.shape[0] != node_df.shape[0]:
        raise ToytreeError(
            "When data is provided to infer_node_states_pgls, rows must not have "
            "missing values in any formula columns."
        )


def _coerce_node_series_from_source(
    tree: ToyTree,
    source_df: pd.DataFrame | None,
    key: str,
) -> pd.Series:
    """Return all-node series from DataFrame-only source or tree features."""
    out = pd.Series(np.nan, index=range(tree.nnodes), dtype=float, name=key)
    if source_df is not None:
        if key not in source_df.columns:
            raise ToytreeError(
                f"Column '{key}' is required in data for infer_node_states_pgls."
            )
        vals = pd.to_numeric(source_df[key], errors="coerce")
        out.loc[vals.index] = vals.to_numpy(dtype=float)
        return out
    ser = tree.get_node_data(key, missing=np.nan)
    ser = pd.to_numeric(ser, errors="coerce")
    ser.index = range(tree.nnodes)
    return ser


def _get_all_node_predictor_source_df(
    tree: ToyTree,
    source_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """Return an all-node predictor table preserving categorical dtypes."""
    if source_df is not None:
        # In data-provided mode we must not fall back to tree values.
        return source_df.reindex(range(tree.nnodes))

    # Tree-sourced mode preserves raw categorical values for Patsy coding.
    all_df = tree.get_node_data()
    if "idx" in all_df.columns:
        all_df = all_df.set_index("idx")
    if not np.issubdtype(all_df.index.dtype, np.integer):
        all_df.index = pd.Index(range(tree.nnodes), dtype=int)
    return all_df.reindex(range(tree.nnodes))


def _reconstruct_node_design_matrix(
    xmat_fit: pd.DataFrame,
    node_predictors: pd.DataFrame,
) -> pd.DataFrame:
    """Rebuild fitted Patsy design rows on nodes using original design_info."""
    if _contains_probabilistic_categorical_values(
        xmat_fit.design_info,
        node_predictors,
    ):
        return _reconstruct_node_design_matrix_with_cat_probs(xmat_fit, node_predictors)
    try:
        xnodes = build_design_matrices(
            [xmat_fit.design_info],
            node_predictors,
            return_type="dataframe",
            NA_action=NAAction(on_NA="raise"),
        )[0]
    except Exception as exc:
        raise ToytreeError(
            "Failed to reconstruct predictor design rows on nodes for "
            "infer_node_states_pgls."
        ) from exc
    if list(xnodes.columns) != list(xmat_fit.columns):
        raise ToytreeError(
            "Reconstructed node predictor design columns do not match the "
            "fitted PGLS design columns."
        )
    xnodes.index = pd.Index(range(node_predictors.shape[0]), dtype=int)
    return xnodes


def _contains_probabilistic_categorical_values(
    design_info,
    node_predictors: pd.DataFrame,
) -> bool:
    """Return True if any categorical predictor cell stores a probability vector."""
    for factor, info in design_info.factor_infos.items():
        if info.type != "categorical":
            continue
        col = _get_raw_factor_column_name(factor.name())
        if col is None or col not in node_predictors.columns:
            continue
        ser = node_predictors[col]
        for val in ser.to_numpy(dtype=object):
            if _is_prob_vector(val):
                return True
    return False


def _get_raw_factor_column_name(factor_name: str) -> str | None:
    """Return a raw column name for simple Patsy factors, else None."""
    if factor_name.startswith("C(") and factor_name.endswith(")"):
        inner = factor_name[2:-1].strip()
        # Support the common simple form C(x). More complex formulas (e.g.,
        # custom contrasts or transformed factors) fall back to tree-only mode.
        if "," in inner or inner.startswith(("Q(", "I(")):
            return None
        return inner
    # Simple numeric factor names map directly to columns.
    if factor_name.isidentifier():
        return factor_name
    return None


def _is_prob_vector(value: object) -> bool:
    """Return True for tuple/list/array-like probability vectors (not strings)."""
    if value is None or isinstance(value, (str, bytes)):
        return False
    if isinstance(value, np.ndarray):
        return value.ndim == 1
    if isinstance(value, (tuple, list)):
        return True
    return False


def _coerce_categorical_probabilities(
    values: pd.Series,
    categories: tuple[object, ...],
) -> np.ndarray:
    """Return row-wise category probabilities from exact states or prob vectors."""
    nrows = values.shape[0]
    ncat = len(categories)
    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    out = np.full((nrows, ncat), np.nan, dtype=float)

    for i, val in enumerate(values.to_numpy(dtype=object)):
        if _is_prob_vector(val):
            arr = np.asarray(val, dtype=float).reshape(-1)
            if arr.shape[0] != ncat:
                raise ToytreeError(
                    "Categorical predictor probability vectors must have length "
                    f"{ncat} to match fitted category order {categories}."
                )
            if np.any(~np.isfinite(arr)) or np.any(arr < 0):
                raise ToytreeError(
                    "Categorical predictor probability vectors must be finite "
                    "and non-negative."
                )
            s = float(arr.sum())
            if not np.isclose(s, 1.0, atol=1e-6):
                raise ToytreeError(
                    "Categorical predictor probability vectors must sum to 1."
                )
            out[i] = arr
            continue
        if pd.isna(val):
            continue

        # Interpret exact states in this predictor's fitted category order only.
        if val not in cat_to_idx:
            raise ToytreeError(
                f"Categorical predictor value {val!r} is not among fitted "
                f"categories {categories}."
            )
        out[i] = 0.0
        out[i, cat_to_idx[val]] = 1.0

    return out


def _rowwise_kron(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return row-wise Kronecker product for two design component matrices."""
    return (a[:, :, None] * b[:, None, :]).reshape(a.shape[0], a.shape[1] * b.shape[1])


def _reconstruct_node_design_matrix_with_cat_probs(
    xmat_fit: pd.DataFrame,
    node_predictors: pd.DataFrame,
) -> pd.DataFrame:
    """Rebuild node design rows allowing categorical probability vectors.

    This supports exact categorical states and probability vectors (tuple/list/
    array) for simple ``C(var)`` factors by taking the expected coded design row
    under the provided category probabilities. More complex factor expressions
    fall back by raising ``ToytreeError`` so the caller can use residual-only
    inference.
    """
    di = xmat_fit.design_info
    nrows = node_predictors.shape[0]
    factor_infos = di.factor_infos
    factor_cache: dict[object, np.ndarray] = {}

    for factor, info in factor_infos.items():
        fname = factor.name()
        col = _get_raw_factor_column_name(fname)
        if col is None or col not in node_predictors.columns:
            raise ToytreeError(
                "Could not reconstruct node predictor design rows for a non-simple "
                f"formula factor: {fname!r}."
            )

        if info.type == "numerical":
            if getattr(info, "num_columns", 1) != 1:
                raise ToytreeError(
                    "Only single-column numeric predictors are currently "
                    "supported for node predictor reconstruction."
                )
            vals = pd.to_numeric(node_predictors[col], errors="coerce").to_numpy(
                dtype=float
            )
            if np.any(~np.isfinite(vals)):
                raise ToytreeError(
                    f"Numeric predictor '{col}' has missing/unusable node values."
                )
            factor_cache[factor] = vals[:, None]
            continue

        if info.type == "categorical":
            factor_cache[factor] = _coerce_categorical_probabilities(
                node_predictors[col], tuple(info.categories)
            )
            continue

        raise ToytreeError(
            f"Unsupported Patsy factor type for node inference: {info.type}"
        )

    col_blocks: list[np.ndarray] = []
    for term in di.terms:
        subterms = di.term_codings.get(term, [])
        for sub in subterms:
            block = np.ones((nrows, 1), dtype=float)
            for factor in sub.factors:
                comp = factor_cache[factor]
                if factor in sub.contrast_matrices:
                    # For probabilistic categorical states, expected coding is
                    # the probability-weighted average of contrast-coded rows for
                    # this predictor's fitted Patsy category order.
                    cmatrix = np.asarray(
                        sub.contrast_matrices[factor].matrix,
                        dtype=float,
                    )
                    comp = comp @ cmatrix
                block = _rowwise_kron(block, np.asarray(comp, dtype=float))
            col_blocks.append(block)

    if not col_blocks:
        raise ToytreeError("Failed to reconstruct node predictor design matrix.")
    xnodes_arr = np.concatenate(col_blocks, axis=1)
    if xnodes_arr.shape[1] != xmat_fit.shape[1]:
        raise ToytreeError(
            "Reconstructed node predictor design has a different number of columns "
            "than the fitted PGLS design."
        )
    xnodes = pd.DataFrame(
        xnodes_arr,
        columns=xmat_fit.columns,
        index=pd.Index(range(nrows), dtype=int),
    )
    return xnodes


def _coerce_node_stderr_series(
    tree: ToyTree,
    y_stderr: str | Mapping | pd.Series | None,
    source_df: pd.DataFrame | None,
) -> pd.Series:
    """Return all-node response standard errors aligned to integer node idx."""
    out = pd.Series(np.nan, index=range(tree.nnodes), dtype=float, name="y_stderr")
    if y_stderr is None:
        return out
    if isinstance(y_stderr, str):
        if source_df is not None:
            if y_stderr not in source_df.columns:
                raise ToytreeError(
                    f"Column '{y_stderr}' was requested as y_stderr but is not "
                    "present in the input data."
                )
            vals = pd.to_numeric(source_df[y_stderr], errors="coerce")
            out.loc[vals.index] = vals.to_numpy(dtype=float)
            return out
        ser = tree.get_node_data(y_stderr, missing=np.nan)
        ser = pd.to_numeric(ser, errors="coerce")
        ser.index = range(tree.nnodes)
        return ser

    if isinstance(y_stderr, pd.Series):
        idx = y_stderr.index
        is_int_index = isinstance(idx, pd.RangeIndex) or (
            hasattr(idx, "dtype") and np.issubdtype(idx.dtype, np.integer)
        )
        if is_int_index:
            vals = pd.to_numeric(y_stderr, errors="coerce")
            for k, v in vals.items():
                ik = int(k)
                if 0 <= ik < tree.nnodes:
                    out.iloc[ik] = v
            return out
        mapping = y_stderr.to_dict()
    elif isinstance(y_stderr, Mapping):
        mapping = y_stderr
    else:
        raise ToytreeError("y_stderr must be a str, Mapping, pandas Series, or None.")

    # Query expansion allows idx labels, names, and regex queries.
    emap = expand_node_mapping(tree, mapping)
    for node, value in emap.items():
        out.iloc[node.idx] = value
    return pd.to_numeric(out, errors="coerce")


def _validate_stderr_to_variance_all(y_stderr: pd.Series) -> pd.Series:
    """Validate all-node response standard errors and return variances."""
    arr = pd.to_numeric(y_stderr, errors="coerce").to_numpy(dtype=float)
    if np.any(np.isinf(arr)):
        raise ToytreeError("y_stderr values must be finite when provided.")
    bad = np.isfinite(arr) & (arr < 0)
    if np.any(bad):
        raise ToytreeError("y_stderr values must be non-negative.")
    arr = np.nan_to_num(arr, nan=0.0)
    return pd.Series(arr**2, index=y_stderr.index, name="obs_var")


def _all_node_bm_covariance(tree: ToyTree) -> np.ndarray:
    """Return all-node Brownian covariance shape matrix using node distances."""
    dmat = tree.distance.get_node_distance_matrix(topology_only=False)
    root_idx = tree.treenode.idx
    root_d = dmat[root_idx]
    # Shared path length from the root to the MRCA of each node pair.
    shared = 0.5 * (root_d[:, None] + root_d[None, :] - dmat)
    return np.clip(shared, 0.0, np.inf)


def _lambda_transform_allnodes(vcv: np.ndarray, lambda_: float) -> np.ndarray:
    """Apply Pagel's lambda to a full-node covariance shape matrix."""
    out = np.array(vcv, copy=True, dtype=float)
    mask = ~np.eye(out.shape[0], dtype=bool)
    out[mask] *= float(lambda_)
    return out


def _infer_with_dense_conditioning(
    prior_mean: np.ndarray,
    latent_cov: np.ndarray,
    obs_values: np.ndarray,
    obs_var: np.ndarray,
    epsilon: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Condition a latent Gaussian vector on noisy observations."""
    obs_mask = np.isfinite(obs_values)
    obs_idx = np.where(obs_mask)[0]
    if obs_idx.size == 0:
        raise ToytreeError(
            "No observed response values are available for node inference."
        )

    mu0 = np.asarray(prior_mean, dtype=float)
    K = np.asarray(latent_cov, dtype=float)
    y = np.asarray(obs_values, dtype=float)
    Rdiag = np.asarray(obs_var, dtype=float)
    if np.any(~np.isfinite(Rdiag[obs_idx])) or np.any(Rdiag[obs_idx] < 0):
        raise ToytreeError("Observation variances must be finite and non-negative.")

    K_oo = K[np.ix_(obs_idx, obs_idx)]
    C_oo_base = K_oo.copy()
    C_oo_base.flat[:: C_oo_base.shape[0] + 1] += Rdiag[obs_idx]
    K_all_o = K[:, obs_idx]
    delta = y[obs_idx] - mu0[obs_idx]

    for jitter in (0.0, epsilon, epsilon * 10, epsilon * 100, 1e-8, 1e-6):
        C_oo = C_oo_base.copy()
        if jitter > 0:
            C_oo.flat[:: C_oo.shape[0] + 1] += jitter
        try:
            L = np.linalg.cholesky(C_oo)
        except np.linalg.LinAlgError:
            continue

        # Solve using Cholesky to avoid explicit matrix inversion in the
        # conditional Gaussian equations.
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, delta))
        mean = mu0 + K_all_o @ alpha
        solved_cross_t = np.linalg.solve(L.T, np.linalg.solve(L, K_all_o.T))
        var = np.diag(K - K_all_o @ solved_cross_t)
        return mean, np.clip(var, 0.0, np.inf)

    raise ToytreeError(
        "Failed to condition node states: observed covariance block is singular."
    )


def _emit_missing_predictor_warning(count: int) -> None:
    """Print the standardized missing-predictor warning to stderr."""
    print(
        "Warning: internal predictor node values are missing for "
        f"{count} node(s). infer_node_states_pgls is proceeding using only the "
        "tree (ignoring predictors in the formula). First infer node states for "
        "those predictors using an appropriate infer_node_state method in "
        "toytree to include predictor effects.",
        file=sys.stderr,
    )


@add_subpackage_method(PhyloCompAPI)
def infer_node_states_pgls(
    tree: ToyTree,
    formula: str,
    data: pd.DataFrame | None = None,
    lambda_: float | None = None,
    y_stderr: str | Mapping | pd.Series | None = None,
    use_internal_node_predictors: bool = True,
    warn_on_missing_predictors: bool = True,
    epsilon: float = 1e-12,
) -> dict[str, object]:
    """Fit Gaussian PGLS and infer response node states by Gaussian conditioning.

    Parameters
    ----------
    tree : ToyTree
        Rooted phylogeny with branch lengths.
    formula : str
        Patsy-style regression formula used to fit the Gaussian PGLS model.
    data : pandas.DataFrame or None, default=None
        Optional trait table. If provided, it is the only source of formula
        columns and rows must not contain missing values in any formula column.
        The table may include tips only or full node data and is aligned by
        integer node idx or unique node names.
    lambda_ : float or None, default=None
        Fixed Pagel's lambda or ``None`` to optimize lambda during fitting.
    y_stderr : str or Mapping or pandas.Series or None, default=None
        Standard error (SE) of observed response estimates. Values are squared
        internally to form observation variances (``SE**2``) for fitting and
        node-state conditioning.
    use_internal_node_predictors : bool, default=True
        If True, use internal-node predictor values when available. If any
        required internal predictor values are missing, inference falls back to
        tree-only / residual-only prediction.
    warn_on_missing_predictors : bool, default=True
        If True, print a warning to stderr when predictor fallback is used.
    epsilon : float, default=1e-12
        Positive floor for clamping branch lengths and numerical jitter.

    Returns
    -------
    dict[str, object]
        Dictionary with keys ``"model_fit"`` (a :class:`PCMPGLSResult`) and
        ``"data"`` (a DataFrame indexed by integer node idx containing inferred
        means, variances, and metadata columns).

    Raises
    ------
    ToytreeError
        If inputs are invalid, formula columns are missing when ``data`` is
        provided, ``y_stderr`` values are invalid, or Gaussian conditioning
        fails numerically.

    Notes
    -----
    Exact internal-node categorical predictor states are supported when Patsy
    can reconstruct node-level predictor design rows matching the fitted model.
    Categorical predictor probability inputs are also supported when entered as
    tuple/list/array values that sum to 1. Tuple order is defined separately
    for each categorical predictor by that predictor's fitted Patsy category
    order, and is unrelated to predictor order in the formula.
    """
    if data is not None:
        node_df = _coerce_node_dataframe(tree, data)
        _validate_formula_complete_on_rows(formula, node_df)
        fit_data = data
    else:
        node_df = None
        fit_data = None

    # Fit on the same scaled/clamped tree convention used by pgls so lambda and
    # sigma2 match the covariance used for node-state conditioning.
    fit_tree, ymat, xmat, y_obs_var = _prepare_pgls_inputs(
        tree=tree,
        formula=formula,
        data=fit_data,
        y_stderr=y_stderr,
        epsilon=epsilon,
    )
    fit_model = PCMPGLSPruningModel(
        fit_tree,
        ymat,
        xmat,
        y_obs_var=y_obs_var,
        epsilon=epsilon,
    )
    fit = fit_model.fit(lambda_=lambda_)

    infer_tree = _scale_and_clamp_tree(tree, epsilon=epsilon)
    response_name = fit.response_name

    # Response observations come only from `data` when provided; otherwise they
    # are read from tree node features.
    response_obs = _coerce_node_series_from_source(infer_tree, node_df, response_name)
    stderr_nodes = _coerce_node_stderr_series(infer_tree, y_stderr, node_df)
    obs_var_nodes = _validate_stderr_to_variance_all(stderr_nodes)

    # Build a node-level prior mean from predictors when possible by
    # reconstructing Patsy design rows on nodes. This supports exact
    # categorical predictor states when they are available on nodes.
    design_cols = list(fit.design_columns)
    non_intercept = [c for c in design_cols if c != "Intercept"]
    fallback_residual_only = False
    predictor_mean_available = pd.Series(
        True,
        index=range(infer_tree.nnodes),
        dtype=bool,
    )
    prior_mean = np.zeros(infer_tree.nnodes, dtype=float)
    if "Intercept" in fit.params.index:
        prior_mean[:] = float(fit.params["Intercept"])

    if non_intercept:
        can_use_predictors = bool(use_internal_node_predictors)
        predictor_source = _get_all_node_predictor_source_df(infer_tree, node_df)
        if not can_use_predictors:
            fallback_residual_only = True
            predictor_mean_available.loc[range(infer_tree.ntips, infer_tree.nnodes)] = (
                False
            )
        else:
            try:
                xnodes = _reconstruct_node_design_matrix(xmat, predictor_source)
                prior_mean = xnodes.to_numpy(dtype=float) @ fit.params.loc[
                    xnodes.columns
                ].to_numpy(dtype=float)
            except ToytreeError:
                fallback_residual_only = True
                predictor_mean_available.loc[
                    range(infer_tree.ntips, infer_tree.nnodes)
                ] = False

        if fallback_residual_only:
            if warn_on_missing_predictors and can_use_predictors:
                count = int((~predictor_mean_available).sum())
                _emit_missing_predictor_warning(
                    max(count, infer_tree.nnodes - infer_tree.ntips)
                )
            # Tree-only fallback ignores non-intercept predictor effects. Keep
            # the intercept as a constant mean term if present.
            predictor_mean_available.loc[:] = False
            if "Intercept" in fit.params.index:
                prior_mean[:] = float(fit.params["Intercept"])
            else:
                prior_mean[:] = 0.0

    # Build latent Gaussian covariance on all nodes and condition on observed
    # response states with optional observation variances.
    vcv_all = _all_node_bm_covariance(infer_tree)
    vcv_all = _lambda_transform_allnodes(vcv_all, fit.lambda_)
    latent_cov = float(fit.sigma2) * vcv_all

    obs_values = response_obs.to_numpy(dtype=float)
    obs_var = obs_var_nodes.to_numpy(dtype=float)
    mean, var = _infer_with_dense_conditioning(
        prior_mean=prior_mean,
        latent_cov=latent_cov,
        obs_values=obs_values,
        obs_var=obs_var,
        epsilon=float(epsilon),
    )

    observed = np.isfinite(obs_values)
    used_obs_var = np.full(infer_tree.nnodes, np.nan, dtype=float)
    used_obs_var[observed] = obs_var[observed]
    source = np.full(infer_tree.nnodes, "imputed", dtype=object)
    source[observed & (used_obs_var == 0)] = "observed_exact"
    source[observed & (used_obs_var > 0)] = "observed_noisy"

    # Exact observations should report exact latent states in the output table.
    exact_obs = observed & (used_obs_var == 0)
    mean[exact_obs] = obs_values[exact_obs]
    var[exact_obs] = 0.0

    out = pd.DataFrame(
        {
            "name": [infer_tree[i].name for i in range(infer_tree.nnodes)],
            "mean": mean,
            "variance": var,
            "observed": observed,
            "used_observation_variance": used_obs_var,
            "source": source,
            "predictor_mean_available": predictor_mean_available.to_numpy(dtype=bool),
            "fallback_residual_only": np.full(
                infer_tree.nnodes,
                bool(fallback_residual_only),
                dtype=bool,
            ),
        },
        index=pd.Index(range(infer_tree.nnodes), name="idx"),
    )
    return {"model_fit": fit, "data": out}
