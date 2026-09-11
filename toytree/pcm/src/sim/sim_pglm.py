#!/usr/bin/env python

"""Simulate non-Gaussian responses under a pruning-style PGLM model.

This simulator generates response traits on the same latent structure used by
phylogenetic generalized linear models:

``eta = X @ beta + epsilon``

where ``epsilon`` is Brownian residual variation on a Pagel-lambda transformed
tree. The latent predictor is mapped to a mean scale via the selected inverse
link, then sampled from the requested response family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

import numpy as np
import pandas as pd

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.phylolinalg._glm_families import get_family_spec
from toytree.pcm.src.sim._regression_sim_shared import (
    build_simulation_design,
    coerce_beta_vector,
    merge_tip_predictor_data,
    simulate_phylogenetic_residual,
)
from toytree.pcm.src.sim._utils import RNGSeed, get_rng, validate_bool
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["simulate_pglm_trait"]


def _require_dispersion_param(
    family: str,
    family_params: dict[str, float] | None,
) -> float:
    """Return required dispersion/precision scalar for simulation families."""
    key_map = {
        "negative_binomial": "alpha",
        "gamma": "dispersion",
        "beta": "phi",
    }
    if family not in key_map:
        raise ToytreeError(
            f"Internal error: no required family param map for {family}."
        )
    key = key_map[family]
    if family_params is None or key not in family_params:
        raise ToytreeError(
            f"simulate_pglm_trait requires family_params={{'{key}': <positive float>}} "
            f"for family='{family}'."
        )
    val = float(family_params[key])
    if (not np.isfinite(val)) or val <= 0:
        raise ToytreeError(f"simulate_pglm_trait requires family_params['{key}'] > 0.")
    return val


def _sample_from_family(
    rng: np.random.Generator,
    family: str,
    mu: np.ndarray,
    family_params: dict[str, float] | None,
) -> np.ndarray:
    """Return sampled response values for a validated family and means."""
    if family == "binomial":
        return rng.binomial(n=1, p=mu, size=mu.size).astype(int)
    if family == "poisson":
        return rng.poisson(lam=mu, size=mu.size).astype(int)
    if family == "negative_binomial":
        alpha = _require_dispersion_param(family, family_params)
        n = 1.0 / alpha
        p = 1.0 / (1.0 + alpha * mu)
        return rng.negative_binomial(n=n, p=p, size=mu.size).astype(int)
    if family == "gamma":
        dispersion = _require_dispersion_param(family, family_params)
        shape = 1.0 / dispersion
        scale = mu * dispersion
        return rng.gamma(shape=shape, scale=scale, size=mu.size)
    if family == "beta":
        phi = _require_dispersion_param(family, family_params)
        a = np.clip(mu * phi, 1e-12, None)
        b = np.clip((1.0 - mu) * phi, 1e-12, None)
        return rng.beta(a=a, b=b, size=mu.size)
    raise ToytreeError(f"Unsupported simulation family '{family}'.")


@add_subpackage_method(PhyloCompAPI)
def simulate_pglm_trait(
    tree: ToyTree,
    formula: str,
    betas: Mapping[str, float],
    family: str = "binomial",
    link: str = "logit",
    family_params: dict[str, float] | None = None,
    lambda_: float = 1.0,
    sigma2: float = 0.5,
    data: pd.DataFrame | None = None,
    return_latent: bool = False,
    seed: RNGSeed = None,
) -> pd.Series | pd.DataFrame:
    """Return simulated response values from a phylogenetic GLM process.

    The simulator follows a latent-variable phylogenetic GLM process:
    ``eta = X @ beta + epsilon``, where ``epsilon`` is Brownian residual noise
    on a lambda-transformed tree. Response means are computed by the
    family-specific inverse link and final observations are sampled from the
    requested family distribution.

    Parameters
    ----------
    tree : ToyTree
        Rooted tree defining latent phylogenetic covariance. A working copy is
        scaled to root height one, so uniformly rescaling the input tree does
        not change the generated response distribution.
    formula : str
        Patsy-style formula with a single response label on the left side.
    betas : Mapping[str, float]
        Coefficients keyed by Patsy-expanded design column names.
    family : str, default="binomial"
        GLM family name. Supported simulation paths are ``binomial``/``bernoulli``
        with ``logit``, ``poisson`` with ``log``, ``negative_binomial`` with
        ``log``, ``gamma`` with ``log`` or ``inverse``, and ``beta`` with
        ``logit``.
    link : str, default="logit"
        Link function used with the selected family.
    family_params : dict[str, float] or None, default=None
        Family-specific parameters. Required for simulation when ``family`` is
        ``negative_binomial`` (``alpha``), ``gamma`` (``dispersion``), or
        ``beta`` (``phi``).
    lambda_ : float, default=1.0
        Pagel's lambda for latent residual covariance on the normalized tree.
        It scales shared covariance while preserving tip variances and must be
        within the tree-specific valid interval.
    sigma2 : float, default=0.5
        Nonnegative latent residual variance on the root-height-one working-tree
        scale. Zero removes the phylogenetic residual but response sampling
        remains stochastic.
    data : pandas.DataFrame or None, default=None
        Optional predictor table alignable to tree tips. Shared columns override
        tree-stored tip features.
    return_latent : bool, default=False
        If True, return a DataFrame with sampled response and latent columns
        ``eta`` and ``mu``. If False, return only sampled response values.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place by
        both latent residual and response sampling.

    Returns
    -------
    pandas.Series or pandas.DataFrame
        Simulated response indexed by retained tip labels. If
        ``return_latent=True``, includes additional ``eta`` and ``mu`` columns.

    Raises
    ------
    ToytreeError
        If formula parsing fails, beta names do not match design columns, family
        or link settings are invalid, required family parameters are missing,
        lambda bounds are violated, or latent means fall outside family domains.

    Notes
    -----
    This function is an exact generator for the stated latent phylogenetic GLM:
    it samples one Gaussian phylogenetic residual, applies the inverse link,
    and then samples the response conditionally. The current ``pglm`` fitter is
    a pruning-based IRLS approximation rather than the exact integrated latent
    likelihood. Simulation-to-fit studies should therefore quantify estimator
    bias and coverage instead of expecting algebraic parameter recovery.
    """
    return_latent = validate_bool(return_latent, "return_latent")
    rng = get_rng(seed)
    tip_data = merge_tip_predictor_data(tree, data)
    ycol, xmat = build_simulation_design(
        formula, tip_data, method_name="simulate_pglm_trait"
    )
    beta_vec = coerce_beta_vector(xmat, betas)

    spec, _ = get_family_spec(
        family=family,
        link=link,
        family_params=family_params,
        response=None,
        response_name=ycol,
    )

    if spec.family in {"negative_binomial", "gamma", "beta"}:
        _require_dispersion_param(spec.family, spec.family_params)

    eta_fixed = xmat.to_numpy(dtype=float) @ beta_vec
    residual = simulate_phylogenetic_residual(
        tree,
        lambda_=lambda_,
        sigma2=sigma2,
        retained_tips=xmat.index,
        seed=rng,
    )
    eta = eta_fixed + residual.to_numpy(dtype=float)
    mu = spec.inv_link(eta)
    spec.validate_mu(mu)

    y = _sample_from_family(rng, spec.family, mu, spec.family_params)
    out = pd.Series(y, index=xmat.index, name=ycol)
    if not return_latent:
        return out

    out_df = pd.DataFrame(index=xmat.index)
    out_df[ycol] = out
    out_df["eta"] = eta
    out_df["mu"] = mu
    return out_df
