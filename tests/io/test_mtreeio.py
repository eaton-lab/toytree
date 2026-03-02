#!/usr/bin/env python

import pytest

import toytree
from toytree.utils import ToytreeError


def test_mtree_rejects_empty_string():
    """Empty-string input should raise a clear user-facing parse error."""
    with pytest.raises(ToytreeError, match="empty input"):
        toytree.mtree("")


def test_mtree_rejects_empty_collection():
    """Empty collections should raise a clear user-facing parse error."""
    with pytest.raises(ToytreeError, match="empty collection"):
        toytree.mtree([])


def test_mtree_rejects_mixed_collection_types():
    """Collections containing mixed types should be rejected."""
    tree = toytree.rtree.unittree(4, seed=123)
    with pytest.raises(ToytreeError, match="mixed data types"):
        toytree.mtree([tree, "((a,b),c);"])
