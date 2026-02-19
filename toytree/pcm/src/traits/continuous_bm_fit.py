#!/usr/bin/env python

"""Fit univariate continuous-trait BM-family models on phylogenies.

This module fits BM, OU, and EB models to one continuous trait on a tree
using Gaussian likelihood with profiled intercept (`mu`) and rate (`sigma2`)
parameters. Model comparison is performed with AIC or AICc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional, Sequence, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.traits.aic_table import ModelResult, aic_table
from toytree.utils import ToytreeError

__all__ = [
    "fit_continuous_bm_model",
]


@dataclass
class FitContinuousModelResult(ModelResult):
    """Container for one fitted continuous-trait model."""

    model: str
    log_likelihood: float
    nparams: int
    nobs: int
    mu: float
    sigma2: float
    alpha: Optional[float]
    r: Optional[float]
    converged: bool
    optimizer_message: str
    anc_mean: pd.Series
    anc_var: pd.Series

    def __repr__(self) -> str:
        return (
            "FitContinuousModelResult(\n"
            f"  model={self.model}, nobs={self.nobs}, nparams={self.nparams}\n"
            f"  log_likelihood={self.log_likelihood:.6g}\n"
            f"  mu={self.mu:.6g}, sigma2={self.sigma2:.6g}, "
            f"alpha={self.alpha}, r={self.r}\n"
            f"  converged={self.converged}, message={self.optimizer_message!r}\n"
            ")"
        )


class ContinuousBMModelFit:
    """Fit BM-family continuous-trait models for one trait."""

    def __init__(
        self,
        tree,
        data: Union[str, pd.Series],
        models: Sequence[Literal["BM", "OU", "EB"]],
        alpha_bounds: tuple[float, float] = (1e-12, 20.0),
        r_bounds: tuple[float, float] = (-20.0, 20.0),
    ) -> None:
        self.tree = tree
        self.models = self._coerce_models(models)
        self.alpha_bounds = alpha_bounds
        self.r_bounds = r_bounds

        self.series = self._coerce_data(data)
        if isinstance(data, str):
            self.trait_name = str(data)
        else:
            self.trait_name = str(self.series.name if self.series.name else "trait")
        self.tip_values = self.series.iloc[: self.tree.ntips].to_numpy(dtype=float)
        self.nobs = int(self.tip_values.size)

        # Precompute root-times and shared-time matrices for tips/all nodes.
        self.root_idx = int(self.tree.treenode.idx)
        self.dmat = self.tree.distance.get_node_distance_matrix()
        self.t_all = self.dmat[:, self.root_idx].astype(float)
        self.t_tips = self.t_all[: self.tree.ntips]
        self.shared_tips = self._compute_shared_time_matrix(
            list(range(self.tree.ntips))
        )
        self.shared_all = self._compute_shared_time_matrix(
            list(range(self.tree.nnodes))
        )

    def _coerce_models(
        self, models: Sequence[Literal["BM", "OU", "EB"]]
    ) -> list[str]:
        if not models:
            raise ToytreeError("models cannot be empty.")
        out: list[str] = []
        for model in models:
            m = str(model).upper()
            if m not in {"BM", "OU", "EB"}:
                raise ToytreeError("models entries must be one of 'BM', 'OU', 'EB'.")
            if m not in out:
                out.append(m)
        return out

    def _coerce_data(self, data: Union[str, pd.Series]) -> pd.Series:
        """Coerce user input to all-node numeric Series indexed by node idx."""
        if isinstance(data, str):
            series = self.tree.get_node_data(data, missing=np.nan)
        elif isinstance(data, pd.Series):
            series = data.copy()
        else:
            raise ToytreeError("data must be a feature name (str) or pandas Series.")

        mapping = dict(series.dropna())
        mapping = expand_node_mapping(self.tree, mapping)
        arr = np.full(self.tree.nnodes, np.nan, dtype=float)
        for node, value in mapping.items():
            try:
                arr[node._idx] = float(value)
            except Exception as exc:
                raise ToytreeError("continuous trait values must be numeric.") from exc

        out = pd.Series(arr, index=range(self.tree.nnodes), name=series.name)
        if out.iloc[: self.tree.ntips].isna().any():
            raise ToytreeError("tip trait values cannot be missing for model fitting.")
        return out

    def _compute_shared_time_matrix(self, node_indices: list[int]) -> np.ndarray:
        """Return matrix of root-to-MRCA shared times for selected nodes."""
        n = len(node_indices)
        shared = np.zeros((n, n), dtype=float)
        for i in range(n):
            ni = node_indices[i]
            shared[i, i] = self.t_all[ni]
            for j in range(i + 1, n):
                nj = node_indices[j]
                mrca = self.tree.get_mrca_node(ni, nj)
                st = float(self.dmat[mrca.idx, self.root_idx])
                shared[i, j] = st
                shared[j, i] = st
        return shared

    def _kernel_bm(self, shared: np.ndarray) -> np.ndarray:
        return shared.copy()

    def _kernel_ou(self, shared: np.ndarray, times: np.ndarray, alpha: float) -> np.ndarray:
        if alpha <= 0:
            return shared.copy()
        ti = times[:, None]
        tj = times[None, :]
        return np.exp(-alpha * (ti + tj - 2.0 * shared)) * (
            (1.0 - np.exp(-2.0 * alpha * shared)) / (2.0 * alpha)
        )

    def _kernel_eb(self, shared: np.ndarray, r: float) -> np.ndarray:
        if np.isclose(r, 0.0):
            return shared.copy()
        return (np.exp(r * shared) - 1.0) / r

    def _stable_profiled_fit(self, y: np.ndarray, R: np.ndarray) -> dict[str, float]:
        """Profile mu and sigma2 from covariance shape matrix R."""
        n = y.size
        ones = np.ones(n, dtype=float)
        base = np.array(R, dtype=float, copy=True)
        if np.any(~np.isfinite(base)):
            raise ToytreeError("covariance kernel contains non-finite values.")

        # Add diagonal jitter progressively until Cholesky succeeds.
        for jitter in (0.0, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4):
            C = base.copy()
            if jitter > 0:
                C.flat[:: C.shape[0] + 1] += jitter
            try:
                L = np.linalg.cholesky(C)
                break
            except np.linalg.LinAlgError:
                L = None
        if L is None:
            raise ToytreeError("failed to factor covariance matrix (non-PD).")

        def solve(v: np.ndarray) -> np.ndarray:
            return np.linalg.solve(L.T, np.linalg.solve(L, v))

        Rinv_y = solve(y)
        Rinv_1 = solve(ones)
        den = float(ones @ Rinv_1)
        if den <= 0 or not np.isfinite(den):
            raise ToytreeError("invalid denominator while profiling mu.")

        mu = float((ones @ Rinv_y) / den)
        res = y - mu
        quad = float(res @ solve(res))
        quad = max(quad, 1e-15)
        sigma2 = max(quad / n, 1e-15)
        logdetR = float(2.0 * np.log(np.diag(L)).sum())
        loglik = -0.5 * (
            n * np.log(2.0 * np.pi) + n * np.log(sigma2) + logdetR + n
        )
        return {"mu": mu, "sigma2": sigma2, "loglik": float(loglik)}

    def _fit_bm(self) -> tuple[dict[str, float], bool, str]:
        R = self._kernel_bm(self.shared_tips)
        fit = self._stable_profiled_fit(self.tip_values, R)
        return fit, True, "closed-form"

    def _fit_ou(self) -> tuple[dict[str, float], bool, str, float]:
        lo, hi = self.alpha_bounds

        def objective(alpha: float) -> float:
            try:
                R = self._kernel_ou(self.shared_tips, self.t_tips, alpha)
                return -self._stable_profiled_fit(self.tip_values, R)["loglik"]
            except Exception:
                return np.inf

        res = minimize_scalar(objective, bounds=(lo, hi), method="bounded")
        alpha_hat = float(res.x)
        R = self._kernel_ou(self.shared_tips, self.t_tips, alpha_hat)
        fit = self._stable_profiled_fit(self.tip_values, R)
        return fit, bool(res.success), str(res.message), alpha_hat

    def _fit_eb(self) -> tuple[dict[str, float], bool, str, float]:
        lo, hi = self.r_bounds

        def objective(r: float) -> float:
            try:
                R = self._kernel_eb(self.shared_tips, r)
                return -self._stable_profiled_fit(self.tip_values, R)["loglik"]
            except Exception:
                return np.inf

        res = minimize_scalar(objective, bounds=(lo, hi), method="bounded")
        r_hat = float(res.x)
        R = self._kernel_eb(self.shared_tips, r_hat)
        fit = self._stable_profiled_fit(self.tip_values, R)
        return fit, bool(res.success), str(res.message), r_hat

    def _compute_ancestral(
        self,
        model: str,
        mu: float,
        sigma2: float,
        alpha: Optional[float],
        r: Optional[float],
    ) -> tuple[pd.Series, pd.Series]:
        """Return all-node conditional means and variances."""
        # Build all-node covariance shape matrix for selected model.
        if model == "BM":
            R_all = self._kernel_bm(self.shared_all)
        elif model == "OU":
            a = 0.0 if alpha is None else float(alpha)
            R_all = self._kernel_ou(self.shared_all, self.t_all, a)
        else:
            rr = 0.0 if r is None else float(r)
            R_all = self._kernel_eb(self.shared_all, rr)

        C_all = sigma2 * R_all
        tips = np.arange(self.tree.ntips, dtype=int)
        ints = np.arange(self.tree.ntips, self.tree.nnodes, dtype=int)
        C_tt = C_all[np.ix_(tips, tips)]
        C_it = C_all[np.ix_(ints, tips)]
        C_ii = C_all[np.ix_(ints, ints)]

        # Stabilize tip block before conditional Gaussian algebra.
        L = None
        C_tt_base = np.array(C_tt, copy=True)
        for jitter in (0.0, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4):
            Cw = C_tt_base.copy()
            if jitter > 0:
                Cw.flat[:: Cw.shape[0] + 1] += jitter
            try:
                L = np.linalg.cholesky(Cw)
                C_tt = Cw
                break
            except np.linalg.LinAlgError:
                continue
        if L is None:
            raise ToytreeError("failed to condition ancestral states: tip covariance not PD.")

        def solve(v: np.ndarray) -> np.ndarray:
            return np.linalg.solve(L.T, np.linalg.solve(L, v))

        y_t = self.tip_values
        delta = y_t - mu
        cond_mean_int = mu + C_it @ solve(delta)
        cond_cov_int = C_ii - C_it @ solve(C_it.T)
        cond_var_int = np.clip(np.diag(cond_cov_int), 0.0, np.inf)

        all_mean = np.full(self.tree.nnodes, np.nan, dtype=float)
        all_var = np.full(self.tree.nnodes, np.nan, dtype=float)
        all_mean[tips] = y_t
        all_var[tips] = 0.0
        all_mean[ints] = cond_mean_int
        all_var[ints] = cond_var_int
        return (
            pd.Series(all_mean, index=range(self.tree.nnodes), name="anc_mean"),
            pd.Series(all_var, index=range(self.tree.nnodes), name="anc_var"),
        )

    def fit(self) -> dict[str, FitContinuousModelResult]:
        """Fit selected models and return model -> result mapping."""
        out: dict[str, FitContinuousModelResult] = {}
        for model in self.models:
            if model == "BM":
                fit, converged, msg = self._fit_bm()
                alpha = None
                r = None
                nparams = 2
            elif model == "OU":
                fit, converged, msg, alpha = self._fit_ou()
                r = None
                nparams = 3
            else:
                fit, converged, msg, r = self._fit_eb()
                alpha = None
                nparams = 3

            anc_mean, anc_var = self._compute_ancestral(
                model=model,
                mu=fit["mu"],
                sigma2=fit["sigma2"],
                alpha=alpha,
                r=r,
            )
            out[model] = FitContinuousModelResult(
                model=model,
                log_likelihood=float(fit["loglik"]),
                nparams=int(nparams),
                nobs=int(self.nobs),
                mu=float(fit["mu"]),
                sigma2=float(fit["sigma2"]),
                alpha=None if alpha is None else float(alpha),
                r=None if r is None else float(r),
                converged=bool(converged),
                optimizer_message=str(msg),
                anc_mean=anc_mean,
                anc_var=anc_var,
            )
        return out


@add_subpackage_method(PhyloCompAPI)
def fit_continuous_bm_model(
    tree,
    data: Union[str, pd.Series],
    models: Sequence[Literal["BM", "OU", "EB"]] = ("BM", "OU", "EB"),
    inplace: bool = False,
    alpha_bounds: tuple[float, float] = (1e-12, 20.0),
    r_bounds: tuple[float, float] = (-20.0, 20.0),
    criterion: Literal["AIC", "AICc"] = "AICc",
    store_prefix: Optional[str] = None,
) -> Dict[str, object]:
    """Fit BM-family models to one continuous trait and select best by AIC/AICc.

    Returns
    -------
    dict
        Dict with keys:
        - "best_fit": FitContinuousModelResult
        - "model_fits": dict[str, FitContinuousModelResult]
        - "model_table": pandas.DataFrame
        - "data": pandas.DataFrame with best-model ancestral estimates
        - "tree": ToyTree (same object if inplace=True, copy otherwise)
    """
    fitter = ContinuousBMModelFit(
        tree=tree,
        data=data,
        models=models,
        alpha_bounds=alpha_bounds,
        r_bounds=r_bounds,
    )
    model_fits = fitter.fit()
    table = aic_table(
        list(model_fits.values()),
        nobs=fitter.nobs,
        rank_by=criterion,
    )
    best_model = str(table.iloc[0]["model"])
    best_fit = model_fits[best_model]
    prefix = store_prefix if store_prefix is not None else fitter.trait_name

    out_df = pd.DataFrame(index=range(tree.nnodes))
    out_df[f"{prefix}_anc"] = best_fit.anc_mean
    out_df[f"{prefix}_anc_var"] = best_fit.anc_var

    target_tree = tree if inplace else tree.copy()
    target_tree.set_node_data(
        f"{prefix}_anc",
        dict(out_df[f"{prefix}_anc"].dropna()),
        default=np.nan,
        inplace=True,
    )
    target_tree.set_node_data(
        f"{prefix}_anc_var",
        dict(out_df[f"{prefix}_anc_var"].dropna()),
        default=np.nan,
        inplace=True,
    )
    return {
        "best_fit": best_fit,
        "model_fits": model_fits,
        "model_table": table,
        "data": out_df,
        "tree": target_tree,
    }
