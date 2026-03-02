#!/usr/bin/env python

"""Tests for UPGMA tree inference."""

from __future__ import annotations

import numpy as np
import pandas as pd

import toytree


def test_upgma_binary_tree_arr(distance_matrix_5taxa_additive: pd.DataFrame) -> None:
    """Build a UPGMA tree from ndarray input."""
    dist = distance_matrix_5taxa_additive.to_numpy()
    tree = toytree.infer.upgma_tree(dist)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == dist.shape[0]
    assert all(float(node.dist) >= 0.0 for node in tree if not node.is_root())


def test_upgma_binary_tree_df(distance_matrix_5taxa_additive: pd.DataFrame) -> None:
    """Build a UPGMA tree from DataFrame input and preserve labels."""
    tree = toytree.infer.upgma_tree(distance_matrix_5taxa_additive)
    assert isinstance(tree, toytree.ToyTree)
    assert set(tree.get_tip_labels()) == set(distance_matrix_5taxa_additive.index)


def test_upgma_equal_dists_tree(distance_matrix_5taxa_equal_tie: pd.DataFrame) -> None:
    """UPGMA should return a valid tree when ties occur."""
    tree = toytree.infer.upgma_tree(distance_matrix_5taxa_equal_tie)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == distance_matrix_5taxa_equal_tie.shape[0]


def test_upgma_polytomy_tree(distance_matrix_5taxa_polytomy_like: np.ndarray) -> None:
    """UPGMA should return a valid tree for polytomy-like distances."""
    tree = toytree.infer.upgma_tree(distance_matrix_5taxa_polytomy_like)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == distance_matrix_5taxa_polytomy_like.shape[0]


def test_upgma_polytomy_and_equal_dists_tree(
    distance_matrix_5taxa_polytomy_like: np.ndarray,
) -> None:
    """Repeated call on polytomy-like matrix should still return valid tree."""
    tree = toytree.infer.upgma_tree(distance_matrix_5taxa_polytomy_like)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == distance_matrix_5taxa_polytomy_like.shape[0]


def test_upgma_identical_names(distance_matrix_5taxa_additive: pd.DataFrame) -> None:
    """Duplicate labels should fallback to integer tip labels."""
    data = distance_matrix_5taxa_additive.copy()
    dup = list("abcdd")
    data.index = dup
    data.columns = dup
    tree = toytree.infer.upgma_tree(data)
    assert set(tree.get_tip_labels()) == {str(i) for i in range(data.shape[0])}
