#!/usr/bin/env python

"""Shared input and latent-residual helpers for PGLS/PGLM simulation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

import numpy as np
import pandas as pd
from patsy import PatsyError, dmatrix

from toytree.pcm.src.phylolinalg.pgls import _coerce_tip_dataframe
from toytree.pcm.src.sim._utils import (
    RNGSeed,
    get_rng,
    validate_finite_float,
    validate_nonnegative_float,
    validate_tree_for_simulation,
)
from toytree.pcm.src.sim.sim_continuous import simulate_continuous_trait
from toytree.pcm.src.traits.phylosignal_lambda import edges_transform_lambda, max_λ
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree


def merge_tip_predictor_data(
    tree: ToyTree,
    data: pd.DataFrame | None,
) -> pd.DataFrame:
    """Return tip-aligned predictors with ``data`` overriding tree features."""
    base = tree.get_tip_data().set_index("name")
    if data is None:
        return base
    aligned = _coerce_tip_dataframe(tree, data)
    merged = base.copy()
    for column in aligned.columns:
        merged[column] = aligned[column]
    return merged


def build_simulation_design(
    formula: str,
    tip_data: pd.DataFrame,
    *,
    method_name: str,
) -> tuple[str, pd.DataFrame]:
    """Return a response name and Patsy RHS design matrix."""
    if not isinstance(formula, str) or not formula.strip():
        raise ToytreeError("formula must be a non-empty str.")
    if formula.count("~") != 1:
        raise ToytreeError(
            "formula must contain one '~' separating response and predictors."
        )
    lhs, rhs = formula.split("~", 1)
    response_name = lhs.strip()
    if not response_name:
        raise ToytreeError("formula must include a non-empty response name.")
    rhs = rhs.strip()
    if not rhs:
        raise ToytreeError("formula must include predictors on the right-hand side.")
    try:
        design = dmatrix(rhs, data=tip_data, return_type="dataframe")
    except (PatsyError, NameError, TypeError, ValueError) as exc:
        raise ToytreeError(f"Invalid formula or data for {method_name}: {exc}") from exc
    if design.shape[0] == 0:
        raise ToytreeError(
            "No rows remain after applying formula and dropping missing values."
        )
    if design.shape[0] < 2:
        raise ToytreeError("At least two retained tips are required for simulation.")
    values = design.to_numpy(dtype=float)
    if not np.all(np.isfinite(values)):
        raise ToytreeError("the retained design matrix must contain finite values.")
    return response_name, design


def coerce_beta_vector(
    design: pd.DataFrame,
    betas: Mapping[str, float],
) -> np.ndarray:
    """Return finite coefficients ordered to exact Patsy design columns."""
    if not isinstance(betas, Mapping):
        raise ToytreeError("betas must be a mapping from design-term names to values.")
    if not all(isinstance(key, str) for key in betas):
        raise ToytreeError("every betas key must be a string Patsy column name.")
    if any(isinstance(value, (bool, np.bool_)) for value in betas.values()):
        raise ToytreeError("betas values must be finite floats, not Booleans.")
    columns = list(design.columns)
    beta_keys = set(betas)
    design_keys = set(columns)
    missing = sorted(design_keys - beta_keys)
    extra = sorted(beta_keys - design_keys)
    if missing or extra:
        chunks = []
        if missing:
            chunks.append(f"missing beta keys: {missing}")
        if extra:
            chunks.append(f"unexpected beta keys: {extra}")
        raise ToytreeError(
            "betas keys must match Patsy design columns; " + "; ".join(chunks)
        )
    try:
        beta = np.asarray([betas[name] for name in columns], dtype=float)
    except (TypeError, ValueError) as exc:
        raise ToytreeError("betas values must be finite floats.") from exc
    if not np.all(np.isfinite(beta)):
        raise ToytreeError("betas values must be finite floats.")
    return beta


def prepare_lambda_tree(
    tree: ToyTree,
    lambda_: float,
) -> tuple[ToyTree, float]:
    """Return the normalized working tree and validated Pagel lambda."""
    tree = validate_tree_for_simulation(tree)
    root_height = float(tree.treenode.height)
    if not np.isfinite(root_height) or root_height <= 0.0:
        raise ToytreeError("tree must have a finite positive root height.")
    lambda_value = validate_finite_float(lambda_, "lambda_")

    # Match pgls/pglm preprocessing: covariance is defined on a copy scaled to
    # root height one, with exact zero edges regularized only where the pruning
    # likelihood requires a positive conditional variance.
    work_tree = tree.mod.edges_scale_to_root_height(1.0)
    for node in work_tree[:-1]:
        if node.dist == 0.0:
            node._dist = 1e-12
    work_tree._update()

    maximum = float(max_λ(work_tree))
    if lambda_value < 0.0 or lambda_value > maximum:
        raise ToytreeError(f"lambda_ must be between 0 and max_λ(tree)={maximum:.6g}.")
    return work_tree, lambda_value


def simulate_phylogenetic_residual(
    tree: ToyTree,
    *,
    lambda_: float,
    sigma2: float,
    retained_tips: pd.Index,
    seed: RNGSeed,
) -> pd.Series:
    """Return a zero-root BM residual on the normalized lambda tree."""
    sigma2_value = validate_nonnegative_float(sigma2, "sigma2")
    work_tree, lambda_value = prepare_lambda_tree(tree, lambda_)
    if sigma2_value == 0.0:
        return pd.Series(0.0, index=retained_tips, name="epsilon")
    residual_tree = edges_transform_lambda(work_tree, lambda_value, inplace=False)
    residual = simulate_continuous_trait(
        residual_tree,
        model="bm",
        params=sigma2_value,
        root_state=0.0,
        name="epsilon",
        tips_only=True,
        seed=get_rng(seed),
    )
    residual.index = residual_tree.get_tip_labels()
    return residual.loc[retained_tips]
