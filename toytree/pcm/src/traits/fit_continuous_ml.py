#!/usr/bin/env python

"""Maximum-likelihood fitting and node-state inference for continuous traits.

This module provides two user-facing functions for univariate Gaussian
comparative models on a phylogeny:

1. ``fit_continuous_ml`` fits one or more candidate models (BM, OU, EB)
   to observed tip trait values.
2. ``infer_ancestral_states_continuous_ml`` fits one selected model and
   computes conditional node-state means/variances.

All models profile the intercept (``mu``) and diffusion rate (``sigma2``)
from a model-specific covariance kernel. OU and EB additionally optimize a
single scalar parameter (``alpha`` or ``r``) by bounded 1-D search.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.pcm.src.traits.aic_table import ModelResult, aic_table
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = [
    "fit_continuous_ml",
    "infer_ancestral_states_continuous_ml",
    "ContinuousMLModelFit",
    "FitContinuousMLResult",
]


@dataclass
class FitContinuousMLResult(ModelResult):
    """Container for one fitted continuous-trait model.

    Parameters
    ----------
    model : str
        Model name (``"BM"``, ``"OU"``, or ``"EB"``).
    log_likelihood : float
        Maximized log-likelihood for this model.
    nparams : int
        Number of fitted parameters used for information criteria.
    nobs : int
        Number of observed tip values.
    mu : float
        Profiled intercept estimate.
    sigma2 : float
        Profiled diffusion rate estimate.
    alpha : float or None
        OU alpha estimate, else ``None``.
    r : float or None
        EB rate-trend estimate, else ``None``.
    converged : bool
        Optimization convergence flag (always True for BM closed-form).
    optimizer_message : str
        Optimizer status message.
    """

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

    def __repr__(self) -> str:
        """Return a concise text summary of one model fit."""
        return (
            "FitContinuousMLResult(\n"
            f"  model={self.model}, nobs={self.nobs}, nparams={self.nparams}\n"
            f"  log_likelihood={self.log_likelihood:.6g}\n"
            f"  mu={self.mu:.6g}, sigma2={self.sigma2:.6g}, "
            f"alpha={self.alpha}, r={self.r}\n"
            f"  converged={self.converged}, message={self.optimizer_message!r}\n"
            ")"
        )


class ContinuousMLModelFit:
    """Fit BM/OU/EB models for a single continuous trait.

    Parameters
    ----------
    tree : ToyTree
        Input phylogeny with branch lengths.
    data : str or pandas.Series
        Trait data as a tree feature name or a Series keyed by node idx/names.
        Tip values must be present for all tips.
    bounds_alpha : tuple[float, float], default=(1e-12, 20.0)
        Search bounds for OU alpha.
    bounds_r : tuple[float, float], default=(-20.0, 20.0)
        Search bounds for EB r.
    """

    def __init__(
        self,
        tree: ToyTree,
        data: Union[str, pd.Series],
        bounds_alpha: tuple[float, float] = (1e-12, 20.0),
        bounds_r: tuple[float, float] = (-20.0, 20.0),
    ) -> None:
        self.tree = tree
        self.bounds_alpha = bounds_alpha
        self.bounds_r = bounds_r

        self.series = self._coerce_data(data)
        if isinstance(data, str):
            self.trait_name = str(data)
        else:
            self.trait_name = str(self.series.name if self.series.name else "trait")

        self.tip_values = self.series.iloc[: self.tree.ntips].to_numpy(dtype=float)
        self.nobs = int(self.tip_values.size)

        # Precompute times/shared-times once because every model kernel uses them.
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

    def _coerce_model(self, model: Optional[Literal["BM", "OU", "EB"]]) -> str:
        """Validate and normalize a single model name."""
        if model is None:
            raise ToytreeError("model cannot be None in single-model fitting context.")
        m = str(model).upper()
        if m not in {"BM", "OU", "EB"}:
            raise ToytreeError("model must be one of 'BM', 'OU', or 'EB'.")
        return m

    def _coerce_data(self, data: Union[str, pd.Series]) -> pd.Series:
        """Coerce trait input to an all-node float Series indexed by node idx."""
        if isinstance(data, str):
            series = self.tree.get_node_data(data, missing=np.nan)
        elif isinstance(data, pd.Series):
            series = data.copy()
        else:
            raise ToytreeError("data must be a feature name (str) or pandas Series.")

        # Expand mixed node queries (idx/name/regex) into canonical Node keys.
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
        """Return root-to-MRCA shared-time matrix for selected node indices."""
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
        """Return BM covariance shape kernel."""
        return shared.copy()

    def _kernel_ou(
        self,
        shared: np.ndarray,
        times: np.ndarray,
        alpha: float,
    ) -> np.ndarray:
        """Return OU covariance shape kernel with scalar alpha."""
        if alpha <= 0:
            return shared.copy()
        ti = times[:, None]
        tj = times[None, :]
        return np.exp(-alpha * (ti + tj - 2.0 * shared)) * (
            (1.0 - np.exp(-2.0 * alpha * shared)) / (2.0 * alpha)
        )

    def _kernel_eb(self, shared: np.ndarray, r: float) -> np.ndarray:
        """Return EB covariance shape kernel with scalar rate trend r."""
        if np.isclose(r, 0.0):
            return shared.copy()
        return (np.exp(r * shared) - 1.0) / r

    def _stable_profiled_fit(
        self,
        y: np.ndarray,
        kernel: np.ndarray,
    ) -> dict[str, float]:
        """Profile ``mu`` and ``sigma2`` from a covariance shape kernel.

        Parameters
        ----------
        y : np.ndarray
            Observed tip trait vector.
        kernel : np.ndarray
            Positive-semidefinite covariance shape matrix before sigma2 scaling.

        Returns
        -------
        dict[str, float]
            Dictionary with keys ``mu``, ``sigma2``, and ``loglik``.

        Raises
        ------
        ToytreeError
            If covariance factorization is numerically unstable.
        """
        n = y.size
        ones = np.ones(n, dtype=float)
        base = np.array(kernel, dtype=float, copy=True)
        if np.any(~np.isfinite(base)):
            raise ToytreeError("covariance kernel contains non-finite values.")

        # Add progressively larger diagonal jitter to stabilize near-singular
        # kernels while preserving the intended covariance shape as much as possible.
        L = None
        for jitter in (0.0, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4):
            cov = base.copy()
            if jitter > 0:
                cov.flat[:: cov.shape[0] + 1] += jitter
            try:
                L = np.linalg.cholesky(cov)
                break
            except np.linalg.LinAlgError:
                continue
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
        # Floor very small numerical negatives to keep sigma2/loglik finite.
        quad = max(quad, 1e-15)
        sigma2 = max(quad / n, 1e-15)
        logdet_r = float(2.0 * np.log(np.diag(L)).sum())
        loglik = -0.5 * (n * np.log(2.0 * np.pi) + n * np.log(sigma2) + logdet_r + n)
        return {"mu": mu, "sigma2": sigma2, "loglik": float(loglik)}

    def _fit_bm(self) -> tuple[dict[str, float], bool, str]:
        """Fit BM by direct profiled likelihood evaluation."""
        kernel = self._kernel_bm(self.shared_tips)
        fit = self._stable_profiled_fit(self.tip_values, kernel)
        return fit, True, "closed-form"

    def _fit_ou(self) -> tuple[dict[str, float], bool, str, float]:
        """Fit OU by bounded scalar optimization over alpha."""
        lo, hi = self.bounds_alpha

        def objective(alpha: float) -> float:
            try:
                kernel = self._kernel_ou(self.shared_tips, self.t_tips, alpha)
                return -self._stable_profiled_fit(self.tip_values, kernel)["loglik"]
            except Exception:
                # Numerical failures at this alpha are treated as invalid space.
                return np.inf

        res = minimize_scalar(objective, bounds=(lo, hi), method="bounded")
        alpha_hat = float(res.x)
        kernel = self._kernel_ou(self.shared_tips, self.t_tips, alpha_hat)
        fit = self._stable_profiled_fit(self.tip_values, kernel)
        return fit, bool(res.success), str(res.message), alpha_hat

    def _fit_eb(self) -> tuple[dict[str, float], bool, str, float]:
        """Fit EB by bounded scalar optimization over r."""
        lo, hi = self.bounds_r

        def objective(r: float) -> float:
            try:
                kernel = self._kernel_eb(self.shared_tips, r)
                return -self._stable_profiled_fit(self.tip_values, kernel)["loglik"]
            except Exception:
                # Numerical failures at this r are treated as invalid space.
                return np.inf

        res = minimize_scalar(objective, bounds=(lo, hi), method="bounded")
        r_hat = float(res.x)
        kernel = self._kernel_eb(self.shared_tips, r_hat)
        fit = self._stable_profiled_fit(self.tip_values, kernel)
        return fit, bool(res.success), str(res.message), r_hat

    def _build_model_result(
        self,
        model: Literal["BM", "OU", "EB"],
        fit: dict[str, float],
        converged: bool,
        message: str,
        alpha: Optional[float],
        r: Optional[float],
    ) -> FitContinuousMLResult:
        """Build a typed model result object from numeric fit outputs."""
        nparams = 2 if model == "BM" else 3
        return FitContinuousMLResult(
            model=model,
            log_likelihood=float(fit["loglik"]),
            nparams=int(nparams),
            nobs=int(self.nobs),
            mu=float(fit["mu"]),
            sigma2=float(fit["sigma2"]),
            alpha=None if alpha is None else float(alpha),
            r=None if r is None else float(r),
            converged=bool(converged),
            optimizer_message=str(message),
        )

    def fit_one(self, model: Literal["BM", "OU", "EB"]) -> FitContinuousMLResult:
        """Fit one selected model and return its ML estimates."""
        model = self._coerce_model(model)
        if model == "BM":
            fit, converged, message = self._fit_bm()
            alpha = None
            r = None
        elif model == "OU":
            fit, converged, message, alpha = self._fit_ou()
            r = None
        else:
            fit, converged, message, r = self._fit_eb()
            alpha = None
        return self._build_model_result(
            model=model,
            fit=fit,
            converged=converged,
            message=message,
            alpha=alpha,
            r=r,
        )

    def fit_all(self) -> dict[str, FitContinuousMLResult]:
        """Fit BM, OU, and EB and return results keyed by model name."""
        return {m: self.fit_one(m) for m in ("BM", "OU", "EB")}

    def _infer_node_states(
        self,
        model_fit: FitContinuousMLResult,
    ) -> tuple[pd.Series, pd.Series]:
        """Infer conditional node means and variances from one fitted model.

        Parameters
        ----------
        model_fit : FitContinuousMLResult
            A fitted model result containing ``model``, ``mu``, ``sigma2``, and
            optional ``alpha``/``r`` parameters.

        Returns
        -------
        tuple[pandas.Series, pandas.Series]
            ``(anc_mean, anc_var)`` vectors for all nodes in node-index order.
        """
        if model_fit.model == "BM":
            r_all = self._kernel_bm(self.shared_all)
        elif model_fit.model == "OU":
            alpha = 0.0 if model_fit.alpha is None else float(model_fit.alpha)
            r_all = self._kernel_ou(self.shared_all, self.t_all, alpha)
        else:
            rate = 0.0 if model_fit.r is None else float(model_fit.r)
            r_all = self._kernel_eb(self.shared_all, rate)

        c_all = float(model_fit.sigma2) * r_all
        tips = np.arange(self.tree.ntips, dtype=int)
        ints = np.arange(self.tree.ntips, self.tree.nnodes, dtype=int)

        # Partition total covariance into observed tips (tt), internal-vs-tip (it),
        # and internal-only (ii) blocks for Gaussian conditioning.
        c_tt = c_all[np.ix_(tips, tips)]
        c_it = c_all[np.ix_(ints, tips)]
        c_ii = c_all[np.ix_(ints, ints)]

        # Re-factor the tip block with diagonal jitter. This keeps conditioning
        # numerically stable when c_tt is near-singular.
        L = None
        c_tt_base = np.array(c_tt, copy=True)
        for jitter in (0.0, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4):
            c_work = c_tt_base.copy()
            if jitter > 0:
                c_work.flat[:: c_work.shape[0] + 1] += jitter
            try:
                L = np.linalg.cholesky(c_work)
                break
            except np.linalg.LinAlgError:
                continue
        if L is None:
            raise ToytreeError(
                "failed to condition node states: tip covariance is not PD."
            )

        def solve(v: np.ndarray) -> np.ndarray:
            return np.linalg.solve(L.T, np.linalg.solve(L, v))

        y_t = self.tip_values
        mu = float(model_fit.mu)
        delta = y_t - mu

        # Conditional Gaussian formulas:
        # E[X_i | X_t] = mu + C_it C_tt^{-1}(y_t - mu)
        # Var[X_i | X_t] = C_ii - C_it C_tt^{-1} C_ti
        cond_mean_int = mu + c_it @ solve(delta)
        cond_cov_int = c_ii - c_it @ solve(c_it.T)
        cond_var_int = np.clip(np.diag(cond_cov_int), 0.0, np.inf)

        all_mean = np.full(self.tree.nnodes, np.nan, dtype=float)
        all_var = np.full(self.tree.nnodes, np.nan, dtype=float)

        # Tip observations are treated as hard constraints in conditioning.
        all_mean[tips] = y_t
        all_var[tips] = 0.0
        all_mean[ints] = cond_mean_int
        all_var[ints] = cond_var_int

        return (
            pd.Series(all_mean, index=range(self.tree.nnodes), name="anc_mean"),
            pd.Series(all_var, index=range(self.tree.nnodes), name="anc_var"),
        )


@add_subpackage_method(PhyloCompAPI)
def fit_continuous_ml(
    tree: ToyTree,
    data: Union[str, pd.Series],
    model: Optional[Literal["BM", "OU", "EB"]] = None,
    bounds_alpha: tuple[float, float] = (1e-12, 20.0),
    bounds_r: tuple[float, float] = (-20.0, 20.0),
) -> FitContinuousMLResult | dict[str, object]:
    """Fit continuous-trait ML models and optionally perform model selection.

    Parameters
    ----------
    tree : ToyTree
        Phylogeny with branch lengths.
    data : str or pandas.Series
        Trait input as a tree feature name or a Series keyed by node idx/name.
    model : {"BM", "OU", "EB"} or None, default=None
        If None, fit BM/OU/EB and return model-selection results ranked by
        AICc. If a model name is provided, fit only that model.
    bounds_alpha : tuple[float, float], default=(1e-12, 20.0)
        OU alpha optimization bounds.
    bounds_r : tuple[float, float], default=(-20.0, 20.0)
        EB r optimization bounds.

    Returns
    -------
    FitContinuousMLResult or dict[str, object]
        If ``model`` is provided, returns one ``FitContinuousMLResult``.
        If ``model`` is None, returns
        ``{"model_fits": dict[str, FitContinuousMLResult], "model_table": DataFrame}``.

    Raises
    ------
    ToytreeError
        If inputs are invalid or covariance operations fail numerically.
    """
    fitter = ContinuousMLModelFit(
        tree=tree,
        data=data,
        bounds_alpha=bounds_alpha,
        bounds_r=bounds_r,
    )
    if model is None:
        model_fits = fitter.fit_all()
        table = aic_table(list(model_fits.values()), nobs=fitter.nobs, rank_by="AICc")
        return {
            "model_fits": model_fits,
            "model_table": table,
        }
    return fitter.fit_one(model)


@add_subpackage_method(PhyloCompAPI)
def infer_ancestral_states_continuous_ml(
    tree: ToyTree,
    data: Union[str, pd.Series],
    model: Literal["BM", "OU", "EB"] = "BM",
    bounds_alpha: tuple[float, float] = (1e-12, 20.0),
    bounds_r: tuple[float, float] = (-20.0, 20.0),
    inplace: bool = False,
) -> dict[str, object]:
    """Infer ancestral continuous states under one ML-fitted model.

    Parameters
    ----------
    tree : ToyTree
        Phylogeny with branch lengths.
    data : str or pandas.Series
        Trait input as a tree feature name or a Series keyed by node idx/name.
    model : {"BM", "OU", "EB"}, default="BM"
        Model to fit before ancestral-state inference.
    bounds_alpha : tuple[float, float], default=(1e-12, 20.0)
        OU alpha optimization bounds.
    bounds_r : tuple[float, float], default=(-20.0, 20.0)
        EB r optimization bounds.
    inplace : bool, default=False
        If True, write ``{trait}_anc`` and ``{trait}_anc_var`` features to the
        input tree.

    Returns
    -------
    dict[str, object]
        Dictionary with keys:

        - ``"model_fit"``: fitted ``FitContinuousMLResult``.
        - ``"data"``: ``pd.DataFrame`` with ``{trait}_anc`` and
          ``{trait}_anc_var`` columns for all nodes.

    Raises
    ------
    ToytreeError
        If inputs are invalid or covariance operations fail numerically.
    """
    fitter = ContinuousMLModelFit(
        tree=tree,
        data=data,
        bounds_alpha=bounds_alpha,
        bounds_r=bounds_r,
    )
    model_fit = fitter.fit_one(model)
    anc_mean, anc_var = fitter._infer_node_states(model_fit)

    out_df = pd.DataFrame(index=range(tree.nnodes))
    out_df[f"{fitter.trait_name}_anc"] = anc_mean
    out_df[f"{fitter.trait_name}_anc_var"] = anc_var

    if inplace:
        tree.set_node_data(
            f"{fitter.trait_name}_anc",
            dict(out_df[f"{fitter.trait_name}_anc"].dropna()),
            default=np.nan,
            inplace=True,
        )
        tree.set_node_data(
            f"{fitter.trait_name}_anc_var",
            dict(out_df[f"{fitter.trait_name}_anc_var"].dropna()),
            default=np.nan,
            inplace=True,
        )

    return {
        "model_fit": model_fit,
        "data": out_df,
    }
