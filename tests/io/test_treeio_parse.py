#!/usr/bin/env python

"""Tests for tree I/O source parsing and translation behavior."""

from __future__ import annotations

from textwrap import dedent

import pytest

import toytree
from toytree.core.multitree import MultiTree
from toytree.core.node import Node
from toytree.io.src.nexus import get_newicks_and_translation_from_nexus
from toytree.io.src.parse import parse_data_from_str, parse_tree, parse_tree_object
from toytree.utils import ToytreeError


def test_tree_rejects_empty_or_whitespace_input() -> None:
    """Public tree parsing should reject empty string input."""
    with pytest.raises(ToytreeError, match="empty input"):
        toytree.tree("")
    with pytest.raises(ToytreeError, match="empty input"):
        toytree.tree("   \n\t")


def test_tree_accepts_node_input_and_detaches_copy() -> None:
    """Passing a `Node` root should still return a detached `ToyTree`."""
    root = Node(name="root")
    parsed = toytree.tree(root)
    assert parsed.ntips == 1
    assert parsed.treenode is not root
    assert parsed.treenode.name == "root"


def test_parse_tree_warns_and_returns_first_tree_for_multiline_input(
    capsys,
) -> None:
    """Single-tree parsing should warn and return the first tree only."""
    data = "((a,b),c);\n((a,c),b);"
    tree = parse_tree(data)
    captured = capsys.readouterr()
    assert "Loading only the first tree" in captured.err
    assert tree.write(dist_formatter=None) == "((a,b),c);"


def test_parse_tree_object_returns_multitree_for_multiple_trees() -> None:
    """Auto object parsing should return a `MultiTree` for multi input."""
    data = "((a,b),c);\n((a,c),b);"
    parsed = parse_tree_object(data)
    assert isinstance(parsed, MultiTree)
    assert parsed.ntrees == 2


def test_parse_tree_object_returns_toytree_for_single_tree() -> None:
    """Auto object parsing should return a `ToyTree` for single input."""
    parsed = parse_tree_object("((a,b),c);")
    assert parsed.write(dist_formatter=None) == "((a,b),c);"


def test_parse_tree_accepts_utf8_bytes_input() -> None:
    """Parser helpers should continue to accept UTF-8 encoded bytes."""
    parsed = parse_tree(b"((a,b),c);")
    assert parsed.write(dist_formatter=None) == "((a,b),c);"


def test_tree_less_nexus_raises_clear_error() -> None:
    """NEXUS input without any trees should raise `ToytreeError`."""
    text = dedent(
        """\
        #NEXUS
        begin trees;
        end;
        """
    )
    with pytest.raises(ToytreeError, match="No trees were found"):
        toytree.tree(text)


def test_nexus_translation_remaps_tips_only_and_keeps_internal_names() -> None:
    """NEXUS translation should affect tip labels but not internal names."""
    text = dedent(
        """\
        #NEXUS
        begin trees;
            translate
                1 apple,
                2 berry,
                3 cherry,
            ;
            tree tree0 = ((1,2)X,3)R;
        end;
        """
    )
    tree = parse_tree(text, internal_labels="name")
    assert tree.get_tip_labels() == ["apple", "berry", "cherry"]
    assert list(tree.get_node_data("name")[-2:]) == ["X", "R"]


def test_nexus_translation_keeps_internal_support_values() -> None:
    """NEXUS translation should leave internal support values untouched."""
    text = dedent(
        """\
        #NEXUS
        begin trees;
            translate
                1 apple,
                2 berry,
                3 cherry,
            ;
            tree tree0 = ((1,2)90,3)100;
        end;
        """
    )
    tree = parse_tree(text)
    supports = set(float(value) for value in tree.get_node_data("support").dropna())
    assert tree.get_tip_labels() == ["apple", "berry", "cherry"]
    assert 90.0 in supports
    assert 100.0 in supports


def test_nexus_translation_missing_tip_token_raises() -> None:
    """Incomplete translation blocks should fail on unresolved tip tokens."""
    text = dedent(
        """\
        #NEXUS
        begin trees;
            translate
                1 apple,
                2 berry,
            ;
            tree tree0 = ((1,2),3);
        end;
        """
    )
    with pytest.raises(ToytreeError, match="translate block"):
        parse_tree(text)


def test_nexus_helper_extracts_newicks_and_translation_map() -> None:
    """Direct NEXUS extraction should parse tree records and translate labels."""
    text = dedent(
        """\
        #NEXUS
        begin trees;
            translate
                1 apple,
                2 berry,
                3 cherry,
            ;
            tree * tree0 = [&R] ((1,2),3);
            tree tree1 = [&U] ((1,3),2);
        end;
        """
    )
    newicks, tdict = get_newicks_and_translation_from_nexus(text)
    assert newicks == ["((1,2),3);", "((1,3),2);"]
    assert tdict == {"1": "apple", "2": "berry", "3": "cherry"}


def test_nexus_helper_unquotes_escaped_translation_labels() -> None:
    """Quoted translate labels should be unescaped during extraction."""
    text = dedent(
        """\
        #NEXUS
        begin trees;
            translate
                1 'alpha beta',
                2 'x,y',
                3 'q''r',
            ;
            tree tree0 = ((1,2),3);
        end;
        """
    )
    newicks, tdict = get_newicks_and_translation_from_nexus(text)
    assert newicks == ["((1,2),3);"]
    assert tdict == {"1": "alpha beta", "2": "x,y", "3": "q'r"}


def test_parse_data_from_str_rejects_empty_serialized_input() -> None:
    """Direct serialized parsing should fail cleanly on empty strings."""
    with pytest.raises(ToytreeError, match="No trees were found"):
        parse_data_from_str("")
