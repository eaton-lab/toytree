#!/usr/bin/env python

"""Tests for variance-covariance helpers in toytree.pcm.vcv."""

import numpy as np
import pandas as pd
import pytest

import toytree


@pytest.fixture
def tree():
    """Return a deterministic ultrametric tree fixture."""
    return toytree.rtree.unittree(ntips=8, treeheight=3.0, seed=123)


@pytest.fixture
def vcv_np(tree):
    """Return unlabeled VCV matrix."""
    return tree.pcm.get_vcv_matrix_from_tree(df=False)


@pytest.fixture
def vcv_df(tree):
    """Return labeled VCV matrix."""
    return tree.pcm.get_vcv_matrix_from_tree(df=True)


def test_get_vcv_matrix_from_tree_array_and_dataframe(tree, vcv_np, vcv_df):
    """Return expected types, symmetry, labels, and root-to-tip diagonal."""
    assert isinstance(vcv_np, np.ndarray)
    assert isinstance(vcv_df, pd.DataFrame)
    assert vcv_np.shape == (tree.ntips, tree.ntips)
    assert vcv_df.shape == (tree.ntips, tree.ntips)
    assert np.allclose(vcv_np, vcv_np.T)
    assert list(vcv_df.index) == tree.get_tip_labels()
    assert list(vcv_df.columns) == tree.get_tip_labels()

    dmat = tree.distance.get_node_distance_matrix()
    expected_diag = np.array([dmat[i, tree.treenode.idx] for i in range(tree.ntips)])
    assert np.allclose(np.diag(vcv_np), expected_diag)
    assert np.allclose(np.diag(vcv_df.to_numpy()), expected_diag)


def test_get_corr_matrix_from_tree_properties(tree):
    """Return valid correlation matrix with unit diagonal and symmetry."""
    corr_np = tree.pcm.get_corr_matrix_from_tree(df=False)
    corr_df = tree.pcm.get_corr_matrix_from_tree(df=True)

    assert isinstance(corr_np, np.ndarray)
    assert isinstance(corr_df, pd.DataFrame)
    assert corr_np.shape == (tree.ntips, tree.ntips)
    assert np.allclose(corr_np, corr_np.T)
    assert np.allclose(np.diag(corr_np), 1.0)
    assert np.isfinite(corr_np).all()
    assert list(corr_df.index) == tree.get_tip_labels()
    assert list(corr_df.columns) == tree.get_tip_labels()
    assert np.allclose(corr_df.to_numpy(), corr_np)


def test_get_distance_matrix_from_vcv_matrix_array(tree, vcv_np):
    """Convert ndarray VCV to symmetric distance matrix with zero diagonal."""
    dist = toytree.pcm.get_distance_matrix_from_vcv_matrix(vcv_np)
    assert isinstance(dist, np.ndarray)
    assert dist.shape == (tree.ntips, tree.ntips)
    assert np.allclose(dist, dist.T)
    assert np.allclose(np.diag(dist), 0.0)

    tip_dmat = tree.distance.get_tip_distance_matrix(df=False)
    assert np.allclose(dist, tip_dmat)


def test_get_distance_matrix_from_vcv_matrix_dataframe(tree, vcv_df):
    """Preserve labels when converting DataFrame VCV to distance matrix."""
    dist = toytree.pcm.get_distance_matrix_from_vcv_matrix(vcv_df)
    assert isinstance(dist, pd.DataFrame)
    assert list(dist.index) == tree.get_tip_labels()
    assert list(dist.columns) == tree.get_tip_labels()
    assert np.allclose(dist.to_numpy(), dist.to_numpy().T)
    assert np.allclose(np.diag(dist.to_numpy()), 0.0)

    tip_dmat = tree.distance.get_tip_distance_matrix(df=True)
    tip_dmat = tip_dmat.loc[dist.index, dist.columns]
    assert np.allclose(dist.to_numpy(), tip_dmat.to_numpy())


def test_get_tree_from_vcv_matrix_returns_toytree_and_tip_count(tree, vcv_np, vcv_df):
    """Reconstruct trees from both ndarray and DataFrame VCV inputs."""
    out_np = toytree.pcm.get_tree_from_vcv_matrix(vcv_np)
    out_df = toytree.pcm.get_tree_from_vcv_matrix(vcv_df)

    assert isinstance(out_np, toytree.ToyTree)
    assert isinstance(out_df, toytree.ToyTree)
    assert out_np.ntips == tree.ntips
    assert out_df.ntips == tree.ntips


def test_get_vcv_matrix_from_tree_package_and_object_api_parity(tree):
    """Package-level and object-level API should produce equivalent output."""
    pkg_vcv = toytree.pcm.get_vcv_matrix_from_tree(tree, df=False)
    obj_vcv = tree.pcm.get_vcv_matrix_from_tree(df=False)
    assert np.allclose(pkg_vcv, obj_vcv)
