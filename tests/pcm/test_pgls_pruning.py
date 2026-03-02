#!/usr/bin/env python

"""Tests for pruning-based PGLS."""

from contextlib import redirect_stderr
from io import StringIO

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.pcm.src.phylolinalg.pgls import PGLSResult
from toytree.utils import ToytreeError


@pytest.fixture
def tree(make_unittree):
    """Create a small reproducible tree."""
    return make_unittree(ntips=16, treeheight=1.0, seed=123)


@pytest.fixture
def data(tree, simulate_mv_continuous_tips):
    """Create reproducible continuous tip data aligned to tip labels."""
    return simulate_mv_continuous_tips(
        tree=tree,
        params=np.diag([0.5, 1.0]),
        seed=123,
        set_tip_index=True,
    )


@pytest.fixture
def tree_tip_labels(tree, tip_labels):
    """Return tip labels in tree order."""
    return tip_labels(tree)


def test_basic_fit_and_api_exposure(tree, data):
    """Fit via package and tree APIs and inspect result structure."""
    fit = toytree.pcm.pgls(tree, "t0 ~ t1", data=data)
    assert isinstance(fit, PGLSResult)
    assert np.isfinite(fit.lambda_)
    assert "Intercept" in fit.params.index
    assert "t1" in fit.params.index

    fit2 = tree.pcm.pgls("t0 ~ t1", data=data)
    assert isinstance(fit2, PGLSResult)


def test_fixed_lambda_override(tree, data):
    """Use a fixed lambda value without optimization."""
    fit = toytree.pcm.pgls(tree, "t0 ~ t1", data=data, lambda_=0.5)
    assert fit.lambda_ == pytest.approx(0.5, abs=1e-8)
    assert not fit.lambda_optimized


def test_alignment_and_missing_rows(tree, data, tree_tip_labels):
    """Align shuffled rows and handle Patsy row dropping for missing data."""
    shuffled = data.sample(frac=1.0, random_state=1)
    fit_a = toytree.pcm.pgls(tree, "t0 ~ t1", data=data, lambda_=1.0)
    fit_b = toytree.pcm.pgls(tree, "t0 ~ t1", data=shuffled, lambda_=1.0)
    assert np.allclose(fit_a.params.values, fit_b.params.values)

    data2 = data.copy()
    data2.loc[tree_tip_labels[0], "t1"] = np.nan
    fit = toytree.pcm.pgls(tree, "t0 ~ t1", data=data2)
    assert fit.nobs == tree.ntips - 1


def test_categorical_response_guard(tree, data):
    """Reject categorical responses with a logistic-regression hint."""
    dat = data.copy()
    dat["y"] = ["A" if i % 2 else "B" for i in range(dat.shape[0])]
    dat["x"] = np.linspace(0, 1, dat.shape[0])
    with pytest.raises(ToytreeError, match="phylogenetic logistic regression"):
        toytree.pcm.pgls(tree, "y ~ x", data=dat)


def test_compare_to_matrix_pgls_fixed_lambda(tree, data):
    """Match matrix-based pgls implementation at fixed lambda."""
    fitp = toytree.pcm.pgls(tree, "t0 ~ t1", data=data, lambda_=1.0)
    fitm = toytree.pcm.pgls_matrix(tree, "t0 ~ t1", data=data, lambda_=1.0)
    assert np.allclose(fitp.params.values, fitm.params.values, atol=1e-6)
    assert np.allclose(
        fitp.fittedvalues.values,
        fitm.fittedvalues.values,
        atol=1e-6,
    )


def test_polytomy_smoke():
    """Support a rooted tree with a multifurcation."""
    tree = toytree.tree("((a:1,b:1,c:1):1,d:2,e:2);")
    data = pd.DataFrame(
        {
            "y": [0.1, 0.2, 0.4, 0.7, 0.6],
            "x": [0.0, 1.0, 0.0, 1.0, 0.5],
        },
        index=tree.get_tip_labels(),
    )
    fit = toytree.pcm.pgls(tree, "y ~ x", data=data, lambda_=0.8)
    assert fit.nobs == tree.ntips
    assert np.isfinite(fit.log_likelihood)


def test_repr_contains_key_fields(tree, data):
    """Include core metadata and coefficient names in text repr."""
    fit = toytree.pcm.pgls(tree, "t0 ~ t1", data=data)
    txt = repr(fit)
    assert "PGLSResult" in txt
    assert "lambda=" in txt
    assert "sigma2=" in txt
    assert "Intercept" in txt


def test_repr_html_contains_table(tree, data):
    """Provide notebook HTML representation with a coefficient table."""
    fit = toytree.pcm.pgls(tree, "t0 ~ t1", data=data)
    txt = fit._repr_html_()
    assert isinstance(txt, str)
    assert "PGLSResult" in txt
    assert "<table" in txt
    assert "Intercept" in txt


def test_y_stderr_changes_fit_and_validates(tree, data, tree_tip_labels):
    """Use response SE in covariance and validate bad values."""
    yse = pd.Series(0.1, index=tree_tip_labels, name="yse")
    fit0 = toytree.pcm.pgls(tree, "t0 ~ t1", data=data, lambda_=1.0)
    fit1 = toytree.pcm.pgls(tree, "t0 ~ t1", data=data, lambda_=1.0, y_stderr=yse)
    assert not np.allclose(fit0.params.values, fit1.params.values)

    bad = yse.copy()
    bad.iloc[0] = -0.1
    with pytest.raises(ToytreeError):
        toytree.pcm.pgls(tree, "t0 ~ t1", data=data, y_stderr=bad)


def test_infer_node_states_pgls_basic_and_warning(tree, data):
    """Infer node states and warn when internal predictor values are missing."""
    tree2 = tree.set_node_data("t0", data["t0"], default=np.nan)
    tree2 = tree2.set_node_data("t1", data["t1"], default=np.nan)
    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "t0 ~ t1",
            data=None,
            lambda_=1.0,
        )
    assert isinstance(out, dict)
    assert "model_fit" in out
    assert "data" in out
    assert isinstance(out["model_fit"], PGLSResult)
    assert "mean" in out["data"].columns
    assert "variance" in out["data"].columns
    assert "fallback_residual_only" in out["data"].columns
    assert np.all(np.isfinite(out["data"]["mean"]))
    assert "internal predictor node values are missing" in buf.getvalue()


def test_infer_node_states_pgls_strict_data_semantics(tree, data, tree_tip_labels):
    """Provided data is the sole source and must be complete for formula rows."""
    node_df = data.copy()
    node_df.loc[tree_tip_labels[0], "t1"] = np.nan
    with pytest.raises(ToytreeError):
        toytree.pcm.infer_node_states_pgls(tree, "t0 ~ t1", data=node_df)


def test_infer_node_states_pgls_uses_categorical_internal_predictors(tree, data):
    """Use exact categorical predictor states on internal nodes when present."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    group_map = {node.idx: ("A" if node.idx % 2 else "B") for node in tree2}
    tree2 = tree2.set_node_data("group", group_map)
    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "y ~ C(group)",
            data=None,
            lambda_=1.0,
        )
    assert buf.getvalue() == ""
    assert not out["data"]["fallback_residual_only"].any()
    assert out["data"]["predictor_mean_available"].all()
    assert np.all(np.isfinite(out["data"]["mean"]))


def test_infer_node_states_pgls_missing_categorical_predictor_warns(tree, data):
    """Missing internal categorical predictor states trigger warning and fallback."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    group_map = {node.idx: ("A" if node.idx % 2 else "B") for node in tree2}
    first_internal = tree2[tree2.ntips].idx
    group_map[first_internal] = np.nan
    tree2 = tree2.set_node_data("group", group_map)
    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "y ~ C(group)",
            data=None,
            lambda_=1.0,
        )
    assert "internal predictor node values are missing" in buf.getvalue()
    assert out["data"]["fallback_residual_only"].all()


def test_infer_node_states_pgls_categorical_predictor_probabilities(tree, data):
    """Use categorical predictor probability vectors on internal nodes."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    group_map = {}
    for node in tree2:
        if node.is_leaf():
            group_map[node.idx] = "A" if node.idx % 2 else "B"
        else:
            group_map[node.idx] = (0.7, 0.3) if node.idx % 2 else (0.2, 0.8)
    tree2 = tree2.set_node_data("group", group_map)
    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "y ~ C(group)",
            data=None,
            lambda_=1.0,
        )
    assert buf.getvalue() == ""
    assert not out["data"]["fallback_residual_only"].any()
    assert out["data"]["predictor_mean_available"].all()
    assert np.all(np.isfinite(out["data"]["mean"]))


def test_infer_node_states_pgls_multi_categorical_probabilities(tree, data):
    """Interpret probability tuples independently for multiple predictors."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    a_map = {}
    b_map = {}
    for node in tree2:
        if node.is_leaf():
            a_map[node.idx] = "A" if node.idx % 2 else "B"
            b_map[node.idx] = ("K", "L", "M")[node.idx % 3]
        else:
            a_map[node.idx] = (0.6, 0.4) if node.idx % 2 else (0.25, 0.75)
            b_map[node.idx] = (0.2, 0.3, 0.5)
    tree2 = tree2.set_node_data("a", a_map)
    tree2 = tree2.set_node_data("b", b_map)

    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "y ~ C(a) * C(b)",
            data=None,
            lambda_=1.0,
        )
    assert buf.getvalue() == ""
    assert not out["data"]["fallback_residual_only"].any()
    assert out["data"]["predictor_mean_available"].all()
    assert np.all(np.isfinite(out["data"]["mean"]))


def test_infer_node_states_pgls_invalid_prob_tuple_falls_back(tree, data):
    """Invalid categorical probability vectors trigger fallback with warning."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    a_map = {}
    b_map = {}
    first_internal = tree2[tree2.ntips].idx
    for node in tree2:
        if node.is_leaf():
            a_map[node.idx] = "A" if node.idx % 2 else "B"
            b_map[node.idx] = ("K", "L", "M")[node.idx % 3]
        else:
            a_map[node.idx] = (0.5, 0.5)
            b_map[node.idx] = (0.2, 0.3, 0.5)
    b_map[first_internal] = (0.4, 0.6)
    tree2 = tree2.set_node_data("a", a_map)
    tree2 = tree2.set_node_data("b", b_map)

    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "y ~ C(a) + C(b)",
            data=None,
            lambda_=1.0,
        )
    assert "internal predictor node values are missing" in buf.getvalue()
    assert out["data"]["fallback_residual_only"].all()
    assert np.all(np.isfinite(out["data"]["mean"]))


def test_infer_node_states_pgls_disable_internal_predictors_no_warning(tree, data):
    """Disabling internal predictors suppresses warning and uses fallback."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    tree2 = tree2.set_node_data(
        "group",
        {node.idx: ("A" if node.idx % 2 else "B") for node in tree2},
    )
    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "y ~ C(group)",
            data=None,
            lambda_=1.0,
            use_internal_node_predictors=False,
        )
    assert buf.getvalue() == ""
    assert out["data"]["fallback_residual_only"].all()


def test_infer_node_states_pgls_strict_data_semantics_categorical(
    tree,
    data,
    tree_tip_labels,
):
    """Missing categorical predictor in provided data raises without fallback."""
    dat = pd.DataFrame(
        {
            "y": data["t0"].values,
            "group": ["A" if i % 2 else "B" for i in range(tree.ntips)],
        },
        index=tree_tip_labels,
    )
    dat.loc[tree_tip_labels[0], "group"] = np.nan
    with pytest.raises(ToytreeError):
        toytree.pcm.infer_node_states_pgls(tree, "y ~ C(group)", data=dat)


def test_pgls_data_index_must_be_unique(tree, data):
    """Reject duplicated DataFrame indexes when aligning tip data."""
    dat = data.copy()
    dat.index = pd.Index([tree.get_tip_labels()[0]] * dat.shape[0])
    with pytest.raises(ToytreeError, match="data index must be unique"):
        toytree.pcm.pgls(tree, "t0 ~ t1", data=dat)


def test_pgls_unalignable_dataframe_index_raises(tree, data):
    """Reject DataFrame indexes that cannot be aligned to tree tips."""
    dat = data.copy()
    dat.index = [f"x{i}" for i in range(dat.shape[0])]
    with pytest.raises(ToytreeError, match="Could not align data rows to tree tips"):
        toytree.pcm.pgls(tree, "t0 ~ t1", data=dat)


def test_pgls_empty_formula_raises(tree, data):
    """Reject an empty formula string."""
    with pytest.raises(ToytreeError, match="formula must be a non-empty str"):
        toytree.pcm.pgls(tree, "", data=data)


def test_pgls_y_stderr_inf_raises(tree, data, tree_tip_labels):
    """Reject infinite response standard errors when provided."""
    yse = pd.Series(0.1, index=tree_tip_labels, name="yse")
    yse.iloc[0] = np.inf
    with pytest.raises(ToytreeError, match="must be finite"):
        toytree.pcm.pgls(tree, "t0 ~ t1", data=data, y_stderr=yse)


def test_infer_warn_flag_suppresses_missing_predictor_warning(tree, data):
    """Disable missing-predictor warning while retaining fallback behavior."""
    tree2 = tree.set_node_data("t0", data["t0"], default=np.nan)
    tree2 = tree2.set_node_data("t1", data["t1"], default=np.nan)
    buf = StringIO()
    with redirect_stderr(buf):
        out = toytree.pcm.infer_node_states_pgls(
            tree2,
            "t0 ~ t1",
            data=None,
            lambda_=1.0,
            warn_on_missing_predictors=False,
        )
    assert buf.getvalue() == ""
    assert out["data"]["fallback_residual_only"].all()


def test_infer_data_mode_missing_y_stderr_column_raises(tree, data):
    """Raise if y_stderr column key is missing from provided data."""
    node_df = data.copy()
    with pytest.raises(ValueError, match="not in tree.features"):
        toytree.pcm.infer_node_states_pgls(
            tree,
            "t0 ~ t1",
            data=node_df,
            lambda_=1.0,
            y_stderr="missing_stderr",
        )


def test_infer_output_source_labels_for_exact_and_noisy_observed(tree, data):
    """Label observed nodes as exact or noisy based on observation variance."""
    tree2 = tree.set_node_data("y", data["t0"], default=np.nan)
    tree2 = tree2.set_node_data("x", data["t1"], default=np.nan)
    yse = pd.Series(np.nan, index=range(tree2.nnodes), dtype=float)
    yse.iloc[0] = 0.0
    yse.iloc[1] = 0.2

    out = toytree.pcm.infer_node_states_pgls(
        tree2,
        "y ~ x",
        data=None,
        lambda_=1.0,
        y_stderr=yse,
        use_internal_node_predictors=False,
        warn_on_missing_predictors=False,
    )
    res = out["data"]
    assert res.loc[0, "source"] == "observed_exact"
    assert res.loc[1, "source"] == "observed_noisy"
    assert float(res.loc[0, "variance"]) == pytest.approx(0.0, abs=1e-12)
