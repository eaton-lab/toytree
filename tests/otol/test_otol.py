#!/usr/bin/env python

"""Tests for OTOL raw JSON API methods."""

from __future__ import annotations

import inspect

import pandas as pd
import pytest

import toytree
from toytree.otol.src import otol
from toytree.utils import ToytreeError


def test_fetch_json_match_names_returns_results_list(monkeypatch):
    """Return raw TNRS results list."""

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        assert endpoint == "tnrs/match_names"
        return {"results": [{"name": "A", "matches": []}]}

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", client)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = otol.fetch_json_match_names(["A"])
    assert isinstance(out, list)
    assert out[0]["name"] == "A"


def test_fetch_json_node_info_accepts_mixed_query(monkeypatch):
    """Normalize mixed query values before node_info call."""

    def _mock_match_names(query, approximate=False, context=None):  # noqa: ARG001
        assert query == ["Homo sapiens"]
        return [{"name": "Homo sapiens", "matches": [{"taxon": {"ott_id": 770315}}]}]

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        assert endpoint == "tree_of_life/node_info"
        assert payload["node_ids"] == ["ott123", "ott770315"]
        return [{"node_id": "ott123"}, {"node_id": "ott770315"}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_match_names)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = client.fetch_json_node_info([123, "Homo sapiens"])
    assert len(out) == 2


def test_fetch_json_mrca(monkeypatch):
    """Return raw mrca payload."""

    def _mock_query_to_node_ids(query):  # noqa: ARG001
        return ["ott1", "ott2"]

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        assert endpoint == "tree_of_life/mrca"
        assert payload == {"node_ids": ["ott1", "ott2"]}
        return {"mrca": {"node_id": "mrcaott1ott2"}}

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "_query_to_node_ids", _mock_query_to_node_ids)
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = client.fetch_json_mrca(["a", "b"])
    assert out["mrca"]["node_id"] == "mrcaott1ott2"


def test_fetch_json_taxon_info_multiple(monkeypatch):
    """Return one taxonomy record per input token."""
    calls = {"n": 0}

    def _mock_taxon_payload_from_query(query):
        if query == "A":
            return {"ott_id": 1}
        return {"ott_id": 2}

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        calls["n"] += 1
        assert endpoint == "taxonomy/taxon_info"
        return {"ott_id": payload["ott_id"]}

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client, "_taxon_payload_from_query", _mock_taxon_payload_from_query
    )
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    out = client.fetch_json_taxon_info(["A", "B"], include_lineage=True)
    assert calls["n"] == 2
    assert [i["ott_id"] for i in out] == [1, 2]


def test_fetch_json_studies_by_doi_normalizes_inputs(monkeypatch):
    """Normalize DOI prefixes before studies query."""
    seen = []

    def _mock_fetch_json_studies(property_name, value, verbose):  # noqa: ARG001
        seen.append((property_name, value))
        return [{"ot:studyId": f"ot_{len(seen)}"}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "_fetch_json_studies", _mock_fetch_json_studies)
    out = client.fetch_json_studies_by_doi(
        [
            "10.1002/ajb2.1019",
            "doi:10.1002/ajb2.1019",
            "https://doi.org/10.1002/ajb2.1019",
        ]
    )
    assert all(i[0] == "ot:studyPublication" for i in seen)
    assert all(i[1] == "10.1002/ajb2.1019" for i in seen)
    assert len(out) == 3


def test_query_to_node_ids_raises_on_ambiguous_name(monkeypatch):
    """Raise clear error on ambiguous name in node-id conversion."""

    def _mock_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": query[0],
                "matches": [{"taxon": {"ott_id": 1}}, {"taxon": {"ott_id": 2}}],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_match_names)
    with pytest.raises(ToytreeError, match="ambiguous name query"):
        client._query_to_node_ids(["Ambiguous"])


def test_default_client_lazy(monkeypatch):
    """Create default client only on first module wrapper call."""
    monkeypatch.setattr(otol, "_DEFAULT_CLIENT", None)
    assert otol._DEFAULT_CLIENT is None

    def _mock_request_json(endpoint, payload, **kwargs):  # noqa: ARG001
        return {"results": []}

    client = otol._get_default_client()
    monkeypatch.setattr(client, "_request_json", _mock_request_json)
    _ = otol.fetch_json_match_names(["X"])
    assert otol._DEFAULT_CLIENT is not None


def test_session_lazy(monkeypatch):
    """Construct network session only when first request is made."""
    client = otol._OTOLClient(cache=False, session=None)
    assert client._session is None
    calls = {"n": 0}

    def _mock_build_session(max_retries, backoff_factor):  # noqa: ARG001
        calls["n"] += 1

        class _Dummy:
            def post(self, *args, **kwargs):  # noqa: ARG002
                class _Resp:
                    @staticmethod
                    def raise_for_status():
                        return None

                    @staticmethod
                    def json():
                        return {"results": []}

                    text = "{}"
                    status_code = 200

                return _Resp()

        return _Dummy()

    monkeypatch.setattr(client, "_build_session", _mock_build_session)
    _ = client.fetch_json_match_names(["X"])
    assert calls["n"] == 1


def test_resolve_taxonomic_names_includes_ncbi_id_and_policies(monkeypatch):
    """Parse ncbi_id and preserve nullable integer columns."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Canis lupus",
                "matches": [
                    {
                        "matched_name": "Canis lupus",
                        "is_synonym": False,
                        "taxon": {
                            "ott_id": 1,
                            "tax_sources": ["ncbi:9612", "gbif:2435099"],
                        },
                    }
                ],
            },
            {"name": "Unknown taxon", "matches": []},
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        ["Canis lupus", "Unknown taxon"],
        on_unresolved="ignore",
    )
    assert list(out.columns) == [
        "key",
        "query",
        "status",
        "matched_name",
        "rank",
        "taxon_name",
        "ott_id",
        "ncbi_id",
        "is_synonym",
        "reason",
    ]
    assert pd.isna(out.loc[0, "key"])
    assert pd.isna(out.loc[1, "key"])
    assert str(out["ott_id"].dtype) == "Int64"
    assert str(out["ncbi_id"].dtype) == "Int64"
    assert int(out.loc[0, "ncbi_id"]) == 9612
    assert pd.isna(out.loc[1, "rank"])
    assert pd.isna(out.loc[1, "taxon_name"])
    assert pd.isna(out.loc[1, "ott_id"])
    assert pd.isna(out.loc[1, "ncbi_id"])


def test_resolve_taxonomic_names_ignore_ambiguous_leaves_taxon_fields_missing(
    monkeypatch,
):
    """Ignore ambiguous rows without leaking or requiring taxon metadata."""

    def _mock_first_ambiguous(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Ambiguous first",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 1},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 2},
                    },
                ],
            }
        ]

    def _mock_after_matched(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Canis lupus",
                "matches": [
                    {
                        "matched_name": "Canis lupus",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Canis lupus",
                            "rank": "species",
                            "ott_id": 9612,
                            "tax_sources": ["ncbi:9612"],
                        },
                    }
                ],
            },
            {
                "name": "Ambiguous after matched",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 3},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 4},
                    },
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)

    monkeypatch.setattr(client, "fetch_json_match_names", _mock_first_ambiguous)
    first = client.resolve_taxonomic_names(["Ambiguous first"], on_ambiguous="ignore")
    assert first.loc[0, "status"] == "ambiguous"
    assert first.loc[0, "matched_name"] is None
    assert first.loc[0, "reason"] == "2_matches"
    assert pd.isna(first.loc[0, "rank"])
    assert pd.isna(first.loc[0, "taxon_name"])
    assert pd.isna(first.loc[0, "ott_id"])
    assert pd.isna(first.loc[0, "ncbi_id"])

    monkeypatch.setattr(client, "fetch_json_match_names", _mock_after_matched)
    after = client.resolve_taxonomic_names(
        ["Canis lupus", "Ambiguous after matched"],
        on_ambiguous="ignore",
    )
    assert after.loc[1, "status"] == "ambiguous"
    assert after.loc[1, "matched_name"] is None
    assert after.loc[1, "reason"] == "2_matches"
    assert pd.isna(after.loc[1, "rank"])
    assert pd.isna(after.loc[1, "taxon_name"])
    assert pd.isna(after.loc[1, "ott_id"])
    assert pd.isna(after.loc[1, "ncbi_id"])


def test_resolve_taxonomic_names_keep_alias_warns_and_maps_to_ignore(
    monkeypatch,
    capsys,
):
    """Accept deprecated keep alias and warn to use ignore instead."""

    def _mock_ambiguous(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Ambiguous name",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 1},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 2},
                    },
                ],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_ambiguous)
    out = client.resolve_taxonomic_names(["Ambiguous name"], on_ambiguous="keep")
    captured = capsys.readouterr()

    assert out.loc[0, "status"] == "ambiguous"
    assert "deprecated" in captured.err
    assert "use 'ignore' instead" in captured.err


def test_resolve_taxonomic_names_defaults_ambiguous_to_first(monkeypatch):
    """Resolve ambiguous names to the first match by default."""

    def _mock_ambiguous(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Ambiguous name",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 1},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 2},
                    },
                ],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_ambiguous)
    out = client.resolve_taxonomic_names(["Ambiguous name"])

    assert out.loc[0, "status"] == "matched"
    assert out.loc[0, "matched_name"] == "Choice A"
    assert int(out.loc[0, "ott_id"]) == 1
    assert out.loc[0, "reason"] == "resolved_first_of_2"


def test_resolve_taxonomic_names_raises_on_unresolved(monkeypatch):
    """Raise when unresolved policy is set to 'raise'."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [{"name": "Unknown taxon", "matches": []}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    with pytest.raises(ToytreeError, match="return_unresolved=True"):
        client.resolve_taxonomic_names(
            ["Unknown taxon"],
            on_unresolved="raise",
        )


def test_resolve_taxonomic_names_warn_prints_to_stderr(monkeypatch, capsys):
    """Print unresolved warning message to stderr when on_unresolved='warn'."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [{"name": "Unknown taxon", "matches": []}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    _ = client.resolve_taxonomic_names(
        ["Unknown taxon"],
        on_unresolved="warn",
    )
    captured = capsys.readouterr()
    assert "unresolved rows" in captured.err
    assert "return_unresolved=True" in captured.err


def test_resolve_taxonomic_names_return_unresolved_filters_rows(monkeypatch):
    """Return only unresolved rows when requested."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Canis lupus",
                "matches": [
                    {
                        "matched_name": "Canis lupus",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Canis lupus",
                            "rank": "species",
                            "ott_id": 1,
                        },
                    }
                ],
            },
            {"name": "Unknown taxon", "matches": []},
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        ["Canis lupus", "Unknown taxon"],
        return_unresolved=True,
    )

    assert list(out["query"]) == ["Unknown taxon"]
    assert list(out["status"]) == ["unmatched"]


def test_resolve_taxonomic_names_return_unresolved_includes_ambiguous_rows(monkeypatch):
    """Include ambiguous rows in unresolved-only output when ambiguity is ignored."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Ambiguous name",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 1},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 2},
                    },
                ],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        ["Ambiguous name"],
        on_ambiguous="ignore",
        return_unresolved=True,
    )

    assert list(out["status"]) == ["ambiguous"]
    assert list(out["query"]) == ["Ambiguous name"]


def test_resolve_taxonomic_names_return_unresolved_returns_empty_when_all_resolved(
    monkeypatch,
):
    """Return an empty table with the standard schema when nothing is unresolved."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Canis lupus",
                "matches": [
                    {
                        "matched_name": "Canis lupus",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Canis lupus",
                            "rank": "species",
                            "ott_id": 1,
                        },
                    }
                ],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        ["Canis lupus"],
        return_unresolved=True,
    )

    assert out.empty
    assert list(out.columns) == [
        "key",
        "query",
        "status",
        "matched_name",
        "rank",
        "taxon_name",
        "ott_id",
        "ncbi_id",
        "is_synonym",
        "reason",
    ]


def test_resolve_taxonomic_names_return_unresolved_still_warns(monkeypatch, capsys):
    """Keep unresolved warn behavior while returning only unresolved rows."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [{"name": "Unknown taxon", "matches": []}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        ["Unknown taxon"],
        on_unresolved="warn",
        return_unresolved=True,
    )
    captured = capsys.readouterr()

    assert list(out["status"]) == ["unmatched"]
    assert "return_unresolved=True" in captured.err


def test_resolve_taxonomic_names_return_unresolved_skips_raise(monkeypatch, capsys):
    """Do not raise when unresolved rows are being returned explicitly."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [{"name": "Unknown taxon", "matches": []}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        ["Unknown taxon"],
        on_unresolved="raise",
        return_unresolved=True,
    )
    captured = capsys.readouterr()

    assert list(out["status"]) == ["unmatched"]
    assert captured.err == ""


def test_resolve_taxonomic_names_mapping_supports_key_column(monkeypatch):
    """Resolve mapping values as queries while preserving mapping keys."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        assert query == ["Canis lupus", "Unknown taxon"]
        return [
            {
                "name": "Canis lupus",
                "matches": [
                    {
                        "matched_name": "Canis lupus",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Canis lupus",
                            "rank": "species",
                            "ott_id": 1,
                        },
                    }
                ],
            },
            {"name": "Unknown taxon", "matches": []},
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        {"wolf": "Canis lupus", "missing": "Unknown taxon"},
        on_unresolved="ignore",
    )

    assert list(out.columns) == [
        "key",
        "query",
        "status",
        "matched_name",
        "rank",
        "taxon_name",
        "ott_id",
        "ncbi_id",
        "is_synonym",
        "reason",
    ]
    assert list(out["key"]) == ["wolf", "missing"]
    assert list(out["query"]) == ["Canis lupus", "Unknown taxon"]
    assert list(out["status"]) == ["matched", "unmatched"]


def test_resolve_taxonomic_names_mapping_return_unresolved_keeps_key(
    monkeypatch,
):
    """Keep mapping keys on unresolved-only returns."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Canis lupus",
                "matches": [
                    {
                        "matched_name": "Canis lupus",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Canis lupus",
                            "rank": "species",
                            "ott_id": 1,
                        },
                    }
                ],
            },
            {"name": "Unknown taxon", "matches": []},
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    out = client.resolve_taxonomic_names(
        {"wolf": "Canis lupus", "missing": "Unknown taxon"},
        return_unresolved=True,
    )

    assert list(out["key"]) == ["missing"]
    assert list(out["query"]) == ["Unknown taxon"]
    assert list(out["status"]) == ["unmatched"]


def test_resolve_taxonomic_names_mapping_ignore_ambiguous_preserves_key(
    monkeypatch,
):
    """Preserve mapping key on ambiguous rows when ambiguity is ignored."""

    def _mock_ambiguous(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Ambiguous name",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 1},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 2},
                    },
                ],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_ambiguous)
    out = client.resolve_taxonomic_names(
        {"sample_a": "Ambiguous name"},
        on_ambiguous="ignore",
    )

    assert list(out["key"]) == ["sample_a"]
    assert list(out["status"]) == ["ambiguous"]
    assert list(out["query"]) == ["Ambiguous name"]


def test_resolve_taxonomic_names_mapping_default_first_preserves_key(monkeypatch):
    """Preserve mapping key when the default ambiguity policy picks first."""

    def _mock_ambiguous(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Ambiguous name",
                "matches": [
                    {
                        "matched_name": "Choice A",
                        "is_synonym": False,
                        "taxon": {"name": "Choice A", "rank": "species", "ott_id": 1},
                    },
                    {
                        "matched_name": "Choice B",
                        "is_synonym": False,
                        "taxon": {"name": "Choice B", "rank": "species", "ott_id": 2},
                    },
                ],
            }
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_ambiguous)
    out = client.resolve_taxonomic_names({"sample_a": "Ambiguous name"})

    assert list(out["key"]) == ["sample_a"]
    assert list(out["status"]) == ["matched"]
    assert list(out["query"]) == ["Ambiguous name"]
    assert out.loc[0, "reason"] == "resolved_first_of_2"


def test_resolve_taxonomic_names_mapping_duplicate_values_preserve_keys(monkeypatch):
    """Preserve distinct keys when a mapping contains duplicate query values."""

    def _mock_duplicate_values(query, approximate=False, context=None):  # noqa: ARG001
        assert query == ["Repeated name", "Repeated name"]
        return [
            {
                "name": "Repeated name",
                "matches": [
                    {
                        "matched_name": "Repeated name",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Repeated name",
                            "rank": "species",
                            "ott_id": 1,
                        },
                    }
                ],
            },
            {
                "name": "Repeated name",
                "matches": [
                    {
                        "matched_name": "Repeated name",
                        "is_synonym": False,
                        "taxon": {
                            "name": "Repeated name",
                            "rank": "species",
                            "ott_id": 2,
                        },
                    }
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_duplicate_values)
    out = client.resolve_taxonomic_names(
        {"sample_a": "Repeated name", "sample_b": "Repeated name"},
        on_duplicate="ignore",
    )

    assert list(out["key"]) == ["sample_a", "sample_b"]
    assert list(out["query"]) == ["Repeated name", "Repeated name"]
    assert list(out["ott_id"]) == [1, 2]


def test_resolve_taxonomic_names_warns_on_duplicate_ott_ids(monkeypatch, capsys):
    """Warn by default when different matched queries resolve to the same OTT id."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Pedicularis groenlandica",
                "matches": [
                    {
                        "matched_name": "Pedicularis groenlandica",
                        "is_synonym": False,
                        "taxon": {"name": "Pedicularis groenlandica", "ott_id": 11},
                    }
                ],
            },
            {
                "name": "Pedicularis cranolopha",
                "matches": [
                    {
                        "matched_name": "Pedicularis cranolopha",
                        "is_synonym": False,
                        "taxon": {"name": "Pedicularis cranolopha", "ott_id": 11},
                    }
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    _ = client.resolve_taxonomic_names(
        ["Pedicularis groenlandica", "Pedicularis cranolopha"],
        on_unresolved="ignore",
    )
    captured = capsys.readouterr()
    assert "ott11" in captured.err
    assert "'Pedicularis groenlandica'" in captured.err
    assert "'Pedicularis cranolopha'" in captured.err


def test_resolve_taxonomic_names_warns_once_per_duplicate_ott_group(
    monkeypatch,
    capsys,
):
    """Emit one stderr line per duplicated OTT id group in warn mode."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Query A1",
                "matches": [
                    {
                        "matched_name": "Match A1",
                        "is_synonym": False,
                        "taxon": {"name": "Match A1", "ott_id": 101},
                    }
                ],
            },
            {
                "name": "Query A2",
                "matches": [
                    {
                        "matched_name": "Match A2",
                        "is_synonym": False,
                        "taxon": {"name": "Match A2", "ott_id": 101},
                    }
                ],
            },
            {
                "name": "Query B1",
                "matches": [
                    {
                        "matched_name": "Match B1",
                        "is_synonym": False,
                        "taxon": {"name": "Match B1", "ott_id": 202},
                    }
                ],
            },
            {
                "name": "Query B2",
                "matches": [
                    {
                        "matched_name": "Match B2",
                        "is_synonym": False,
                        "taxon": {"name": "Match B2", "ott_id": 202},
                    }
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    _ = client.resolve_taxonomic_names(
        ["Query A1", "Query A2", "Query B1", "Query B2"],
        on_unresolved="ignore",
        on_duplicate="warn",
    )
    captured = capsys.readouterr()
    lines = [line for line in captured.err.strip().splitlines() if line]
    assert len(lines) == 2
    assert "ott101" in lines[0]
    assert "'Query A1'" in lines[0]
    assert "'Query A2'" in lines[0]
    assert "ott202" in lines[1]
    assert "'Query B1'" in lines[1]
    assert "'Query B2'" in lines[1]


def test_resolve_taxonomic_names_ignores_duplicate_ott_warning_when_configured(
    monkeypatch,
    capsys,
):
    """Suppress duplicate-OTT warnings when on_duplicate='ignore'."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Query A",
                "matches": [
                    {
                        "matched_name": "Match A",
                        "is_synonym": False,
                        "taxon": {"name": "Match A", "ott_id": 101},
                    }
                ],
            },
            {
                "name": "Query B",
                "matches": [
                    {
                        "matched_name": "Match B",
                        "is_synonym": False,
                        "taxon": {"name": "Match B", "ott_id": 101},
                    }
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    _ = client.resolve_taxonomic_names(
        ["Query A", "Query B"],
        on_unresolved="ignore",
        on_duplicate="ignore",
    )
    captured = capsys.readouterr()
    assert "multiple matched queries resolve to ott" not in captured.err


def test_resolve_taxonomic_names_raises_on_duplicate_ott_ids(monkeypatch):
    """Raise on duplicate matched OTT ids when on_duplicate='raise'."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Query A",
                "matches": [
                    {
                        "matched_name": "Match A",
                        "is_synonym": False,
                        "taxon": {"name": "Match A", "ott_id": 101},
                    }
                ],
            },
            {
                "name": "Query B",
                "matches": [
                    {
                        "matched_name": "Match B",
                        "is_synonym": False,
                        "taxon": {"name": "Match B", "ott_id": 101},
                    }
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    with pytest.raises(ToytreeError, match="ott101"):
        client.resolve_taxonomic_names(
            ["Query A", "Query B"],
            on_unresolved="ignore",
            on_duplicate="raise",
        )


def test_resolve_taxonomic_names_no_duplicate_ott_warning_when_ids_unique(
    monkeypatch,
    capsys,
):
    """Stay silent when matched OTT ids are unique."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [
            {
                "name": "Query A",
                "matches": [
                    {
                        "matched_name": "Match A",
                        "is_synonym": False,
                        "taxon": {"name": "Match A", "ott_id": 101},
                    }
                ],
            },
            {
                "name": "Query B",
                "matches": [
                    {
                        "matched_name": "Match B",
                        "is_synonym": False,
                        "taxon": {"name": "Match B", "ott_id": 202},
                    }
                ],
            },
        ]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    _ = client.resolve_taxonomic_names(
        ["Query A", "Query B"],
        on_unresolved="ignore",
        on_duplicate="warn",
    )
    captured = capsys.readouterr()
    assert "multiple matched queries resolve to ott" not in captured.err


def test_public_signatures_and_removed_old_api():
    """Expose explicit signatures and remove old method names."""
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
        "fetch_json_match_names": ["query", "approximate", "context"],
        "fetch_json_node_info": ["query", "include_lineage"],
        "fetch_json_mrca": ["query"],
        "fetch_json_taxon_info": [
            "query",
            "include_lineage",
            "include_children",
            "include_terminal_descendants",
        ],
        "fetch_json_taxonomy_about": [],
        "fetch_json_subtree": ["query", "extra_params"],
        "fetch_json_induced_subtree": ["query", "label_format"],
        "fetch_json_studies_by_author": ["query", "verbose"],
        "fetch_json_studies_by_taxa": ["query", "verbose"],
        "fetch_json_studies_by_doi": ["query", "verbose"],
        "resolve_taxonomic_names": [
            "query",
            "approximate",
            "context",
            "include_synonyms",
            "on_unresolved",
            "on_ambiguous",
            "on_duplicate",
            "return_unresolved",
        ],
        "fetch_newick_subtree_from_taxonomy": ["resolved", "label_template"],
        "fetch_newick_induced_tree_otol": [
            "resolved",
            "label_template",
            "constrain_by_taxonomy",
        ],
    }
    for name, params in expected.items():
        fn = getattr(otol, name)
        sig = inspect.signature(fn)
        assert list(sig.parameters) == params
        for par in sig.parameters.values():
            assert par.kind is not inspect.Parameter.VAR_POSITIONAL
            assert par.kind is not inspect.Parameter.VAR_KEYWORD

    rsig = inspect.signature(otol.resolve_taxonomic_names)
    assert rsig.parameters["on_ambiguous"].default == "first"
    assert rsig.parameters["return_unresolved"].default is False

    assert not hasattr(otol, "match_names")
    assert not hasattr(otol, "taxon_info")
    assert not hasattr(otol, "induced_subtree")


def _lineage_records_fixture():
    """Return deterministic lineage records with tribe/subfamily/family structure."""
    return [
        {
            "ott_id": 1,
            "name": "SpeciesA",
            "unique_name": "SpeciesA",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "GenusA", "rank": "genus"},
                {"ott_id": 21, "name": "TribeX", "rank": "tribe"},
                {"ott_id": 31, "name": "SubfamilyY", "rank": "subfamily"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 2,
            "name": "SpeciesB",
            "unique_name": "SpeciesB",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "GenusB", "rank": "genus"},
                {"ott_id": 21, "name": "TribeX", "rank": "tribe"},
                {"ott_id": 31, "name": "SubfamilyY", "rank": "subfamily"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 3,
            "name": "SpeciesC",
            "unique_name": "SpeciesC",
            "rank": "species",
            "lineage": [
                {"ott_id": 13, "name": "GenusC", "rank": "genus"},
                {"ott_id": 22, "name": "TribeQ", "rank": "tribe"},
                {"ott_id": 32, "name": "SubfamilyQ", "rank": "subfamily"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
    ]


def _resolved_df_from_lineages(
    lineages: list[dict[str, object]],
    *,
    use_query: bool = False,
    use_key: bool = False,
) -> pd.DataFrame:
    """Return a resolved-name table compatible with fetch_newick_* methods."""
    rows = []
    for idx, rec in enumerate(lineages):
        ott = int(rec["ott_id"])
        name = str(rec.get("name", f"ott{ott}"))
        row = {
            "key": rec.get("key", f"k{idx}") if use_key else pd.NA,
            "query": f"q{idx}" if use_query else name,
            "status": "matched",
            "matched_name": name,
            "ott_id": ott,
            "ncbi_id": pd.NA,
            "is_synonym": False,
            "reason": "ok",
        }
        rows.append(row)
    out = pd.DataFrame(rows)
    out["ott_id"] = pd.array(out["ott_id"], dtype="Int64")
    out["ncbi_id"] = pd.array(out["ncbi_id"], dtype="Int64")
    return out


def _resolved_df_from_records(
    records: list[dict[str, object]],
) -> pd.DataFrame:
    """Return a resolved-name table from explicit row records."""
    rows = []
    for idx, rec in enumerate(records):
        row = {
            "key": rec.get("key", pd.NA),
            "query": rec.get("query", f"q{idx}"),
            "status": rec.get("status", "matched"),
            "matched_name": rec.get("matched_name", rec.get("query", f"q{idx}")),
            "ott_id": rec["ott_id"],
            "ncbi_id": rec.get("ncbi_id", pd.NA),
            "is_synonym": rec.get("is_synonym", False),
            "reason": rec.get("reason", "ok"),
        }
        rows.append(row)
    out = pd.DataFrame(rows)
    out["ott_id"] = pd.array(out["ott_id"], dtype="Int64")
    out["ncbi_id"] = pd.array(out["ncbi_id"], dtype="Int64")
    return out


def test_pairwise_shared_rank_distance_from_lineages_sequence():
    """Compute matrix from sequence input using inferred unique-name labels."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineage_records_fixture()
    dist = client._pairwise_shared_rank_distance_from_lineages_info(lineages)
    assert list(dist.index) == ["SpeciesA", "SpeciesB", "SpeciesC"]
    assert int(dist.loc["SpeciesA", "SpeciesB"]) == 2  # tribe
    assert int(dist.loc["SpeciesA", "SpeciesC"]) == 4  # family
    assert int(dist.loc["SpeciesB", "SpeciesC"]) == 4  # family
    assert int(dist.iloc[0, 0]) == 0
    assert (dist.values == dist.values.T).all()


def test_pairwise_shared_rank_distance_from_lineages_mapping_uses_keys():
    """Use mapping keys as labels instead of record unique_name values."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineage_records_fixture()
    mapping = {"a": lineages[0], "b": lineages[1], "c": lineages[2]}
    dist = client._pairwise_shared_rank_distance_from_lineages_info(mapping)
    assert list(dist.index) == ["a", "b", "c"]
    assert int(dist.loc["a", "b"]) == 2


def test_pairwise_shared_rank_distance_uses_no_shared_fallback():
    """Assign fallback code when no mapped shared ranks exist."""
    client = otol._OTOLClient(cache=False)
    data = [
        {"ott_id": 100, "name": "A", "rank": "no rank", "lineage": []},
        {"ott_id": 200, "name": "B", "rank": "clade", "lineage": []},
    ]
    dist = client._pairwise_shared_rank_distance_from_lineages_info(data)
    assert int(dist.loc["A", "B"]) == 11


def test_fetch_newick_subtree_from_taxonomy_lineage_labels(monkeypatch):
    """Build Newick subtree and label internals from shared lineage ancestors."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: _lineage_records_fixture(),
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(_lineage_records_fixture())
    nwk = client.fetch_newick_subtree_from_taxonomy(resolved)
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == {
        "SpeciesA_ott1",
        "SpeciesB_ott2",
        "SpeciesC_ott3",
    }
    internals = [str(i.name) for i in tree[tree.ntips :] if str(i.name)]
    assert any(name == "TribeX_ott21" for name in internals)
    assert any(name == "FamilyZ_ott41" for name in internals)


def test_newick_subtree_from_taxonomy_normalizes_internal_lineage_spaces(monkeypatch):
    """Convert internal lineage labels with whitespace to underscore tokens."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 1,
            "name": "Species A",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "Genus A", "rank": "genus"},
                {"ott_id": 41, "name": "Family Z", "rank": "family"},
            ],
        },
        {
            "ott_id": 2,
            "name": "Species B",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "Genus B", "rank": "genus"},
                {"ott_id": 41, "name": "Family Z", "rank": "family"},
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(data)
    nwk = client.fetch_newick_subtree_from_taxonomy(resolved)
    tree = toytree.tree(nwk)
    internals = {str(node.name) for node in tree[tree.ntips :] if str(node.name)}
    assert "Family_Z_ott41" in internals
    assert set(tree.get_tip_labels()) == {"Species_A_ott1", "Species_B_ott2"}


@pytest.mark.parametrize(
    "template, expected",
    [
        (
            "{matched_name}_ott{ott_id}",
            {"SpeciesA_ott1", "SpeciesB_ott2", "SpeciesC_ott3"},
        ),
        ("{matched_name}", {"SpeciesA", "SpeciesB", "SpeciesC"}),
        ("ott{ott_id}", {"ott1", "ott2", "ott3"}),
        ("{query_id}_{ott_id}", {"q0_1", "q1_2", "q2_3"}),
        ("{key}_{ott_id}", {"k0_1", "k1_2", "k2_3"}),
    ],
)
def test_fetch_newick_subtree_from_taxonomy_label_templates(
    monkeypatch,
    template,
    expected,
):
    """Apply label templates to output tip labels."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineage_records_fixture()
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(lineages, use_query=True, use_key=True)
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template=template,
    )
    assert set(tree.get_tip_labels()) == expected


def test_fetch_newick_subtree_from_taxonomy_missing_key_formats_as_empty(
    monkeypatch,
):
    """Render missing key values as empty strings in label templates."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineage_records_fixture()[:2]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_records(
        [
            {
                "key": pd.NA,
                "query": "q0",
                "matched_name": "SpeciesA",
                "ott_id": 1,
            },
            {
                "key": None,
                "query": "q1",
                "matched_name": "SpeciesB",
                "ott_id": 2,
            },
        ]
    )
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{key}{query}_{ott_id}",
    )
    assert set(tree.get_tip_labels()) == {"q0_1", "q1_2"}


def test_format_resolved_taxon_label_supports_key_and_missing_values():
    """Expose key in the shared OTOL label formatter and blank missing keys."""
    client = otol._OTOLClient(cache=False)

    keyed = client._format_resolved_taxon_label(
        row={
            "key": "sample_a",
            "query": "Canis lupus",
            "matched_name": "Canis lupus",
            "ott_id": 1,
            "ncbi_id": pd.NA,
        },
        label_template="{key}_{ott_id}",
        idx=0,
    )
    missing = client._format_resolved_taxon_label(
        row={
            "key": pd.NA,
            "query": "Canis lupus",
            "matched_name": "Canis lupus",
            "ott_id": 1,
            "ncbi_id": pd.NA,
        },
        label_template="{key}{query_id}_{ott_id}",
        idx=0,
    )

    assert keyed == "sample_a_1"
    assert missing == "Canis_lupus_1"


def test_newick_subtree_from_taxonomy_normalizes_whitespace_in_names(monkeypatch):
    """Convert whitespace in taxa names to underscores in output labels."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 1,
            "name": "Pedicularis anas",
            "rank": "species",
            "lineage": [{"ott_id": 11, "name": "Pedicularis", "rank": "genus"}],
        },
        {
            "ott_id": 2,
            "name": "Castilleja campestris",
            "rank": "species",
            "lineage": [{"ott_id": 12, "name": "Castilleja", "rank": "genus"}],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(data)
    nwk = client.fetch_newick_subtree_from_taxonomy(resolved)
    tree = toytree.tree(nwk)
    assert "Pedicularis_anas_ott1" in set(tree.get_tip_labels())
    assert "Castilleja_campestris_ott2" in set(tree.get_tip_labels())


def _mock_taxonomy_distance_matrix(label_to_lineage):
    """Return a simple symmetric matrix keyed to current leaf labels."""
    labels = list(label_to_lineage)
    data = [
        [0 if i == j else 1 for j in range(len(labels))] for i in range(len(labels))
    ]
    dist = pd.DataFrame(data, index=labels, columns=labels)
    return dist, None


def test_fetch_newick_subtree_from_taxonomy_reassigns_internal_input_tip(
    monkeypatch,
    capsys,
):
    """Retain mixed-rank ancestor inputs as internals instead of duplicate tips."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 11,
            "name": "Pedicularis",
            "rank": "genus",
            "lineage": [
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                }
            ],
        },
        {
            "ott_id": 1,
            "name": "Pedicularis anas",
            "rank": "species",
            "lineage": [
                {
                    "ott_id": 11,
                    "name": "Pedicularis",
                    "rank": "genus",
                    "tax_sources": [],
                },
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
        {
            "ott_id": 2,
            "name": "Pedicularis groenlandica",
            "rank": "species",
            "lineage": [
                {
                    "ott_id": 11,
                    "name": "Pedicularis",
                    "rank": "genus",
                    "tax_sources": [],
                },
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        otol.induced_tree,
        "build_cophenetic_distance_matrix_from_taxonomy",
        _mock_taxonomy_distance_matrix,
    )
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("(ott11,(ott1,ott2)X)Root;"),
    )  # noqa: ARG005,E501

    resolved = _resolved_df_from_lineages(data)
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{matched_name}_ott{ott_id}",
    )
    captured = capsys.readouterr()

    assert set(tree.get_tip_labels()) == {
        "Pedicularis_anas_ott1",
        "Pedicularis_groenlandica_ott2",
    }
    assert not any(
        node.is_leaf() and getattr(node, "ott_id", None) == 11 for node in tree
    )
    assert sum(getattr(node, "ott_id", None) == 11 for node in tree) == 1
    assert "assigned to internal node" in captured.err
    assert "returning 2 tips for 3 matched taxa" in captured.err


def test_fetch_newick_subtree_from_taxonomy_groups_duplicate_tip_matches(
    monkeypatch,
    capsys,
):
    """Expand duplicate terminal OTT matches under an artificial parent."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 11,
            "name": "Pedicularis",
            "rank": "genus",
            "lineage": [
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                }
            ],
        },
        {
            "ott_id": 2,
            "name": "Castilleja campestris",
            "rank": "species",
            "lineage": [
                {
                    "ott_id": 12,
                    "name": "Castilleja",
                    "rank": "genus",
                    "tax_sources": [],
                },
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        otol.induced_tree,
        "build_cophenetic_distance_matrix_from_taxonomy",
        _mock_taxonomy_distance_matrix,
    )
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("(ott11,ott2)Root;"),
    )  # noqa: ARG005,E501

    resolved = _resolved_df_from_records(
        [
            {"query": "ped_a", "matched_name": "Pedicularis", "ott_id": 11},
            {"query": "ped_b", "matched_name": "Pedicularis", "ott_id": 11},
            {
                "query": "castilleja",
                "matched_name": "Castilleja campestris",
                "ott_id": 2,
            },
        ]
    )
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{query}_{ott_id}",
    )
    captured = capsys.readouterr()

    assert captured.err == ""
    assert set(tree.get_tip_labels()) == {"ped_a_11", "ped_b_11", "castilleja_2"}
    group = next(node for node in tree if node.name == "Pedicularis_ott11_group")
    assert pd.isna(group.ott_id)
    assert [child.name for child in group.children] == ["ped_a_11", "ped_b_11"]
    assert [int(child.ott_id) for child in group.children] == [11, 11]


def test_fetch_newick_subtree_from_taxonomy_collapses_duplicate_internal_matches(
    monkeypatch,
    capsys,
):
    """Keep duplicated ancestor matches only on the inferred internal node."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 11,
            "name": "Pedicularis",
            "rank": "genus",
            "lineage": [
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                }
            ],
        },
        {
            "ott_id": 1,
            "name": "Pedicularis anas",
            "rank": "species",
            "lineage": [
                {
                    "ott_id": 11,
                    "name": "Pedicularis",
                    "rank": "genus",
                    "tax_sources": [],
                },
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
        {
            "ott_id": 2,
            "name": "Pedicularis groenlandica",
            "rank": "species",
            "lineage": [
                {
                    "ott_id": 11,
                    "name": "Pedicularis",
                    "rank": "genus",
                    "tax_sources": [],
                },
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        otol.induced_tree,
        "build_cophenetic_distance_matrix_from_taxonomy",
        _mock_taxonomy_distance_matrix,
    )
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("(ott11,(ott1,ott2)X)Root;"),
    )  # noqa: ARG005,E501

    resolved = _resolved_df_from_records(
        [
            {"query": "ped_a", "matched_name": "Pedicularis", "ott_id": 11},
            {"query": "ped_b", "matched_name": "Pedicularis", "ott_id": 11},
            {"query": "anas", "matched_name": "Pedicularis anas", "ott_id": 1},
            {
                "query": "groenlandica",
                "matched_name": "Pedicularis groenlandica",
                "ott_id": 2,
            },
        ]
    )
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{query}",
    )
    captured = capsys.readouterr()

    assert set(tree.get_tip_labels()) == {"anas", "groenlandica"}
    assert not any(
        node.is_leaf()
        and pd.notna(getattr(node, "ott_id", pd.NA))
        and int(node.ott_id) == 11
        for node in tree
    )
    assert (
        sum(
            pd.notna(getattr(node, "ott_id", pd.NA)) and int(node.ott_id) == 11
            for node in tree
        )
        == 1
    )
    assert all(not str(node.name).endswith("_group") for node in tree)
    assert "assigned to internal node" in captured.err
    assert "returning 2 tips for 4 matched taxa" in captured.err


def test_fetch_newick_subtree_from_taxonomy_warns_on_duplicate_group_tip_labels(
    monkeypatch,
    capsys,
):
    """Warn, but still return a tree, on duplicate terminal group-tip labels."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 11,
            "name": "Pedicularis",
            "rank": "genus",
            "lineage": [
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                }
            ],
        },
        {
            "ott_id": 2,
            "name": "Castilleja campestris",
            "rank": "species",
            "lineage": [
                {
                    "ott_id": 12,
                    "name": "Castilleja",
                    "rank": "genus",
                    "tax_sources": [],
                },
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        otol.induced_tree,
        "build_cophenetic_distance_matrix_from_taxonomy",
        _mock_taxonomy_distance_matrix,
    )
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("(ott11,ott2)Root;"),
    )  # noqa: ARG005,E501

    resolved = _resolved_df_from_records(
        [
            {"query": "ped_a", "matched_name": "Pedicularis", "ott_id": 11},
            {"query": "ped_b", "matched_name": "Pedicularis", "ott_id": 11},
            {
                "query": "castilleja",
                "matched_name": "Castilleja campestris",
                "ott_id": 2,
            },
        ]
    )
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{matched_name}",
    )
    captured = capsys.readouterr()

    assert tree.get_tip_labels().count("Pedicularis") == 2
    assert "duplicate tip labels" in captured.err
    assert "'Pedicularis' (2)" in captured.err
    assert "Choose a more specific label_template" in captured.err


def test_fetch_newick_subtree_from_taxonomy_warns_on_duplicate_labels_across_ott_ids(
    monkeypatch,
    capsys,
):
    """Warn, but still return a tree, when different OTT tips share one label."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 1,
            "name": "SpeciesA",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "GenusA", "rank": "genus", "tax_sources": []},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family", "tax_sources": []},
            ],
        },
        {
            "ott_id": 2,
            "name": "SpeciesB",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "GenusB", "rank": "genus", "tax_sources": []},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family", "tax_sources": []},
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        otol.induced_tree,
        "build_cophenetic_distance_matrix_from_taxonomy",
        _mock_taxonomy_distance_matrix,
    )
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("(ott1,ott2)Root;"),
    )  # noqa: ARG005,E501

    resolved = _resolved_df_from_records(
        [
            {"query": "q0", "matched_name": "Pedicularis", "ott_id": 1},
            {"query": "q1", "matched_name": "Pedicularis", "ott_id": 2},
        ]
    )
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{matched_name}",
    )
    captured = capsys.readouterr()

    assert tree.get_tip_labels() == ["Pedicularis", "Pedicularis"]
    assert "duplicate tip labels" in captured.err
    assert "'Pedicularis' (2)" in captured.err
    assert "Choose a more specific label_template" in captured.err


def test_fetch_newick_subtree_from_taxonomy_skips_warning_without_internal_match(
    monkeypatch,
    capsys,
):
    """Do not warn or drop tips when no matched input maps to an internal OTT."""
    client = otol._OTOLClient(cache=False)
    data = [
        {
            "ott_id": 1,
            "name": "SpeciesA",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "GenusA", "rank": "genus", "tax_sources": []},
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
        {
            "ott_id": 2,
            "name": "SpeciesB",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "GenusB", "rank": "genus", "tax_sources": []},
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
        {
            "ott_id": 3,
            "name": "SpeciesC",
            "rank": "species",
            "lineage": [
                {"ott_id": 13, "name": "GenusC", "rank": "genus", "tax_sources": []},
                {
                    "ott_id": 41,
                    "name": "FamilyZ",
                    "rank": "family",
                    "tax_sources": [],
                },
            ],
        },
    ]
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: data,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        otol.induced_tree,
        "build_cophenetic_distance_matrix_from_taxonomy",
        _mock_taxonomy_distance_matrix,
    )
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("((ott1,ott2)X,ott3)Root;"),
    )  # noqa: ARG005,E501

    resolved = _resolved_df_from_lineages(data)
    tree = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template="{matched_name}_ott{ott_id}",
    )
    captured = capsys.readouterr()

    assert set(tree.get_tip_labels()) == {
        "SpeciesA_ott1",
        "SpeciesB_ott2",
        "SpeciesC_ott3",
    }
    assert captured.err == ""


def _lineages_for_taxonomy_rooting_fixture():
    """Return lineages that define two family-level clades."""
    return [
        {
            "ott_id": 1,
            "name": "SpeciesA",
            "rank": "species",
            "lineage": [{"ott_id": 41, "name": "FamilyOne", "rank": "family"}],
        },
        {
            "ott_id": 2,
            "name": "SpeciesB",
            "rank": "species",
            "lineage": [{"ott_id": 41, "name": "FamilyOne", "rank": "family"}],
        },
        {
            "ott_id": 3,
            "name": "SpeciesC",
            "rank": "species",
            "lineage": [{"ott_id": 42, "name": "FamilyTwo", "rank": "family"}],
        },
        {
            "ott_id": 4,
            "name": "SpeciesD",
            "rank": "species",
            "lineage": [{"ott_id": 42, "name": "FamilyTwo", "rank": "family"}],
        },
    ]


def test_fetch_newick_subtree_from_taxonomy_roots_on_taxonomy_clade(monkeypatch):
    """Root inferred topology on a compatible taxonomy-defined outgroup clade."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineages_for_taxonomy_rooting_fixture()
    resolved = _resolved_df_from_lineages(lineages)
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("((ott1,ott2)AB,ott3,ott4)R;"),
    )  # noqa: ARG005,E501

    tree = toytree.tree(client.fetch_newick_subtree_from_taxonomy(resolved))
    assert tree.is_rooted()
    root_child_sets = [
        {str(i.name) for i in child.iter_leaves()} for child in tree.treenode.children
    ]
    assert {"SpeciesA_ott1", "SpeciesB_ott2"} in root_child_sets


def test_fetch_newick_subtree_from_taxonomy_falls_back_to_midpoint_root(monkeypatch):
    """Use midpoint fallback if no taxonomy-defined clade is monophyletic."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineages_for_taxonomy_rooting_fixture()
    resolved = _resolved_df_from_lineages(lineages)
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        toytree.infer,
        "upgma_tree",
        lambda dist: toytree.tree("((ott1,ott3)AC,ott2,ott4)R;"),
    )  # noqa: ARG005,E501

    tree = toytree.tree(client.fetch_newick_subtree_from_taxonomy(resolved))
    assert tree.is_rooted()


def test_fetch_newick_methods_raise_on_unresolved_rows(monkeypatch):
    """Reject resolved tables that still include unresolved rows."""
    client = otol._OTOLClient(cache=False)
    lineages = _lineage_records_fixture()
    unresolved = _resolved_df_from_lineages(lineages)
    unresolved.loc[0, "status"] = "unmatched"
    unresolved.loc[0, "ott_id"] = pd.NA
    unresolved["ott_id"] = pd.array(unresolved["ott_id"], dtype="Int64")

    with pytest.raises(ToytreeError, match="contains unresolved rows"):
        client.fetch_newick_subtree_from_taxonomy(unresolved)

    with pytest.raises(ToytreeError, match="contains unresolved rows"):
        client.fetch_newick_induced_tree_otol(unresolved)


def _induced_payload_fixture():
    """Return induced payload with one broken taxon constrained to AnchorAB."""
    return {
        "newick": "((SpeciesA_ott1,SpeciesB_ott2)AnchorAB,SpeciesC_ott3)Root;",
        "broken": {"ott4": "AnchorAB"},
    }


def _induced_lineages_fixture():
    """Return lineage records for induced-tree insertion tests."""
    return [
        {
            "ott_id": 1,
            "name": "SpeciesA",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "GenusA", "rank": "genus"},
                {"ott_id": 21, "name": "TribeX", "rank": "tribe"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 2,
            "name": "SpeciesB",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "GenusB", "rank": "genus"},
                {"ott_id": 21, "name": "TribeX", "rank": "tribe"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 3,
            "name": "SpeciesC",
            "rank": "species",
            "lineage": [
                {"ott_id": 13, "name": "GenusC", "rank": "genus"},
                {"ott_id": 22, "name": "TribeQ", "rank": "tribe"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 4,
            "name": "SpeciesD",
            "rank": "species",
            "lineage": [
                {"ott_id": 14, "name": "GenusD", "rank": "genus"},
                {"ott_id": 21, "name": "TribeX", "rank": "tribe"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
    ]


def test_fetch_newick_induced_tree_otol_unconstrained_inserts_broken_by_anchor(
    monkeypatch,
):
    """Insert broken taxon inside anchor clade using constrained overlap ties."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": _induced_payload_fixture(),
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: _induced_lineages_fixture(),
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(_induced_lineages_fixture())
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        constrain_by_taxonomy=False,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == {
        "SpeciesA_ott1",
        "SpeciesB_ott2",
        "SpeciesC_ott3",
        "SpeciesD_ott4",
    }
    anchor = tree.get_nodes("AnchorAB")[0]
    leaves = {i.name for i in anchor.iter_leaves()}
    assert "SpeciesD_ott4" in leaves
    assert "SpeciesC_ott3" not in leaves


@pytest.mark.parametrize(
    "template, expected",
    [
        (
            "{matched_name}_ott{ott_id}",
            {"SpeciesA_ott1", "SpeciesB_ott2", "SpeciesC_ott3", "SpeciesD_ott4"},
        ),
        ("{matched_name}", {"SpeciesA", "SpeciesB", "SpeciesC", "SpeciesD"}),
        ("ott{ott_id}", {"ott1", "ott2", "ott3", "ott4"}),
        ("{query_id}_{ott_id}", {"q0_1", "q1_2", "q2_3", "q3_4"}),
    ],
)
def test_fetch_newick_induced_tree_otol_unconstrained_label_templates(
    monkeypatch,
    template,
    expected,
):
    """Apply label templates after broken-node insertion."""
    client = otol._OTOLClient(cache=False)
    lineages = _induced_lineages_fixture()
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": _induced_payload_fixture(),
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(lineages, use_query=True)
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        label_template=template,
        constrain_by_taxonomy=False,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == expected


def test_newick_induced_tree_otol_unconstrained_normalizes_whitespace_in_names(
    monkeypatch,
):
    """Normalize whitespace in names before relabeling induced-tree tips."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": {
            "newick": "(Pedicularisanas_ott1,Castillejacampestris_ott2)Root;",
            "broken": {},
        },
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: [
            {
                "ott_id": 1,
                "name": "Pedicularis anas",
                "rank": "species",
                "lineage": [],
            },
            {
                "ott_id": 2,
                "name": "Castilleja campestris",
                "rank": "species",
                "lineage": [],
            },
        ],
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(
        [
            {"ott_id": 1, "name": "Pedicularis anas"},
            {"ott_id": 2, "name": "Castilleja campestris"},
        ]
    )
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        constrain_by_taxonomy=False,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == {
        "Pedicularis_anas_ott1",
        "Castilleja_campestris_ott2",
    }


def _induced_payload_alt_refine_fixture():
    """Return induced payload used to refine a taxonomy polytomy."""
    return {
        "newick": "((SpeciesA_ott1,SpeciesB_ott2)AnchorAB,SpeciesC_ott3)Root;",
        "broken": {"ott4": "AnchorAB"},
    }


def _induced_lineages_alt_refine_fixture():
    """Return lineages yielding a family-level polytomy in taxonomy scaffold."""
    return [
        {
            "ott_id": 1,
            "name": "SpeciesA",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "GenusA", "rank": "genus"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 2,
            "name": "SpeciesB",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "GenusB", "rank": "genus"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 3,
            "name": "SpeciesC",
            "rank": "species",
            "lineage": [
                {"ott_id": 13, "name": "GenusC", "rank": "genus"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
        {
            "ott_id": 4,
            "name": "SpeciesD",
            "rank": "species",
            "lineage": [
                {"ott_id": 14, "name": "GenusD", "rank": "genus"},
                {"ott_id": 41, "name": "FamilyZ", "rank": "family"},
            ],
        },
    ]


def test_fetch_newick_induced_tree_otol_constrained_refines_and_inserts(monkeypatch):
    """Refine taxonomy scaffold by induced clade and then insert broken taxa."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": _induced_payload_alt_refine_fixture(),
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: _induced_lineages_alt_refine_fixture(),
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(_induced_lineages_alt_refine_fixture())
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == {
        "SpeciesA_ott1",
        "SpeciesB_ott2",
        "SpeciesC_ott3",
        "SpeciesD_ott4",
    }
    # induced refinement should resolve A/B as a clade separate from C.
    ab = tree.get_mrca_node("SpeciesA_ott1", "SpeciesB_ott2")
    leaves = {i.name for i in ab.iter_leaves()}
    assert "SpeciesA_ott1" in leaves
    assert "SpeciesB_ott2" in leaves
    assert "SpeciesC_ott3" not in leaves


def test_fetch_newick_induced_tree_otol_constrained_fallback_for_extra_ott(
    monkeypatch,
    capsys,
):
    """Fallback-label tips added in constrained mode when resolved table lacks OTT."""
    client = otol._OTOLClient(cache=False)
    lineages = _induced_lineages_alt_refine_fixture()
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": _induced_payload_alt_refine_fixture(),
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(lineages[:3])
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        constrain_by_taxonomy=True,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == {
        "SpeciesA_ott1",
        "SpeciesB_ott2",
        "SpeciesC_ott3",
        "SpeciesD_ott4",
    }
    captured = capsys.readouterr()
    assert "fallback" in captured.err
    assert "4" in captured.err


def test_augment_missing_tip_labels_recovers_name_from_node_info(monkeypatch):
    """Recover missing OTT label by mapping node_info query token to tip ott_id."""
    client = otol._OTOLClient(cache=False)
    tree = toytree.tree("(ott1,ott1058517)Root;")
    label_by_ott = {1: "SpeciesA_ott1"}
    rec_by_ott = {1: {"ott_id": 1, "name": "SpeciesA"}}

    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=False: [],
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_node_info",
        lambda query, include_lineage=False: [
            {
                "query": "ott1058517",
                "taxon": {"name": "Mesangiospermae", "ott_id": 5298374},
            }
        ],
    )  # noqa: ARG005,E501
    out = client._augment_missing_tip_labels(
        tree=tree,
        label_by_ott=label_by_ott,
        rec_by_ott=rec_by_ott,
    )
    assert out[1] == "SpeciesA_ott1"
    assert out[1058517] == "Mesangiospermae_ott1058517"


def test_augment_missing_tip_labels_falls_back_to_ott_id(monkeypatch):
    """Use ott{id} fallback when no taxonomy or node-info name can be resolved."""
    client = otol._OTOLClient(cache=False)
    tree = toytree.tree("(ott1058517,ott1)Root;")
    label_by_ott = {1: "SpeciesA_ott1"}
    rec_by_ott = {1: {"ott_id": 1, "name": "SpeciesA"}}

    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=False: [],
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_node_info",
        lambda query, include_lineage=False: [],
    )  # noqa: ARG005,E501
    out = client._augment_missing_tip_labels(
        tree=tree,
        label_by_ott=label_by_ott,
        rec_by_ott=rec_by_ott,
    )
    assert out[1058517] == "ott1058517"


@pytest.mark.parametrize(
    "template, expected",
    [
        (
            "{matched_name}_ott{ott_id}",
            {"SpeciesA_ott1", "SpeciesB_ott2", "SpeciesC_ott3", "SpeciesD_ott4"},
        ),
        ("{matched_name}", {"SpeciesA", "SpeciesB", "SpeciesC", "SpeciesD"}),
        ("ott{ott_id}", {"ott1", "ott2", "ott3", "ott4"}),
    ],
)
def test_fetch_newick_induced_tree_otol_constrained_label_templates(
    monkeypatch,
    template,
    expected,
):
    """Apply label templates in constrained induced OTOL strategy."""
    client = otol._OTOLClient(cache=False)
    lineages = _induced_lineages_alt_refine_fixture()
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": _induced_payload_alt_refine_fixture(),
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: lineages,
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(lineages)
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        label_template=template,
        constrain_by_taxonomy=True,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == expected


def test_newick_induced_tree_otol_constrained_normalizes_whitespace_in_names(
    monkeypatch,
):
    """Normalize whitespace in names for alternative induced OTOL strategy."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query, label_format="name_and_id": {
            "newick": "(Pedicularisanas_ott1,Castillejacampestris_ott2)Root;",
            "broken": {},
        },
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: [
            {
                "ott_id": 1,
                "name": "Pedicularis anas",
                "rank": "species",
                "lineage": [{"ott_id": 11, "name": "Pedicularis", "rank": "genus"}],
            },
            {
                "ott_id": 2,
                "name": "Castilleja campestris",
                "rank": "species",
                "lineage": [{"ott_id": 12, "name": "Castilleja", "rank": "genus"}],
            },
        ],
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(
        [
            {"ott_id": 1, "name": "Pedicularis anas"},
            {"ott_id": 2, "name": "Castilleja campestris"},
        ]
    )
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        constrain_by_taxonomy=True,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == {
        "Pedicularis_anas_ott1",
        "Castilleja_campestris_ott2",
    }


def _induced_payload_genus_conflict_fixture():
    """Return induced payload that conflicts with taxonomy genus groupings."""
    return {
        "newick": (
            "((Pedicularisalpha_ott1,Castillejaalpha_ott3)X,"
            "(Pedicularisbeta_ott2,Castillejabeta_ott4)Y)Root;"
        ),
        "broken": {},
    }


def _lineages_genus_conflict_fixture():
    """Return lineages where taxonomy enforces Pedicularis and Castilleja clades."""
    return [
        {
            "ott_id": 1,
            "name": "Pedicularisalpha",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "Pedicularis", "rank": "genus"},
                {"ott_id": 51, "name": "Orobanchaceae", "rank": "family"},
            ],
        },
        {
            "ott_id": 2,
            "name": "Pedicularisbeta",
            "rank": "species",
            "lineage": [
                {"ott_id": 11, "name": "Pedicularis", "rank": "genus"},
                {"ott_id": 51, "name": "Orobanchaceae", "rank": "family"},
            ],
        },
        {
            "ott_id": 3,
            "name": "Castillejaalpha",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "Castilleja", "rank": "genus"},
                {"ott_id": 51, "name": "Orobanchaceae", "rank": "family"},
            ],
        },
        {
            "ott_id": 4,
            "name": "Castillejabeta",
            "rank": "species",
            "lineage": [
                {"ott_id": 12, "name": "Castilleja", "rank": "genus"},
                {"ott_id": 51, "name": "Orobanchaceae", "rank": "family"},
            ],
        },
    ]


def test_fetch_newick_induced_tree_otol_preserves_taxonomy_genus_constraints(
    monkeypatch,
):
    """Do not allow induced refinement to split locked taxonomy genus clades."""
    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(
        client,
        "fetch_json_induced_subtree",
        lambda query,
        label_format="name_and_id": _induced_payload_genus_conflict_fixture(),
    )  # noqa: ARG005,E501
    monkeypatch.setattr(
        client,
        "fetch_json_taxon_info",
        lambda query, include_lineage=True: _lineages_genus_conflict_fixture(),
    )  # noqa: ARG005,E501
    resolved = _resolved_df_from_lineages(_lineages_genus_conflict_fixture())
    nwk = client.fetch_newick_induced_tree_otol(
        resolved,
        constrain_by_taxonomy=True,
    )
    tree = toytree.tree(nwk)
    pmrca = tree.get_mrca_node("Pedicularisalpha_ott1", "Pedicularisbeta_ott2")
    cmrca = tree.get_mrca_node("Castillejaalpha_ott3", "Castillejabeta_ott4")
    assert {i.name for i in pmrca.iter_leaves()} == {
        "Pedicularisalpha_ott1",
        "Pedicularisbeta_ott2",
    }
    assert {i.name for i in cmrca.iter_leaves()} == {
        "Castillejaalpha_ott3",
        "Castillejabeta_ott4",
    }
