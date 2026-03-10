#!/usr/bin/env python

"""Regression tests for Newick parsing behavior and error handling."""

from __future__ import annotations

import pytest

import toytree
from toytree.io.src.newick import meta_parser, parse_newick_string_custom
from toytree.utils import ToytreeError


def test_parse_topology_only_with_empty_labels() -> None:
    """Topology-only trees with empty labels should still parse."""
    tree = toytree.tree("((,),(,,));")
    assert tree.nnodes == 8
    assert tree.ntips == 5


def test_parse_internal_names_and_distances() -> None:
    """Internal names and distances should parse onto the expected features."""
    tree = toytree.tree("((a:2,b:2)A:2,c:2)B:2;", internal_labels="name")
    assert tree.nnodes == 5
    assert tree.ntips == 3
    assert list(tree.get_node_data("name")[-2:]) == ["A", "B"]
    assert all(tree.get_node_data("dist")[:-1] == 2.0)
    assert tree.treenode.dist == 0.0


def test_parse_edge_metadata_marks_edge_features() -> None:
    """Metadata after edge lengths should be recorded as edge features."""
    tree = toytree.tree("((a:1,b:1)A:2[&posterior=0.9],c:1)R;")
    assert "posterior" in tree.features
    assert "posterior" in tree.edge_features
    assert tree.get_node_data("posterior").iloc[3] == 0.9


def test_parse_node_metadata_does_not_mark_edge_features() -> None:
    """Metadata on node labels should not be marked as edge features."""
    tree = toytree.tree("((a:1,b:1)A[&state=1]:2,c:1)R;")
    assert "state" in tree.features
    assert "state" not in tree.edge_features
    assert tree.get_node_data("state").iloc[3] == 1.0


def test_parse_metadata_without_prefix_under_default_settings() -> None:
    """Default parsing should still accept metadata blocks without `&`."""
    tree = toytree.tree("((a[x=0]:1,b[x=3,y=1]:1)A:1,c[x=2]:1)R:1;")
    data = tree.get_node_data(["x", "y"])
    assert data.iloc[0, 0] == 0.0
    assert data.iloc[1, 0] == 3.0
    assert data.iloc[1, 1] == 1.0
    assert data.iloc[2, 0] == 2.0


def test_meta_parser_accepts_explicit_empty_prefix() -> None:
    """An empty prefix should parse metadata without stripping characters."""
    assert meta_parser("x=1,y=2", prefix="") == {"x": 1.0, "y": 2.0}
    assert meta_parser("&x=1", prefix="") == {"&x": 1.0}


def test_parse_exact_nhx_prefix_preserves_leading_chars_in_keys() -> None:
    """Exact prefix handling should not strip unrelated leading key characters."""
    tree = toytree.tree(
        "((a[&&NHX:Hx=1]:1,b:1):1,c:1);",
        feature_prefix="&&NHX:",
    )
    assert "Hx" in tree.features
    assert tree.get_node_data("Hx").iloc[0] == 1.0


def test_parse_metadata_with_nested_braces_preserves_value() -> None:
    """Commas inside brace-delimited values should not split metadata items."""
    tree = toytree.tree(
        "((a[&range={0.1,0.2},label=A]:1,b:1):1,c:1);",
    )
    data = tree.get_node_data(["range", "label"])
    assert data.iloc[0, 0] == "{0.1,0.2}"
    assert data.iloc[0, 1] == "A"


def test_reserved_metadata_feature_names_are_remapped() -> None:
    """Reserved feature names in metadata should be renamed safely."""
    tree = toytree.tree("((a[&dist=7]:1,b:1):1,c:1);")
    assert getattr(tree[0], "__dist") == 7.0


def test_root_numeric_label_is_parsed_as_support() -> None:
    """Numeric root labels should populate root support instead of root name."""
    tree = toytree.tree("((a:1,b:1)90:1,c:1)100;")
    assert tree.treenode.support == 100
    assert tree.treenode.name == ""


def test_custom_formatters_and_aggregator_are_respected() -> None:
    """Custom parse hooks should still shape values during tree construction."""

    def dist_formatter(text: str) -> float:
        return float(text) * 10.0

    def feat_formatter(text: str) -> dict[str, str]:
        return {"raw_meta": text}

    def aggregator(label, children, distance, features):
        node = toytree.Node(name=label)
        node._dist = distance
        for child in children:
            node._add_child(child)
        for key, value in features.items():
            setattr(node, key, value)
        node.source = "custom"
        return node

    tree = parse_newick_string_custom(
        "((a[&x=1]:1,b:2)X:3,c:4)R;",
        dist_formatter=dist_formatter,
        feat_formatter=feat_formatter,
        aggregator=aggregator,
        internal_labels="name",
    )

    assert tree.treenode.source == "custom"
    assert tree[0].dist == 10.0
    assert tree[1].dist == 20.0
    assert tree[3].dist == 30.0
    assert tree[0].raw_meta == "&x=1"


def test_deeply_nested_newick_parses_without_recursion_error() -> None:
    """Deeply nested trees should parse without recursive descent limits."""
    labels = [f"t{i}:1" for i in range(250)]
    nwk = labels[0]
    for label in labels[1:]:
        nwk = f"({nwk},{label})"
    tree = toytree.tree(f"{nwk};")
    assert tree.ntips == 250


@pytest.mark.parametrize(
    "newick, match",
    [
        ("((a,b),c)", "end with ';'"),
        ("((a,b),c));", "parentheses are imbalanced"),
        ("((a[&x=1,b):1,c:1);", "metadata blocks are imbalanced"),
        ("((a[&&NHX:x=1]:1,b:1):1,c:1);", "feature_prefix"),
    ],
)
def test_invalid_newick_inputs_raise_toytree_error(newick: str, match: str) -> None:
    """Malformed inputs should raise `ToytreeError` with clear messages."""
    kwargs = {}
    if "&&NHX" in newick:
        kwargs["feature_prefix"] = "&&NXH:"
    with pytest.raises(ToytreeError, match=match):
        toytree.tree(newick, **kwargs)
