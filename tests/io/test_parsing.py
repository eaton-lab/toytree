#!/usr/bin/env python

"""Tests for internal-label parsing behavior."""

from __future__ import annotations

import numpy as np

import toytree


def test_numeric_with_missing_infers_support_no_warning(capsys) -> None:
    """Numeric internal labels with missing values infer support silently."""
    nwk = "((a:1,b:1)90:1,((c:1,d:1)80:1,(e:1,f:1):1):1);"
    tree = toytree.tree(nwk)
    captured = capsys.readouterr()
    assert captured.err.strip() == ""

    supports = tree.get_node_data("support")[tree.ntips : -1].to_numpy()
    assert 90 in supports
    assert 80 in supports
    assert np.isnan(supports).any()


def test_mixed_numeric_and_string_warns_and_keeps_names(capsys) -> None:
    """Mixed label types warn and preserve internal labels as names."""
    nwk = "((a:1,b:1)90:1,(c:1,d:1)X:1);"
    tree = toytree.tree(nwk)
    captured = capsys.readouterr()
    assert "mixed numeric and non-numeric" in captured.err

    names = tree.get_node_data("name")[tree.ntips : -1].to_list()
    assert "90" in names
    assert "X" in names


def test_force_name_override_keeps_numeric_labels_as_names() -> None:
    """`internal_labels='name'` should not infer support values."""
    nwk = "((a:1,b:1)90:1,(c:1,d:1)80:1);"
    tree = toytree.tree(nwk, internal_labels="name")
    names = tree.get_node_data("name")[tree.ntips : -1].to_list()
    assert "90" in names
    assert "80" in names


def test_force_support_override_parses_support() -> None:
    """`internal_labels='support'` should parse numeric support values."""
    nwk = "((a:1,b:1)90:1,(c:1,d:1)80:1);"
    tree = toytree.tree(nwk, internal_labels="support")
    supports = tree.get_node_data("support")[tree.ntips : -1].to_numpy()
    assert 90 in supports
    assert 80 in supports


def test_curly_suffix_labels_extract_trait_for_all_nodes() -> None:
    """Strict all-node `name{value}` labels should extract `trait` feature."""
    nwk = "((a{1}:1,b{2}:1)90{3}:1,c{4}:1)100{5}:0;"
    tree = toytree.tree(nwk)
    assert "trait" in tree.features

    traits = tree.get_node_data("trait")
    assert traits.iloc[0] == 1
    assert traits.iloc[1] == 2
    assert traits.iloc[2] == 4
    assert traits.iloc[3] == 3
    assert traits.iloc[4] == 5

    supports = tree.get_node_data("support")
    assert 90 in set(float(i) for i in supports.dropna())
    assert 100 in set(float(i) for i in supports.dropna())
    assert tree.get_node_data("name").iloc[0] == "a"


def test_curly_suffix_labels_allow_root_without_curly() -> None:
    """Curly extraction should allow root to omit curly suffix."""
    nwk = "((a{1}:1,b{2}:1)90{3}:1,c{4}:1)100:0;"
    tree = toytree.tree(nwk)
    assert "trait" in tree.features

    traits = tree.get_node_data("trait")
    assert traits.iloc[0] == 1
    assert traits.iloc[1] == 2
    assert traits.iloc[2] == 4
    assert traits.iloc[3] == 3
    assert np.isnan(traits.iloc[4])

    supports = tree.get_node_data("support")
    assert 90 in set(float(i) for i in supports.dropna())
    assert 100 in set(float(i) for i in supports.dropna())


def test_curly_suffix_extraction_is_skipped_if_any_label_missing_curly() -> None:
    """Curly extraction should not apply unless every node label matches."""
    nwk = "((a{1}:1,b{2}:1)90:1,c{4}:1)100{5}:0;"
    tree = toytree.tree(nwk, internal_labels="name")
    assert "trait" not in tree.features

    names = tree.get_node_data("name")
    assert names.iloc[0] == "a{1}"
    assert names.iloc[1] == "b{2}"
    assert names.iloc[2] == "c{4}"
    assert names.iloc[3] == "90"
    assert names.iloc[4] == "100{5}"


def test_curly_suffix_values_auto_coerce_numeric_then_string() -> None:
    """Curly suffix parsing should coerce int/float and preserve strings."""
    nwk = "((a{1.5}:1,b{foo}:1)x{2}:1,c{3}:1)r{bar}:0;"
    tree = toytree.tree(nwk, internal_labels="name")
    traits = tree.get_node_data("trait")
    assert traits.iloc[0] == 1.5
    assert traits.iloc[1] == "foo"
    assert traits.iloc[2] == 3
    assert traits.iloc[3] == 2
    assert traits.iloc[4] == "bar"


def test_curly_suffix_extraction_skips_root_only_tree_without_curly() -> None:
    """Root-only trees without curly labels should not create `trait`."""
    tree = toytree.tree("root;")
    assert "trait" not in tree.features


def test_nhx_list_like_values_unpack_by_default() -> None:
    """Default NHX parsing should unpack list-like values delimited by `|`."""
    nwk = "((a[&p=0.1|0.9]:1,b[&p=0.2|0.8]:1):1,c:1);"
    tree = toytree.tree(nwk)
    value = tree.get_node_data("p").iloc[0]
    assert value == [0.1, 0.9]


def test_nhx_name_values_never_unpack() -> None:
    """Built-in scalar `name` metadata should preserve `|` as raw text."""
    nwk = "((a[&name=x|y]:1,b:1):1,c:1);"
    tree = toytree.tree(nwk)
    assert tree.get_node_data("name").iloc[0] == "x|y"


def test_nhx_list_like_values_respect_custom_unpack_or_disable() -> None:
    """Custom or disabled unpack tokens should change parsing behavior."""
    nwk = "((a[&p=0.1;0.9]:1,b[&p=0.2;0.8]:1):1,c:1);"

    # Parse with a custom unpack token.
    tree = toytree.tree(nwk, feature_unpack=";")
    assert tree.get_node_data("p").iloc[0] == [0.1, 0.9]

    # Disable unpacking and keep values as raw scalar strings.
    tree_disabled = toytree.tree(
        "((a[&p=0.1|0.9]:1,b[&p=0.2|0.8]:1):1,c:1);",
        feature_unpack="",
    )
    assert tree_disabled.get_node_data("p").iloc[0] == "0.1|0.9"
