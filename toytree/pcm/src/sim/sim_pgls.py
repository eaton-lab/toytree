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
...     name="group",
...     tips_only=True,
...     inplace=True,
...     seed=2,
... )
>>> y = tree.pcm.simulate_pgls_trait(
...     formula="y ~ x1 + group",
...     betas={"Intercept": 0.0, "x1": 1.2, "group[T.B]": -0.8},
...     lambda_=0.7,
...     sigma2=0.3,
...     seed=3,
... )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

import pandas as pd

from toytree.core.apis import PhyloCompAPI, add_subpackage_method
from toytree.pcm.src.sim._regression_sim_shared import (
    build_simulation_design,
    coerce_beta_vector,
    merge_tip_predictor_data,
    simulate_phylogenetic_residual,
)
from toytree.pcm.src.sim._utils import RNGSeed, get_rng

if TYPE_CHECKING:
    from toytree.core import ToyTree

__all__ = ["simulate_pgls_trait"]


@add_subpackage_method(PhyloCompAPI)
def simulate_pgls_trait(
    tree: ToyTree,
    formula: str,
    betas: Mapping[str, float],
    lambda_: float = 1.0,
    sigma2: float = 1.0,
    data: pd.DataFrame | None = None,
    seed: RNGSeed = None,
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
        Rooted tree used to define phylogenetic covariance. A working copy is
        scaled to root height one, so multiplying every input branch length by
        the same positive constant does not change the response distribution.
    formula : str
        Patsy-style formula with a single response, e.g. ``"y ~ x1 + C(group)"``.
    betas : Mapping[str, float]
        Ground-truth coefficients keyed by Patsy-expanded design column names
        (e.g., ``"Intercept"``, ``"x1"``, ``"C(group)[T.B]"``).
    lambda_ : float, default=1.0
        Pagel's lambda for residual covariance. Must satisfy
        ``0 <= lambda_ <= max_λ(tree)`` on the normalized working tree. It
        scales shared phylogenetic covariance while preserving tip variances.
    sigma2 : float, default=1.0
        Nonnegative residual variance on the root-height-one working-tree
        scale. A value of zero returns the deterministic mean ``X @ beta``.
    data : pandas.DataFrame or None, default=None
        Optional predictor table alignable to tree tips. If both tree tip
        features and ``data`` provide a predictor, ``data`` values override.
    seed : int, numpy.random.Generator, numpy.random.SeedSequence, or None
        Random-number source. A supplied Generator is consumed in place.

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
    ...     name="ecotype",
    ...     tips_only=True,
    ...     inplace=True,
    ...     seed=12,
    ... )
    >>> y = tree.pcm.simulate_pgls_trait(
    ...     formula="y ~ size + ecotype",
    ...     betas={"Intercept": 0.5, "size": 1.0, "ecotype[T.B]": -0.3},
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
    rng = get_rng(seed)
    tip_data = merge_tip_predictor_data(tree, data)
    ycol, xmat = build_simulation_design(
        formula, tip_data, method_name="simulate_pgls_trait"
    )
    beta_vec = coerce_beta_vector(xmat, betas)

    mu = xmat.to_numpy(dtype=float) @ beta_vec
    residual = simulate_phylogenetic_residual(
        tree,
        lambda_=lambda_,
        sigma2=sigma2,
        retained_tips=xmat.index,
        seed=rng,
    )
    out = pd.Series(mu + residual.to_numpy(dtype=float), index=xmat.index, name=ycol)
    return out
