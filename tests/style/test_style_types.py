#!/usr/bin/env python

"""Tests for builtin style preset classes and lookup."""

from __future__ import annotations

import pytest

from toytree.core.style_types import (
    STYLE_DICTS,
    TreeStyleU,
    get_base_tree_style_by_name,
)
from toytree.utils import ToytreeError


def test_style_registry_keys_match_supported_set() -> None:
    """Preset registry should expose the expected one-letter style keys."""
    assert set(STYLE_DICTS) == {"n", "s", "p", "o", "c", "d", "b", "u", "r"}


@pytest.mark.parametrize("key", sorted(STYLE_DICTS))
def test_get_base_tree_style_by_name_instantiates_expected_style(key: str) -> None:
    """Each one-letter key should instantiate a matching preset style."""
    style = get_base_tree_style_by_name(key)
    assert style.tree_style == key


def test_get_base_tree_style_by_name_normalizes_case_and_whitespace() -> None:
    """Style lookup should support mixed case and surrounding whitespace."""
    style = get_base_tree_style_by_name(" U ")
    assert style.tree_style == "u"


def test_get_base_tree_style_by_name_rejects_invalid_key() -> None:
    """Unknown style keys should raise a clear ToytreeError."""
    with pytest.raises(ToytreeError, match="not recognized"):
        get_base_tree_style_by_name("normal")


def test_get_base_tree_style_by_name_rejects_non_string() -> None:
    """Non-string style lookup inputs should raise ToytreeError."""
    with pytest.raises(ToytreeError, match="must be a string"):
        get_base_tree_style_by_name(1)  # type: ignore[arg-type]


def test_tree_style_u_overrides_are_applied() -> None:
    """Unrooted preset should apply its own dataclass field overrides."""
    style = TreeStyleU()
    assert style.tree_style == "u"
    assert style.layout == "unrooted"
    assert style.edge_type == "c"
    assert style.use_edge_lengths is False
    assert style.node_colors == "white"
    assert style.node_sizes == 6
    assert style.node_labels == "idx"
