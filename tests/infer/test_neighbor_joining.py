#!/usr/bin/env python

"""Tests for neighbor-joining tree inference."""

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.utils import ToytreeError


def _example_distance_matrix() -> pd.DataFrame:
    """Return a labeled additive distance matrix used by multiple tests."""
    labels = ["a", "b", "c", "d", "e"]
    dist = np.array(
        [
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 2],
            [6, 6, 6, 2, 0],
        ],
        dtype=float,
    )
    return pd.DataFrame(dist, index=labels, columns=labels)


def test_neighbor_joining_tree_from_ndarray():
    """Build a tree from ndarray and preserve tip count."""
    data = _example_distance_matrix().to_numpy()
    tree = toytree.infer.neighbor_joining_tree(data)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == data.shape[0]


def test_neighbor_joining_tree_from_dataframe_preserves_labels():
    """Build a tree from DataFrame and preserve tip label set."""
    data = _example_distance_matrix()
    tree = toytree.infer.neighbor_joining_tree(data)
    assert set(tree.get_tip_labels()) == set(data.index)


def test_neighbor_joining_tree_duplicate_labels_falls_back_to_int_and_warns(capsys):
    """Fallback to integer tip labels when duplicate DataFrame labels are present."""
    data = _example_distance_matrix().copy()
    dup = ["a", "b", "c", "d", "d"]
    data.index = dup
    data.columns = dup

    tree = toytree.infer.neighbor_joining_tree(data)
    assert set(tree.get_tip_labels()) == {str(i) for i in range(data.shape[0])}
    captured = capsys.readouterr()
    assert "duplicate labels found" in captured.err.lower()
    assert "neighbor-joining tree" in captured.err.lower()


def test_neighbor_joining_tree_equal_distances_case_runs() -> None:
    """Equal-distance ties should still yield a valid tree."""
    dist = np.array(
        [
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 3],
            [6, 6, 6, 3, 0],
        ],
        dtype=float,
    )
    data = pd.DataFrame(dist, index=list("abcde"), columns=list("abcde"))
    tree = toytree.infer.neighbor_joining_tree(data)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == data.shape[0]
    assert all(float(node.dist) >= 0.0 for node in tree if not node.is_root())


def test_neighbor_joining_tree_polytomy_like_case_runs() -> None:
    """Polytomy-like distance patterns should still yield a valid tree."""
    dist = np.array(
        [
            [0, 2, 2, 4, 4],
            [2, 0, 2, 4, 4],
            [2, 2, 0, 4, 4],
            [4, 4, 4, 0, 2],
            [4, 4, 4, 2, 0],
        ],
        dtype=float,
    )
    tree = toytree.infer.neighbor_joining_tree(dist)
    assert isinstance(tree, toytree.ToyTree)
    assert tree.ntips == dist.shape[0]
    assert all(float(node.dist) >= 0.0 for node in tree if not node.is_root())


@pytest.mark.parametrize(
    "data, message",
    [
        (np.array([0.0, 1.0]), "2-dimensional"),
        (np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 2.0]]), "square"),
        (np.array([[0.0, 1.0], [1.0, 0.0]]), "at least 3"),
        (np.array([[0.0, 1.0, np.nan], [1.0, 0.0, 2.0], [np.nan, 2.0, 0.0]]), "finite"),
        (np.array([[0.0, -1.0, 2.0], [-1.0, 0.0, 2.0], [2.0, 2.0, 0.0]]), "negative"),
        (np.array([[1.0, 1.0, 2.0], [1.0, 0.0, 2.0], [2.0, 2.0, 0.0]]), "diagonal"),
        (np.array([[0.0, 1.0, 3.0], [2.0, 0.0, 2.0], [3.0, 2.0, 0.0]]), "symmetric"),
        (
            pd.DataFrame(
                [[0.0, 1.0, 2.0], [1.0, 0.0, 3.0], [2.0, 3.0, 0.0]],
                index=["a", "b", "c"],
                columns=["a", "c", "b"],
            ),
            "identical index/columns",
        ),
    ],
)
def test_neighbor_joining_tree_validation_errors(data, message):
    """Raise ToytreeError for invalid distance matrix inputs."""
    with pytest.raises(ToytreeError, match=message):
        toytree.infer.neighbor_joining_tree(data)
