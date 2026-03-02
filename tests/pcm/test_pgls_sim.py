#!/usr/bin/env python

"""Tests for PGLS response simulation under Patsy formulas."""

import numpy as np
import pandas as pd
import pytest
from patsy import dmatrix

from toytree.utils import ToytreeError


@pytest.fixture
def tree(make_unittree):
    """Create a reproducible test tree."""
    return make_unittree(ntips=18, treeheight=1.0, seed=123)


@pytest.fixture
def tips(tree, tip_labels):
    """Return tip labels in tree order."""
    return tip_labels(tree)


@pytest.fixture
def data(tree, tips):
    """Create reproducible predictor data aligned to tree tips."""
    rng = np.random.default_rng(12)
    return pd.DataFrame(
        {
            "x1": rng.normal(0, 1, tree.ntips),
            "group": rng.choice(["A", "B"], tree.ntips),
        },
        index=tips,
    )


def test_returns_series_named_by_response(tree, data):
    """Return a named response series aligned to retained tips."""
    out = tree.pcm.simulate_pgls_trait(
        formula="y ~ x1",
        betas={"Intercept": 0.5, "x1": 1.0},
        data=data,
        seed=1,
    )
    assert isinstance(out, pd.Series)
    assert out.name == "y"
    assert out.shape[0] == tree.ntips


def test_invalid_lambda_raises(tree, data):
    """Reject lambda values outside tree-specific valid bounds."""
    upper = tree.mod.edges_scale_to_root_height(1.0).treenode.height
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pgls_trait(
            formula="y ~ x1",
            betas={"Intercept": 0.0, "x1": 1.0},
            lambda_=upper + 10,
            data=data,
            seed=1,
        )


def test_beta_key_matching_required(tree, data):
    """Require exact beta key match to Patsy design columns."""
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pgls_trait(
            formula="y ~ x1",
            betas={"Intercept": 0.0},
            data=data,
            seed=2,
        )
    with pytest.raises(ToytreeError):
        tree.pcm.simulate_pgls_trait(
            formula="y ~ x1",
            betas={"Intercept": 0.0, "x1": 1.0, "extra": 5.0},
            data=data,
            seed=2,
        )


def test_categorical_design_columns_supported(tree, data):
    """Support Patsy categorical coding in predictor design."""
    out = tree.pcm.simulate_pgls_trait(
        formula="y ~ x1 + C(group)",
        betas={"Intercept": 1.0, "x1": 2.0, "C(group)[T.B]": -0.5},
        data=data,
        seed=3,
    )
    assert isinstance(out, pd.Series)
    assert out.shape[0] == tree.ntips


def test_data_overrides_tree_features(tree, data, tips):
    """Prefer `data` predictor values over overlapping tree features."""
    tree = tree.set_node_data(
        "x1",
        {i: 100.0 for i in range(tree.ntips)},
        inplace=False,
        default=np.nan,
    )
    out = tree.pcm.simulate_pgls_trait(
        formula="y ~ x1",
        betas={"Intercept": 0.0, "x1": 1.0},
        lambda_=0.0,
        sigma2=1e-12,
        data=data,
        seed=4,
    )
    expected = data["x1"].astype(float)
    assert np.allclose(out.loc[tips].to_numpy(), expected.to_numpy())


def test_missing_rows_follow_patsy_drop(tree, data, tips):
    """Drop rows with missing RHS values consistently with Patsy."""
    data = data.copy()
    data.loc[tips[0], "x1"] = np.nan
    out = tree.pcm.simulate_pgls_trait(
        formula="y ~ x1 + C(group)",
        betas={"Intercept": 0.0, "x1": 1.0, "C(group)[T.B]": 0.2},
        data=data,
        seed=5,
    )
    xmat = dmatrix("x1 + C(group)", data=data, return_type="dataframe")
    assert list(out.index) == list(xmat.index)
    assert out.shape[0] == tree.ntips - 1


def test_sigma2_near_zero_matches_deterministic_mean(tree, data):
    """Approximate deterministic mean when residual variance is near zero."""
    out = tree.pcm.simulate_pgls_trait(
        formula="y ~ x1 + C(group)",
        betas={"Intercept": 0.5, "x1": -1.2, "C(group)[T.B]": 0.7},
        lambda_=1.0,
        sigma2=1e-12,
        data=data,
        seed=6,
    )
    xmat = dmatrix("x1 + C(group)", data=data, return_type="dataframe")
    beta_map = {"Intercept": 0.5, "x1": -1.2}
    cat_cols = [col for col in xmat.columns if col not in {"Intercept", "x1"}]
    assert len(cat_cols) == 1
    beta_map[cat_cols[0]] = 0.7
    beta = np.array([beta_map[col] for col in xmat.columns], dtype=float)
    expected = xmat.to_numpy() @ beta
    assert np.allclose(out.to_numpy(), expected, atol=1e-4)
