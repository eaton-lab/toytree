#!/usr/bin/env python

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.pcm.src.traits.fit_continuous_ml import FitContinuousMLResult
from toytree.utils import ToytreeError


@pytest.fixture
def tree_with_x(make_unittree, add_feature_from_tip_series):
    """Return a tree populated with one simulated tip trait named X."""
    tree = make_unittree(ntips=20, treeheight=1.0, seed=7)
    trait = tree.pcm.simulate_continuous_trait(
        "bm",
        params=1.0,
        tips_only=True,
        seed=11,
    )
    return add_feature_from_tip_series(tree, "X", trait, default=np.nan)


def test_fit_accepts_feature_name_single_model(tree_with_x):
    """Single-model fit returns one FitContinuousMLResult."""
    out = tree_with_x.pcm.fit_continuous_ml("X", model="BM")
    assert isinstance(out, FitContinuousMLResult)
    assert out.model == "BM"
    assert np.isfinite(float(out.log_likelihood))


def test_fit_accepts_series(tree_with_x, tip_labels):
    """Fit accepts a tip-indexed numeric Series."""
    series = tree_with_x.get_node_data("X", missing=np.nan).iloc[: tree_with_x.ntips]
    series.index = tip_labels(tree_with_x)
    out = toytree.pcm.fit_continuous_ml(tree_with_x, series, model="OU")
    assert isinstance(out, FitContinuousMLResult)
    assert out.model == "OU"
    assert np.isfinite(float(out.sigma2))


def test_fit_none_returns_model_fits_and_aicc_table(tree_with_x):
    """model=None fits BM/OU/EB and returns AICc-ranked table."""
    out = tree_with_x.pcm.fit_continuous_ml("X", model=None)
    assert "model_fits" in out
    assert "model_table" in out

    model_fits = out["model_fits"]
    table = out["model_table"]
    assert set(model_fits) == {"BM", "OU", "EB"}
    assert all(isinstance(v, FitContinuousMLResult) for v in model_fits.values())
    assert "AIC" in table.columns
    assert "AICc" in table.columns
    assert "weight_AIC" in table.columns
    assert "weight_AICc" in table.columns
    assert table.iloc[0]["rank_by"] == "AICc"


def test_infer_states_output_columns(tree_with_x):
    """Inference output includes ancestral means and variances."""
    out = tree_with_x.pcm.infer_ancestral_states_continuous_ml("X", model="BM")
    data = out["data"]

    assert "X_anc" in data.columns
    assert "X_anc_var" in data.columns
    assert data.shape[0] == tree_with_x.nnodes
    assert (data["X_anc_var"].iloc[: tree_with_x.ntips] == 0.0).all()


def test_infer_states_inplace_true_sets_features(tree_with_x):
    """inplace=True writes inferred features to the same tree object."""
    tree = tree_with_x.copy()
    _ = tree.pcm.infer_ancestral_states_continuous_ml("X", model="BM", inplace=True)
    assert "X_anc" in tree.features
    assert "X_anc_var" in tree.features


def test_reject_non_series_dataframe(tree_with_x):
    """DataFrame input for trait data is rejected."""
    data = pd.DataFrame({"x": np.arange(tree_with_x.ntips)})
    with pytest.raises(ToytreeError):
        toytree.pcm.fit_continuous_ml(tree_with_x, data)


def test_reject_invalid_model_name(tree_with_x):
    """Invalid model name raises a ToytreeError."""
    with pytest.raises(ToytreeError):
        tree_with_x.pcm.fit_continuous_ml("X", model="XYZ")


def test_aic_table_backward_compatible(tree_with_x):
    """aic_table output remains backward compatible for AIC-only fields."""
    m1 = toytree.pcm.fit_continuous_ml(tree_with_x, "X", model="BM")
    m2 = toytree.pcm.fit_continuous_ml(tree_with_x, "X", model="OU")
    tbl = toytree.pcm.aic_table([m1, m2])
    assert "AIC" in tbl.columns
    assert "weight" in tbl.columns
    assert "AICc" not in tbl.columns


def test_fit_accepts_new_bounds_arg_names(tree_with_x):
    """Renamed optimizer bounds args are accepted."""
    out = tree_with_x.pcm.fit_continuous_ml(
        "X",
        model="OU",
        bounds_alpha=(1e-10, 10.0),
    )
    assert isinstance(out, FitContinuousMLResult)

    out2 = tree_with_x.pcm.fit_continuous_ml(
        "X",
        model="EB",
        bounds_r=(-5.0, 5.0),
    )
    assert isinstance(out2, FitContinuousMLResult)
