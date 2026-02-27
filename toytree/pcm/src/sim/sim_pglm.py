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
from patsy import PatsyError, dmatrix

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.phylolinalg._glm_families import get_family_spec
from toytree.pcm.src.phylolinalg.pgls import _coerce_tip_dataframe
from toytree.pcm.src.sim.sim_continuous import simulate_continuous_trait
from toytree.pcm.src.traits.phylosignal_lambda import edges_transform_lambda, max_λ
from toytree.utils.src.exceptions import ToytreeError

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["simulate_pglm_trait"]


def _merge_tip_predictor_data(
    tree: ToyTree,
    data: pd.DataFrame | None,
) -> pd.DataFrame:
    """Return tip predictors with DataFrame values overriding tree features."""
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
    """Return response name and Patsy design matrix from formula RHS."""
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
            f"Invalid formula or data for simulate_pglm_trait: {exc}"
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
    seed: int | np.random.Generator | None = None,
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
        Tree defining phylogenetic covariance for latent residual simulation.
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
        Pagel's lambda for latent residual covariance.
    sigma2 : float, default=0.5
        Brownian variance rate for latent residual simulation.
    data : pandas.DataFrame or None, default=None
        Optional predictor table alignable to tree tips. Shared columns override
        tree-stored tip features.
    return_latent : bool, default=False
        If True, return a DataFrame with sampled response and latent columns
        ``eta`` and ``mu``. If False, return only sampled response values.
    seed : int | numpy.random.Generator | None, default=None
        Seed or random-number generator.

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
    """
    if not isinstance(formula, str) or not formula.strip():
        raise ToytreeError("formula must be a non-empty str.")
    if not np.isfinite(float(sigma2)) or float(sigma2) <= 0:
        raise ToytreeError("sigma2 must be a finite float > 0.")
    if not np.isfinite(float(lambda_)):
        raise ToytreeError("lambda_ must be a finite float.")

    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)

    # Work on a scaled copy so lambda bounds/transform match pglm and pgls APIs.
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

    spec, _ = get_family_spec(
        family=family,
        link=link,
        family_params=family_params,
        response=None,
        response_name=ycol,
    )

    if spec.family in {"negative_binomial", "gamma", "beta"}:
        _require_dispersion_param(spec.family, spec.family_params)

    mu_fixed = xmat.to_numpy(dtype=float) @ beta_vec
    sim_tree = edges_transform_lambda(work_tree, lambda_val, inplace=False)
    eps = simulate_continuous_trait(
        sim_tree,
        model="bm",
        params=float(sigma2),
        root_state=0.0,
        name="epsilon",
        tips_only=True,
        seed=rng,
    )
    eps.index = sim_tree.get_tip_labels()
    eps = eps.loc[xmat.index]
    eta = mu_fixed + eps.to_numpy(dtype=float)
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
