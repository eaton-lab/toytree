#!/usr/bin/env python

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.pcm.src.traits import phylosignal_lambda as psl


def _as_series_or_array(values):
    """Normalize simulated trait output to a single vector."""
    if isinstance(values, pd.DataFrame):
        return values.iloc[:, 0]
    return values


def test_profiled_nll_invariant_to_scalar_covariance():
    """Profiled NLL should be invariant to scalar covariance scaling."""
    rng = np.random.default_rng(123)
    y = rng.normal(size=8)
    a_mat = rng.normal(size=(8, 8))
    cov = a_mat @ a_mat.T + np.eye(8) * 0.1
    nll1 = psl._profiled_gaussian_nll(y, cov)
    nll2 = psl._profiled_gaussian_nll(y, cov * 3.0)
    assert np.isfinite(nll1)
    assert np.isfinite(nll2)
    assert nll1 == pytest.approx(nll2, abs=1e-8)


def test_lambda_public_output_is_finite_without_se(make_unittree):
    """Public lambda API returns finite values and expected output keys."""
    tree = make_unittree(ntips=30, treeheight=1.0, seed=123)
    trait = tree.pcm.simulate_continuous_trait(
        "bm", params=1.0, seed=321, tips_only=True
    )
    values = _as_series_or_array(trait)
    res = psl.phylogenetic_signal_lambda(tree, values)
    assert "lambda" in res
    assert "P-value" in res
    assert "LR_test" in res
    assert "log-likelihood_λ" in res
    assert "log-likelihood_λ0" in res
    assert np.isfinite(float(res["lambda"]))
    assert np.isfinite(float(res["P-value"]))
    assert float(res["LR_test"]) >= 0.0


def test_lambda_with_se_uses_exact_lambda_zero_null(make_unittree):
    """SE-aware fit should use the exact lambda-zero null likelihood."""
    tree = make_unittree(ntips=24, treeheight=1.0, seed=77)
    traits = tree.pcm.simulate_continuous_trait(
        "bm", params=1.0, seed=88, tips_only=True
    )
    error = np.full(tree.ntips, 0.05)
    values = _as_series_or_array(traits)
    res = psl.phylogenetic_signal_lambda(tree, values, error=error)

    vcv = psl.get_vcv_matrix_from_tree(tree)
    err_cov = np.diag(error**2)
    fit0 = psl._estimate_sigma2_given_λ(np.asarray(values), vcv, err_cov, λ=0.0)
    expected_ll0 = -float(fit0.fun)

    assert "sig2" in res
    assert np.isfinite(float(res["sig2"]))
    assert float(res["LR_test"]) >= 0.0
    assert float(res["log-likelihood_λ0"]) == pytest.approx(expected_ll0, abs=1e-8)


def test_near_zero_branch_lengths_remain_stable():
    """Near-zero branch lengths should still return finite likelihood outputs."""
    tree = toytree.tree("((a:1e-9,b:1e-9):1e-9,(c:1e-9,d:1e-9):1e-9);")
    trait = np.array([0.1, 0.2, 0.4, 0.8], dtype=float)
    res = psl.phylogenetic_signal_lambda(tree, trait)
    assert np.isfinite(float(res["lambda"]))
    assert np.isfinite(float(res["log-likelihood_λ"]))
    assert np.isfinite(float(res["log-likelihood_λ0"]))
