# ruff: noqa: D103
"""Offline tests for the public OpenTree client and tree builders."""

from __future__ import annotations

import inspect
from pathlib import Path

import pandas as pd
import pytest

import toytree
from toytree.core import ToyTree
from toytree.otol.src import otol
from toytree.otol.src._transport import JSONServiceClient
from toytree.utils import ToytreeError


def _resolved(ids=(1, 2, 3, 4)) -> pd.DataFrame:
    names = {1: "Alpha one", 2: "Alpha two", 3: "Beta three", 4: "Beta four"}
    return pd.DataFrame(
        {
            "key": [f"k{i}" for i in ids],
            "query": [f"q{i}" for i in ids],
            "status": ["matched"] * len(ids),
            "matched_name": [names[i] for i in ids],
            "ott_id": pd.array(ids, dtype="Int64"),
            "ncbi_id": pd.array([100 + i for i in ids], dtype="Int64"),
        }
    )


def _lineages(ids=(1, 2, 3, 4)) -> list[dict]:
    genera = {1: (11, "Alpha"), 2: (11, "Alpha"), 3: (12, "Beta"), 4: (12, "Beta")}
    names = {1: "Alpha one", 2: "Alpha two", 3: "Beta three", 4: "Beta four"}
    rows = []
    for ott in ids:
        genus, genus_name = genera[ott]
        rows.append(
            {
                "ott_id": ott,
                "name": names[ott],
                "rank": "species",
                "lineage": [
                    {"ott_id": genus, "name": genus_name, "rank": "genus"},
                    {"ott_id": 40, "name": "Family Z", "rank": "family"},
                    {"ott_id": 99, "name": "Life", "rank": "no rank"},
                ],
            }
        )
    return rows


def test_query_normalization_and_raw_endpoint_payloads(monkeypatch):
    client = otol._OTOLClient(cache=False)
    calls = []

    def request(endpoint, payload, **kwargs):
        calls.append((endpoint, payload, kwargs))
        if endpoint == "tnrs/match_names":
            return {
                "results": [
                    {"name": name, "matches": [{"taxon": {"ott_id": idx + 1}}]}
                    for idx, name in enumerate(payload["names"])
                ]
            }
        if endpoint == "tree_of_life/node_info":
            return {"results": [{"node_id": i} for i in payload["node_ids"]]}
        if endpoint == "tree_of_life/mrca":
            return {"mrca": {"node_id": "ott99"}}
        if endpoint == "taxonomy/taxon_info":
            return {"ott_id": payload["ott_id"]}
        if endpoint == "taxonomy/about":
            return {"name": "ott"}
        if endpoint in {"tree_of_life/subtree", "tree_of_life/induced_subtree"}:
            return {"newick": "(ott1,ott2);", "broken": {}}
        raise AssertionError(endpoint)

    monkeypatch.setattr(client, "_request_json", request)
    assert client._query_to_node_ids([1, "ott2", "Alpha one"]) == [
        "ott1",
        "ott2",
        "ott1",
    ]
    assert len(client.fetch_json_node_info([1, 2])) == 2
    assert client.fetch_json_mrca([1, 2])["mrca"]["node_id"] == "ott99"
    assert client.fetch_json_taxon_info([1, 2]) == [{"ott_id": 1}, {"ott_id": 2}]
    assert client.fetch_json_taxonomy_about()["name"] == "ott"
    assert "newick" in client.fetch_json_subtree(1)
    assert "newick" in client.fetch_json_induced_subtree([1, 2])
    assert any(kwargs.get("use_cache") for _, _, kwargs in calls)


def test_query_rejects_empty_unmatched_and_ambiguous(monkeypatch):
    client = otol._OTOLClient(cache=False)
    with pytest.raises(ToytreeError, match="empty"):
        client._query_to_node_ids([""])
    monkeypatch.setattr(
        client,
        "fetch_json_match_names",
        lambda names: [{"name": names[0], "matches": []}],
    )
    with pytest.raises(ToytreeError, match="unmatched"):
        client._query_to_node_ids(["unknown"])
    monkeypatch.setattr(
        client,
        "fetch_json_match_names",
        lambda names: [{"name": names[0], "matches": [{}, {}]}],
    )
    with pytest.raises(ToytreeError, match="ambiguous"):
        client._query_to_node_ids(["ambiguous"])


def test_resolve_names_preserves_order_keys_and_ids(monkeypatch):
    client = otol._OTOLClient(cache=False)
    payload = {
        "results": [
            {
                "id": "Alpha one",
                "matches": [
                    {
                        "is_synonym": False,
                        "taxon": {
                            "ott_id": 1,
                            "name": "Alpha one",
                            "unique_name": "Alpha one",
                            "rank": "species",
                            "tax_sources": ["ncbi:101"],
                        },
                    }
                ],
            },
            {"id": "Missing", "matches": []},
        ]
    }
    monkeypatch.setattr(
        client, "fetch_json_match_names", lambda *args, **kwargs: payload["results"]
    )
    table = client.resolve_taxonomic_names(
        {"a": "Alpha one", "b": "Missing"},
        on_unresolved="ignore",
    )
    assert table["key"].tolist() == ["a", "b"]
    assert table["status"].tolist() == ["matched", "unmatched"]
    assert table.loc[0, "ott_id"] == 1
    assert table.loc[0, "ncbi_id"] == 101


def test_resolved_table_validation_does_not_mutate_input():
    client = otol._OTOLClient(cache=False)
    frame = _resolved().drop(columns="ncbi_id")
    before = frame.copy(deep=True)
    checked = client._validate_resolved_taxa_table(frame)
    pd.testing.assert_frame_equal(frame, before)
    assert "ncbi_id" in checked
    bad = frame.copy()
    bad.loc[0, "status"] = "unmatched"
    with pytest.raises(ToytreeError, match="unresolved"):
        client._validate_resolved_taxa_table(bad)


def test_taxonomy_builder_uses_identity_trie_and_metadata(monkeypatch):
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client, "fetch_json_taxon_info", lambda *args, **kwargs: _lineages()
    )
    tree = client.fetch_tree_from_taxonomy(_resolved())
    assert isinstance(tree, ToyTree)
    assert set(tree.get_tip_labels()) == {
        "Alpha_one_ott1",
        "Alpha_two_ott2",
        "Beta_three_ott3",
        "Beta_four_ott4",
    }
    alpha = tree.get_mrca_node("Alpha_one_ott1", "Alpha_two_ott2")
    beta = tree.get_mrca_node("Beta_three_ott3", "Beta_four_ott4")
    assert alpha.name == "Alpha_ott11"
    assert beta.name == "Beta_ott12"
    assert alpha.ott_id == 11
    assert alpha.taxonomic_rank == "genus"
    assert tree.treenode.name == "Life_ott99"
    assert all(node.dist == 1 for node in tree if not node.is_root())


def test_taxonomy_builder_forces_queried_ancestor_to_tip(monkeypatch):
    records = _lineages((1, 2))
    records.insert(
        0,
        {
            "ott_id": 11,
            "name": "Alpha",
            "rank": "genus",
            "lineage": [
                {"ott_id": 40, "name": "Family Z", "rank": "family"},
                {"ott_id": 99, "name": "Life", "rank": "no rank"},
            ],
        },
    )
    resolved = pd.concat(
        [
            pd.DataFrame(
                {
                    "query": ["Alpha"],
                    "status": ["matched"],
                    "matched_name": ["Alpha"],
                    "ott_id": pd.array([11], dtype="Int64"),
                    "ncbi_id": pd.array([111], dtype="Int64"),
                }
            ),
            _resolved((1, 2)),
        ],
        ignore_index=True,
    )
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client, "fetch_json_taxon_info", lambda *args, **kwargs: records
    )
    forced = client.fetch_tree_from_taxonomy(resolved, force_as_tips=True)
    natural = client.fetch_tree_from_taxonomy(resolved, force_as_tips=False)
    assert "Alpha_ott11" in forced.get_tip_labels()
    assert "Alpha_ott11" not in natural.get_tip_labels()
    assert natural.get_nodes("Alpha_ott11")[0].is_leaf() is False


def test_taxonomy_builder_rejects_duplicate_ids_and_labels(monkeypatch):
    client = otol._OTOLClient(cache=False)
    duplicate = pd.concat([_resolved((1, 2)), _resolved((1,))], ignore_index=True)
    with pytest.raises(ToytreeError, match="duplicate ott_id"):
        client.fetch_tree_from_taxonomy(duplicate)
    monkeypatch.setattr(
        client, "fetch_json_taxon_info", lambda *args, **kwargs: _lineages((1, 2))
    )
    with pytest.raises(ToytreeError, match="duplicate labels"):
        client.fetch_tree_from_taxonomy(_resolved((1, 2)), label_template="same")


def test_synthesis_builder_unconstrained_and_broken(monkeypatch):
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda *args, **kwargs: {
            "newick": (
                "(Alpha_one_ott1,(Alpha_two_ott2,Beta_three_ott3)" "mrcaott2ott3)root;"
            ),
            "broken": {"ott4": "mrcaott2ott3"},
        },
    )
    monkeypatch.setattr(
        client, "fetch_json_taxon_info", lambda *args, **kwargs: _lineages()
    )
    tree = client.fetch_tree_from_synthesis(
        _resolved(),
        constrain_by_taxonomy=False,
    )
    assert isinstance(tree, ToyTree)
    assert set(tree.get_tip_labels()) == {
        "Alpha_one_ott1",
        "Alpha_two_ott2",
        "Beta_three_ott3",
        "Beta_four_ott4",
    }
    node = tree.get_mrca_node("Alpha_two_ott2", "Beta_three_ott3", "Beta_four_ott4")
    assert set(node.get_leaf_names()) == {
        "Alpha_two_ott2",
        "Beta_three_ott3",
        "Beta_four_ott4",
    }


def test_synthesis_builder_can_lock_taxonomy_clades(monkeypatch):
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda *args, **kwargs: {
            "newick": (
                "((Alpha_one_ott1,Beta_three_ott3)," "(Alpha_two_ott2,Beta_four_ott4));"
            ),
            "broken": {},
        },
    )
    monkeypatch.setattr(
        client, "fetch_json_taxon_info", lambda *args, **kwargs: _lineages()
    )
    tree = client.fetch_tree_from_synthesis(_resolved(), constrain_by_taxonomy=True)
    alpha = tree.get_mrca_node("Alpha_one_ott1", "Alpha_two_ott2")
    assert set(alpha.get_leaf_names()) == {"Alpha_one_ott1", "Alpha_two_ott2"}


def test_deprecated_newick_wrappers_return_roundtrippable_strings(monkeypatch):
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client, "fetch_json_taxon_info", lambda *args, **kwargs: _lineages()
    )
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda *args, **kwargs: {
            "newick": (
                "((Alpha_one_ott1,Alpha_two_ott2)," "(Beta_three_ott3,Beta_four_ott4));"
            ),
            "broken": {},
        },
    )
    with pytest.warns(DeprecationWarning):
        taxonomy_newick = client.fetch_newick_subtree_from_taxonomy(_resolved())
    with pytest.warns(DeprecationWarning):
        synthesis_newick = client.fetch_newick_induced_tree_otol(_resolved())
    assert type(taxonomy_newick) is str
    assert type(synthesis_newick) is str
    assert toytree.tree(taxonomy_newick).ntips == 4
    assert toytree.tree(synthesis_newick).ntips == 4


class _Response:
    status_code = 200
    text = "ok"

    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class _Session:
    def __init__(self):
        self.calls = []
        self.closed = False

    def post(self, url, json, timeout):
        self.calls.append(("POST", url, json, timeout))
        return _Response({"value": json["value"]})

    def get(self, url, params, timeout):
        self.calls.append(("GET", url, params, timeout))
        return _Response({"value": params["value"]})

    def close(self):
        self.closed = True


def test_shared_transport_json_cache_and_external_session_lifecycle(tmp_path: Path):
    session = _Session()
    client = JSONServiceClient(
        "https://example.test/api",
        session=session,
        cache_dir=tmp_path,
        cache_ttl=None,
    )
    assert client._request_json("x", {"value": 1}, use_cache=True) == {"value": 1}
    assert client._request_json("x", {"value": 1}, use_cache=True) == {"value": 1}
    assert len(session.calls) == 1
    cache_files = list(tmp_path.rglob("*.json"))
    assert len(cache_files) == 1
    assert not list(tmp_path.rglob("*.pkl"))
    cache_files[0].write_text("truncated", encoding="utf-8")
    assert client._request_json("x", {"value": 1}, use_cache=True) == {"value": 1}
    assert len(session.calls) == 2
    client.close()
    assert session.closed is False


def test_client_configuration_validation_and_owned_session_close(monkeypatch):
    with pytest.raises(ValueError, match="base_url"):
        JSONServiceClient("not-a-url")
    with pytest.raises(ValueError, match="timeout"):
        JSONServiceClient("https://example.test", timeout=0)
    with pytest.raises(ValueError, match="max_retries"):
        JSONServiceClient("https://example.test", max_retries=-1)
    session = _Session()
    monkeypatch.setattr(JSONServiceClient, "_build_session", lambda *args: session)
    client = JSONServiceClient("https://example.test", cache=False)
    assert client.session is session
    client.close()
    assert session.closed is True


def test_public_api_signatures_and_exports():
    expected = {
        "configure_client": [
            "base_url",
            "timeout",
            "max_retries",
            "backoff_factor",
            "cache",
            "cache_dir",
            "cache_ttl",
            "session",
        ],
        "fetch_tree_from_taxonomy": ["resolved", "label_template", "force_as_tips"],
        "fetch_tree_from_synthesis": [
            "resolved",
            "label_template",
            "constrain_by_taxonomy",
            "force_as_tips",
        ],
        "fetch_newick_subtree_from_taxonomy": ["resolved", "label_template"],
        "fetch_newick_induced_tree_otol": [
            "resolved",
            "label_template",
            "constrain_by_taxonomy",
            "force_as_tips",
        ],
    }
    for name, params in expected.items():
        assert name in otol.__all__
        assert list(inspect.signature(getattr(otol, name)).parameters) == params
