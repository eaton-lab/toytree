#!/usr/bin/env python

"""Tests for deterministic DLC reconciliation."""

from __future__ import annotations

import pytest

import toytree
from toytree.infer.src.dlc_reconcile import reconcile_gene_tree_dlc


@pytest.fixture
def sptree() -> toytree.ToyTree:
    """Return a rooted species tree for reconciliation tests."""
    return toytree.tree("((A,B),C);")


def test_requires_rooted_trees(sptree: toytree.ToyTree) -> None:
    """Both gene and species trees must be rooted."""
    gtree = toytree.tree("((a1,a2),c1);")
    imap = {"a1": "A", "a2": "A", "c1": "C"}
    with pytest.raises(ValueError):
        reconcile_gene_tree_dlc(gtree.unroot(), sptree, imap)
    with pytest.raises(ValueError):
        reconcile_gene_tree_dlc(gtree, sptree.unroot(), imap)


def test_imap_required_or_exact_match(sptree: toytree.ToyTree) -> None:
    """Reconciliation requires either explicit map or exact-name fallback."""
    gtree = toytree.tree("((x1,x2),x3);")
    with pytest.raises(TypeError):
        reconcile_gene_tree_dlc(gtree, sptree)

    gtree2 = toytree.tree("((A,B),C);")
    with pytest.raises(TypeError):
        reconcile_gene_tree_dlc(gtree2, sptree)

    imap = {"A": "A", "B": "B", "C": "C"}
    out = reconcile_gene_tree_dlc(gtree2, sptree, imap=imap)
    assert "summary" in out


def test_basic_counts_known_case(sptree: toytree.ToyTree) -> None:
    """Known case should report at least one duplication."""
    gtree = toytree.tree("((a1,a2),c1);")
    imap = {"a1": "A", "a2": "A", "c1": "C"}
    out = reconcile_gene_tree_dlc(gtree, sptree, imap)
    assert out["summary"]["duplications"] == 1
    assert out["summary"]["losses"] >= 0
    assert out["summary"]["coalescences"] >= 0
    assert out["summary"]["score"] == (
        out["summary"]["duplications"]
        + out["summary"]["losses"]
        + out["summary"]["coalescences"]
    )


def test_data_table_and_annotations(sptree: toytree.ToyTree) -> None:
    """Result should include per-node table and node annotations."""
    gtree = toytree.tree("((a1,a2),c1);")
    imap = {"a1": "A", "a2": "A", "c1": "C"}
    out = reconcile_gene_tree_dlc(gtree, sptree, imap)
    data = out["data"]
    assert data.shape[0] == gtree.nnodes
    assert "dlc_ns" in data.columns
    assert "dlc_dups" in data.columns
    assert "dlc_losses" in data.columns
    assert "dlc_extra_lineages" in data.columns

    feats = out["tree"].get_node_data()
    assert "dlc_ns" in feats.columns
    assert "dlc_dups" in feats.columns


def test_inplace_behavior(sptree: toytree.ToyTree) -> None:
    """`inplace=True` should annotate and return the same gene-tree object."""
    gtree = toytree.tree("((a1,a2),c1);")
    imap = {"a1": "A", "a2": "A", "c1": "C"}
    out = reconcile_gene_tree_dlc(gtree, sptree, imap, inplace=True)
    assert out["tree"] is gtree
