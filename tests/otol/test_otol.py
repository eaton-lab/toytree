#!/usr/bin/env python

"""Tests for OTOL module-level API."""

from __future__ import annotations

import inspect

import pandas as pd
import pytest

from toytree.otol.src import otol
from toytree.utils import ToytreeError


def test_match_names_reports_matched_ambiguous_unmatched(monkeypatch):
    """Return standardized statuses from TNRS-like JSON."""

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {
            "results": [
                {
                    "name": "A",
                    "matches": [
                        {
                            "matched_name": "A",
                            "is_synonym": False,
                            "taxon": {"ott_id": 1},
                        }
                    ],
                },
                {"name": "B", "matches": []},
                {
                    "name": "C",
                    "matches": [
                        {
                            "matched_name": "C1",
                            "is_synonym": False,
                            "taxon": {"ott_id": 2},
                        },
                        {
                            "matched_name": "C2",
                            "is_synonym": False,
                            "taxon": {"ott_id": 3},
                        },
                    ],
                },
            ]
        }

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    table = otol.match_names(["A", "B", "C"])
    assert isinstance(table, pd.DataFrame)
    assert list(table["status"]) == ["matched", "unmatched", "ambiguous"]
    assert str(table["ott_id"].dtype) == "Int64"
    assert pd.isna(table.iloc[1]["ott_id"])
    assert pd.isna(table.iloc[2]["ott_id"])


def test_match_names_on_unresolved_raise(monkeypatch):
    """Raise on unmatched rows when on_unresolved='raise'."""

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {"results": [{"name": "X", "matches": []}]}

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    with pytest.raises(ToytreeError, match="unresolved rows"):
        otol.match_names(["X"], on_unresolved="raise")


def test_match_names_on_unresolved_warn(monkeypatch):
    """Warn and return table when unresolved rows exist."""

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {"results": [{"name": "X", "matches": []}]}

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    with pytest.warns(UserWarning, match="unresolved rows"):
        table = otol.match_names(["X"], on_unresolved="warn")
    assert list(table["status"]) == ["unmatched"]


def test_match_names_on_ambiguous_first(monkeypatch):
    """Resolve ambiguous rows deterministically when requested."""

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {
            "results": [
                {
                    "name": "C",
                    "matches": [
                        {
                            "matched_name": "C1",
                            "is_synonym": False,
                            "taxon": {"ott_id": 2},
                        },
                        {
                            "matched_name": "C2",
                            "is_synonym": False,
                            "taxon": {"ott_id": 3},
                        },
                    ],
                }
            ]
        }

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    table = otol.match_names(["C"], on_ambiguous="first")
    assert list(table["status"]) == ["matched"]
    assert int(table.iloc[0]["ott_id"]) == 2
    assert table.iloc[0]["reason"] == "resolved_first_of_2"


def test_match_names_on_ambiguous_raise(monkeypatch):
    """Raise immediately when ambiguity policy is raise."""

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {
            "results": [
                {
                    "name": "C",
                    "matches": [
                        {
                            "matched_name": "C1",
                            "is_synonym": False,
                            "taxon": {"ott_id": 2},
                        },
                        {
                            "matched_name": "C2",
                            "is_synonym": False,
                            "taxon": {"ott_id": 3},
                        },
                    ],
                }
            ]
        }

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    with pytest.raises(ToytreeError, match="ambiguous resolution failed"):
        otol.match_names(["C"], on_ambiguous="raise")


def test_match_names_raw_output(monkeypatch):
    """Return raw TNRS payload when output='raw'."""
    payload = {"results": [{"name": "X", "matches": []}]}

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {"results": [{"name": "X", "matches": []}]}

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = otol.match_names(["X"], output="raw")
    assert out == payload


def test_match_names_raw_rejects_table_only_options(monkeypatch):
    """Reject table-only options when output='raw'."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    with pytest.raises(ToytreeError, match="only valid when output='table'"):
        otol.match_names(["X"], output="raw", on_unresolved="warn")


def test_query_to_node_ids_mixed_inputs(monkeypatch):
    """Convert mixed ids and names to node IDs preserving order."""

    def _mock_resolve(
        query,
        do_approximate_matching=False,
        context=None,
        include_synonyms=True,
        on_unresolved="ignore",  # noqa: ARG001
        on_ambiguous="keep",  # noqa: ARG001
    ):
        return pd.DataFrame(
            [
                {
                    "query": "Homo sapiens",
                    "status": "matched",
                    "matched_name": "Homo sapiens",
                    "ott_id": 770315,
                    "is_synonym": False,
                    "reason": "ok",
                }
            ]
        )

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "resolve_names", _mock_resolve)
    out = client._query_to_node_ids(["ott123", 456, "Homo sapiens"])
    assert out == ["ott123", "ott456", "ott770315"]


def test_parse_ott_ids_from_tip_labels():
    """Extract OTT IDs from mixed labels."""
    labels = ["A_ott1", "B", "C_ott20"]
    assert otol._OTOLClient.parse_ott_ids_from_tip_labels(labels) == [1, 20]


def test_get_taxon_lineage_top_can_match_rank_or_name(monkeypatch):
    """Stop lineage at `top` when it matches rank or unique_name."""
    client = otol._OTOLClient(cache=False)

    def _mock_get_taxon_info(query, include_lineage=False, **kwargs):  # noqa: ARG001
        return {
            "lineage": [
                {"rank": "order", "unique_name": "Carnivora"},
                {"rank": "class", "unique_name": "Mammalia"},
                {"rank": "phylum", "unique_name": "Chordata"},
                {"rank": "kingdom", "unique_name": "Metazoa"},
            ]
        }

    monkeypatch.setattr(client, "get_taxon_info", _mock_get_taxon_info)

    by_rank = client.get_taxon_lineage("Panthera", rank_only=True, top="phylum")
    assert list(by_rank.keys()) == ["order", "class", "phylum"]

    by_name = client.get_taxon_lineage("Panthera", rank_only=True, top="Chordata")
    assert list(by_name.keys()) == ["order", "class", "phylum"]


def test_default_client_is_lazy_and_created_on_first_wrapper_call(monkeypatch):
    """Create default client only when wrapper method is first called."""
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", None)
    assert otol._DEFAULT_CLIENT is None

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {"results": [{"name": "X", "matches": []}]}

    created = otol._get_default_client()
    monkeypatch.setattr(created, "_request_json", _mock_request_json)
    _ = otol.match_names(["X"])
    assert otol._DEFAULT_CLIENT is not None


def test_otolclient_session_is_lazy(monkeypatch):
    """Defer session construction until session property is first accessed."""
    client = otol._OTOLClient(cache=False, session=None)
    assert client._session is None

    calls = {"n": 0}

    def _mock_build_session(max_retries, backoff_factor):  # noqa: ARG001
        calls["n"] += 1

        class _Dummy:
            def post(self, *args, **kwargs):  # noqa: ARG002
                class _Resp:
                    status_code = 200
                    text = "{}"

                    @staticmethod
                    def raise_for_status():
                        return None

                    @staticmethod
                    def json():
                        return {"ok": True}

                return _Resp()

            def get(self, *args, **kwargs):  # noqa: ARG002
                class _Resp:
                    status_code = 200
                    text = "ok"

                    @staticmethod
                    def raise_for_status():
                        return None

                return _Resp()

        return _Dummy()

    monkeypatch.setattr(client, "_build_session", _mock_build_session)
    out = client._request_json("x", {}, use_cache=False)
    assert out == {"ok": True}
    assert calls["n"] == 1


def test_core_wrapper_signatures_are_explicit_and_non_variadic():
    """Expose explicit wrapper signatures without *args/**kwargs."""
    expected = {
        "configure_client": [
            "base_url",
            "timeout",
            "max_retries",
            "backoff_factor",
            "cache",
            "cache_dir",
            "session",
        ],
        "reset_client": [],
        "match_names": [
            "query",
            "approximate",
            "context",
            "include_synonyms",
            "on_unresolved",
            "on_ambiguous",
            "output",
        ],
        "taxonomy": [],
        "taxon_info": [
            "query",
            "include_lineage",
            "include_children",
            "include_terminal_descendants",
        ],
        "taxon_lineage": ["query", "full_json", "rank_only", "max_height", "top"],
        "taxon_parent": ["query", "full_json", "rank_only"],
        "taxon_descendants": ["query", "min_rank", "terminal_only"],
        "taxon_id": ["query"],
        "node_info": ["query", "include_lineage"],
        "node_id": ["query"],
        "mrca": ["query"],
        "mrca_node_id": ["query"],
        "mrca_taxon_id": ["query"],
        "synthetic_subtree": ["query", "full_json", "extra_params"],
        "induced_subtree": [
            "query",
            "full_json",
            "label_format",
            "insert_broken_nodes",
        ],
        "taxonomy_subtree": ["query", "min_rank"],
        "supporting_studies": ["query"],
        "study_tree": ["study_id", "tree_id", "label_format"],
    }
    for name, params in expected.items():
        fn = getattr(otol, name)
        sig = inspect.signature(fn)
        assert list(sig.parameters) == params
        for par in sig.parameters.values():
            assert par.kind is not inspect.Parameter.VAR_POSITIONAL
            assert par.kind is not inspect.Parameter.VAR_KEYWORD

    assert not hasattr(otol, "resolve_names")
    assert not hasattr(otol, "get_matched_names")
    assert not hasattr(otol, "get_taxon_id_table")
    assert not hasattr(otol, "get_synthetic_induced_subtree")
