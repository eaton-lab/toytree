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

    supports = tree.get_node_data("support")[tree.ntips:-1].to_numpy()
    assert 90 in supports
    assert 80 in supports
    assert np.isnan(supports).any()


def test_mixed_numeric_and_string_warns_and_keeps_names(capsys) -> None:
    """Mixed label types warn and preserve internal labels as names."""
    nwk = "((a:1,b:1)90:1,(c:1,d:1)X:1);"
    tree = toytree.tree(nwk)
    captured = capsys.readouterr()
    assert "mixed numeric and non-numeric" in captured.err

    names = tree.get_node_data("name")[tree.ntips:-1].to_list()
    assert "90" in names
    assert "X" in names


def test_force_name_override_keeps_numeric_labels_as_names() -> None:
    """`internal_labels='name'` should not infer support values."""
    nwk = "((a:1,b:1)90:1,(c:1,d:1)80:1);"
    tree = toytree.tree(nwk, internal_labels="name")
    names = tree.get_node_data("name")[tree.ntips:-1].to_list()
    assert "90" in names
    assert "80" in names


def test_force_support_override_parses_support() -> None:
    """`internal_labels='support'` should parse numeric support values."""
    nwk = "((a:1,b:1)90:1,(c:1,d:1)80:1);"
    tree = toytree.tree(nwk, internal_labels="support")
    supports = tree.get_node_data("support")[tree.ntips:-1].to_numpy()
    assert 90 in supports
    assert 80 in supports
