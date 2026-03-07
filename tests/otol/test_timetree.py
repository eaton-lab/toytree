#!/usr/bin/env python

"""Tests for TimeTree API helpers."""

from __future__ import annotations

import inspect

import pandas as pd
import pytest

import toytree
from toytree.otol.src import timetree
from toytree.utils import ToytreeError


def _tree_with_ncbi() -> toytree.ToyTree:
    """Return a small tree with ncbi_id set on tips and one internal node."""
    tree = toytree.tree("((A,B)X,C)R;")
    return tree.set_node_data(
        "ncbi_id",
        {
            0: 11,
            1: 22,
            2: 33,
            3: 111,
        },
        inplace=False,
    )


def test_fetch_json_timetree_pairwise_endpoint_path(monkeypatch):
    """Build expected pairwise endpoint path."""

    def _mock_request_json(endpoint, **kwargs):  # noqa: ARG001
        assert endpoint == "pairwise/9606/10090/summaryjson"
        return {"precomputed_age": 87.2}

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = client.fetch_json_timetree_pairwise(9606, 10090)
    assert float(out["precomputed_age"]) == pytest.approx(87.2)


def test_fetch_json_timetree_mrca_endpoint_path(monkeypatch):
    """Build expected MRCA endpoint path."""

    def _mock_request_json(endpoint, **kwargs):  # noqa: ARG001
        assert endpoint == "mrca/id/9606+10090+9685/json"
        return {"precomputed_age": 94.0}

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = client.fetch_json_timetree_mrca([9606, 10090, 9685], endpoint="json")
    assert float(out["precomputed_age"]) == pytest.approx(94.0)


def test_get_timetree_node_ages_pairwise_uses_child_internal_id(monkeypatch):
    """Use child internal node ncbi_id directly, skipping descendant sampling."""
    tree = _tree_with_ncbi()
    calls: list[tuple[int, int]] = []

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        pair = (a_id, b_id)
        calls.append(pair)
        return {"precomputed_age": float(a_id + b_id)}

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")
    assert list(table.index) == [3, 4]
    # node 3 uses tips A and B; node 4 uses internal child X (=111) and tip C (=33)
    assert calls == [(11, 22), (33, 111)]
    assert table.loc[3, "status"] == "ok"
    assert table.loc[4, "status"] == "ok"
    assert float(table.loc[4, "age"]) == pytest.approx(144.0)


def test_get_timetree_node_ages_pairwise_descendant_fallback(monkeypatch):
    """If child has no ncbi_id, use nearest descendants as pairwise candidates."""
    tree = _tree_with_ncbi().set_node_data("ncbi_id", {3: pd.NA}, inplace=False)
    calls: list[tuple[int, int]] = []

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        pair = (a_id, b_id)
        calls.append(pair)
        return {"precomputed_age": 10.0}

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")
    # root node should pair nearest descendant from X clade (A=11) with C=33.
    assert calls[1] == (11, 33)
    assert table.loc[4, "status"] == "ok"


def test_get_timetree_node_ages_data_override(monkeypatch):
    """Use data Series overrides by node idx without mutating tree features."""
    tree = _tree_with_ncbi()
    calls: list[tuple[int, int]] = []

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        calls.append((a_id, b_id))
        return {"precomputed_age": 9.0}

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    overrides = pd.Series({3: 999})
    table = client.get_timetree_node_ages(
        tree=tree,
        endpoint="pairwise",
        data=overrides,
    )
    assert calls[1] == (33, 999)
    assert table.loc[4, "status"] == "ok"
    # tree feature unchanged
    assert int(tree.get_node_data("ncbi_id").iloc[3]) == 111


def test_get_timetree_node_ages_age_columns_and_ci_clip(monkeypatch):
    """Conflicting calibrated descendants are clipped using feasible CI bounds."""
    tree = _tree_with_ncbi()

    payloads = {
        (11, 22): {
            "precomputed_age": 20.0,
            "precomputed_ci_low": 5.0,
            "precomputed_ci_high": 9.5,
        },
        (33, 111): {"precomputed_age": 10.0},
    }

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        return payloads[(a_id, b_id)]

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")
    assert "age_raw" in table.columns
    assert "age_set_method" in table.columns
    assert float(table.loc[3, "age_raw"]) == pytest.approx(20.0)
    assert float(table.loc[3, "age"]) == pytest.approx(9.5)
    assert table.loc[3, "age_set_method"] == "calibrated_ci_clipped"


def test_get_timetree_node_ages_forced_clip_when_ci_infeasible(monkeypatch):
    """Conflicting calibrated descendants are forced-clipped when CI cannot fit."""
    tree = _tree_with_ncbi()

    payloads = {
        (11, 22): {
            "precomputed_age": 20.0,
            "precomputed_ci_low": 12.0,
            "precomputed_ci_high": 25.0,
        },
        (33, 111): {"precomputed_age": 10.0},
    }

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        return payloads[(a_id, b_id)]

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")
    assert float(table.loc[3, "age"]) < float(table.loc[4, "age"])
    assert table.loc[3, "age_set_method"] == "calibrated_forced_clip"


def test_get_timetree_node_ages_imputed_edge_count(monkeypatch):
    """Fill missing internal ages by equal edge-count spacing between anchors."""
    tree = toytree.tree("(((A,B)X,C)Y,D)R;").set_node_data(
        "ncbi_id",
        {
            0: 11,
            1: 22,
            2: 33,
            3: 44,
            4: 444,  # X
            5: 555,  # Y
        },
        inplace=False,
    )

    payloads = {
        (11, 22): {"precomputed_age": 4.0},  # node X
        (33, 444): {"precomputed_age": 0.0, "adjusted_age": 0.0},  # node Y missing
        (44, 555): {"precomputed_age": 10.0},  # root
    }

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        return payloads[(a_id, b_id)]

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")
    # Y idx=5 receives path medians: [7, 7, 5] -> 7.
    assert float(table.loc[5, "age"]) == pytest.approx(7.0)
    assert table.loc[5, "age_set_method"] == "imputed_edge_count"


def test_get_timetree_node_ages_imputed_root(monkeypatch):
    """Impute root age when root retrieval is missing but descendants are known."""
    tree = _tree_with_ncbi()

    payloads = {
        (11, 22): {"precomputed_age": 5.0},  # child internal node
        (33, 111): {"precomputed_age": 0.0, "adjusted_age": 0.0},  # root missing
    }

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        return payloads[(a_id, b_id)]

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")
    assert table.loc[4, "age_set_method"] == "imputed_root"
    assert float(table.loc[4, "age"]) > float(table.loc[3, "age"])


def test_get_timetree_node_ages_internal_monotonicity(monkeypatch):
    """Final post-processing guarantees parent ages are not younger than children."""
    tree = toytree.tree("(((A,B)X,C)Y,D)R;").set_node_data(
        "ncbi_id",
        {
            0: 11,
            1: 22,
            2: 33,
            3: 44,
            4: 444,  # X
            5: 555,  # Y
        },
        inplace=False,
    )

    payloads = {
        (11, 22): {"precomputed_age": 8.0},  # node X
        (33, 444): {"precomputed_age": 0.0, "adjusted_age": 0.0},  # node Y missing
        (44, 555): {"precomputed_age": 6.0},  # root younger than X
    }

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        return payloads[(a_id, b_id)]

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="pairwise")

    for parent in tree[tree.ntips :]:
        parent_age = float(table.loc[parent.idx, "age"])
        for child in parent.children:
            if child.is_leaf():
                continue
            child_age = float(table.loc[child.idx, "age"])
            assert parent_age >= child_age


def test_get_timetree_node_ages_pairwise_respects_max_pairs(monkeypatch):
    """Try multiple pairs up to max_pairs and aggregate successful ages by median."""
    tree = toytree.tree("((A,B)X,(C,D)Y)R;").set_node_data(
        "ncbi_id",
        {
            0: 11,
            1: 22,
            2: 33,
            3: 44,
        },
        inplace=False,
    )
    calls: list[tuple[int, int]] = []

    payloads = {
        (11, 22): {"precomputed_age": 10.0},
        (33, 44): {"precomputed_age": 20.0},
        (11, 33): {"precomputed_age": 0.0, "adjusted_age": 0.0},
        (11, 44): {
            "precomputed_age": 40.0,
            "precomputed_ci_low": 30,
            "precomputed_ci_high": 41,
        },
        (22, 33): {
            "precomputed_age": 50.0,
            "precomputed_ci_low": 45,
            "precomputed_ci_high": 60,
        },
    }

    def _mock_fetch_json_timetree_pairwise(a_id, b_id, endpoint="summaryjson"):  # noqa: ARG001
        pair = (a_id, b_id)
        calls.append(pair)
        return payloads[pair]

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_pairwise",
        _mock_fetch_json_timetree_pairwise,
    )
    table = client.get_timetree_node_ages(
        tree=tree,
        endpoint="pairwise",
        max_pairs=3,
    )
    # Two internal child-node calls + exactly 3 root-level attempts.
    assert len(calls) == 5
    assert calls[2:] == [(11, 33), (11, 44), (22, 33)]
    # root median of successful pair ages [40, 50]
    assert float(table.loc[6, "age"]) == pytest.approx(45.0)
    assert int(table.loc[6, "n_pairs_attempted"]) == 3
    assert int(table.loc[6, "n_pairs_success"]) == 2
    assert float(table.loc[6, "ci_low"]) == pytest.approx(30.0)
    assert float(table.loc[6, "ci_high"]) == pytest.approx(60.0)


def test_get_timetree_node_ages_mrca(monkeypatch):
    """Run one MRCA query per internal node using child representatives."""
    tree = _tree_with_ncbi()
    calls: list[tuple[int, ...]] = []

    def _mock_fetch_json_timetree_mrca(ncbi_ids, endpoint="json"):  # noqa: ARG001
        calls.append(tuple(ncbi_ids))
        return {
            "precomputed_age": float(sum(ncbi_ids)),
            "precomputed_ci_low": 1.0,
            "precomputed_ci_high": 2.0,
            "all_total": 5,
            "taxon_id": 77,
            "mrca_ttid": 88,
        }

    client = timetree._TimeTreeClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_timetree_mrca",
        _mock_fetch_json_timetree_mrca,
    )
    table = client.get_timetree_node_ages(tree=tree, endpoint="mrca")
    assert calls == [(11, 22), (111, 33)]
    assert table.loc[4, "status"] == "ok"
    assert int(table.loc[4, "taxon_id"]) == 77


def test_get_timetree_node_ages_requires_ncbi_feature():
    """Raise if tree lacks ncbi_id feature."""
    tree = toytree.tree("((A,B),C);")
    client = timetree._TimeTreeClient(cache=False)
    with pytest.raises(ToytreeError, match="missing required 'ncbi_id'"):
        client.get_timetree_node_ages(tree=tree)


def test_get_timetree_node_ages_data_index_validation():
    """Raise on invalid data index types for override Series."""
    tree = _tree_with_ncbi()
    client = timetree._TimeTreeClient(cache=False)
    bad = pd.Series([1], index=["not_an_idx"])
    with pytest.raises(ToytreeError, match="integer node idx labels"):
        client.get_timetree_node_ages(tree=tree, data=bad)


def test_public_signatures():
    """Expose explicit signatures for public wrappers."""
    expected = {
        "configure_timetree_client": [
            "base_url",
            "timeout",
            "max_retries",
            "backoff_factor",
            "cache",
            "cache_dir",
            "session",
        ],
        "reset_timetree_client": [],
        "fetch_json_timetree_pairwise": [
            "taxon_a_id",
            "taxon_b_id",
            "endpoint",
        ],
        "fetch_json_timetree_mrca": [
            "ncbi_ids",
            "endpoint",
        ],
        "get_timetree_node_ages": [
            "tree",
            "endpoint",
            "data",
            "max_pairs",
        ],
    }
    for name, params in expected.items():
        fn = getattr(timetree, name)
        sig = inspect.signature(fn)
        assert list(sig.parameters) == params
        for par in sig.parameters.values():
            assert par.kind is not inspect.Parameter.VAR_POSITIONAL
            assert par.kind is not inspect.Parameter.VAR_KEYWORD
