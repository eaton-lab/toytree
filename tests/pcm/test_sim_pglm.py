#!/usr/bin/env python

"""Tests for phylogenetic GLM response simulation."""

import numpy as np
import pandas as pd
import pytest

from toytree import ToytreeError
from toytree.pcm.src.traits.phylosignal_lambda import max_λ


@pytest.fixture
def tree(make_unittree):
    """Return reusable tree fixture."""
    return make_unittree(ntips=24, treeheight=1.0, seed=123)


@pytest.fixture
def data(tree, rng_factory, tip_labels):
    """Return predictor data aligned to tip labels."""
    rng = rng_factory(123)
    return pd.DataFrame(
        {
            "x": rng.normal(size=tree.ntips),
            "xpos": rng.uniform(0.25, 1.5, size=tree.ntips),
            "group": np.where(np.arange(tree.ntips) % 2 == 0, "A", "B"),
        },
        index=tip_labels(tree),
    )


def test_simulate_pglm_trait_binomial_returns_binary_series(tree, data):
    """Simulate Bernoulli responses under binomial-logit."""
    out = tree.pcm.simulate_pglm_trait(
        formula="y ~ x + C(group)",
        betas={"Intercept": 0.2, "x": 0.8, "C(group)[T.B]": -0.3},
        family="binomial",
        link="logit",
        data=data,
        lambda_=0.7,
        sigma2=0.3,
        seed=10,
    )
    assert isinstance(out, pd.Series)
    assert out.name == "y"
    assert set(out.unique()).issubset({0, 1})


def test_simulate_pglm_trait_return_latent_dataframe(tree, data):
    """Return eta and mu columns when return_latent is enabled."""
    out = tree.pcm.simulate_pglm_trait(
        formula="y ~ x",
        betas={"Intercept": -0.1, "x": 0.5},
        family="binomial",
        link="logit",
        data=data,
        return_latent=True,
        seed=11,
    )
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ["y", "eta", "mu"]
    assert ((out["mu"] > 0) & (out["mu"] < 1)).all()


def test_simulate_pglm_trait_poisson_and_negative_binomial_outputs(tree, data):
    """Simulate non-negative integer responses for count families."""
    pois = tree.pcm.simulate_pglm_trait(
        formula="y ~ x",
        betas={"Intercept": 0.3, "x": 0.4},
        family="poisson",
        link="log",
        data=data,
        lambda_=0.5,
        sigma2=0.2,
        seed=12,
    )
    assert np.issubdtype(pois.dtype, np.integer)
    assert (pois >= 0).all()

    nb = tree.pcm.simulate_pglm_trait(
        formula="y ~ x",
        betas={"Intercept": 0.1, "x": 0.3},
        family="negative_binomial",
        link="log",
        family_params={"alpha": 0.7},
        data=data,
        lambda_=0.5,
        sigma2=0.2,
        seed=13,
    )
    assert np.issubdtype(nb.dtype, np.integer)
    assert (nb >= 0).all()


def test_simulate_pglm_trait_gamma_and_beta_outputs(tree, data):
    """Simulate domain-valid responses for gamma and beta families."""
    gamma_log = tree.pcm.simulate_pglm_trait(
        formula="y ~ xpos",
        betas={"Intercept": 0.3, "xpos": 0.2},
        family="gamma",
        link="log",
        family_params={"dispersion": 0.4},
        data=data,
        lambda_=0.3,
        sigma2=0.05,
        seed=14,
    )
    assert (gamma_log > 0).all()

    gamma_inv = tree.pcm.simulate_pglm_trait(
        formula="y ~ xpos",
        betas={"Intercept": 2.0, "xpos": 0.3},
        family="gamma",
        link="inverse",
        family_params={"dispersion": 0.6},
        data=data,
        lambda_=0.0,
        sigma2=0.001,
        seed=15,
    )
    assert (gamma_inv > 0).all()

    beta = tree.pcm.simulate_pglm_trait(
        formula="y ~ x",
        betas={"Intercept": 0.0, "x": 0.5},
        family="beta",
        link="logit",
        family_params={"phi": 20.0},
        data=data,
        lambda_=0.5,
        sigma2=0.2,
        seed=16,
    )
    assert ((beta > 0) & (beta < 1)).all()


def test_simulate_pglm_trait_required_family_params(tree, data):
    """Require concrete dispersion/precision inputs for simulation."""
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.1, "x": 0.2},
            family="negative_binomial",
            link="log",
            data=data,
            seed=17,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.1, "x": 0.2},
            family="gamma",
            link="log",
            data=data,
            seed=18,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.1, "x": 0.2},
            family="beta",
            link="logit",
            data=data,
            seed=19,
        )


def test_simulate_pglm_trait_beta_key_validation_and_lambda_bounds(tree, data):
    """Reject invalid beta key maps and out-of-range lambda values."""
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x + C(group)",
            betas={"Intercept": 0.0, "x": 1.0},
            family="binomial",
            link="logit",
            data=data,
            seed=20,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
            lambda_=-0.1,
            seed=21,
        )


def test_simulate_pglm_trait_formula_validation(tree, data):
    """Reject malformed formulas before simulation."""
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ ",
            betas={"Intercept": 0.0},
            family="binomial",
            link="logit",
            data=data,
        )


def test_simulate_pglm_trait_sigma2_and_lambda_finite_validation(tree, data):
    """Reject invalid sigma2 and non-finite lambda values."""
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
            sigma2=0.0,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
            sigma2=np.inf,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
            lambda_=np.nan,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
            lambda_=np.inf,
        )


def test_simulate_pglm_trait_lambda_upper_bound_validation(tree, data):
    """Reject lambda values above max_λ(tree)."""
    upper = float(max_λ(tree.mod.edges_scale_to_root_height(1.0)))
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=data,
            lambda_=upper + 1e-3,
        )


def test_simulate_pglm_trait_tip_data_override_smoke(tree, data):
    """Allow predictor table values to override tree-stored tip features."""
    # Store baseline feature on tree then override in data; simulation should run.
    tree = tree.set_node_data(
        "x",
        {name: -999.0 for name in tree.get_tip_labels()},
        inplace=False,
    )
    out = tree.pcm.simulate_pglm_trait(
        formula="y ~ x",
        betas={"Intercept": 0.0, "x": 0.4},
        family="binomial",
        link="logit",
        data=data,
        seed=22,
    )
    assert isinstance(out, pd.Series)
    assert len(out) == tree.ntips


def test_simulate_pglm_trait_requires_two_retained_tips(tree, data):
    """Reject designs that retain fewer than two rows after NA dropping."""
    bad = data.copy()
    bad["x"] = np.nan
    bad.iloc[0, bad.columns.get_loc("x")] = 0.5
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pglm_trait(
            formula="y ~ x",
            betas={"Intercept": 0.0, "x": 0.4},
            family="binomial",
            link="logit",
            data=bad,
        )
