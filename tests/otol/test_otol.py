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
        "query",
        "status",
        "matched_name",
        "ott_id",
        "ncbi_id",
        "is_synonym",
        "reason",
    ]
    assert str(out["ott_id"].dtype) == "Int64"
    assert str(out["ncbi_id"].dtype) == "Int64"
    assert int(out.loc[0, "ncbi_id"]) == 9612
    assert pd.isna(out.loc[1, "ott_id"])
    assert pd.isna(out.loc[1, "ncbi_id"])


def test_resolve_taxonomic_names_raises_on_unresolved(monkeypatch):
    """Raise when unresolved policy is set to 'raise'."""

    def _mock_fetch_json_match_names(query, approximate=False, context=None):  # noqa: ARG001
        return [{"name": "Unknown taxon", "matches": []}]

    client = otol._OTOLClient(cache=False)
    monkeypatch.setattr(client, "fetch_json_match_names", _mock_fetch_json_match_names)
    with pytest.raises(ToytreeError, match="unresolved rows"):
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
) -> pd.DataFrame:
    """Return a resolved-name table compatible with fetch_newick_* methods."""
    rows = []
    for idx, rec in enumerate(lineages):
        ott = int(rec["ott_id"])
        name = str(rec.get("name", f"ott{ott}"))
        row = {
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
    resolved = _resolved_df_from_lineages(lineages, use_query=True)
    nwk = client.fetch_newick_subtree_from_taxonomy(
        resolved,
        label_template=template,
    )
    tree = toytree.tree(nwk)
    assert set(tree.get_tip_labels()) == expected


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
        lambda dist: toytree.tree(
            "((SpeciesA_ott1,SpeciesB_ott2)AB,SpeciesC_ott3,SpeciesD_ott4)R;"
        ),
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
        lambda dist: toytree.tree(
            "((SpeciesA_ott1,SpeciesC_ott3)AC,SpeciesB_ott2,SpeciesD_ott4)R;"
        ),
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
