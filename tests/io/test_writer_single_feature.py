#!/usr/bin/env python

"""Tests for `write_single_feature` Newick serialization mode."""

from __future__ import annotations

import numpy as np
import pytest

import toytree
from toytree.utils import ToytreeError


def test_write_single_feature_roundtrip_to_trait() -> None:
    """Writing `name{value}` labels should roundtrip parse to `trait`."""
    tree = toytree.rtree.unittree(4, seed=123)
    name_map = {node.idx: f"n{node.idx}" for node in tree}
    tree = tree.set_node_data("name", name_map)
    tree = tree.set_node_data("state", default=1)

    nwk = tree.write(
        internal_labels="name",
        dist_formatter=None,
        write_single_feature="state",
    )
    assert "n0{1}" in nwk

    parsed = toytree.tree(nwk, internal_labels="name")
    assert "trait" in parsed.features
    traits = parsed.get_node_data("trait")
    assert set(traits.dropna().tolist()) == {1}


def test_write_single_feature_respects_internal_labels_support() -> None:
    """Curly suffix writing should append to support labels when requested."""
    tree = toytree.tree("((a:1,b:1)90:1,c:1)100:0;")
    tree = tree.set_node_data("state", default=7)
    nwk = tree.write(write_single_feature="state")
    assert "90{7}" in nwk
    assert "100{7}" in nwk


def test_write_single_feature_missing_feature_raises() -> None:
    """Selected write feature must exist in the tree."""
    tree = toytree.rtree.unittree(4, seed=123)
    with pytest.raises(ToytreeError, match="not present"):
        tree.write(write_single_feature="state")


def test_write_single_feature_nan_values_raise() -> None:
    """Selected feature cannot contain NaN values."""
    tree = toytree.rtree.unittree(4, seed=123)
    tree = tree.set_node_data("state", {0: np.nan}, default=1)
    with pytest.raises(ToytreeError, match="cannot include NaN values"):
        tree.write(write_single_feature="state")


def test_write_single_feature_is_not_supported_for_nexus() -> None:
    """Curly-suffix single-feature mode is disabled for Nexus output."""
    tree = toytree.rtree.unittree(4, seed=123)
    tree = tree.set_node_data("state", default=1)
    with pytest.raises(ToytreeError, match="not supported with nexus=True"):
        tree.write(write_single_feature="state", nexus=True)


def test_write_feature_pack_serializes_list_like_values() -> None:
    """List-like metadata values should be packed using `feature_pack`."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("posterior", default=[0.1, 0.9])
    nwk = tree.write(features=["posterior"])
    assert "[&posterior=0.1|0.9]" in nwk

    parsed = toytree.tree(nwk)
    assert parsed.get_node_data("posterior").iloc[0] == [0.1, 0.9]


def test_write_feature_pack_custom_separator_roundtrips() -> None:
    """Custom pack separators should roundtrip with matching unpack token."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("posterior", default=[0.2, 0.8])
    nwk = tree.write(features=["posterior"], feature_pack=";")
    assert "[&posterior=0.2;0.8]" in nwk

    parsed = toytree.tree(nwk, feature_unpack=";")
    assert parsed.get_node_data("posterior").iloc[0] == [0.2, 0.8]


def test_write_feature_pack_conflict_raises() -> None:
    """Packed-value token cannot overlap metadata key/value delimiters."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("posterior", default=[0.2, 0.8])
    with pytest.raises(ToytreeError, match="feature_pack cannot match"):
        tree.write(
            features=["posterior"],
            feature_pack=",",
            features_delim=",",
        )


@pytest.mark.parametrize(
    ("kwargs", "param_name"),
    [
        ({"dist_formatter": "abc"}, "dist_formatter"),
        ({"internal_labels_formatter": "abc"}, "internal_labels_formatter"),
        ({"features_formatter": "abc"}, "features_formatter"),
    ],
)
def test_write_rejects_invalid_formatter_strings(
    kwargs: dict[str, str],
    param_name: str,
) -> None:
    """Invalid writer format strings should raise `ToytreeError`."""
    tree = toytree.rtree.unittree(3, seed=123)
    with pytest.raises(ToytreeError, match=param_name):
        tree.write(**kwargs)


def test_write_rejects_missing_internal_label_feature() -> None:
    """A missing internal-label feature should fail instead of vanishing."""
    tree = toytree.rtree.unittree(4, seed=123)
    with pytest.raises(ToytreeError, match="internal_labels='bogus'"):
        tree.write(dist_formatter=None, internal_labels="bogus")


def test_write_allows_partial_internal_label_data() -> None:
    """Missing values on some internal nodes should still serialize cleanly."""
    tree = toytree.rtree.unittree(4, seed=123)
    tree = tree.set_node_data("tag", {tree.ntips: "X"})
    nwk = tree.write(dist_formatter=None, internal_labels="tag")
    assert "X" in nwk


def test_write_preserves_requested_feature_order() -> None:
    """Feature metadata should preserve the caller's requested order."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("alpha", default=1)
    tree = tree.set_node_data("beta", default=2)
    nwk = tree.write(
        dist_formatter=None,
        internal_labels=None,
        features=["beta", "alpha"],
    )
    assert "[&beta=2,alpha=1]" in nwk


def test_write_rejects_ambiguous_string_feature_values() -> None:
    """String metadata containing active delimiter tokens should fail."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data("grp", default="A,B")
    with pytest.raises(ToytreeError, match="reserved metadata token ','"):
        tree.write(features=["grp"])


def test_write_accepts_path_objects(tmp_path) -> None:
    """`pathlib.Path` output should write text and return None."""
    tree = toytree.rtree.unittree(3, seed=123)
    outpath = tmp_path / "tree.nwk"
    result = tree.write(path=outpath, dist_formatter=None, internal_labels=None)
    assert result is None
    assert outpath.read_text(encoding="utf-8").strip() == tree.write(
        dist_formatter=None,
        internal_labels=None,
    )


def test_write_wraps_path_failures_as_toytreeerror(tmp_path) -> None:
    """File output failures should be normalized to `ToytreeError`."""
    tree = toytree.rtree.unittree(3, seed=123)
    outpath = tmp_path / "missing" / "tree.nwk"
    with pytest.raises(ToytreeError, match="Could not write tree data"):
        tree.write(path=outpath)


def test_write_nexus_quotes_and_roundtrips_special_tip_names() -> None:
    """NEXUS translation labels should quote and unquote special names."""
    tree = toytree.rtree.unittree(3, seed=123)
    tree = tree.set_node_data(
        "name",
        {
            0: "alpha beta",
            1: "x,y",
            2: "q'r",
        },
    )
    nexus = tree.write(nexus=True, dist_formatter=None, internal_labels=None)
    assert "0 'alpha beta'," in nexus
    assert "1 'x,y'," in nexus
    assert "2 'q''r'," in nexus
    parsed = toytree.tree(nexus)
    assert parsed.get_tip_labels() == ["alpha beta", "x_y", "q'r"]
