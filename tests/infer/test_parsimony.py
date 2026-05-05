#!/usr/bin/env python

"""Tests for parsimony score and homoplasy index utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import toytree
from toytree.infer.src.parsimony import (
    consistency_and_retention_indices,
    convert_trait_to_idx_dict,
    fitch_parsimony_score,
)


def _example_tree() -> toytree.ToyTree:
    """Return a small rooted tree with stable tip labels."""
    return toytree.tree("((a,b),(c,d));")


def _example_trait() -> dict[str, str]:
    """Return a discrete trait with one change between sister clades."""
    return {"a": "A", "b": "A", "c": "B", "d": "B"}


def test_convert_trait_to_idx_dict_accepts_mixed_tip_selectors() -> None:
    """Normalize mixed selector types into tip-indexed trait values."""
    tree = _example_tree()
    tip_a = tree.get_nodes("a")[0]
    trait = {
        tip_a: "A",
        "b": "A",
        tree.get_nodes("c")[0].idx: "B",
        "d": "B",
    }

    result = convert_trait_to_idx_dict(tree, trait)

    assert result == {0: "A", 1: "A", 2: "B", 3: "B"}


def test_convert_trait_to_idx_dict_rejects_missing_tip_values() -> None:
    """Raise if any tip state is omitted from the mapping."""
    tree = _example_tree()
    trait = {"a": "A", "b": "A", "c": "B"}

    with pytest.raises(ValueError, match="missing values for one or more tips"):
        convert_trait_to_idx_dict(tree, trait)


def test_convert_trait_to_idx_dict_rejects_internal_node_selectors() -> None:
    """Raise if trait mappings include an internal node."""
    tree = _example_tree()
    trait = {"a": "A", "b": "A", tree.treenode: "B", "d": "B"}

    with pytest.raises(ValueError, match="defined on tips only"):
        convert_trait_to_idx_dict(tree, trait)


def test_convert_trait_to_idx_dict_rejects_unhashable_states() -> None:
    """Raise if trait values are not discrete hashable states."""
    tree = _example_tree()
    trait = {"a": ["A"], "b": "A", "c": "B", "d": "B"}

    with pytest.raises(ValueError, match="discrete, hashable states"):
        convert_trait_to_idx_dict(tree, trait)


def test_fitch_parsimony_score_accepts_feature_name_and_series() -> None:
    """Compute the same score from both tree feature and Series inputs."""
    tree = _example_tree()
    trait = pd.Series(_example_trait())
    tree = tree.set_node_data("state", trait.to_dict())

    score_from_feature = fitch_parsimony_score(tree, "state")
    score_from_series = fitch_parsimony_score(tree, trait)

    assert score_from_feature == 1
    assert score_from_series == 1


def test_consistency_and_retention_indices_returns_dataframe_result() -> None:
    """Return a DataFrame with expected rows, columns, and attrs."""
    tree = _example_tree()
    result = consistency_and_retention_indices(
        tree,
        _example_trait(),
        npermutations=20,
        rng=123,
    )

    assert isinstance(result, pd.DataFrame)
    assert list(result.index) == [
        "fitch_parsimony_score",
        "CI",
        "RI",
        "RCI",
    ]
    assert list(result.columns) == [
        "observed",
        "null_mean",
        "p_value_greater",
        "p_value_less",
        "signal_tail",
    ]
    assert result.attrs["npermutations"] == 20
    assert result.attrs["null_model"] == "tip_state_permutation_preserving_state_counts"
    assert result.loc["fitch_parsimony_score", "observed"] == 1.0
    assert result.loc["CI", "observed"] == 1.0
    assert result.loc["RI", "observed"] == 1.0
    assert result.loc["RCI", "observed"] == 1.0
    assert result.loc["fitch_parsimony_score", "signal_tail"] == "less"
    assert result.loc["CI", "signal_tail"] == "greater"
    assert result.loc["RI", "signal_tail"] == "greater"
    assert result.loc["RCI", "signal_tail"] == "greater"
    assert np.all(result["p_value_greater"].between(0.0, 1.0))
    assert np.all(result["p_value_less"].between(0.0, 1.0))


def test_consistency_and_retention_indices_accepts_generator_rng() -> None:
    """Allow callers to pass a NumPy Generator directly."""
    tree = _example_tree()
    rng = np.random.default_rng(321)

    result = consistency_and_retention_indices(
        tree,
        _example_trait(),
        npermutations=5,
        rng=rng,
    )

    assert isinstance(result, pd.DataFrame)
    assert result.attrs["npermutations"] == 5


def test_consistency_and_retention_indices_rejects_zero_permutations() -> None:
    """Require at least one permutation for the null distribution."""
    tree = _example_tree()

    with pytest.raises(ValueError, match="npermutations must be >= 1"):
        consistency_and_retention_indices(
            tree,
            _example_trait(),
            npermutations=0,
        )
