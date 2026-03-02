#!/usr/bin/env python

"""Tests for Blomberg's K phylogenetic signal metric."""

import numpy as np
import pytest

from toytree.pcm.src.traits import phylosignal_k as psk


@pytest.fixture
def tree(make_unittree):
    """Return a reproducible tree for phylogenetic-signal tests."""
    return make_unittree(ntips=24, treeheight=1.0, seed=123)


@pytest.fixture
def trait(tree):
    """Return reproducible BM-simulated tip trait values."""
    return tree.pcm.simulate_continuous_trait(
        "bm",
        params=1.0,
        tips_only=True,
        seed=321,
    )


def test_phylogenetic_signal_k_output_without_permutations(tree, trait):
    """nsims=0 returns finite K and NaN permutation fields."""
    res = psk.phylogenetic_signal_k(tree=tree, data=trait, nsims=0)
    assert "K" in res
    assert "P-value" in res
    assert "permutations" in res
    assert np.isfinite(float(res["K"]))
    assert np.isnan(float(res["P-value"]))
    assert np.isnan(float(res["permutations"]))


def test_phylogenetic_signal_k_output_with_permutations(tree, trait):
    """Permutation mode returns bounded p-value and permutation count."""
    res = psk.phylogenetic_signal_k(tree=tree, data=trait, nsims=25)
    assert np.isfinite(float(res["K"]))
    assert 0.0 <= float(res["P-value"]) <= 1.0
    assert int(res["permutations"]) == 25


def test_phylogenetic_signal_k_accepts_feature_name(tree, trait):
    """Data can be supplied as a tree feature name string."""
    tree2 = tree.set_node_data("x", trait, default=np.nan, inplace=False)
    res = psk.phylogenetic_signal_k(tree=tree2, data="x", nsims=0)
    assert np.isfinite(float(res["K"]))


def test_phylogenetic_signal_k_with_error_sequence(tree, trait):
    """Error-aware mode returns additional model diagnostics."""
    err = np.full(tree.ntips, 0.05, dtype=float)
    res = psk.phylogenetic_signal_k(tree=tree, data=trait, error=err, nsims=0)
    assert "K" in res
    assert "sig2" in res
    assert "log-likelihood" in res
    assert "convergence" in res
    assert np.isfinite(float(res["K"]))
    assert np.isfinite(float(res["sig2"]))


def test_phylogenetic_signal_k_with_error_feature_name(tree, trait):
    """Error values can be supplied as a tree feature name string."""
    tree2 = tree.set_node_data("x", trait, default=np.nan, inplace=False)
    se_map = {idx: 0.05 for idx in range(tree.ntips)}
    tree2 = tree2.set_node_data("se", se_map, default=np.nan)
    res = psk.phylogenetic_signal_k(tree=tree2, data="x", error="se", nsims=0)
    assert np.isfinite(float(res["K"]))
    assert np.isfinite(float(res["sig2"]))


def test_phylogenetic_signal_k_invalid_length_raises(tree):
    """Mismatched data length is rejected by feature validation."""
    bad = np.array([0.1, 0.2, 0.3], dtype=float)
    with pytest.raises(Exception):
        psk.phylogenetic_signal_k(tree=tree, data=bad, nsims=0)


def test_phylogenetic_signal_k_invalid_error_length_raises(tree, trait):
    """Mismatched error length is rejected by feature validation."""
    bad_err = np.array([0.1, 0.2, 0.3], dtype=float)
    with pytest.raises(Exception):
        psk.phylogenetic_signal_k(tree=tree, data=trait, error=bad_err, nsims=0)


def test_phylogenetic_signal_k_api_exposure(tree, trait):
    """Tree API wrapper delegates to the same implementation."""
    res = tree.pcm.phylogenetic_signal_k(data=trait, nsims=0)
    assert "K" in res
    assert np.isfinite(float(res["K"]))
