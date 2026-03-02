#!/usr/bin/env python

"""Tests for matrix/statsmodels Brownian-motion PGLS."""

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.utils import ToytreeError


@pytest.fixture
def tree(make_unittree):
    """Return a reproducible tree for PGLS matrix tests."""
    return make_unittree(ntips=12, treeheight=1.0, seed=123)


@pytest.fixture
def traits(tree, simulate_mv_continuous_tips):
    """Return reproducible simulated multivariate tip traits."""
    return simulate_mv_continuous_tips(
        tree=tree,
        params=np.diag([0.5, 1.0]),
        seed=123,
        set_tip_index=False,
    )


def test_basic_fit_succeeds(tree, traits):
    """Fit succeeds and returns expected result attributes."""
    fit = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits)
    assert hasattr(fit, "params")
    assert hasattr(fit, "fittedvalues")
    assert hasattr(fit, "resid")
    assert "Intercept" in fit.params.index
    assert "t1" in fit.params.index
    assert hasattr(fit, "_toytree_lambda")
    assert fit._toytree_lambda_optimized
    assert np.isfinite(float(fit._toytree_lambda))


def test_tree_api_exposure(tree, traits):
    """Tree API exposure mirrors package-level API behavior."""
    fit = tree.pcm.pgls_matrix("t0 ~ t1", data=traits)
    assert hasattr(fit, "params")
    assert hasattr(fit, "_toytree_lambda")


def test_tip_label_index_alignment(tree, traits):
    """Tip-label indexed data aligns correctly regardless of row order."""
    tips = tree.get_tip_labels()
    data = traits.copy()
    data.index = tips
    shuffled = data.sample(frac=1.0, random_state=1)
    fit_a = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=data)
    fit_b = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=shuffled)
    assert np.allclose(fit_a.params.values, fit_b.params.values)
    assert hasattr(fit_b, "_toytree_lambda")


def test_node_idx_index_alignment(tree):
    """Node-indexed DataFrame is accepted and aligned to tip rows."""
    data = tree.get_node_data().copy()
    data["x"] = np.arange(tree.nnodes, dtype=float)
    data["y"] = np.arange(tree.nnodes, dtype=float) * 2.0
    fit = toytree.pcm.pgls_matrix(tree, "y ~ x", data=data)
    assert hasattr(fit, "params")
    assert int(fit.nobs) == tree.ntips


def test_missing_formula_rows_are_dropped(tree, traits):
    """Rows with formula-missing values are dropped by Patsy."""
    data = traits.copy()
    data.index = tree.get_tip_labels()
    data.loc[data.index[0], "t1"] = np.nan
    fit = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=data)
    assert int(fit.nobs) == tree.ntips - 1
    assert np.isfinite(float(fit._toytree_lambda))


def test_fixed_lambda_override_is_respected(tree, traits):
    """Fixed lambda override is respected and marked non-optimized."""
    fit = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits, lambda_=0.5)
    assert not fit._toytree_lambda_optimized
    assert float(fit._toytree_lambda) == pytest.approx(0.5, abs=1e-8)


def test_fixed_lambda_repeatability(tree, traits):
    """Fixed lambda fit is deterministic for identical inputs."""
    fit_a = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits, lambda_=1.0)
    fit_b = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits, lambda_=1.0)
    assert np.allclose(fit_a.params.values, fit_b.params.values)


def test_fixed_lambda_out_of_bounds_raises(tree, traits):
    """Out-of-bounds lambda values raise errors."""
    with pytest.raises(ToytreeError):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits, lambda_=-0.1)
    upper = tree.mod.edges_scale_to_root_height(1.0).treenode.height
    with pytest.raises(ToytreeError):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits, lambda_=upper + 10)


def test_unalignable_dataframe_index_raises(tree, traits):
    """Unalignable DataFrame indexes are rejected."""
    data = traits.copy()
    data.index = [f"x{i}" for i in range(data.shape[0])]
    with pytest.raises(ToytreeError):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=data)


def test_invalid_formula_raises(tree, traits):
    """Empty formula string is rejected."""
    with pytest.raises(ToytreeError):
        toytree.pcm.pgls_matrix(tree, "", data=traits)


def test_none_data_uses_tree_node_data(tree, traits):
    """None data uses tree node data as predictor/response source."""
    tree = tree.set_node_data_from_dataframe(
        traits.rename(columns={"t0": "x", "t1": "y"}),
        inplace=False,
    )
    fit = tree.pcm.pgls_matrix("y ~ x")
    assert hasattr(fit, "params")


def test_string_response_raises(tree, traits):
    """String response values are rejected as categorical outcomes."""
    data = traits.copy()
    data.index = tree.get_tip_labels()
    data["y"] = ["A" if i % 2 else "B" for i in range(tree.ntips)]
    data["x"] = np.linspace(0, 1, tree.ntips)
    with pytest.raises(ToytreeError, match="phylogenetic logistic regression"):
        toytree.pcm.pgls_matrix(tree, "y ~ x", data=data)


def test_categorical_response_raises(tree, traits):
    """Pandas categorical responses are rejected."""
    data = traits.copy()
    data.index = tree.get_tip_labels()
    data["y"] = pd.Categorical(["A" if i % 2 else "B" for i in range(tree.ntips)])
    data["x"] = np.linspace(0, 1, tree.ntips)
    with pytest.raises(ToytreeError, match="categorical dependent variables"):
        toytree.pcm.pgls_matrix(tree, "y ~ x", data=data)


def test_bool_response_raises(tree, traits):
    """Boolean responses are rejected as categorical outcomes."""
    data = traits.copy()
    data.index = tree.get_tip_labels()
    data["y"] = [bool(i % 2) for i in range(tree.ntips)]
    data["x"] = np.linspace(0, 1, tree.ntips)
    with pytest.raises(ToytreeError, match="phylogenetic logistic regression"):
        toytree.pcm.pgls_matrix(tree, "y ~ x", data=data)


def test_explicit_categorical_formula_response_raises(tree, traits):
    """Explicit categorical response formula is rejected."""
    data = traits.copy()
    data.index = tree.get_tip_labels()
    data["y"] = ["A" if i % 2 else "B" for i in range(tree.ntips)]
    data["x"] = np.linspace(0, 1, tree.ntips)
    with pytest.raises(ToytreeError, match="categorical dependent variables"):
        toytree.pcm.pgls_matrix(tree, "C(y) ~ x", data=data)


# Additional source-driven tests.


def test_duplicate_data_index_raises(tree, traits):
    """Duplicate data indexes are rejected during tip alignment."""
    data = traits.copy()
    data.index = ["dup"] * data.shape[0]
    with pytest.raises(ToytreeError, match="data index must be unique"):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=data)


def test_non_dataframe_data_raises(tree):
    """Non-DataFrame data argument is rejected."""
    with pytest.raises(ToytreeError, match="data must be a pandas DataFrame"):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data={"t0": [1], "t1": [2]})


def test_nonfinite_lambda_raises(tree, traits):
    """Non-finite lambda override values are rejected."""
    with pytest.raises(ToytreeError, match="lambda_ must be a finite float"):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=traits, lambda_=np.inf)


def test_no_rows_after_missing_drop_raises(tree, traits):
    """Raise when Patsy drops all rows for formula variables."""
    data = traits.copy()
    data.index = tree.get_tip_labels()
    data["t1"] = np.nan
    with pytest.raises(
        ToytreeError,
        match="No rows remain after applying formula and dropping missing values",
    ):
        toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=data)
