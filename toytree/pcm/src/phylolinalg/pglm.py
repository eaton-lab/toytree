#!/usr/bin/env python

"""Pruning-based phylogenetic generalized linear models.

This module implements a phase-1 pruning-backed phylogenetic GLM API focused on
binary logistic regression. It follows a user-facing design similar to
``toytree.pcm.pgls`` while using the pruning algebra engine to avoid dense VCV
matrix calculations in the core weighted least-squares updates.

Current support fully implements binomial-logit, poisson-log,
negative-binomial-log, gamma-log, and beta-logit models. Gamma-inverse is
recognized and validated, but currently raises explicit ``NotImplemented``
errors after input validation.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import pandas as pd
from patsy import PatsyError, dmatrix
from scipy.optimize import minimize_scalar
from scipy.stats import norm

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.phylolinalg._glm_families import (
    GLMFamilySpec,
    _make_sm_family,
    get_family_spec,
)
from toytree.pcm.src.phylolinalg.pgls import PhyloPruningEngine, _max_lambda
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["PGLMResult", "PGLMPruningModel", "pglm"]


@dataclass
class PGLMResult:
    """Container for pruning-based phylogenetic GLM fit results."""

    params: pd.Series
    bse: pd.Series
    vcov: pd.DataFrame
    fittedvalues: pd.Series
    fitted_mean: pd.Series
    resid_response: pd.Series
    log_likelihood: float
    penalized_log_likelihood: float
    lambda_: float
    lambda_optimized: bool
    lambda_bounds: tuple[float, float]
    nobs: int
    response_name: str
    design_columns: list[str]
    converged: bool
    optimizer_message: str
    irls_iterations: int
    firth: bool
    family: str
    link: str
    dispersion_params: dict[str, float] | None = None
    dispersion_estimated: bool = False
    response_levels: tuple[str, str] | None = None
    response_transform: str | None = None
    response_transform_applied: bool = False
    response_transform_n: int = 0

    def _coef_table(self) -> pd.DataFrame:
        """Return a compact coefficient summary table for display."""
        coef = self.params.astype(float)
        se = self.bse.reindex(coef.index).astype(float)
        zvals = pd.Series(np.nan, index=coef.index, dtype=float)
        mask = se.to_numpy() != 0
        if np.any(mask):
            zvals.iloc[mask] = coef.iloc[mask] / se.iloc[mask]
        pvals = pd.Series(2.0 * norm.sf(np.abs(zvals.to_numpy())), index=coef.index)
        return pd.DataFrame({"coef": coef, "std err": se, "z": zvals, "p": pvals})

    def _pseudo_r_squared(self) -> float:
        """Return an Efron-style pseudo R-squared on the probability scale."""
        y = self.fitted_mean.to_numpy(dtype=float) + self.resid_response.to_numpy(
            dtype=float
        )
        p = self.fitted_mean.to_numpy(dtype=float)
        denom = np.sum((y - np.mean(y)) ** 2)
        if denom <= 0:
            return np.nan
        return float(1.0 - (np.sum((y - p) ** 2) / denom))

    @property
    def fitted_probabilities(self) -> pd.Series:
        """Return fitted response means (binomial-compatible alias)."""
        return self.fitted_mean

    @staticmethod
    def _fmt(value: Any) -> str:
        """Format scalar values compactly for text and HTML summaries."""
        if isinstance(value, (bool, np.bool_)):
            return str(bool(value))
        if value is None:
            return "None"
        try:
            if np.isscalar(value) and np.isfinite(value):
                return f"{float(value):.6g}"
        except Exception:
            pass
        return str(value)

    def __repr__(self) -> str:
        """Return a compact text summary."""
        lines = ["PGLMResult", "-" * 10]
        lines.append(
            f"response={self.response_name}  nobs={self.nobs}  "
            f"k_params={len(self.design_columns)}"
        )
        lines.append(
            f"family={self.family}  link={self.link}  "
            f"firth={self.firth}  iter={self.irls_iterations}"
        )
        lines.append(
            "lambda="
            f"{self._fmt(self.lambda_)}  optimized={self.lambda_optimized}  "
            f"bounds=({self._fmt(self.lambda_bounds[0])}, "
            f"{self._fmt(self.lambda_bounds[1])})"
        )
        lines.append(
            f"log_likelihood={self._fmt(self.log_likelihood)}  "
            "penalized_log_likelihood="
            f"{self._fmt(self.penalized_log_likelihood)}  "
            f"pseudo_R2={self._fmt(self._pseudo_r_squared())}  "
            f"converged={self.converged}"
        )
        if self.response_levels is not None:
            lines.append(f"response_levels={self.response_levels}")
        if self.response_transform_applied:
            lines.append(f"response_transform={self.response_transform}")
            lines.append(f"response_transform_n={self.response_transform_n}")
        if self.dispersion_params:
            lines.append(f"dispersion_params={self.dispersion_params}")
            lines.append(f"dispersion_estimated={self.dispersion_estimated}")
        if self.optimizer_message:
            lines.append(f"optimizer_message={self.optimizer_message}")
        lines.append("")
        lines.append("Coefficients")
        tbl = self._coef_table().copy()
        for col in tbl.columns:
            tbl[col] = tbl[col].map(self._fmt)
        lines.append(tbl.to_string())
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        """Return a notebook-friendly HTML summary."""
        tbl = self._coef_table().round(6)
        rows = [
            ("response", self.response_name),
            ("nobs", self.nobs),
            ("k_params", len(self.design_columns)),
            ("family", self.family),
            ("link", self.link),
            ("firth", self.firth),
            ("irls_iterations", self.irls_iterations),
            ("lambda", self._fmt(self.lambda_)),
            ("lambda_optimized", self.lambda_optimized),
            (
                "lambda_bounds",
                f"({self._fmt(self.lambda_bounds[0])}, "
                f"{self._fmt(self.lambda_bounds[1])})",
            ),
            ("log_likelihood", self._fmt(self.log_likelihood)),
            ("penalized_log_likelihood", self._fmt(self.penalized_log_likelihood)),
            ("pseudo_R2", self._fmt(self._pseudo_r_squared())),
            ("converged", self.converged),
        ]
        if self.response_levels is not None:
            rows.append(("response_levels", self.response_levels))
        if self.response_transform_applied:
            rows.append(("response_transform", self.response_transform))
            rows.append(("response_transform_n", self.response_transform_n))
        if self.dispersion_params:
            rows.append(("dispersion_params", self.dispersion_params))
            rows.append(("dispersion_estimated", self.dispersion_estimated))
        meta_html = "".join(
            (
                "<tr>"
                + "<th style='text-align:left;padding:2px 8px 2px 0;'>"
                + html.escape(str(k))
                + "</th>"
                + "<td style='text-align:left;padding:2px 0;'>"
                + html.escape(str(v))
                + "</td>"
                + "</tr>"
            )
            for k, v in rows
        )
        msg_html = ""
        if self.optimizer_message:
            msg_html = (
                "<div style='margin-top:6px;'>"
                "<strong>optimizer_message:</strong> "
                f"{html.escape(self.optimizer_message)}"
                "</div>"
            )
        coef_html = tbl.to_html(border=0, classes="toytree-pglm-coef")
        return (
            "<div style='font-family:sans-serif;line-height:1.3;'>"
            "<div style='font-weight:600;margin-bottom:4px;'>PGLMResult</div>"
            "<table style='border-collapse:collapse;margin-bottom:6px;'>"
            f"{meta_html}</table>"
            f"{coef_html}{msg_html}</div>"
        )


@dataclass
class _IRLSFit:
    """Internal IRLS fit state at a fixed lambda."""

    beta: np.ndarray
    vcov: np.ndarray
    eta: np.ndarray
    mu: np.ndarray
    llf: float
    pll: float
    converged: bool
    n_iter: int
    message: str


def _coerce_tip_dataframe(tree: ToyTree, data: pd.DataFrame | None) -> pd.DataFrame:
    """Return a DataFrame aligned to tree tip order and indexed by tip names."""
    tip_labels = tree.get_tip_labels()
    tip_idx = list(range(tree.ntips))

    if data is None:
        return tree.get_tip_data().set_index("name")
    if not isinstance(data, pd.DataFrame):
        raise ToytreeError("data must be a pandas DataFrame or None")

    frame = data.copy()
    if not frame.index.is_unique:
        raise ToytreeError("data index must be unique to align rows to tree tips")
    if set(tip_labels).issubset(set(frame.index)):
        frame = frame.loc[tip_labels].copy()
        frame.index = tip_labels
        return frame
    is_int_index = isinstance(frame.index, pd.RangeIndex) or np.issubdtype(
        frame.index.dtype, np.integer
    )
    if is_int_index and set(tip_idx).issubset(set(frame.index)):
        frame = frame.loc[tip_idx].copy()
        frame.index = tip_labels
        return frame
    raise ToytreeError(
        "Could not align data rows to tree tips. Set DataFrame index to tip names "
        "or node/tip idx labels."
    )


def _parse_formula(formula: str) -> tuple[str, str]:
    """Return left- and right-hand formula strings."""
    if not isinstance(formula, str) or not formula.strip():
        raise ToytreeError("formula must be a non-empty str")
    if "~" not in formula:
        raise ToytreeError("formula must contain '~' with response on the left side.")
    lhs, rhs = formula.split("~", 1)
    lhs = lhs.strip()
    rhs = rhs.strip()
    if (not lhs) or (not rhs):
        raise ToytreeError("formula must contain non-empty left and right sides.")
    return lhs, rhs


def _build_design_and_response(
    formula: str,
    tip_data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, str]:
    """Build predictor design matrix and response series from a simple formula."""
    lhs, rhs = _parse_formula(formula)
    if lhs not in tip_data.columns:
        raise ToytreeError(
            "pglm currently requires a simple response column name on the left-hand "
            f"side of the formula. '{lhs}' was not found in the data."
        )

    # Build only the predictor design matrix so response validation can be
    # delegated to family-specific code while preserving Patsy's row dropping.
    try:
        xmat = dmatrix(rhs, data=tip_data, return_type="dataframe")
    except PatsyError as exc:
        raise ToytreeError(f"Invalid formula or data for pglm: {exc}") from exc

    yser = tip_data[lhs].loc[xmat.index]
    if xmat.shape[0] == 0:
        raise ToytreeError(
            "No rows remain after applying formula and dropping missing values."
        )
    return xmat, yser, lhs


def _apply_beta_boundary_squeeze(
    series: pd.Series,
) -> tuple[pd.Series, bool, int]:
    """Apply a Smithson-Verkuilen-style squeeze transform to [0, 1] values.

    This is applied after Patsy row filtering so the sample size used in the
    transform matches the rows used in the fit.
    """
    y = pd.to_numeric(series, errors="coerce").astype(float).copy()
    non_missing = y.dropna()
    if non_missing.empty:
        return y, False, 0
    vals = non_missing.to_numpy()
    if np.any((vals < 0) | (vals > 1)):
        raise ToytreeError(
            "family='beta' with boundary='squeeze' still requires response "
            "values within [0, 1]."
        )
    nobs = int(non_missing.shape[0])
    y_new = y.copy()
    y_new.loc[non_missing.index] = (non_missing * (nobs - 1) + 0.5) / nobs
    before = non_missing.to_numpy(dtype=float)
    after = y_new.loc[non_missing.index].to_numpy(dtype=float)
    n_changed = int(np.sum(~np.isclose(before, after)))
    return y_new, bool(n_changed), n_changed


class PGLMPruningModel:
    """Phylogenetic GLM using pruning-based IRLS for supported families."""

    def __init__(
        self,
        tree: ToyTree,
        y: np.ndarray,
        xmat: pd.DataFrame,
        response_name: str,
        response_levels: tuple[str, str] | None,
        *,
        spec: GLMFamilySpec,
        firth: bool = True,
        epsilon: float = 1e-12,
        tol: float = 1e-8,
        max_iter: int = 100,
    ):
        self.tree = tree
        self.y = np.asarray(y, dtype=float)
        self.xmat = xmat
        self.X = xmat.to_numpy(dtype=float)
        self.tip_labels = list(xmat.index)
        self.response_name = response_name
        self.response_levels = response_levels
        self.spec = spec
        self.family = spec.family
        self.link = spec.link
        self.firth = bool(firth)
        self.epsilon = float(epsilon)
        self.tol = float(tol)
        self.max_iter = int(max_iter)
        self.engine = PhyloPruningEngine(tree, epsilon=self.epsilon)
        self.nobs, self.ncoef = self.X.shape
        if self.y.shape != (self.nobs,):
            raise ToytreeError("Response length does not match design rows.")
        if self.firth and (not self.spec.supports_firth):
            raise ToytreeError(
                "Firth penalty is not implemented for this family/link in pglm."
            )
        self._dispersion_bounds_map = {
            "negative_binomial": (1e-8, 100.0),
            "gamma": (1e-8, 100.0),
            "beta": (1e-6, 1e4),
        }

    def _dispersion_param_name(self) -> str | None:
        """Return the profiled scalar dispersion parameter name for the family."""
        if self.family == "negative_binomial":
            return "alpha"
        if self.family == "gamma":
            return "dispersion"
        if self.family == "beta":
            return "phi"
        return None

    def _dispersion_bounds(self) -> tuple[float, float] | None:
        """Return bounded-search limits for the family dispersion parameter."""
        return self._dispersion_bounds_map.get(self.family)

    def _dispersion_is_estimated(self) -> bool:
        """Return True if the family dispersion parameter should be profiled."""
        pname = self._dispersion_param_name()
        return bool(
            pname is not None
            and (not self.spec.family_params or pname not in self.spec.family_params)
        )

    def _spec_with_dispersion(self, value: float | None) -> GLMFamilySpec:
        """Return a family spec with a concrete dispersion value when needed."""
        pname = self._dispersion_param_name()
        if pname is None:
            return self.spec
        if value is None:
            if self.spec.family_params and pname in self.spec.family_params:
                value = float(self.spec.family_params[pname])
            else:
                raise ToytreeError(f"{self.family} fitting requires a concrete {pname}")
        params = {pname: float(value)}
        # Rebuild the statsmodels family object so variance and loglik math use
        # the candidate family parameter during profile optimization.
        return replace(
            self.spec,
            family_params=params,
            sm_family=_make_sm_family(self.family, self.link, params),
        )

    def _weighted_precision_system(
        self,
        xw: np.ndarray,
        zw: np.ndarray,
        lambda_: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return normal-equation matrix and RHS under weighted pruning precision."""
        M = np.zeros((self.ncoef, self.ncoef), dtype=float)
        rhs = np.zeros(self.ncoef, dtype=float)
        for i in range(self.ncoef):
            for j in range(i, self.ncoef):
                quad, _ = self.engine.bilinear_and_logdet(xw[:, i], xw[:, j], lambda_)
                M[i, j] = quad
                M[j, i] = quad
            rhs[i] = self.engine.bilinear_and_logdet(xw[:, i], zw, lambda_)[0]
        return M, rhs

    def _firth_adjustment(self, mu: np.ndarray, W: np.ndarray) -> np.ndarray:
        """Return an approximate Firth adjustment term for the IRLS score.

        We use the standard GLM leverage-based Firth correction computed from a
        non-phylogenetic weighted hat matrix approximation. This is a pragmatic
        bias-reduction stabilizer in the current phase, while the phylogenetic
        dependence is still handled in the weighted pruning solve.
        """
        xw = self.X * np.sqrt(W)[:, None]
        xtwx = xw.T @ xw
        xtwx_inv = np.linalg.pinv(xtwx)
        # h is the diagonal of the weighted hat matrix and controls the local
        # Jeffreys/Firth score adjustment magnitude at each observation.
        h = np.einsum("ij,jk,ik->i", xw, xtwx_inv, xw)
        h = np.clip(h, 0.0, 1.0)
        if self.family == "binomial" and self.link == "logit":
            return (0.5 - mu) * h
        if self.family == "poisson" and self.link == "log":
            # For canonical Poisson-log IRLS, the Firth adjustment enters the
            # score as +0.5*h in the (y - mu) term used to build the
            # pseudo-response update.
            return 0.5 * h
        raise ToytreeError(
            "Firth adjustment is not implemented for this family/link in pglm."
        )

    def _loglik(
        self,
        eta: np.ndarray,
        M: np.ndarray,
        spec: GLMFamilySpec | None = None,
    ) -> tuple[float, float]:
        """Return unpenalized and penalized log-likelihood values."""
        active_spec = self.spec if spec is None else spec
        mu = active_spec.inv_link(eta)
        ll = active_spec.loglik(self.y, mu)
        if not self.firth:
            return ll, ll
        sign, logdet = np.linalg.slogdet(M)
        if sign <= 0 or (not np.isfinite(logdet)):
            return -np.inf, -np.inf
        pll = ll + 0.5 * float(logdet)
        return ll, pll

    def fit_fixed_lambda(
        self,
        lambda_: float,
        dispersion: float | None = None,
    ) -> _IRLSFit:
        """Fit the family-specific GLM at a fixed lambda using IRLS."""
        active_spec = self._spec_with_dispersion(dispersion)
        beta = np.zeros(self.ncoef, dtype=float)
        if "Intercept" in self.xmat.columns:
            int_idx = self.xmat.columns.get_loc("Intercept")
            if self.family == "binomial":
                ybar = float(np.clip(np.mean(self.y), 1e-6, 1 - 1e-6))
                beta[int_idx] = np.log(ybar / (1.0 - ybar))
            elif self.family == "beta":
                ybar = float(np.clip(np.mean(self.y), 1e-6, 1.0 - 1e-6))
                beta[int_idx] = np.log(ybar / (1.0 - ybar))
            elif self.family in {"poisson", "negative_binomial", "gamma"}:
                ybar = float(np.clip(np.mean(self.y), 1e-6, None))
                beta[int_idx] = np.log(ybar)
        last_M = np.eye(self.ncoef)
        message = ""
        converged = False
        n_iter = 0

        for n_iter in range(1, self.max_iter + 1):
            eta = self.X @ beta
            mu = active_spec.inv_link(eta)
            active_spec.validate_mu(mu)
            dmu = active_spec.dmu_deta(eta, mu)
            var_mu = active_spec.variance(mu)
            # Statsmodels link derivatives can underflow to exactly zero at
            # extreme eta values (e.g., logit saturation). Clamp the working
            # derivative/variance terms for numerical stability while keeping
            # strict domain checks on the mean itself.
            dmu = np.clip(dmu, 1e-12, None)
            var_mu = np.clip(var_mu, 1e-12, None)
            W = np.clip((dmu**2) / var_mu, 1e-12, None)
            # Firth is currently only enabled for binomial-logit. Keeping the
            # adjustment isolated here makes family-specific extensions easier.
            adj = self._firth_adjustment(mu, W) if self.firth else 0.0
            # Cap the pseudo-response increment to avoid runaway IRLS proposals
            # when dmu becomes numerically tiny near boundary means.
            z_step = np.clip((self.y - mu + adj) / dmu, -50.0, 50.0)
            z = eta + z_step

            sw = np.sqrt(W)
            xw = self.X * sw[:, None]
            zw = z * sw
            M, rhs = self._weighted_precision_system(xw, zw, lambda_)
            last_M = M
            beta_prop = np.linalg.pinv(M) @ rhs

            # Step-halving guards against overshooting in difficult separation
            # cases and keeps the penalized likelihood monotone in practice.
            ll_old, pll_old = self._loglik(eta, M, active_spec)
            best_obj_old = pll_old if self.firth else ll_old
            step = 1.0
            min_step = 1.0 / (2**20)
            beta_new = beta_prop
            saw_valid_step = False
            while step >= min_step:
                eta_new = self.X @ beta_new
                # Invalid mean values (e.g., future identity-link fits) are
                # rejected before likelihood evaluation; we keep shrinking the
                # step until the proposal re-enters the family domain.
                try:
                    mu_new = active_spec.inv_link(eta_new)
                    active_spec.validate_mu(mu_new)
                    saw_valid_step = True
                except ToytreeError:
                    step *= 0.5
                    beta_new = beta + step * (beta_prop - beta)
                    continue
                ll_new, pll_new = self._loglik(eta_new, M, active_spec)
                best_obj_new = pll_new if self.firth else ll_new
                if np.isfinite(best_obj_new) and best_obj_new >= best_obj_old - 1e-10:
                    break
                step *= 0.5
                beta_new = beta + step * (beta_prop - beta)
            else:
                if saw_valid_step:
                    # If proposals remain in-domain but none improves the
                    # objective, treat this as a stalled IRLS step rather than
                    # an invalid-domain failure. Keeping the current beta lets
                    # the convergence criterion stop cleanly.
                    beta_new = beta.copy()
                else:
                    raise ToytreeError(
                        "IRLS step produced invalid mean values for the selected "
                        "family/link domain and no valid step was found after "
                        "step-halving."
                    )

            eta = self.X @ beta_new
            mu = active_spec.inv_link(eta)
            active_spec.validate_mu(mu)
            ll, pll = self._loglik(eta, M, active_spec)
            if np.max(np.abs(beta_new - beta)) < self.tol:
                beta = beta_new
                converged = True
                message = "IRLS converged"
                break
            beta = beta_new
        else:
            eta = self.X @ beta
            mu = active_spec.inv_link(eta)
            active_spec.validate_mu(mu)
            ll, pll = self._loglik(eta, last_M, active_spec)
            message = "IRLS failed to converge"

        try:
            vcov = np.linalg.pinv(last_M)
        except np.linalg.LinAlgError:
            vcov = np.full((self.ncoef, self.ncoef), np.nan, dtype=float)

        return _IRLSFit(
            beta=beta,
            vcov=vcov,
            eta=eta,
            mu=mu,
            llf=float(ll),
            pll=float(pll),
            converged=converged,
            n_iter=n_iter,
            message=message,
        )

    def _fit_profile_dispersion_at_lambda(
        self,
        lambda_: float,
    ) -> tuple[_IRLSFit, float, bool, str]:
        """Profile a family dispersion parameter at a fixed lambda."""
        pname = self._dispersion_param_name()
        if pname is None:
            fit = self.fit_fixed_lambda(lambda_)
            return fit, np.nan, True, fit.message
        if not self._dispersion_is_estimated():
            disp = float(self.spec.family_params[pname])
            fit = self.fit_fixed_lambda(lambda_, dispersion=disp)
            return fit, disp, True, fit.message

        best_fit: _IRLSFit | None = None
        best_disp: float | None = None

        def objective(value: float) -> float:
            nonlocal best_fit, best_disp
            try:
                fit = self.fit_fixed_lambda(lambda_, dispersion=float(value))
            except (ToytreeError, np.linalg.LinAlgError, ValueError):
                return np.inf
            obj = -(fit.pll if self.firth else fit.llf)
            if np.isfinite(obj) and (
                best_fit is None
                or obj < (-(best_fit.pll if self.firth else best_fit.llf))
            ):
                best_fit = fit
                best_disp = float(value)
            return obj

        bounds = self._dispersion_bounds()
        if bounds is None:
            raise ToytreeError("No dispersion bounds configured for this family.")
        alo, ahi = bounds
        opt = minimize_scalar(
            objective,
            bounds=(alo, ahi),
            method="bounded",
        )
        if best_fit is None or best_disp is None:
            raise ToytreeError(f"Failed to optimize {self.family} {pname}.")
        # Refit at the optimizer result when available so the returned fit and
        # optimizer message are synchronized with the chosen profile optimum.
        if opt.success and np.isfinite(float(opt.x)):
            best_disp = float(opt.x)
            best_fit = self.fit_fixed_lambda(lambda_, dispersion=best_disp)
        return best_fit, best_disp, bool(opt.success), str(opt.message)

    def fit(self, lambda_: float | None = None) -> PGLMResult:
        """Fit the model with fixed or optimized Pagel's lambda."""
        upper = float(_max_lambda(self.tree))
        if not np.isfinite(upper) or upper <= 0:
            raise ToytreeError("Could not determine a valid upper bound for lambda.")
        bounds = (0.0, upper)

        best_fit: _IRLSFit | None = None
        best_dispersion: float | None = None
        dispersion_name = self._dispersion_param_name()
        dispersion_estimated = bool(self._dispersion_is_estimated())
        dispersion_opt_message = ""

        def objective(lam: float) -> float:
            nonlocal best_fit, best_dispersion, dispersion_opt_message
            try:
                if dispersion_name is not None:
                    fit, disp_hat, _, disp_msg = self._fit_profile_dispersion_at_lambda(
                        float(lam)
                    )
                else:
                    fit = self.fit_fixed_lambda(float(lam))
                    disp_hat = np.nan
                    disp_msg = ""
            except (ToytreeError, np.linalg.LinAlgError, ValueError):
                return np.inf
            obj = -(fit.pll if self.firth else fit.llf)
            if np.isfinite(obj) and (
                best_fit is None
                or obj < (-(best_fit.pll if self.firth else best_fit.llf))
            ):
                best_fit = fit
                best_dispersion = None if np.isnan(disp_hat) else float(disp_hat)
                dispersion_opt_message = disp_msg
            return obj

        if lambda_ is None:
            eps = 1e-12
            opt = minimize_scalar(
                objective,
                bounds=(
                    bounds[0] + eps,
                    bounds[1] - eps if bounds[1] > eps else bounds[1],
                ),
                method="bounded",
            )
            if (not opt.success) or (not np.isfinite(float(opt.x))):
                raise ToytreeError(f"Failed to optimize lambda for pglm: {opt.message}")
            lambda_hat = float(opt.x)
            lambda_optimized = True
            optimizer_message = str(opt.message)
            converged = bool(opt.success)
            if dispersion_name is not None:
                fit, disp_hat, disp_conv, disp_msg = (
                    self._fit_profile_dispersion_at_lambda(lambda_hat)
                )
                best_dispersion = float(disp_hat)
                dispersion_opt_message = disp_msg
                converged = bool(converged and disp_conv and fit.converged)
            else:
                fit = self.fit_fixed_lambda(lambda_hat)
        else:
            lambda_hat = float(lambda_)
            if (
                (not np.isfinite(lambda_hat))
                or lambda_hat < bounds[0]
                or lambda_hat > bounds[1]
            ):
                raise ToytreeError(
                    f"lambda_ must be between 0 and max_lambda(tree)={upper:.6g}."
                )
            if dispersion_name is not None:
                fit, disp_hat, disp_conv, disp_msg = (
                    self._fit_profile_dispersion_at_lambda(lambda_hat)
                )
                best_dispersion = float(disp_hat)
                dispersion_opt_message = disp_msg
                converged = bool(disp_conv and fit.converged)
            else:
                fit = self.fit_fixed_lambda(lambda_hat)
            lambda_optimized = False
            optimizer_message = fit.message
            if dispersion_name is None:
                converged = fit.converged

        dispersion_params = self.spec.family_params
        if dispersion_name is not None:
            if best_dispersion is None:
                # This should not happen if fit succeeded, but keep the error
                # explicit because the result object reports the dispersion.
                raise ToytreeError(
                    f"{self.family} fit completed without {dispersion_name}."
                )
            dispersion_params = {dispersion_name: float(best_dispersion)}
            if dispersion_estimated and dispersion_opt_message:
                optimizer_message = "; ".join(
                    [
                        s
                        for s in [
                            optimizer_message,
                            f"{dispersion_name}: {dispersion_opt_message}",
                        ]
                        if s
                    ]
                )

        vcov_df = pd.DataFrame(
            fit.vcov,
            index=self.xmat.columns,
            columns=self.xmat.columns,
        )
        bse = pd.Series(np.sqrt(np.diag(vcov_df)), index=self.xmat.columns, name="bse")
        params = pd.Series(fit.beta, index=self.xmat.columns, name="coef")
        eta_ser = pd.Series(fit.eta, index=self.tip_labels, name="eta")
        mu_ser = pd.Series(fit.mu, index=self.tip_labels, name="mu")
        resid_ser = pd.Series(
            self.y - fit.mu,
            index=self.tip_labels,
            name="resid_response",
        )

        return PGLMResult(
            params=params,
            bse=bse,
            vcov=vcov_df,
            fittedvalues=eta_ser,
            fitted_mean=mu_ser,
            resid_response=resid_ser,
            log_likelihood=float(fit.llf),
            penalized_log_likelihood=float(fit.pll),
            lambda_=float(lambda_hat),
            lambda_optimized=lambda_optimized,
            lambda_bounds=bounds,
            nobs=int(self.nobs),
            response_name=self.response_name,
            design_columns=list(self.xmat.columns),
            converged=bool(fit.converged and converged),
            optimizer_message=optimizer_message or fit.message,
            irls_iterations=int(fit.n_iter),
            firth=self.firth,
            family=self.family,
            link=self.link,
            dispersion_params=dispersion_params,
            dispersion_estimated=bool(
                dispersion_estimated and dispersion_name is not None
            ),
            response_levels=self.response_levels,
        )


@add_subpackage_method(PhyloCompAPI)
def pglm(
    tree: ToyTree,
    formula: str,
    data: pd.DataFrame | None = None,
    lambda_: float | None = None,
    family: str = "binomial",
    link: str = "logit",
    family_params: dict[str, Any] | None = None,
    boundary: Literal["error", "squeeze"] = "error",
    max_iter: int = 100,
    tol: float = 1e-8,
    epsilon: float = 1e-12,
) -> PGLMResult:
    """Fit a pruning-based phylogenetic generalized linear model.

    This method uses pruning-based IRLS updates with Pagel's lambda to fit
    phylogenetic GLMs without constructing a dense VCV matrix in the core
    weighted least-squares solves. Current fitting support includes
    ``binomial``/``bernoulli`` with ``logit``, ``poisson`` with ``log``, and
    ``negative_binomial`` with ``log``, ``gamma`` with ``log``, and ``beta``
    with ``logit``. ``gamma`` with ``inverse`` is recognized and its
    response/``family_params`` are validated, but fitting for that path is not
    implemented yet. This is the non-Gaussian response method in
    ``toytree.pcm``; see also ``pgls`` for Gaussian continuous-response
    models.

    Parameters
    ----------
    tree : ToyTree
        Rooted phylogeny with branch lengths.
    formula : str
        Patsy / statsmodels-style formula with a simple response column on the
        left-hand side (e.g., ``"y ~ x + C(group)"``).
    data : pandas.DataFrame or None, default=None
        Trait table aligned to tree tips by index (tip labels preferred; tip or
        node idx labels also accepted). If ``None``, tip data are read from the
        tree.
    lambda_ : float or None, default=None
        Pagel's lambda value. If ``None``, lambda is optimized by bounded
        scalar optimization. If a float is provided, it is used as a fixed
        value.
    family : str, default="binomial"
        GLM family. Implemented in this phase: ``"binomial"`` / ``"bernoulli"``
        with ``link="logit"``, ``"poisson"`` with ``link="log"``,
        ``"negative_binomial"`` with ``link="log"``, and ``"gamma"`` with
        ``link="log"``, and ``"beta"`` with ``link="logit"``. ``"gamma"``
        with ``link="inverse"`` is accepted for validation and will raise
        ``ToytreeError`` noting that fitting is not implemented yet.
    link : str, default="logit"
        Link function for the selected family. Only canonical links are
        implemented in this phase (`logit` for binomial/beta, `log` for
        poisson/negative binomial/gamma, and `inverse` for gamma
        validation-only path).
    family_params : dict[str, Any] or None, default=None
        Optional family-specific parameters. For ``negative_binomial`` this may
        be ``{'alpha': <positive float>}`` to fix the dispersion parameter, or
        ``None`` to estimate ``alpha`` by profile likelihood. For
        ``gamma``+``log`` this may be ``{'dispersion': <positive float>}`` to
        fix the Gamma dispersion, or ``None`` to estimate it by profile
        likelihood. For ``beta``+``logit`` this may be
        ``{'phi': <positive float>}`` to fix precision, or ``None`` to
        estimate ``phi`` by profile likelihood. Implemented ``binomial`` and
        ``poisson`` fits expect ``None``. Scaffolded families require:
        ``{'dispersion': ...}`` for gamma+inverse.
    boundary : {"error", "squeeze"}, default="error"
        Boundary handling policy for Beta responses. ``"error"`` requires
        responses strictly in ``(0, 1)``. ``"squeeze"`` applies a
        Smithson-Verkuilen-style transform after Patsy row filtering to map
        values in ``[0, 1]`` into ``(0, 1)``. This option is supported only
        for ``family="beta"``.
    max_iter : int, default=100
        Maximum IRLS iterations at each lambda value.
    tol : float, default=1e-8
        Absolute coefficient convergence tolerance for IRLS.
    epsilon : float, default=1e-12
        Positive floor used to clamp zero/negative branch lengths and protect
        numerical calculations.

    Returns
    -------
    PGLMResult
        A fitted pruning-based phylogenetic GLM result object. The ``firth``
        field reports whether a Firth-style penalty was applied. It is applied
        automatically for implemented binomial and poisson families and not
        applied for negative-binomial, gamma, or beta families. The
        ``dispersion_params`` and ``dispersion_estimated`` fields report
        family-specific dispersion handling for negative-binomial, gamma, and
        beta. If ``boundary="squeeze"`` is used for Beta, response transform
        metadata are recorded on the result object.

    Raises
    ------
    ToytreeError
        If the formula is invalid, the response is invalid for the selected
        family, the family/link combination is unsupported, ``family_params``
        are invalid, data cannot be aligned to tips, lambda is invalid,
        boundary handling is invalid for the selected family, optimization /
        IRLS fails, or fitting is not implemented for the selected validated
        family.

    See Also
    --------
    pgls
        Pruning-based Gaussian phylogenetic linear model for continuous
        responses.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(20, seed=123)
    >>> rng = np.random.default_rng(123)
    >>> x = rng.normal(size=tree.ntips)
    >>> y = (x + rng.normal(scale=0.5, size=tree.ntips) > 0).astype(int)
    >>> df = pd.DataFrame({"x": x, "y": y}, index=tree.get_tip_labels())
    >>> fit = tree.pcm.pglm("y ~ x", data=df, family="binomial", link="logit")
    >>> fit.family, fit.link
    ('binomial', 'logit')
    """
    # Rescale and clamp the working tree before building pruning recursions.
    work_tree = tree.mod.edges_scale_to_root_height(1.0)
    for node in work_tree:
        if node._dist <= 0:
            node._dist = float(epsilon)
    work_tree._update()

    tip_data = _coerce_tip_dataframe(work_tree, data)
    xmat, yser_raw, response_name = _build_design_and_response(
        formula,
        tip_data,
    )
    family_norm = str(family).lower()
    if family_norm != "beta" and boundary != "error":
        raise ToytreeError(
            "boundary='squeeze' is currently supported only for family='beta'."
        )
    response_transform = None
    response_transform_applied = False
    response_transform_n = 0
    if family_norm == "beta" and boundary == "squeeze":
        # Apply the transform after Patsy row filtering so n matches the rows
        # entering the Beta likelihood and profile-likelihood fit.
        yser_raw, response_transform_applied, response_transform_n = (
            _apply_beta_boundary_squeeze(yser_raw)
        )
        response_transform = "beta_boundary_squeeze_sv"
    # Validate family/link and coerce the response after Patsy has already
    # dropped rows for predictors used in the formula.
    spec, yser = get_family_spec(
        family=family,
        link=link,
        family_params=family_params,
        response=yser_raw,
        response_name=response_name,
    )
    if yser is None:
        raise ToytreeError("Internal error: response coercion returned None.")
    keep = yser.notna()
    xmat = xmat.loc[keep]
    y = yser.loc[keep].to_numpy(dtype=float)
    if y.size < 2:
        raise ToytreeError("At least two observed tips are required for pglm.")
    if not spec.implemented:
        raise ToytreeError(
            f"pglm fitting is not implemented yet for family='{spec.family}' with "
            f"link='{spec.link}'."
        )

    kept_tips = list(xmat.index)
    kept_set = set(kept_tips)
    dropped = [lab for lab in work_tree.get_tip_labels() if lab not in kept_set]
    fit_tree = work_tree if not dropped else work_tree.mod.drop_tips(*dropped)
    xmat = xmat.loc[fit_tree.get_tip_labels()]
    y = (
        pd.Series(y, index=kept_tips)
        .loc[fit_tree.get_tip_labels()]
        .to_numpy(dtype=float)
    )

    # Firth application is an internal family-level policy: enabled for
    # implemented binomial/poisson fits and disabled otherwise. We keep the
    # flag on the result object for transparency but do not expose it in the
    # public API.
    auto_firth = bool(spec.supports_firth and spec.implemented)
    model = PGLMPruningModel(
        fit_tree,
        y,
        xmat,
        response_name,
        spec.response_levels,
        spec=spec,
        firth=auto_firth,
        epsilon=epsilon,
        tol=tol,
        max_iter=max_iter,
    )
    fit = model.fit(lambda_=lambda_)
    fit.response_transform = response_transform
    fit.response_transform_applied = bool(response_transform_applied)
    fit.response_transform_n = int(response_transform_n)
    return fit


def _example():
    """Run a quick manual smoke test for binary phylogenetic logistic regression."""
    from scipy.special import expit

    import toytree

    rng = np.random.default_rng(123)
    tree = toytree.rtree.unittree(50, treeheight=1.0, seed=123)
    x = rng.normal(size=tree.ntips)
    vcv = tree.pcm.get_vcv_matrix_from_tree()
    phylo_eff = rng.multivariate_normal(np.zeros(tree.ntips), 0.3 * vcv)
    p = expit(-0.5 + 1.25 * x + phylo_eff)
    y = rng.binomial(1, p, size=tree.ntips)
    df = pd.DataFrame({"x": x, "y": y}, index=tree.get_tip_labels())
    fit = pglm(tree, "y ~ x", data=df)
    print(fit)


if __name__ == "__main__":
    _example()
