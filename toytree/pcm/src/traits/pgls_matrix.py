#!/usr/bin/env python

"""Matrix-based phylogenetic generalized least squares (PGLS) using statsmodels.

This module implements Brownian-motion PGLS by fitting a generalized least
squares model with a phylogenetic variance-covariance matrix derived from a
tree. Regression design matrices are constructed from a Patsy / statsmodels
formula, and the phylogenetic covariance matrix is subset to the rows retained
after formula parsing and missing-data dropping.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pandas import CategoricalDtype
from patsy import PatsyError, dmatrices
from scipy.optimize import minimize_scalar
from statsmodels.api import GLS
from statsmodels.regression.linear_model import RegressionResultsWrapper

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["pgls_matrix"]


def _coerce_tip_dataframe(
    tree: ToyTree,
    data: pd.DataFrame | None,
) -> pd.DataFrame:
    """Return a DataFrame aligned to tree tip order and indexed by tip names."""
    tip_labels = tree.get_tip_labels()
    tip_idx = list(range(tree.ntips))

    # extract features from the tree data itself when 'data' arg is empty
    # and return as a dataframe of tip data only
    if data is None:
        data = tree.get_tip_data()
        return data.set_index("name")

    # data must be a dataframe
    if not isinstance(data, pd.DataFrame):
        raise ToytreeError("data must be a pandas DataFrame or None")

    # cannot have duplicate labels in the index
    frame = data.copy()
    if not frame.index.is_unique:
        raise ToytreeError("data index must be unique to align rows to tree tips")

    # Preferred path: explicit tip-label index (robust to row order shuffling).
    if set(tip_labels).issubset(set(frame.index)):
        frame = frame.loc[tip_labels].copy()
        frame.index = tip_labels
        return frame

    # Secondary path: integer-like node or tip idx labels, which are then
    # subset/reordered to tree tip idx order and relabeled to tip names.
    is_int_index = isinstance(frame.index, pd.RangeIndex) or np.issubdtype(
        frame.index.dtype,
        np.integer,
    )
    if is_int_index:
        if set(tip_idx).issubset(set(frame.index)):
            frame = frame.loc[tip_idx].copy()
            frame.index = tip_labels
            return frame

    raise ToytreeError(
        "Could not align data rows to tree tips. Set DataFrame index to tip names "
        "or node/tip idx labels."
    )


def _build_design_and_vcv(
    formula: str,
    tip_data: pd.DataFrame,
    vcv: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return design matrices and a phylogenetic VCV subset aligned to them."""
    try:
        ymat, xmat = dmatrices(formula, data=tip_data, return_type="dataframe")
    except PatsyError as exc:
        raise ToytreeError(f"Invalid formula or data for pgls_matrix: {exc}") from exc

    # Patsy drops rows with missing values used by the formula. Subset the
    # Brownian VCV to those exact rows, then apply lambda on this retained set.
    row_labels = ymat.index
    vcv_subset = vcv.loc[row_labels, row_labels].copy()
    return ymat, xmat, vcv_subset


def _lambda_transform_vcv(vcv: np.ndarray, lambda_: float) -> np.ndarray:
    """Return a Pagel's lambda transformed covariance matrix."""
    mat = np.asarray(vcv, dtype=float).copy()
    # Pagel's lambda scales shared-history covariance (off-diagonals) while
    # leaving tip variances (diagonal terms) unchanged.
    mask = ~np.eye(mat.shape[0], dtype=bool)
    mat[mask] *= float(lambda_)
    return mat


def _max_lambda(tree: ToyTree) -> float:
    """Return the maximum valid Pagel's lambda for a tree."""
    # This mirrors the bound used in the phylogenetic-signal lambda estimator,
    # but is implemented locally to avoid a circular import through toytree.pcm.
    root_to_tip_dists = tree.distance.get_node_distance_matrix()[-1]
    internal_dists = root_to_tip_dists[tree.ntips :]
    return float(tree.treenode.height / max(internal_dists))


def _fit_gls_for_lambda(
    ymat: pd.DataFrame,
    xmat: pd.DataFrame,
    vcv_df: pd.DataFrame,
    lambda_: float,
) -> RegressionResultsWrapper:
    """Fit a GLS model using a lambda-transformed phylogenetic covariance."""
    sigma = _lambda_transform_vcv(vcv_df.to_numpy(dtype=float), lambda_)
    return GLS(ymat, xmat, sigma=sigma).fit()


def _neg_loglik_pgls_lambda(
    lambda_: float,
    ymat: pd.DataFrame,
    xmat: pd.DataFrame,
    vcv_df: pd.DataFrame,
) -> float:
    """Return negative log-likelihood for a candidate lambda value."""
    try:
        fit = _fit_gls_for_lambda(ymat, xmat, vcv_df, lambda_)
    except (np.linalg.LinAlgError, ValueError):
        return np.inf
    llf = float(fit.llf)
    return np.inf if not np.isfinite(llf) else -llf


def _estimate_pgls_lambda(
    tree: ToyTree,
    ymat: pd.DataFrame,
    xmat: pd.DataFrame,
    vcv_df: pd.DataFrame,
) -> tuple[float, tuple[float, float]]:
    """Estimate Pagel's lambda by bounded ML optimization."""
    upper = float(_max_lambda(tree))
    if not np.isfinite(upper) or upper <= 0:
        raise ToytreeError("Could not determine a valid upper bound for lambda.")
    bounds = (0.0, upper)
    eps = 1e-12
    fit = minimize_scalar(
        _neg_loglik_pgls_lambda,
        args=(ymat, xmat, vcv_df),
        bounds=(bounds[0] + eps, bounds[1] - eps if bounds[1] > eps else bounds[1]),
        method="bounded",
    )
    if (not fit.success) or (not np.isfinite(float(fit.x))):
        raise ToytreeError(f"Failed to optimize lambda for pgls_matrix: {fit.message}")
    return float(fit.x), bounds


def _check_response_is_continuous(
    formula: str,
    tip_data: pd.DataFrame,
    ymat: pd.DataFrame,
) -> None:
    """Raise if the dependent variable is categorical."""
    lhs = formula.split("~", 1)[0].strip()

    # Patsy may expand a categorical response to multiple columns. PGLS here is
    # implemented for a single continuous response only.
    if ymat.shape[1] != 1:
        raise ToytreeError(
            "pgls_matrix is not suitable for categorical dependent variables (Y); "
            "consider phylogenetic logistic regression."
        )

    if lhs in tip_data.columns:
        series = tip_data[lhs]
        if isinstance(series.dtype, CategoricalDtype):
            raise ToytreeError(
                "pgls_matrix is not suitable for categorical dependent variables (Y); "
                "consider phylogenetic logistic regression."
            )
        if pd.api.types.is_bool_dtype(series):
            raise ToytreeError(
                "pgls_matrix is not suitable for categorical dependent variables (Y); "
                "consider phylogenetic logistic regression."
            )
        if pd.api.types.is_object_dtype(series):
            non_missing = series.dropna()
            if non_missing.empty or non_missing.map(lambda x: isinstance(x, str)).all():
                raise ToytreeError(
                    "pgls_matrix is not suitable for categorical dependent "
                    "variables (Y); "
                    "consider phylogenetic logistic regression."
                )

    if not np.issubdtype(ymat.dtypes.iloc[0], np.number):
        raise ToytreeError(
            "pgls_matrix is not suitable for categorical dependent variables (Y); "
            "consider phylogenetic logistic regression."
        )


@add_subpackage_method(PhyloCompAPI)
def pgls_matrix(
    tree: ToyTree,
    formula: str,
    data: pd.DataFrame | None = None,
    lambda_: float | None = None,
) -> RegressionResultsWrapper:
    """Fit a Brownian-motion phylogenetic GLS regression model.

    This function fits a generalized least squares model using
    :class:`statsmodels.regression.linear_model.GLS` with a phylogenetic
    covariance matrix derived from the input tree. A Brownian-motion VCV is
    computed from the tree, then optionally transformed by Pagel's lambda
    before fitting.

    The regression model is specified with a Patsy / statsmodels formula (for
    example, ``"y ~ x"`` or ``"y ~ x - 1"``). Data rows are aligned to the
    tree tips by tip-name index (preferred) or by tip/node idx labels. Patsy
    drops rows with missing values used by the formula, and the phylogenetic
    covariance matrix is subset to exactly those retained rows before fitting.

    Parameters
    ----------
    tree : ToyTree
        Tree with branch lengths. The phylogenetic covariance matrix is computed
        from this tree using ``tree.pcm.get_vcv_matrix_from_tree(df=True)``.
    formula : str
        Patsy / statsmodels regression formula. The left-hand side is the
        response and the right-hand side contains one or more predictors.
    data : pandas.DataFrame or None, default=None
        Tabular trait data. If provided, rows must be alignable to tree tips by
        tip names or tip/node idx labels. If ``None``, node data are read from
        ``tree.get_node_data()`` and tip rows are used.
    lambda_ : float or None, default=None
        Pagel's lambda parameter used to transform the phylogenetic covariance
        matrix. If ``None``, lambda is estimated by maximum likelihood over the
        interval ``[0, max_lambda(tree)]`` on the internally rescaled tree. If
        a float is provided, that fixed value is used directly.

    Returns
    -------
    statsmodels.regression.linear_model.RegressionResultsWrapper
        A fitted statsmodels GLS result object. The object includes attached
        metadata attributes ``_toytree_lambda``, ``_toytree_lambda_optimized``,
        ``_toytree_lambda_bounds``, and ``_toytree_formula``.

    Raises
    ------
    ToytreeError
        If ``formula`` is empty, if ``data`` is not a DataFrame, if data rows
        cannot be aligned to the tree tips, if Patsy formula parsing fails, or
        if the dependent variable is categorical (for example, string, boolean,
        or categorical dtype), or if ``lambda_`` is outside valid bounds for
        the tree, or if lambda optimization fails.
    ValueError
        Propagated if too few rows remain after missing-data filtering or if the
        GLS fit cannot be performed with the resulting design / covariance.

    Notes
    -----
    The tree is internally rescaled to root height ``1.0`` before fitting to
    improve comparability across trees and stabilize lambda optimization.

    PGLS is mathematically equivalent to Phylogenetic Independent Contrasts
    (PIC) if the model includes an intercept and uses a Brownian-motion VCV.

    Examples
    --------
    >>> tree = toytree.rtree.unittree(ntips=20, seed=123)
    >>> traits = tree.pcm.simulate_multivariate_continuous_trait(model="bm", params=np.diag([1.0, 2.0]), tips_only=True, seed=123)
    >>> fit = tree.pcm.pgls_matrix("t0 ~ t1", data=traits)
    >>> fit.params.index.tolist()
    ['Intercept', 't1']
    >>> 0 <= fit._toytree_lambda <= fit._toytree_lambda_bounds[1]
    True
    >>> fit_fixed = tree.pcm.pgls_matrix("t0 ~ t1", data=traits, lambda_=1.0)
    >>> fit_fixed._toytree_lambda_optimized
    False
    """
    # check that format of the formula str is valid
    if not isinstance(formula, str) or not formula.strip():
        raise ToytreeError("formula must be a non-empty str")

    # rescale tree to max-height 1.0 to make comparisons across trees similar
    # and set the min dist value to 1e-12
    tree = tree.mod.edges_scale_to_root_height(1.0)
    for node in tree:
        if node._dist <= 0:
            node._dist = 1e-12
    tree._update()

    # get dataframe of tips only
    tip_data = _coerce_tip_dataframe(tree, data)

    # get VCV from 1-scaled tree
    vcv = tree.pcm.get_vcv_matrix_from_tree(df=True)

    # Patsy parses the formula, applies coding, and drops rows with missing
    # values. We subset the Brownian VCV to the same retained tips here.
    ymat, xmat, vcv_subset = _build_design_and_vcv(formula, tip_data, vcv)
    _check_response_is_continuous(formula, tip_data, ymat)

    # ensure data exists after dropping nans
    if ymat.shape[0] == 0:
        raise ToytreeError(
            "No rows remain after applying formula and dropping missing values."
        )

    # Estimate lambda by ML unless the user provides a fixed override.
    if lambda_ is None:
        lambda_hat, bounds = _estimate_pgls_lambda(tree, ymat, xmat, vcv_subset)
        lambda_optimized = True
    else:
        upper = float(_max_lambda(tree))
        if not np.isfinite(float(lambda_)):
            raise ToytreeError("lambda_ must be a finite float or None.")
        lambda_hat = float(lambda_)
        bounds = (0.0, upper)
        if lambda_hat < bounds[0] or lambda_hat > bounds[1]:
            raise ToytreeError(
                f"lambda_ must be between 0 and max_lambda(tree)={upper:.6g}."
            )
        lambda_optimized = False

    # Fit the final GLS model using the chosen lambda-transformed covariance.
    fit = _fit_gls_for_lambda(ymat, xmat, vcv_subset, lambda_hat)
    fit._toytree_lambda = lambda_hat
    fit._toytree_lambda_optimized = lambda_optimized
    fit._toytree_lambda_bounds = bounds
    fit._toytree_formula = formula
    return fit


if __name__ == "__main__":
    import toytree

    tree = toytree.rtree.unittree(ntips=25, treeheight=1.0, seed=123)
    traits = tree.pcm.simulate_multivariate_continuous_trait(
        model="bm",
        params=np.diag([0.1, 0.001]),
        seed=123,
        tips_only=True,
        inplace=True,
    )
    model = pgls_matrix(tree, "t0 ~ t1")  # , data=traits)
    print(model.summary())
