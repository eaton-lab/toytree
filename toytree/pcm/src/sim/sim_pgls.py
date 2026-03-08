#!/usr/bin/env python

"""Simulate quantitative responses under a Patsy-specified PGLS model.

The simulator uses a two-part evolutionary data-generating process:
``Y = X @ beta + epsilon``. The fixed-effects component ``X @ beta`` is built
from tip-level predictors using Patsy, while ``epsilon`` is a continuous trait
simulated under Brownian motion on a Pagel-lambda transformed tree.

This setup is useful for benchmarking PGLS implementations because both
regression coefficients and phylogenetic signal are known by construction.

Examples
--------
Generate tip predictors on the tree, then simulate a PGLS response:

>>> import toytree
>>> tree = toytree.rtree.unittree(ntips=40, seed=123)
>>> tree.pcm.simulate_continuous_trait(
...     model="bm",
...     params=0.5,
...     name="x1",
...     tips_only=True,
...     inplace=True,
...     seed=1,
... )
>>> tree.pcm.simulate_discrete_trait(
...     nstates=2,
...     model="ER",
...     rate_scalar=0.8,
...     trait_name="group",
...     tips_only=True,
...     inplace=True,
...     seed=2,
... )
>>> y = tree.pcm.simulate_pgls_trait(
...     formula="y ~ x1 + group",
...     betas={"Intercept": 0.0, "x1": 1.2, "group": -0.8},
...     lambda_=0.7,
...     sigma2=0.3,
...     seed=3,
... )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

import numpy as np
import pandas as pd
from patsy import PatsyError, dmatrix

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.phylolinalg.pgls import _coerce_tip_dataframe
from toytree.pcm.src.sim.sim_continuous import simulate_continuous_trait
from toytree.pcm.src.traits.phylosignal_lambda import edges_transform_lambda, max_λ
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["simulate_pgls_trait"]

_SIGMA2_DETERMINISTIC_EPS = 1e-10


def _merge_tip_predictor_data(
    tree: ToyTree,
    data: pd.DataFrame | None,
) -> pd.DataFrame:
    """Return a tip-aligned predictor table with data overriding tree features."""
    base = tree.get_tip_data().set_index("name")
    if data is None:
        return base
    aligned = _coerce_tip_dataframe(tree, data)
    merged = base.copy()
    for col in aligned.columns:
        merged[col] = aligned[col]
    return merged


def _build_design_for_sim(
    formula: str,
    tip_data: pd.DataFrame,
) -> tuple[str, pd.DataFrame]:
    """Return response name and Patsy RHS design matrix."""
    if "~" not in formula:
        raise ToytreeError("formula must include '~' with response and predictors.")
    lhs, rhs = formula.split("~", 1)
    response_name = lhs.strip()
    if not response_name:
        raise ToytreeError("formula must include a non-empty response name.")
    rhs = rhs.strip()
    if not rhs:
        raise ToytreeError("formula must include predictors on the right-hand side.")
    try:
        xmat = dmatrix(rhs, data=tip_data, return_type="dataframe")
    except PatsyError as exc:
        raise ToytreeError(
            f"Invalid formula or data for simulate_pgls_trait: {exc}"
        ) from exc
    if xmat.shape[0] == 0:
        raise ToytreeError(
            "No rows remain after applying formula and dropping missing values."
        )
    if xmat.shape[0] < 2:
        raise ToytreeError("At least two retained tips are required for simulation.")
    return response_name, xmat


def _coerce_beta_vector(
    xmat: pd.DataFrame,
    betas: Mapping[str, float],
) -> np.ndarray:
    """Return beta vector ordered to design columns with strict key matching."""
    if not isinstance(betas, Mapping):
        raise ToytreeError("betas must be a mapping from design-term names to values.")
    colnames = list(xmat.columns)
    bkeys = set(str(i) for i in betas)
    xkeys = set(colnames)
    missing = sorted(xkeys - bkeys)
    extra = sorted(bkeys - xkeys)
    if missing or extra:
        chunks = []
        if missing:
            chunks.append(f"missing beta keys: {missing}")
        if extra:
            chunks.append(f"unexpected beta keys: {extra}")
        raise ToytreeError(
            "betas keys must match Patsy design columns; " + "; ".join(chunks)
        )
    return np.asarray([float(betas[name]) for name in colnames], dtype=float)


@add_subpackage_method(PhyloCompAPI)
def simulate_pgls_trait(
    tree: ToyTree,
    formula: str,
    betas: Mapping[str, float],
    lambda_: float = 1.0,
    sigma2: float = 1.0,
    data: pd.DataFrame | None = None,
    seed: int | np.random.Generator | None = None,
) -> pd.Series:
    """Return a simulated quantitative response from a PGLS data-generating model.

    The simulator builds deterministic expectations from a Patsy design matrix
    (``X @ beta``) and adds phylogenetic residual variation drawn under BM on a
    lambda-transformed tree. Conceptually, fixed effects set expected trait
    means, and Brownian residual evolution induces covariance among related
    tips as controlled by ``lambda_`` and ``sigma2``.

    Parameters
    ----------
    tree : ToyTree
        Tree used to define phylogenetic covariance for residual simulation.
    formula : str
        Patsy-style formula with a single response, e.g. ``"y ~ x1 + C(group)"``.
    betas : Mapping[str, float]
        Ground-truth coefficients keyed by Patsy-expanded design column names
        (e.g., ``"Intercept"``, ``"x1"``, ``"C(group)[T.B]"``).
    lambda_ : float, default=1.0
        Pagel's lambda for residual covariance. Must satisfy
        ``0 <= lambda_ <= max_λ(tree)``.
    sigma2 : float, default=1.0
        Brownian variance rate for residual simulation.
    data : pandas.DataFrame or None, default=None
        Optional predictor table alignable to tree tips. If both tree tip
        features and ``data`` provide a predictor, ``data`` values override.
    seed : int | numpy.random.Generator | None, default=None
        Seed or random-number generator.

    Returns
    -------
    pandas.Series
        Simulated response values indexed by retained tip labels (after Patsy
        row dropping). The series name is the response variable label.

    Raises
    ------
    ToytreeError
        If inputs are invalid, lambda bounds are violated, Patsy parsing fails,
        beta names do not match design columns, or too few rows remain.

    Examples
    --------
    Simulate predictors directly on the tree and use them in the formula:

    >>> import toytree
    >>> tree = toytree.rtree.unittree(ntips=30, seed=10)
    >>> tree.pcm.simulate_continuous_trait(
    ...     model="bm",
    ...     params=1.0,
    ...     name="size",
    ...     tips_only=True,
    ...     inplace=True,
    ...     seed=11,
    ... )
    >>> tree.pcm.simulate_discrete_trait(
    ...     nstates=2,
    ...     model="ER",
    ...     trait_name="ecotype",
    ...     tips_only=True,
    ...     inplace=True,
    ...     seed=12,
    ... )
    >>> y = tree.pcm.simulate_pgls_trait(
    ...     formula="y ~ size + ecotype",
    ...     betas={"Intercept": 0.5, "size": 1.0, "ecotype": -0.3},
    ...     lambda_=0.6,
    ...     sigma2=0.4,
    ...     seed=13,
    ... )

    Use a DataFrame to override or provide predictor values:

    >>> import pandas as pd
    >>> data = pd.DataFrame(
    ...     {"size": np.linspace(-1.0, 1.0, tree.ntips)},
    ...     index=tree.get_tip_labels(),
    ... )
    >>> y2 = tree.pcm.simulate_pgls_trait(
    ...     formula="y2 ~ size",
    ...     betas={"Intercept": 0.2, "size": -1.0},
    ...     data=data,
    ...     sigma2=0.2,
    ...     seed=14,
    ... )
    """
    if not isinstance(formula, str) or not formula.strip():
        raise ToytreeError("formula must be a non-empty str.")
    sigma2_val = float(sigma2)
    if not np.isfinite(sigma2_val) or sigma2_val <= 0:
        raise ToytreeError("sigma2 must be a finite float > 0.")
    if not np.isfinite(float(lambda_)):
        raise ToytreeError("lambda_ must be a finite float.")

    # Work on a scaled copy so lambda bounds/transform match the PGLS fit API.
    work_tree = tree.mod.edges_scale_to_root_height(1.0)
    for node in work_tree:
        if node._dist <= 0:
            node._dist = 1e-12
    work_tree._update()

    max_lambda = float(max_λ(work_tree))
    lambda_val = float(lambda_)
    if lambda_val < 0.0 or lambda_val > max_lambda:
        raise ToytreeError(
            f"lambda_ must be between 0 and max_λ(tree)={max_lambda:.6g}."
        )

    tip_data = _merge_tip_predictor_data(work_tree, data)
    ycol, xmat = _build_design_for_sim(formula, tip_data)
    beta_vec = _coerce_beta_vector(xmat, betas)

    mu = xmat.to_numpy(dtype=float) @ beta_vec
    if sigma2_val <= _SIGMA2_DETERMINISTIC_EPS:
        return pd.Series(mu, index=xmat.index, name=ycol)

    sim_tree = edges_transform_lambda(work_tree, lambda_val, inplace=False)
    eps = simulate_continuous_trait(
        sim_tree,
        model="bm",
        params=sigma2_val,
        root_state=0.0,
        name="epsilon",
        tips_only=True,
        seed=seed,
    )
    eps.index = sim_tree.get_tip_labels()
    eps = eps.loc[xmat.index]
    out = pd.Series(mu + eps.to_numpy(dtype=float), index=xmat.index, name=ycol)
    return out
