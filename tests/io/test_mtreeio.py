#!/usr/bin/env python

from pathlib import Path

import pytest

import toytree
from toytree.utils import ToytreeError


def test_mtree_rejects_empty_string():
    """Empty-string input should raise a clear user-facing parse error."""
    with pytest.raises(ToytreeError, match="empty input"):
        toytree.mtree("")


def test_mtree_rejects_whitespace_only_string():
    """Whitespace-only input should raise a clear user-facing parse error."""
    with pytest.raises(ToytreeError, match="empty input"):
        toytree.mtree("   \n\t")


def test_mtree_rejects_empty_bytes():
    """Empty bytes input should raise a clear user-facing parse error."""
    with pytest.raises(ToytreeError, match="empty input"):
        toytree.mtree(b"")


def test_mtree_accepts_direct_bytes_input():
    """Direct bytes input should parse like any other multitree source."""
    mtree = toytree.mtree(b"((a,b),c);\n((a,c),b);")
    assert mtree.ntrees == 2
    assert mtree[0].write(dist_formatter=None) == "((a,b),c);"


def test_mtree_rejects_empty_collection():
    """Empty collections should raise a clear user-facing parse error."""
    with pytest.raises(ToytreeError, match="empty collection"):
        toytree.mtree([])


def test_mtree_accepts_mixed_serialized_collection_types(tmp_path: Path):
    """Ordered serialized inputs may mix strings, paths, and bytes."""
    path = tmp_path / "tree.nwk"
    path.write_text("((a,d),c);", encoding="utf-8")
    mtree = toytree.mtree(
        [
            "((a,b),c);",
            path,
            b"((a,c),b);",
        ]
    )
    assert mtree.ntrees == 3
    assert [tree.write(dist_formatter=None) for tree in mtree] == [
        "((a,b),c);",
        "((a,d),c);",
        "((a,c),b);",
    ]


def test_mtree_accepts_generator_input():
    """Ordered generators should be parsed once in yielded order."""
    mtree = toytree.mtree(i for i in ["((a,b),c);", "((a,c),b);"])
    assert mtree.ntrees == 2
    assert mtree[1].write(dist_formatter=None) == "((a,c),b);"


def test_mtree_write_deprecated_kwargs_warns_on_stderr(capsys):
    """Deprecated MultiTree.write kwargs should warn on stderr."""
    mtree = toytree.mtree(["((a,b),c);", "((a,c),b);"])

    result = mtree.write(legacy=True)
    captured = capsys.readouterr()

    assert result == "\n".join(tree.write() for tree in mtree)
    assert "Deprecated args to write()" in captured.err


def test_mtree_get_consensus_tree_deprecated_kwargs_warns_on_stderr(capsys):
    """Deprecated MultiTree consensus kwargs should warn on stderr."""
    mtree = toytree.mtree(["((a,b),c);", "((a,c),b);"])

    tree = mtree.get_consensus_tree(legacy=True)
    captured = capsys.readouterr()

    assert tree.get_tip_labels() == ["a", "b", "c"]
    assert "Deprecated args to get_consensus_tree()" in captured.err


@pytest.mark.parametrize(
    "data",
    [
        {"((a,b),c);", "((a,c),b);"},
        frozenset({"((a,b),c);", "((a,c),b);"}),
    ],
)
def test_mtree_rejects_unordered_collections(data):
    """Unordered containers should be rejected to preserve tree order."""
    with pytest.raises(ToytreeError, match="unordered collections"):
        toytree.mtree(data)


def test_mtree_rejects_mapping_input():
    """Mappings should be rejected instead of iterating over keys."""
    with pytest.raises(ToytreeError, match="mapping input"):
        toytree.mtree({"tree0": "((a,b),c);"})


def test_mtree_rejects_mixed_tree_and_serialized_collection():
    """Collections cannot mix `ToyTree` objects with serialized inputs."""
    tree = toytree.rtree.unittree(4, seed=123)
    with pytest.raises(ToytreeError, match="cannot mix ToyTree objects"):
        toytree.mtree([tree, "((a,b),c);"])
