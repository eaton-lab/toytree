#!/usr/bin/env python

"""Linear-time phylogenetic GLS via pruning recursions.

This module implements a pruning-based Gaussian phylogenetic linear model
backend inspired by Ho and Ane (2014). The phase-1 public API is ``pgls()``,
which fits a PGLS model for a continuous response using a
Patsy formula and Pagel's lambda optimization.

The implementation avoids constructing an ``N x N`` phylogenetic covariance
matrix in the core likelihood / normal-equation calculations by using a
postorder pruning recursion to evaluate bilinear forms of the type
``a.T @ V^-1 @ b`` and ``log|V|`` in linear time in the number of tips.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

import numpy as np
import pandas as pd
from pandas import CategoricalDtype
from patsy import PatsyError, dmatrices
from scipy.optimize import minimize_scalar
from scipy.stats import norm

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.data._src.expand_node_mapping import expand_node_mapping
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = [
    "PGLSResult",
    "PGLSPruningModel",
    "pgls",
]


@dataclass
class PGLSResult:
    """Container for pruning-based PGLS fit results.

    The object stores coefficient estimates, uncertainty summaries, fitted
    values, residuals, and model-level likelihood metadata. It implements
    terminal and notebook display helpers through ``__repr__`` and
    ``_repr_html_``.
    """

    params: pd.Series
    bse: pd.Series
    vcov: pd.DataFrame
    fittedvalues: pd.Series
    resid: pd.Series
    log_likelihood: float
    sigma2: float
    lambda_: float
    lambda_optimized: bool
    lambda_bounds: tuple[float, float]
    nobs: int
    response_name: str
    design_columns: list[str]
    converged: bool
    optimizer_message: str

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

    def _r_squared(self) -> float:
        """Return a simple response-scale coefficient of determination."""
        y = self.fittedvalues.to_numpy(dtype=float) + self.resid.to_numpy(dtype=float)
        yhat = self.fittedvalues.to_numpy(dtype=float)
        denom = np.sum((y - np.mean(y)) ** 2)
        if denom <= 0:
            return np.nan
        return float(1.0 - (np.sum((y - yhat) ** 2) / denom))

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
        """Return a statsmodels-like compact text summary."""
        lines = ["PGLSResult", "-" * 10]
        lines.append(
            f"response={self.response_name}  nobs={self.nobs}  "
            f"k_params={len(self.design_columns)}"
        )
        lines.append(
            "lambda="
            f"{self._fmt(self.lambda_)}  optimized={self.lambda_optimized}  "
            f"bounds=({self._fmt(self.lambda_bounds[0])}, "
            f"{self._fmt(self.lambda_bounds[1])})"
        )
        lines.append(
            f"log_likelihood={self._fmt(self.log_likelihood)}  "
            f"sigma2={self._fmt(self.sigma2)}  "
            f"R_squared={self._fmt(self._r_squared())}  "
            f"converged={self.converged}"
        )
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
            ("lambda", self._fmt(self.lambda_)),
            ("lambda_optimized", self.lambda_optimized),
            (
                "lambda_bounds",
                f"({self._fmt(self.lambda_bounds[0])}, "
                f"{self._fmt(self.lambda_bounds[1])})",
            ),
            ("log_likelihood", self._fmt(self.log_likelihood)),
            ("sigma2", self._fmt(self.sigma2)),
            ("R_squared", self._fmt(self._r_squared())),
            ("converged", self.converged),
        ]
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
        coef_html = tbl.to_html(border=0, classes="toytree-pgls-coef")
        return (
            "<div style='font-family:sans-serif;line-height:1.3;'>"
            "<div style='font-weight:600;margin-bottom:4px;'>PGLSResult</div>"
            "<table style='border-collapse:collapse;margin-bottom:6px;'>"
            f"{meta_html}</table>"
            f"{coef_html}"
            f"{msg_html}</div>"
        )


@dataclass
class _ProfileStats:
    """Internal profiled-Gaussian statistics at a fixed lambda."""

    beta: np.ndarray
    xt_vinv_x: np.ndarray
    rss: float
    logdet: float
    llf: float


def _coerce_tip_dataframe(
    tree: ToyTree,
    data: pd.DataFrame | None,
) -> pd.DataFrame:
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
        frame.index.dtype,
        np.integer,
    )
    if is_int_index and set(tip_idx).issubset(set(frame.index)):
        frame = frame.loc[tip_idx].copy()
        frame.index = tip_labels
        return frame

    raise ToytreeError(
        "Could not align data rows to tree tips. Set DataFrame index to tip names "
        "or node/tip idx labels."
    )


def _build_design(
    formula: str,
    tip_data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return Patsy response and design matrices after dropping missing rows."""
    try:
        ymat, xmat = dmatrices(formula, data=tip_data, return_type="dataframe")
    except PatsyError as exc:
        raise ToytreeError(f"Invalid formula or data for pgls: {exc}") from exc
    return ymat, xmat


def _check_response_is_continuous(
    formula: str,
    tip_data: pd.DataFrame,
    ymat: pd.DataFrame,
) -> None:
    """Raise if the dependent variable is categorical."""
    lhs = formula.split("~", 1)[0].strip()

    # Patsy expands categorical responses to multiple columns. This phase-1
    # engine supports a single continuous response only.
    if ymat.shape[1] != 1:
        raise ToytreeError(
            "pgls is not suitable for categorical dependent variables (Y); "
            "consider phylogenetic logistic regression."
        )

    if lhs in tip_data.columns:
        series = tip_data[lhs]
        if isinstance(series.dtype, CategoricalDtype):
            raise ToytreeError(
                "pgls is not suitable for categorical dependent variables "
                "(Y); consider phylogenetic logistic regression."
            )
        if pd.api.types.is_bool_dtype(series):
            raise ToytreeError(
                "pgls is not suitable for categorical dependent variables "
                "(Y); consider phylogenetic logistic regression."
            )
        if pd.api.types.is_object_dtype(series):
            non_missing = series.dropna()
            if non_missing.empty or non_missing.map(lambda x: isinstance(x, str)).all():
                raise ToytreeError(
                    "pgls is not suitable for categorical dependent "
                    "variables (Y); consider phylogenetic logistic regression."
                )

    if not np.issubdtype(ymat.dtypes.iloc[0], np.number):
        raise ToytreeError(
            "pgls is not suitable for categorical dependent variables (Y); "
            "consider phylogenetic logistic regression."
        )


def _max_lambda(tree: ToyTree) -> float:
    """Return a tree-specific upper bound on Pagel's lambda."""
    root_to_tip_dists = tree.distance.get_node_distance_matrix()[-1]
    internal_dists = root_to_tip_dists[tree.ntips :]
    return float(tree.treenode.height / max(internal_dists))


def _coerce_tip_stderr_series(
    tree: ToyTree,
    y_stderr: str | Mapping | pd.Series | None,
    tip_data: pd.DataFrame | None = None,
) -> pd.Series:
    """Return tip-aligned response standard errors indexed by tip labels."""
    tip_labels = tree.get_tip_labels()
    out = pd.Series(np.nan, index=tip_labels, dtype=float, name="y_stderr")
    if y_stderr is None:
        return out
    if isinstance(y_stderr, str):
        # When data is provided to pgls/infer wrappers, users expect that all
        # formula inputs and associated response uncertainty come from that
        # table only (no tree fallback). Prefer the aligned tip table column.
        if tip_data is not None and y_stderr in tip_data.columns:
            ser = tip_data[y_stderr].copy()
            ser.index = tip_labels
            return pd.to_numeric(ser, errors="coerce")
        ser = tree.get_node_data(y_stderr, missing=np.nan).iloc[: tree.ntips].copy()
        ser.index = tip_labels
        return pd.to_numeric(ser, errors="coerce")
    if isinstance(y_stderr, pd.Series):
        idx = y_stderr.index
        if set(tip_labels).issubset(set(idx)):
            ser = y_stderr.loc[tip_labels].copy()
            ser.index = tip_labels
            return pd.to_numeric(ser, errors="coerce")
        is_int_index = isinstance(idx, pd.RangeIndex) or (
            hasattr(idx, "dtype") and np.issubdtype(idx.dtype, np.integer)
        )
        if is_int_index and set(range(tree.ntips)).issubset(set(idx)):
            ser = y_stderr.loc[list(range(tree.ntips))].copy()
            ser.index = tip_labels
            return pd.to_numeric(ser, errors="coerce")
        mapping = y_stderr.to_dict()
    elif isinstance(y_stderr, Mapping):
        mapping = y_stderr
    else:
        raise ToytreeError("y_stderr must be a str, Mapping, pandas Series, or None.")

    # Query expansion supports idx labels, names, and regex queries. We keep
    # only tip matches because PGLS fitting operates on observed tips.
    emap = expand_node_mapping(tree, mapping)
    for node, value in emap.items():
        if node.idx < tree.ntips:
            out.iloc[node.idx] = value
    return pd.to_numeric(out, errors="coerce")


def _validate_stderr_to_variance(y_stderr: pd.Series) -> np.ndarray:
    """Validate response standard errors and return squared observation variances."""
    arr = pd.to_numeric(y_stderr, errors="coerce").to_numpy(dtype=float)
    bad_inf = np.isinf(arr)
    if np.any(bad_inf):
        raise ToytreeError("y_stderr values must be finite when provided.")
    bad_neg = np.isfinite(arr) & (arr < 0)
    if np.any(bad_neg):
        raise ToytreeError("y_stderr values must be non-negative.")
    arr = np.nan_to_num(arr, nan=0.0)
    return arr**2


def _prepare_pgls_inputs(
    tree: ToyTree,
    formula: str,
    data: pd.DataFrame | None,
    y_stderr: str | Mapping | pd.Series | None,
    epsilon: float,
) -> tuple[ToyTree, pd.DataFrame, pd.DataFrame, np.ndarray]:
    """Prepare aligned fit-tree, design matrices, and tip observation variances."""
    if not isinstance(formula, str) or not formula.strip():
        raise ToytreeError("formula must be a non-empty str")

    # Rescale and clamp the working tree before building pruning recursions.
    work_tree = tree.mod.edges_scale_to_root_height(1.0)
    for node in work_tree:
        if node._dist <= 0:
            node._dist = float(epsilon)
    work_tree._update()

    tip_data = _coerce_tip_dataframe(work_tree, data)
    ymat, xmat = _build_design(formula, tip_data)
    _check_response_is_continuous(formula, tip_data, ymat)

    if ymat.shape[0] == 0:
        raise ToytreeError(
            "No rows remain after applying formula and dropping missing values."
        )
    if ymat.shape[0] < 2:
        raise ToytreeError("At least two observed tips are required for pgls.")

    y_stderr_tips = _coerce_tip_stderr_series(
        work_tree,
        y_stderr,
        tip_data=tip_data,
    ).reindex(tip_data.index)

    # Patsy drops rows in-place relative to the tip-order dataframe. We prune a
    # temporary tree to the exact retained tips so all pruning vectors map
    # directly to subtree tip idx order with no missing-tip bookkeeping.
    kept_tips = list(ymat.index)
    dropped = [lab for lab in work_tree.get_tip_labels() if lab not in set(kept_tips)]
    fit_tree = work_tree if not dropped else work_tree.mod.drop_tips(*dropped)
    x_design_info = getattr(xmat, "design_info", None)
    ymat = ymat.loc[fit_tree.get_tip_labels()]
    xmat = xmat.loc[fit_tree.get_tip_labels()]
    if x_design_info is not None:
        # Pandas row selection drops ad-hoc attributes; reattach Patsy design
        # metadata so downstream node-state inference can rebuild predictor
        # design rows for internal nodes using the fitted coding scheme.
        xmat.design_info = x_design_info
    y_obs_var = _validate_stderr_to_variance(
        y_stderr_tips.loc[fit_tree.get_tip_labels()]
    )
    return fit_tree, ymat, xmat, y_obs_var


class PhyloPruningEngine:
    """Pruning-based linear algebra engine for Gaussian phylogenetic models.

    Parameters
    ----------
    tree : ToyTree
        Rooted tree containing only the observed tips used in the model fit.
    epsilon : float, default=1e-12
        Minimum positive edge length used to clamp zero / negative edge lengths
        for numerical stability.
    """

    def __init__(self, tree: ToyTree, epsilon: float = 1e-12):
        self.tree = tree
        self.epsilon = float(epsilon)
        self.ntips = tree.ntips
        self.nnodes = tree.nnodes
        self.root_idx = tree.treenode.idx
        self.parent_idx = np.full(self.nnodes, -1, dtype=int)
        self.dist_by_child = np.zeros(self.nnodes, dtype=float)
        self.root_to_node = np.zeros(self.nnodes, dtype=float)
        self.tip_root_dists = np.zeros(self.ntips, dtype=float)
        self.postorder = []
        self.children = [[] for _ in range(self.nnodes)]
        self._build_topology_arrays()

    def _build_topology_arrays(self) -> None:
        """Cache traversal and edge arrays used in pruning recursions."""
        # The engine assumes tips are indexed 0..ntips-1 in toytree's standard
        # node ordering. This is relied on to index leaf payload vectors fast.
        for tidx in range(self.ntips):
            if self.tree[tidx].idx != tidx:
                raise ToytreeError("PhyloPruningEngine requires standard tip idxs.")

        for node in self.tree.traverse("preorder"):
            self.parent_idx[node.idx] = -1 if node.up is None else node.up.idx
            if node.up is not None:
                self.children[node.up.idx].append(node.idx)
                self.dist_by_child[node.idx] = max(float(node.dist), self.epsilon)
                self.root_to_node[node.idx] = (
                    self.root_to_node[node.up.idx] + self.dist_by_child[node.idx]
                )
            if node.idx < self.ntips:
                self.tip_root_dists[node.idx] = self.root_to_node[node.idx]

        self.postorder = [node.idx for node in self.tree.traverse("postorder")]

    def _leaf_nugget(self, lambda_: float) -> np.ndarray:
        """Return tip-specific residual variances induced by Pagel's lambda."""
        # Lambda scales shared covariance. The diagonal is preserved by adding a
        # tip-specific independent variance term (the "nugget").
        return (1.0 - float(lambda_)) * self.tip_root_dists

    def bilinear_and_logdet(
        self,
        a: np.ndarray,
        b: np.ndarray,
        lambda_: float,
        obs_var: np.ndarray | None = None,
    ) -> tuple[float, float]:
        """Return ``a.T @ V^-1 @ b`` and ``log|V|`` using a pruning recursion."""
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        if a.shape != (self.ntips,) or b.shape != (self.ntips,):
            raise ToytreeError("Pruning vectors must have length equal to ntips.")

        V = np.zeros(self.nnodes, dtype=float)
        Za = np.zeros(self.nnodes, dtype=float)
        Zb = np.zeros(self.nnodes, dtype=float)
        logdet = 0.0
        quad = 0.0
        lam = float(lambda_)
        leaf_nugget = self._leaf_nugget(lam)
        if obs_var is not None:
            obs_var = np.asarray(obs_var, dtype=float)
            if obs_var.shape != (self.ntips,):
                raise ToytreeError("obs_var must have length ntips.")
            if np.any(~np.isfinite(obs_var)) or np.any(obs_var < 0):
                raise ToytreeError("obs_var must be finite and non-negative.")
            # Response measurement-error variance contributes only to tip
            # diagonals, so it enters the recursion as an added leaf nugget.
            leaf_nugget = leaf_nugget + obs_var

        for idx in self.postorder:
            child_idxs = self.children[idx]

            if idx < self.ntips and not child_idxs:
                # Leaf payloads are initialized with observed vector values and
                # a lambda-dependent tip nugget that preserves the diagonal of
                # Pagel's transformed covariance matrix.
                V[idx] = leaf_nugget[idx]
                Za[idx] = a[idx]
                Zb[idx] = b[idx]
                continue

            if not child_idxs:
                raise ToytreeError("Encountered an unexpected non-tip leaf node.")

            # Each child subtree sends a Gaussian message to the current node.
            # The message variance is the child subtree variance plus the edge
            # variance on the branch entering that child.
            first = child_idxs[0]
            w = V[first] + lam * self.dist_by_child[first]
            if w <= 0 or not np.isfinite(w):
                raise np.linalg.LinAlgError("Non-positive pruning variance.")
            za = Za[first]
            zb = Zb[first]

            # For polytomies, we combine child messages sequentially. This is
            # algebraically equivalent to integrating all children jointly but
            # keeps the recursion simple and linear in the number of children.
            for cidx in child_idxs[1:]:
                w2 = V[cidx] + lam * self.dist_by_child[cidx]
                if w2 <= 0 or not np.isfinite(w2):
                    raise np.linalg.LinAlgError("Non-positive pruning variance.")
                z2a = Za[cidx]
                z2b = Zb[cidx]
                den = w + w2
                if den <= 0 or not np.isfinite(den):
                    raise np.linalg.LinAlgError("Invalid pruning denominator.")

                quad += ((za - z2a) * (zb - z2b)) / den
                logdet += float(np.log(den))

                w_new = (w * w2) / den
                za_new = (za * w2 + z2a * w) / den
                zb_new = (zb * w2 + z2b * w) / den
                w, za, zb = w_new, za_new, zb_new

            V[idx] = w
            Za[idx] = za
            Zb[idx] = zb

        vroot = V[self.root_idx]
        if vroot <= 0 or not np.isfinite(vroot):
            raise np.linalg.LinAlgError("Invalid root pruning variance.")

        # The final root term closes the recursion and yields the full bilinear
        # form and determinant for the observed-tip covariance matrix.
        quad += (Za[self.root_idx] * Zb[self.root_idx]) / vroot
        logdet += float(np.log(vroot))

        if not (np.isfinite(quad) and np.isfinite(logdet)):
            raise np.linalg.LinAlgError("Non-finite pruning result.")
        return float(quad), float(logdet)


class PGLSPruningModel:
    """Gaussian PGLS fitted using pruning-based linear algebra."""

    def __init__(
        self,
        tree: ToyTree,
        ymat: pd.DataFrame,
        xmat: pd.DataFrame,
        y_obs_var: np.ndarray | None = None,
        epsilon: float = 1e-12,
    ):
        self.tree = tree
        self.ymat = ymat
        self.xmat = xmat
        self.epsilon = float(epsilon)
        self.response_name = ymat.columns[0]
        self.tip_labels = list(ymat.index)
        self.engine = PhyloPruningEngine(tree, epsilon=self.epsilon)
        self._y = ymat.iloc[:, 0].to_numpy(dtype=float)
        self._X = xmat.to_numpy(dtype=float)
        self._y_obs_var = y_obs_var
        self.nobs, self.ncoef = self._X.shape

    def _profile_stats(self, lambda_: float) -> _ProfileStats:
        """Return profiled Gaussian statistics at a fixed lambda."""
        xt_vinv_x = np.zeros((self.ncoef, self.ncoef), dtype=float)
        xt_vinv_y = np.zeros(self.ncoef, dtype=float)
        logdet = None

        for i in range(self.ncoef):
            for j in range(i, self.ncoef):
                quad, ldet = self.engine.bilinear_and_logdet(
                    self._X[:, i],
                    self._X[:, j],
                    lambda_,
                    obs_var=self._y_obs_var,
                )
                xt_vinv_x[i, j] = quad
                xt_vinv_x[j, i] = quad
                if logdet is None:
                    logdet = ldet

        for i in range(self.ncoef):
            quad, _ = self.engine.bilinear_and_logdet(
                self._X[:, i],
                self._y,
                lambda_,
                obs_var=self._y_obs_var,
            )
            xt_vinv_y[i] = quad

        try:
            beta = np.linalg.solve(xt_vinv_x, xt_vinv_y)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(xt_vinv_x, xt_vinv_y, rcond=None)[0]

        resid = self._y - self._X.dot(beta)
        rss, ldet2 = self.engine.bilinear_and_logdet(
            resid,
            resid,
            lambda_,
            obs_var=self._y_obs_var,
        )
        if logdet is None:
            logdet = ldet2
        n = float(self.nobs)
        if rss <= 0 or not np.isfinite(rss):
            raise np.linalg.LinAlgError("Invalid residual sum of squares.")
        llf = -0.5 * (n * (np.log(2.0 * np.pi) + 1.0 + np.log(rss / n)) + logdet)

        return _ProfileStats(
            beta=beta,
            xt_vinv_x=xt_vinv_x,
            rss=float(rss),
            logdet=float(logdet),
            llf=float(llf),
        )

    def _neg_loglik(self, lambda_: float) -> float:
        """Optimization objective: negative profiled log-likelihood."""
        try:
            stats = self._profile_stats(lambda_)
        except (np.linalg.LinAlgError, ValueError, ToytreeError, ZeroDivisionError):
            return np.inf
        return np.inf if not np.isfinite(stats.llf) else -float(stats.llf)

    def fit(self, lambda_: float | None = None) -> PGLSResult:
        """Fit the linear PGLS model with fixed or optimized Pagel's lambda."""
        upper = float(_max_lambda(self.tree))
        if not np.isfinite(upper) or upper <= 0:
            raise ToytreeError("Could not determine a valid upper bound for lambda.")
        bounds = (0.0, upper)

        if lambda_ is None:
            eps = 1e-12
            opt = minimize_scalar(
                self._neg_loglik,
                bounds=(
                    bounds[0] + eps,
                    bounds[1] - eps if bounds[1] > eps else bounds[1],
                ),
                method="bounded",
            )
            if (not opt.success) or (not np.isfinite(float(opt.x))):
                raise ToytreeError(f"Failed to optimize lambda for pgls: {opt.message}")
            lambda_hat = float(opt.x)
            lambda_optimized = True
            optimizer_message = str(opt.message)
            converged = bool(opt.success)
        else:
            if not np.isfinite(float(lambda_)):
                raise ToytreeError("lambda_ must be a finite float or None.")
            lambda_hat = float(lambda_)
            if lambda_hat < bounds[0] or lambda_hat > bounds[1]:
                raise ToytreeError(
                    f"lambda_ must be between 0 and max_lambda(tree)={upper:.6g}."
                )
            lambda_optimized = False
            optimizer_message = ""
            converged = True

        stats = self._profile_stats(lambda_hat)
        dof = max(self.nobs - self.ncoef, 1)
        sigma2 = float(stats.rss / dof)
        xt_vinv_x_inv = np.linalg.pinv(stats.xt_vinv_x)
        vcov = sigma2 * xt_vinv_x_inv
        params = pd.Series(stats.beta, index=self.xmat.columns, name="coef")
        vcov_df = pd.DataFrame(vcov, index=self.xmat.columns, columns=self.xmat.columns)
        bse = pd.Series(np.sqrt(np.diag(vcov_df)), index=self.xmat.columns, name="bse")
        fitted = pd.Series(
            self._X.dot(stats.beta),
            index=self.tip_labels,
            name="fitted",
        )
        resid = pd.Series(
            self._y - fitted.to_numpy(),
            index=self.tip_labels,
            name="resid",
        )

        return PGLSResult(
            params=params,
            bse=bse,
            vcov=vcov_df,
            fittedvalues=fitted,
            resid=resid,
            log_likelihood=float(stats.llf),
            sigma2=sigma2,
            lambda_=lambda_hat,
            lambda_optimized=lambda_optimized,
            lambda_bounds=bounds,
            nobs=int(self.nobs),
            response_name=self.response_name,
            design_columns=list(self.xmat.columns),
            converged=converged,
            optimizer_message=optimizer_message,
        )


@add_subpackage_method(PhyloCompAPI)
def pgls(
    tree: ToyTree,
    formula: str,
    data: pd.DataFrame | None = None,
    lambda_: float | None = None,
    y_stderr: str | Mapping | pd.Series | None = None,
    epsilon: float = 1e-12,
) -> PGLSResult:
    """Fit a linear-time phylogenetic GLS model using pruning recursions.

    This function fits a Gaussian phylogenetic linear model for a continuous
    response using a Ho and Ane (2014)-style pruning recursion to avoid
    constructing a dense tip-by-tip covariance matrix in the core likelihood
    calculations. Predictors are specified with a Patsy formula, so both
    quantitative and categorical predictors are supported. This is the
    Gaussian-response method in ``toytree.pcm``; see also ``pglm`` for
    non-Gaussian response distributions (binomial, count, positive, and
    proportion models).

    The response variable must be continuous. Categorical responses (string,
    boolean, pandas categorical, or Patsy-expanded categorical response terms)
    are rejected because they require a different model family (for example,
    phylogenetic logistic regression).

    Parameters
    ----------
    tree : ToyTree
        Rooted phylogeny with branch lengths.
    formula : str
        Patsy / statsmodels-style formula, e.g. ``"y ~ x"`` or
        ``"y ~ C(group) + x"``.
    data : pandas.DataFrame or None, default=None
        Trait table aligned to tree tips by index. Tip names are preferred.
        Tip/node idx labels are also accepted. If ``None``, tip data are read
        from the tree.
    lambda_ : float or None, default=None
        Pagel's lambda. If ``None`` (default), lambda is optimized by maximum
        likelihood. If a float is provided, it is treated as a fixed value.
    y_stderr : str or Mapping or pandas.Series or None, default=None
        Standard error (SE) for observed response values on tips. Values are
        aligned to fit tips and internally converted to observation variances
        as ``SE**2``. Missing values are treated as ``0`` (exact observation).
    epsilon : float, default=1e-12
        Positive floor used to clamp zero or negative branch lengths during the
        pruning recursion for numerical stability.

    Returns
    -------
    PGLSResult
        A fitted pruning-based PGLS result object containing coefficient
        estimates, uncertainty summaries, fitted values, residuals, and model
        metadata including the fitted Pagel's lambda.

    Raises
    ------
    ToytreeError
        If the formula is invalid, data cannot be aligned to tree tips, the
        response variable is categorical, no rows remain after Patsy removes
        missing values, ``y_stderr`` is invalid, the lambda value is invalid,
        or lambda optimization fails.

    Notes
    -----
    The tree is internally rescaled to root height 1.0 before fitting to
    stabilize comparisons and lambda optimization. Tip rows dropped by Patsy
    are pruned from a temporary tree so the pruning engine operates only on the
    observed rows retained in the design matrix.

    See Also
    --------
    infer_node_states_pgls
        Fit a Gaussian PGLS model and infer/impute response states on tips and
        internal nodes using conditional Gaussian prediction.
    pglm
        Pruning-based phylogenetic generalized linear model for non-Gaussian
        response families.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=20, seed=123)
    >>> dat = tree.pcm.simulate_multivariate_continuous_trait(model="bm", params=np.diag([0.5, 1.0]), tips_only=True, seed=123)
    >>> fit = tree.pcm.pgls("t0 ~ t1", data=dat)
    >>> fit.params.index.tolist()
    ['Intercept', 't1']
    >>> fit.lambda_ >= 0
    True
    """
    fit_tree, ymat, xmat, y_obs_var = _prepare_pgls_inputs(
        tree=tree,
        formula=formula,
        data=data,
        y_stderr=y_stderr,
        epsilon=epsilon,
    )
    model = PGLSPruningModel(
        fit_tree,
        ymat,
        xmat,
        y_obs_var=y_obs_var,
        epsilon=epsilon,
    )
    fit = model.fit(lambda_=lambda_)
    return fit


def _example(
    sigma2: float = 0.5,
    lambda_: float = 0.75,
    intercept: float = 1,
    slope: float = 2,
    ntips: int = 100,
):
    """Run a quick manual smoke test for the pruning-based PGLS fitter."""
    import toytree

    rng = np.random.default_rng(123)
    tree = toytree.rtree.unittree(ntips=ntips, treeheight=1.0, seed=123)

    # Simulate a predictor and a phylogenetically correlated response for a
    # quick sanity check of fitting and repr output.
    x = rng.normal(0.0, 1.0, tree.ntips)
    vcv = tree.pcm.get_vcv_matrix_from_tree()
    vcv_lam = vcv.copy()
    mask = ~np.eye(vcv.shape[0], dtype=bool)
    vcv_lam[mask] *= lambda_

    eps = rng.multivariate_normal(np.zeros(tree.ntips), vcv_lam * sigma2)
    y = intercept + slope * x + eps

    df = pd.DataFrame({"x": x, "y": y}, index=tree.get_tip_labels())
    fit = pgls(tree, "y ~ x", data=df)
    print(fit)

    # validation against alternate implementation
    fitm = tree.pcm.pgls_matrix("y ~ x", data=df, lambda_=fit.lambda_)
    print(
        "\nValidation\nmatrix_vs_pruning_coef_diff:",
        fitm.params.values - fit.params.values,
    )


if __name__ == "__main__":
    _example()
