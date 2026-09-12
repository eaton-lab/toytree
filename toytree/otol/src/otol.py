#!/usr/bin/env python
# ruff: noqa: E501,D401

"""Open Tree of Life (OTOL) raw JSON API utilities.

This module is a thin interface to OTOL REST endpoints and returns endpoint
payloads as JSON-like Python objects. Public methods are prefixed with
``fetch_json_`` to signal they return raw API response content.

Tree data concepts
------------------
- A synthetic subtree comes from ``tree_of_life/subtree`` under one queried
  root node on the synthetic tree.
- An induced subtree comes from ``tree_of_life/induced_subtree`` and connects
  a set of queried tips / nodes in the synthetic tree.
- A taxonomy subtree is built from parent-child taxonomy relationships and is
  conceptually separate from synthetic-tree topology.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, Sequence

import pandas as pd
from requests import Session

from toytree.core import ToyTree
from toytree.utils import ToytreeError

from . import induced_tree
from ._transport import JSONServiceClient

URI = "https://api.opentreeoflife.org/v3/"
HEADERS_JSON = {"content-type": "application/json", "User-Agent": "toytree"}
NODE_ID_PATTERN = re.compile(r"^(ott\d+|mrcaott\d+(?:ott\d+)*)$")
DOI_PREFIX_PATTERN = re.compile(r"^(?:doi:|https?://(?:dx\.)?doi\.org/)", re.I)

FLEX_QUERY = str | int | Sequence[str] | Sequence[int]
TAXON_QUERY = str | int | dict[str, int] | Sequence[str | int | dict[str, int]]

__all__ = [
    "FLEX_QUERY",
    "TAXON_QUERY",
    "configure_client",
    "reset_client",
    "fetch_json_match_names",
    "fetch_json_node_info",
    "fetch_json_mrca",
    "fetch_json_taxon_info",
    "fetch_json_taxonomy_about",
    "fetch_json_subtree",
    "fetch_json_induced_subtree",
    "fetch_json_studies_by_author",
    "fetch_json_studies_by_taxa",
    "fetch_json_studies_by_doi",
    "resolve_taxonomic_names",
    "fetch_tree_from_taxonomy",
    "fetch_tree_from_synthesis",
    "fetch_newick_subtree_from_taxonomy",
    "fetch_newick_induced_tree_otol",
]


class _OTOLClient(JSONServiceClient):
    """Private OTOL client for transport, retries, and cache."""

    def __init__(
        self,
        base_url: str = URI,
        timeout: float = 20.0,
        max_retries: int = 4,
        backoff_factor: float = 0.5,
        cache: bool = True,
        cache_dir: str | Path | None = None,
        cache_ttl: float | None = 7 * 24 * 60 * 60,
        session: Session | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            cache=cache,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            session=session,
        )

    service_name = "opentree"
    default_headers = HEADERS_JSON

    @staticmethod
    def _to_list(query: str | int | Sequence[str] | Sequence[int]) -> list[str | int]:
        """Normalize scalar or sequence query into list preserving order."""
        if isinstance(query, (str, int)):
            return [query]
        return list(query)

    def _query_to_node_ids(self, query: FLEX_QUERY) -> list[str]:
        """Convert mixed user query values to OTOL node-id strings."""
        items = self._to_list(query)
        out: list[str] = [""] * len(items)
        name_positions: list[int] = []
        names: list[str] = []

        for idx, item in enumerate(items):
            if isinstance(item, int):
                out[idx] = f"ott{item}"
                continue
            text = str(item).strip()
            if not text:
                raise ToytreeError("empty query entry is not allowed.")
            if NODE_ID_PATTERN.match(text):
                out[idx] = text
                continue
            name_positions.append(idx)
            names.append(text)

        if names:
            results = self.fetch_json_match_names(names)
            for idx, rec in zip(name_positions, results):
                matches = list(rec.get("matches", []))
                if not matches:
                    raise ToytreeError(f"unmatched name query: {rec.get('name')!r}")
                if len(matches) > 1:
                    raise ToytreeError(
                        f"ambiguous name query: {rec.get('name')!r} ({len(matches)} matches)"
                    )
                taxon = matches[0].get("taxon", {})
                if "ott_id" not in taxon:
                    raise ToytreeError(
                        f"matched name has no ott_id: {rec.get('name')!r}"
                    )
                out[idx] = f"ott{int(taxon['ott_id'])}"
        return out

    def _taxon_payload_from_query(
        self, query: str | int | dict[str, int]
    ) -> dict[str, Any]:
        """Convert one taxon-query token to taxonomy/taxon_info payload."""
        if isinstance(query, dict):
            key = next(iter(query))
            return {"source_id": f"{key}:{query[key]}"}
        if isinstance(query, int):
            return {"ott_id": query}

        node_id = self._query_to_node_ids(query)[0]
        if node_id.startswith("ott"):
            return {"ott_id": int(node_id[3:])}

        records = self.fetch_json_node_info(node_id, include_lineage=False)
        taxon = records[0].get("taxon", {}) if records else {}
        if "ott_id" not in taxon:
            raise ToytreeError(f"could not resolve taxon query: {query!r}")
        return {"ott_id": int(taxon["ott_id"])}

    def _fetch_json_studies(
        self,
        property_name: str,
        value: str,
        verbose: bool,
    ) -> list[dict[str, Any]]:
        """Fetch one studies/find_studies request and return matched_studies."""
        payload = {"property": property_name, "value": value, "verbose": bool(verbose)}
        data = self._request_json(
            "studies/find_studies",
            payload,
            use_cache=True,
            cache_namespace="studies",
        )
        matched = data.get("matched_studies", [])
        return matched if isinstance(matched, list) else []

    def fetch_json_match_names(
        self,
        query: str | Sequence[str],
        approximate: bool = False,
        context: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch raw results from tnrs/match_names."""
        names = [query] if isinstance(query, str) else list(query)
        payload: dict[str, Any] = {"names": names}
        if approximate:
            payload["do_approximate_matching"] = True
        if context is not None:
            payload["context"] = context
        data = self._request_json(
            "tnrs/match_names",
            payload,
            use_cache=True,
            cache_namespace="matches",
        )
        results = data.get("results", [])
        if not isinstance(results, list):
            raise ToytreeError("unexpected response shape from tnrs/match_names")
        return results

    @staticmethod
    def _extract_ncbi_id_from_taxon(taxon: dict[str, Any]) -> int | None:
        """Return NCBI identifier parsed from TNRS taxon metadata."""
        for source in taxon.get("tax_sources", []) or []:
            text = str(source)
            match = re.search(r"\bncbi:(\d+)\b", text, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))
        source_id = taxon.get("source_id")
        if source_id is not None:
            match = re.search(r"\bncbi:(\d+)\b", str(source_id), flags=re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def resolve_taxonomic_names(
        self,
        query: Sequence[str] | Mapping[str, str],
        approximate: bool = False,
        context: str | None = None,
        include_synonyms: bool = True,
        on_unresolved: Literal["raise", "warn", "ignore"] = "ignore",
        on_ambiguous: Literal["ignore", "first", "raise"] = "first",
        on_duplicate: Literal["ignore", "warn", "raise"] = "warn",
        return_unresolved: bool = False,
    ) -> pd.DataFrame:
        """Resolve taxon names through OTOL TNRS and return a standardized table.

        Parameters
        ----------
        query : Sequence[str] or Mapping[str, str]
            Taxon-name strings to resolve. If a mapping is provided then its
            values are used as TNRS queries and its keys are stored in the
            returned ``key`` column.
        approximate : bool, default=False
            If True, enable approximate matching in TNRS.
        context : str or None, default=None
            Optional TNRS context.
        include_synonyms : bool, default=True
            If False, synonym matches are filtered before status assignment.
        on_unresolved : {"raise", "warn", "ignore"}, default="ignore"
            Behavior when unmatched or ambiguous rows remain. The "warn"
            mode prints a message to stderr.
        on_ambiguous : {"ignore", "first", "raise"}, default="first"
            Behavior when a query has multiple TNRS matches.
        on_duplicate : {"ignore", "warn", "raise"}, default="warn"
            Behavior when multiple matched queries resolve to the same OTT id.
        return_unresolved : bool, default=False
            If True, return only rows whose status is not ``"matched"``.

        Returns
        -------
        pandas.DataFrame
            Columns are ``key``, ``query``, ``status``, ``matched_name``,
            ``rank``, ``taxon_name``, ``ott_id``, ``ncbi_id``,
            ``is_synonym``, and ``reason``. Rows kept as ambiguous leave
            taxon-specific fields missing because no single TNRS match was
            selected. Duplicate matched OTT ids are handled according to
            ``on_duplicate``. For sequence input, ``key`` values are missing.
            If ``return_unresolved=True``, only unresolved rows are returned.
        """
        if on_unresolved not in ("raise", "warn", "ignore"):
            raise ToytreeError(f"invalid on_unresolved option: {on_unresolved!r}")
        if on_ambiguous == "keep":
            print(
                "WARNING: on_ambiguous='keep' is deprecated; use 'ignore' instead.",
                file=sys.stderr,
            )
            on_ambiguous = "ignore"
        if on_ambiguous not in ("ignore", "first", "raise"):
            raise ToytreeError(f"invalid on_ambiguous option: {on_ambiguous!r}")
        if on_duplicate not in ("ignore", "warn", "raise"):
            raise ToytreeError(f"invalid on_duplicate option: {on_duplicate!r}")

        # normalize ordered query rows before calling TNRS so mapping keys
        # can be reattached even when query values are duplicated.
        if isinstance(query, Mapping):
            query_pairs = [(str(key), str(val)) for key, val in query.items()]
        else:
            query_pairs = [(pd.NA, str(val)) for val in query]
        query_values = [pair[1] for pair in query_pairs]

        # get JSON API result
        results = self.fetch_json_match_names(
            query=query_values,
            approximate=approximate,
            context=context,
        )
        if len(results) != len(query_pairs):
            raise ToytreeError(
                "unexpected response shape from tnrs/match_names: "
                "could not align returned rows to input queries."
            )

        # iterate over results filling a list of dicts
        rows: list[dict[str, Any]] = []
        for (qkey, qname), item in zip(query_pairs, results):
            # top level has 'name' str and 'matches' dict.
            matches = list(item.get("matches", []))

            # Optionally only examine matches where query is not a synonym.
            if not include_synonyms:
                matches = [m for m in matches if not bool(m.get("is_synonym", False))]

            # append an empty record for queries with no hits
            if not matches:
                rows.append(
                    {
                        "key": qkey,
                        "query": qname,
                        "status": "unmatched",
                        "matched_name": None,
                        "rank": pd.NA,
                        "taxon_name": pd.NA,
                        "ott_id": pd.NA,
                        "ncbi_id": pd.NA,
                        "is_synonym": None,
                        "reason": "no_match",
                    }
                )
                continue

            # parse the matched hits to query
            if len(matches) > 1:
                if on_ambiguous == "raise":
                    raise ToytreeError(
                        f"TNRS ambiguous resolution failed for {qname!r}."
                    )
                if on_ambiguous == "first":
                    match = matches[0]
                    taxon = match.get("taxon", {})
                    rows.append(
                        {
                            "key": qkey,
                            "query": qname,
                            "status": "matched",
                            "matched_name": match.get(
                                "matched_name", taxon.get("name")
                            ),  # noqa
                            "rank": taxon.get("rank"),
                            "taxon_name": taxon.get("name"),
                            "ott_id": int(taxon["ott_id"])
                            if "ott_id" in taxon
                            else pd.NA,  # noqa
                            "ncbi_id": self._extract_ncbi_id_from_taxon(taxon) or pd.NA,
                            "is_synonym": bool(match.get("is_synonym", False)),
                            "reason": f"resolved_first_of_{len(matches)}",
                        }
                    )
                    continue
                rows.append(
                    {
                        "key": qkey,
                        "query": qname,
                        "status": "ambiguous",
                        "matched_name": None,
                        "rank": pd.NA,
                        "taxon_name": pd.NA,
                        "ott_id": pd.NA,
                        "ncbi_id": pd.NA,
                        "is_synonym": None,
                        "reason": f"{len(matches)}_matches",
                    }
                )
                continue

            match = matches[0]
            taxon = match.get("taxon", {})
            rows.append(
                {
                    "key": qkey,
                    "query": qname,
                    "status": "matched",
                    "matched_name": match.get("matched_name", taxon.get("name")),
                    "rank": taxon.get("rank"),
                    "taxon_name": taxon.get("name"),
                    "ott_id": int(taxon["ott_id"]) if "ott_id" in taxon else pd.NA,
                    "ncbi_id": self._extract_ncbi_id_from_taxon(taxon) or pd.NA,
                    "is_synonym": bool(match.get("is_synonym", False)),
                    "reason": "ok",
                }
            )

        # store as a dataframe and add ID columns
        columns = [
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
        table = pd.DataFrame(rows, columns=columns)
        table["ott_id"] = pd.array(table["ott_id"], dtype="Int64")
        table["ncbi_id"] = pd.array(table["ncbi_id"], dtype="Int64")

        # detect duplicate matched OTT ids for downstream warning or error handling
        matched = table[(table["status"] == "matched") & table["ott_id"].notna()]
        duplicate_queries_by_ott: dict[int, list[str]] = {}
        for row in matched[["query", "ott_id"]].itertuples(index=False):
            ott = int(row.ott_id)
            duplicate_queries_by_ott.setdefault(ott, []).append(str(row.query))
        duplicate_messages = []
        for ott, queries in duplicate_queries_by_ott.items():
            if len(queries) > 1:
                qtext = ", ".join(repr(query) for query in queries)
                duplicate_messages.append(
                    f"multiple matched queries resolve to ott{ott}: {qtext}"
                )

        if duplicate_messages:
            if on_duplicate == "raise":
                raise ToytreeError("; ".join(duplicate_messages))
            if on_duplicate == "warn":
                for message in duplicate_messages:
                    print(f"WARNING: {message}", file=sys.stderr)

        unresolved = table[table["status"] != "matched"].reset_index(drop=True)
        if not unresolved.empty and on_unresolved in ("raise", "warn"):
            amb = int((unresolved["status"] == "ambiguous").sum())
            unm = int((unresolved["status"] == "unmatched").sum())
            message = (
                "TNRS resolution has unresolved rows: "
                f"{amb} ambiguous, {unm} unmatched. "
                "Use return_unresolved=True to see which names remain unresolved."
            )

            if on_unresolved == "raise" and not return_unresolved:
                raise ToytreeError(message)
            if on_unresolved == "warn":
                print(message, file=sys.stderr)

        if return_unresolved:
            return unresolved
        return table

    def fetch_json_node_info(
        self,
        query: FLEX_QUERY,
        include_lineage: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch raw records from tree_of_life/node_info."""
        node_ids = self._query_to_node_ids(query)
        data = self._request_json(
            "tree_of_life/node_info",
            {"node_ids": node_ids, "include_lineage": include_lineage},
        )
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "node_id" in data:
            return [data]
        if isinstance(data, dict) and isinstance(data.get("results"), list):
            return data["results"]
        raise ToytreeError("unexpected response shape from tree_of_life/node_info")

    def fetch_json_mrca(self, query: FLEX_QUERY) -> dict[str, Any]:
        """Fetch raw payload from tree_of_life/mrca."""
        node_ids = self._query_to_node_ids(query)
        return self._request_json("tree_of_life/mrca", {"node_ids": node_ids})

    def fetch_json_taxon_info(
        self,
        query: TAXON_QUERY,
        include_lineage: bool = False,
        include_children: bool = False,
        include_terminal_descendants: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch raw payload(s) from taxonomy/taxon_info."""
        items = [query] if isinstance(query, (str, int, dict)) else list(query)
        out: list[dict[str, Any]] = []
        for item in items:
            payload = self._taxon_payload_from_query(item)
            payload.update(
                {
                    "include_lineage": include_lineage,
                    "include_children": include_children,
                    "include_terminal_descendants": include_terminal_descendants,
                }
            )
            out.append(self._request_json("taxonomy/taxon_info", payload))
        return out

    def fetch_json_taxonomy_about(self) -> dict[str, Any]:
        """Fetch raw payload from taxonomy/about."""
        return self._request_json(
            "taxonomy/about",
            {},
            use_cache=True,
            cache_namespace="taxonomy",
        )

    def fetch_json_subtree(
        self,
        query: int | str,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Fetch raw payload from tree_of_life/subtree."""
        node_id = self._query_to_node_ids(query)[0]
        payload = {"node_id": node_id} | ({} if extra_params is None else extra_params)
        data = self._request_json("tree_of_life/subtree", payload)
        if "newick" not in data:
            raise ToytreeError("unexpected response shape from tree_of_life/subtree")
        return data

    def fetch_json_induced_subtree(
        self,
        query: Sequence[int | str],
        label_format: str = "name_and_id",
    ) -> dict[str, Any]:
        """Fetch raw payload from tree_of_life/induced_subtree."""
        node_ids = self._query_to_node_ids(query)
        payload = {"node_ids": node_ids, "label_format": label_format}
        data = self._request_json(
            "tree_of_life/induced_subtree",
            payload,
            use_cache=True,
            cache_namespace="induced_subtrees",
        )
        if "newick" not in data:
            raise ToytreeError(
                "unexpected response shape from tree_of_life/induced_subtree"
            )
        return data

    def fetch_json_studies_by_author(
        self,
        query: str | Sequence[str],
        verbose: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch matched studies by publication-reference text query."""
        items = [query] if isinstance(query, str) else list(query)
        rows: list[dict[str, Any]] = []
        for item in items:
            rows.extend(
                self._fetch_json_studies(
                    "ot:studyPublicationReference", str(item), verbose
                )
            )
        return _dedupe_studies(rows)

    def fetch_json_studies_by_taxa(
        self,
        query: str | Sequence[str],
        verbose: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch matched studies by focal clade/taxon text query."""
        items = [query] if isinstance(query, str) else list(query)
        rows: list[dict[str, Any]] = []
        for item in items:
            rows.extend(
                self._fetch_json_studies(
                    "ot:focalCladeOTTTaxonName", str(item), verbose
                )
            )
        return _dedupe_studies(rows)

    def fetch_json_studies_by_doi(
        self,
        query: str | Sequence[str],
        verbose: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch matched studies by DOI query."""
        items = [query] if isinstance(query, str) else list(query)
        rows: list[dict[str, Any]] = []
        for item in items:
            doi = DOI_PREFIX_PATTERN.sub("", str(item).strip())
            rows.extend(self._fetch_json_studies("ot:studyPublication", doi, verbose))
        return _dedupe_studies(rows)

    @staticmethod
    def _normalize_label_token(text: str) -> str:
        """Replace whitespace with underscore for Newick-safe taxon tokens."""
        return re.sub(r"\s+", "_", str(text).strip())

    def _validate_resolved_taxa_table(self, resolved: pd.DataFrame) -> pd.DataFrame:
        """Validate resolved rows shared by OTOL tree-building helpers."""
        # input must be a dataframe with the expected columns
        if not isinstance(resolved, pd.DataFrame):
            raise ToytreeError("resolved must be a pandas DataFrame.")
        required = {"query", "status", "matched_name", "ott_id"}
        missing = [i for i in required if i not in resolved.columns]
        if missing:
            raise ToytreeError(
                f"resolved DataFrame is missing required columns: {missing!r}"
            )
        if "ncbi_id" not in resolved.columns:
            resolved = resolved.copy()
            resolved["ncbi_id"] = pd.array([pd.NA] * len(resolved), dtype="Int64")

        # all taxa must be successfully resolved in the dataframe
        bad = resolved[(resolved["status"] != "matched") | (resolved["ott_id"].isna())]
        if not bad.empty:
            raise ToytreeError(
                "resolved DataFrame contains unresolved rows. "
                "Use resolve_taxonomic_names(..., on_unresolved='raise' or "
                "on_ambiguous='first') or filter to matched rows."
            )
        return resolved

    def _format_resolved_taxon_label(
        self,
        row: pd.Series | dict[str, Any],
        label_template: str,
        idx: object,
    ) -> str:
        """Apply label_template to one resolved row and normalize the token."""
        ott = int(row["ott_id"])
        ncbi_val = row.get("ncbi_id", pd.NA)
        ncbi_text = ""
        if pd.notna(ncbi_val):
            ncbi_text = str(int(ncbi_val))
        key_val = row.get("key", "")
        if pd.isna(key_val):
            key_text = ""
        else:
            key_text = str(key_val)
        context = {
            "key": key_text,
            "query": row.get("query"),
            "matched_name": row.get("matched_name"),
            "ott_id": ott,
            "ncbi_id": ncbi_text,
            "query_id": str(row.get("query", idx)),
            "ncbi_suffix": f"_ncbi{ncbi_text}" if ncbi_text else "",
        }
        try:
            label = label_template.format(**context)
        except KeyError as exc:
            fields = ", ".join(sorted(context))
            raise ToytreeError(
                f"label_template uses unknown field {exc!s}; "
                f"available fields are: {fields}"
            ) from exc
        return induced_tree._normalize_label_token(str(label))

    def _coerce_resolved_taxa(
        self,
        resolved: pd.DataFrame,
        label_template: str,
    ) -> dict[int, str]:
        """Validate resolved table and return dict[int, str] of ids to names."""
        resolved = self._validate_resolved_taxa_table(resolved)

        # no names can be duplicated
        ott_ids = [int(i) for i in resolved["ott_id"].tolist()]
        if len(set(ott_ids)) != len(ott_ids):
            raise ToytreeError("resolved DataFrame contains duplicate ott_id values.")
        # ---------------------------------------------------------

        # extract names using label_template and fill the dict
        labels: dict[int, str] = {}
        for idx, row in resolved.iterrows():
            ott = int(row["ott_id"])
            labels[ott] = self._format_resolved_taxon_label(
                row=row,
                label_template=label_template,
                idx=idx,
            )

        # raise on duplciates
        if len(set(labels.values())) != len(labels):
            raise ToytreeError(
                "label_template formatting produced duplicate labels; "
                "choose a more specific template."
            )
        return labels

    def fetch_tree_from_taxonomy(
        self,
        resolved: pd.DataFrame,
        label_template: str = "{matched_name}_ott{ott_id}",
        force_as_tips: bool = True,
    ) -> ToyTree:
        """Return a ToyTree representing OpenTree taxonomy ancestry.

        Taxonomic lineage identities are merged directly into a parent-child
        trie. Ranks are retained as metadata but are not treated as distances;
        every edge therefore has arbitrary unit length.
        """
        resolved = self._validate_resolved_taxa_table(resolved)
        labels = self._coerce_resolved_taxa(resolved, label_template)
        ott_ids = list(labels)
        records = self.fetch_json_taxon_info(ott_ids, include_lineage=True)
        tree = induced_tree.build_taxonomy_tree(
            records,
            ott_ids,
            force_as_tips=force_as_tips,
        )
        ncbi_by_ott = {
            int(row["ott_id"]): row["ncbi_id"] for row in resolved.to_dict("records")
        }
        for node in tree:
            ott = getattr(node, "ott_id", pd.NA)
            if pd.isna(ott):
                node.ncbi_id = pd.NA
                continue
            ott = int(ott)
            node.ncbi_id = ncbi_by_ott.get(ott, pd.NA)
            if node.is_leaf() and ott in labels:
                node.name = labels[ott]
        tree._update()
        return tree

    def fetch_tree_from_synthesis(
        self,
        resolved: pd.DataFrame,
        label_template: str = "{matched_name}_ott{ott_id}",
        constrain_by_taxonomy: bool = True,
        force_as_tips: bool = True,
    ) -> ToyTree:
        """Return a ToyTree induced from the OpenTree synthetic tree."""
        import toytree

        resolved = self._validate_resolved_taxa_table(resolved)
        labels = self._coerce_resolved_taxa(resolved, label_template)
        ott_ids = list(labels)
        payload = self.fetch_json_induced_subtree(ott_ids, label_format="name_and_id")
        newick = payload.get("newick")
        broken = payload.get("broken", {})
        if not isinstance(newick, str) or not newick.strip():
            raise ToytreeError("induced subtree response has no usable Newick tree.")
        if not isinstance(broken, dict):
            raise ToytreeError("induced subtree response has malformed 'broken' data.")

        induced = toytree.tree(newick)
        induced, present = induced_tree._normalize_induced_tips_to_ott(induced)
        records = self.fetch_json_taxon_info(ott_ids, include_lineage=True)

        if constrain_by_taxonomy:
            tree = induced_tree.build_taxonomy_tree(
                records,
                ott_ids,
                force_as_tips=force_as_tips,
            )
            tree = induced_tree._refine_scaffold_with_induced(tree, induced)
        else:
            tree = induced
            for token, anchor_label in broken.items():
                ott = induced_tree._parse_ott_id_token(token)
                anchor = induced_tree._resolve_anchor_node(tree, str(anchor_label))
                tree = tree.mod.add_child_node(anchor, name=f"ott{ott}", dist=1.0)

            if force_as_tips:
                present_set = set(present)
                for node in list(tree[tree.ntips :]):
                    ott = induced_tree._parse_ott_id_from_label(str(node.name))
                    if ott in labels and ott not in present_set:
                        node.name = ""
                        child = toytree.Node(name=f"ott{ott}", dist=1.0)
                        child.ott_id = ott
                        node._add_child(child)
                tree._update()

        ncbi_by_ott = {
            int(row["ott_id"]): row["ncbi_id"] for row in resolved.to_dict("records")
        }
        for node in tree:
            existing = getattr(node, "ott_id", pd.NA)
            if pd.notna(existing):
                ott = int(existing)
            else:
                parsed = induced_tree._parse_ott_id_from_label(str(node.name))
                # Synthetic internal labels such as ``mrcaott2ott3`` are node
                # identifiers, not taxon identities. Only query tips receive
                # taxon metadata from a parsed label.
                ott = parsed if node.is_leaf() and parsed in labels else None
            if ott is None:
                if not hasattr(node, "ott_id"):
                    node.ott_id = pd.NA
                if not hasattr(node, "ncbi_id"):
                    node.ncbi_id = pd.NA
                continue
            node.ott_id = ott
            node.ncbi_id = ncbi_by_ott.get(ott, pd.NA)
            if node.is_leaf() and ott in labels:
                node.name = labels[ott]
        tree.mod.edges_extend_tips_to_align(inplace=True)
        tree.mod.ladderize(inplace=True)
        return tree

    def fetch_newick_induced_tree_otol(
        self,
        resolved: pd.DataFrame,
        label_template: str = "{matched_name}",
        constrain_by_taxonomy: bool = True,
        force_as_tips: bool = True,
    ) -> str:
        """Deprecated string wrapper around :meth:`fetch_tree_from_synthesis`."""
        import warnings

        warnings.warn(
            "fetch_newick_induced_tree_otol() is deprecated; use "
            "fetch_tree_from_synthesis() for a ToyTree result.",
            DeprecationWarning,
            stacklevel=2,
        )
        tree = self.fetch_tree_from_synthesis(
            resolved,
            label_template=label_template,
            constrain_by_taxonomy=constrain_by_taxonomy,
            force_as_tips=force_as_tips,
        )
        return tree.write(
            internal_labels="name",
            dist_formatter=None,
            features=["ott_id", "ncbi_id"],
        )

    def fetch_newick_subtree_from_taxonomy(
        self,
        resolved: pd.DataFrame,
        label_template: str = "{matched_name}_ott{ott_id}",
    ) -> str:
        """Return deprecated Newick serialization of a taxonomy tree.

        Parameters
        ----------
        resolved : pandas.DataFrame
            Output table from ``resolve_taxonomic_names`` with one matched row
            per unique OTOL taxon.
        label_template : str, default="{matched_name}_ott{ott_id}"
            Python format string applied to each resolved row to generate the
            final output tip labels. Available fields include ``key``,
            ``query``, ``matched_name``, ``ott_id``, ``ncbi_id``,
            ``query_id``, and ``ncbi_suffix``.

        Returns
        -------
        str
            A rooted Newick string with NHX identifier metadata. The topology
            is built directly from taxonomy ancestry and edge lengths are
            arbitrary units.

        Raises
        ------
        ToytreeError
            If rows, labels, or lineage records are invalid.

        Notes
        -----
        This compatibility wrapper emits ``DeprecationWarning``. Use
        :meth:`fetch_tree_from_taxonomy` for the primary ToyTree API.
        """
        import warnings

        warnings.warn(
            "fetch_newick_subtree_from_taxonomy() is deprecated; use "
            "fetch_tree_from_taxonomy() for a ToyTree result.",
            DeprecationWarning,
            stacklevel=2,
        )
        tree = self.fetch_tree_from_taxonomy(resolved, label_template)
        return tree.write(
            internal_labels="name",
            dist_formatter=None,
            features=["ott_id", "ncbi_id", "taxonomic_rank"],
        )


_DEFAULT_CLIENT: _OTOLClient | None = None


def _dedupe_studies(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate studies by ot:studyId, or record hash when absent."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for rec in records:
        key = str(rec.get("ot:studyId", ""))
        if not key:
            key = json.dumps(rec, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


def _get_default_client() -> _OTOLClient:
    """Return module default OTOL client, creating it lazily."""
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = _OTOLClient()
    return _DEFAULT_CLIENT


def configure_client(
    base_url: str = URI,
    timeout: float = 20.0,
    max_retries: int = 4,
    backoff_factor: float = 0.5,
    cache: bool = True,
    cache_dir: str | Path | None = None,
    cache_ttl: float | None = 7 * 24 * 60 * 60,
    session: Session | None = None,
) -> None:
    """Configure the module-level OTOL client.

    Parameters
    ----------
    base_url : str, default=URI
        Base URL for OTOL API requests.
    timeout : float, default=20.0
        Network timeout (seconds) applied to each HTTP request.
    max_retries : int, default=4
        Maximum retry count for transient HTTP failures.
    backoff_factor : float, default=0.5
        Retry backoff scale for repeated transient failures.
    cache : bool, default=True
        If True, cache selected endpoint responses on disk.
    cache_dir : str or pathlib.Path or None, default=None
        Directory used for cache files.
    cache_ttl : float or None, default=604800
        Maximum cache age in seconds. Set to ``None`` to retain entries
        indefinitely or zero to force revalidation on every request.
    session : requests.Session or None, default=None
        Optional user-provided session.

    Returns
    -------
    None

    Raises
    ------
    ToytreeError
        Raised later by network methods if configuration is invalid.

    Examples
    --------
    >>> toytree.otol.configure_client(timeout=10.0, cache=True)

    API Call (curl)
    ---------------
    This function configures local behavior only and does not call an OTOL endpoint.
    """
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is not None:
        _DEFAULT_CLIENT.close()
    _DEFAULT_CLIENT = _OTOLClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        cache=cache,
        cache_dir=cache_dir,
        cache_ttl=cache_ttl,
        session=session,
    )


def reset_client() -> None:
    """Reset the module-level OTOL client to default lazy initialization.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    ToytreeError
        Not raised directly by this function.

    Examples
    --------
    >>> toytree.otol.reset_client()

    API Call (curl)
    ---------------
    This function resets local state only and does not call an OTOL endpoint.
    """
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is not None:
        _DEFAULT_CLIENT.close()
    _DEFAULT_CLIENT = None


def fetch_json_match_names(
    query: str | Sequence[str],
    approximate: bool = False,
    context: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch raw TNRS match records from ``tnrs/match_names``.

    Parameters
    ----------
    query : str or Sequence[str]
        One name or list of names to resolve through OTOL TNRS.
    approximate : bool, default=False
        If True, request approximate (fuzzy) matching.
    context : str or None, default=None
        Optional TNRS context filter (for example, ``"Animals"``).

    Returns
    -------
    list[dict[str, Any]]
        Raw ``results`` records from the TNRS payload.

    Raises
    ------
    ToytreeError
        If request fails or payload lacks expected ``results`` shape.

    Examples
    --------
    >>> rows = toytree.otol.fetch_json_match_names(["Homo sapiens", "Pan troglodytes"])

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/tnrs/match_names -H "content-type: application/json" -d '{"names": ["Homo sapiens"]}'``
    """
    return _get_default_client().fetch_json_match_names(
        query=query,
        approximate=approximate,
        context=context,
    )


def fetch_json_node_info(
    query: FLEX_QUERY,
    include_lineage: bool = False,
) -> list[dict[str, Any]]:
    """Fetch raw node records from ``tree_of_life/node_info``.

    Parameters
    ----------
    query : FLEX_QUERY
        Name(s), OTT ID(s), node ID(s), or mixtures of these.
    include_lineage : bool, default=False
        If True, include lineage metadata in returned records when available.

    Returns
    -------
    list[dict[str, Any]]
        Raw node-info records in endpoint order.

    Raises
    ------
    ToytreeError
        If query normalization fails, request fails, or payload shape is invalid.

    Examples
    --------
    >>> recs = toytree.otol.fetch_json_node_info(["Homo sapiens", 770315])

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/tree_of_life/node_info -H "content-type: application/json" -d '{"node_ids": ["ott770315"], "include_lineage": false}'``
    """
    return _get_default_client().fetch_json_node_info(
        query=query,
        include_lineage=include_lineage,
    )


def fetch_json_mrca(query: FLEX_QUERY) -> dict[str, Any]:
    """Fetch raw MRCA payload from ``tree_of_life/mrca``.

    Parameters
    ----------
    query : FLEX_QUERY
        Name(s), OTT ID(s), node ID(s), or mixtures of these.

    Returns
    -------
    dict[str, Any]
        Raw MRCA response payload.

    Raises
    ------
    ToytreeError
        If query normalization fails or request fails.

    Examples
    --------
    >>> out = toytree.otol.fetch_json_mrca(["Homo sapiens", "Pan troglodytes"])

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/tree_of_life/mrca -H "content-type: application/json" -d '{"node_ids": ["ott770315", "ott542509"]}'``
    """
    return _get_default_client().fetch_json_mrca(query=query)


def fetch_json_taxon_info(
    query: TAXON_QUERY,
    include_lineage: bool = False,
    include_children: bool = False,
    include_terminal_descendants: bool = False,
) -> list[dict[str, Any]]:
    """Fetch raw taxonomy records from ``taxonomy/taxon_info``.

    Parameters
    ----------
    query : TAXON_QUERY
        One query or sequence of queries as names, OTT IDs, or source-id dicts
        (for example ``{"ncbi": 9606}``).
    include_lineage : bool, default=False
        If True, include lineage info in each returned record.
    include_children : bool, default=False
        If True, include immediate child-taxa metadata.
    include_terminal_descendants : bool, default=False
        If True, include terminal descendant IDs where supported.

    Returns
    -------
    list[dict[str, Any]]
        One raw record per input query.

    Raises
    ------
    ToytreeError
        If any query cannot be resolved or any request fails.

    Examples
    --------
    >>> recs = toytree.otol.fetch_json_taxon_info(["Primates", {"ncbi": 9606}], include_lineage=True)

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/taxonomy/taxon_info -H "content-type: application/json" -d '{"ott_id": 770315, "include_lineage": true, "include_children": false, "include_terminal_descendants": false}'``
    """
    return _get_default_client().fetch_json_taxon_info(
        query=query,
        include_lineage=include_lineage,
        include_children=include_children,
        include_terminal_descendants=include_terminal_descendants,
    )


def fetch_json_taxonomy_about() -> dict[str, Any]:
    """Fetch raw taxonomy metadata from ``taxonomy/about``.

    Parameters
    ----------
    None

    Returns
    -------
    dict[str, Any]
        Raw taxonomy metadata payload.

    Raises
    ------
    ToytreeError
        If the request fails.

    Examples
    --------
    >>> meta = toytree.otol.fetch_json_taxonomy_about()

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/taxonomy/about -H "content-type: application/json" -d '{}'``
    """
    return _get_default_client().fetch_json_taxonomy_about()


def fetch_json_subtree(
    query: int | str,
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fetch raw synthetic-subtree payload from ``tree_of_life/subtree``.

    Parameters
    ----------
    query : int or str
        Taxon name, OTT ID, or node ID used as subtree root.
    extra_params : dict[str, Any] or None, default=None
        Optional extra endpoint parameters merged into request payload.

    Returns
    -------
    dict[str, Any]
        Raw subtree payload containing at least ``newick``.

    Raises
    ------
    ToytreeError
        If query resolution fails, request fails, or payload lacks ``newick``.

    Examples
    --------
    >>> payload = toytree.otol.fetch_json_subtree("Homo")

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/tree_of_life/subtree -H "content-type: application/json" -d '{"node_id": "ott770309"}'``
    """
    return _get_default_client().fetch_json_subtree(
        query=query,
        extra_params=extra_params,
    )


def fetch_json_induced_subtree(
    query: Sequence[int | str],
    label_format: str = "name_and_id",
) -> dict[str, Any]:
    """Fetch raw induced-subtree payload from ``tree_of_life/induced_subtree``.

    Parameters
    ----------
    query : Sequence[int | str]
        Names, OTT IDs, node IDs, or mixed sequence used to induce a subtree.
    label_format : str, default="name_and_id"
        OTOL label format for tips in the returned Newick.

    Returns
    -------
    dict[str, Any]
        Raw induced-subtree payload containing at least ``newick``.

    Raises
    ------
    ToytreeError
        If query normalization fails, request fails, or payload lacks ``newick``.

    Examples
    --------
    >>> payload = toytree.otol.fetch_json_induced_subtree(["Homo sapiens", "Pan troglodytes"])

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/tree_of_life/induced_subtree -H "content-type: application/json" -d '{"node_ids": ["ott770315", "ott542509"], "label_format": "name_and_id"}'``
    """
    return _get_default_client().fetch_json_induced_subtree(
        query=query,
        label_format=label_format,
    )


def fetch_json_studies_by_author(
    query: str | Sequence[str],
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Fetch raw study records by author/publication-reference query.

    Parameters
    ----------
    query : str or Sequence[str]
        One author-like text query or many queries.
    verbose : bool, default=True
        Forwarded to OTOL studies endpoint verbosity option.

    Returns
    -------
    list[dict[str, Any]]
        De-duplicated study records from ``matched_studies``.

    Raises
    ------
    ToytreeError
        If requests to studies endpoint fail.

    Examples
    --------
    >>> rows = toytree.otol.fetch_json_studies_by_author("Smith")

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/studies/find_studies -H "content-type: application/json" -d '{"property": "ot:studyPublicationReference", "value": "Smith", "verbose": true}'``
    """
    return _get_default_client().fetch_json_studies_by_author(
        query=query, verbose=verbose
    )


def fetch_json_studies_by_taxa(
    query: str | Sequence[str],
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Fetch raw study records by focal-clade / taxa text query.

    Parameters
    ----------
    query : str or Sequence[str]
        One clade/taxon text query or many queries.
    verbose : bool, default=True
        Forwarded to OTOL studies endpoint verbosity option.

    Returns
    -------
    list[dict[str, Any]]
        De-duplicated study records from ``matched_studies``.

    Raises
    ------
    ToytreeError
        If requests to studies endpoint fail.

    Examples
    --------
    >>> rows = toytree.otol.fetch_json_studies_by_taxa("Primates")

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/studies/find_studies -H "content-type: application/json" -d '{"property": "ot:focalCladeOTTTaxonName", "value": "Primates", "verbose": true}'``
    """
    return _get_default_client().fetch_json_studies_by_taxa(
        query=query, verbose=verbose
    )


def fetch_json_studies_by_doi(
    query: str | Sequence[str],
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Fetch raw study records by DOI query.

    Parameters
    ----------
    query : str or Sequence[str]
        One DOI-like query or many; DOI URLs and ``doi:`` prefixes are accepted.
    verbose : bool, default=True
        Forwarded to OTOL studies endpoint verbosity option.

    Returns
    -------
    list[dict[str, Any]]
        De-duplicated study records from ``matched_studies``.

    Raises
    ------
    ToytreeError
        If requests to studies endpoint fail.

    Examples
    --------
    >>> rows = toytree.otol.fetch_json_studies_by_doi("https://doi.org/10.1002/ajb2.1019")

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/studies/find_studies -H "content-type: application/json" -d '{"property": "ot:studyPublication", "value": "10.1002/ajb2.1019", "verbose": true}'``
    """
    return _get_default_client().fetch_json_studies_by_doi(query=query, verbose=verbose)


def resolve_taxonomic_names(
    query: Sequence[str] | Mapping[str, str],
    approximate: bool = False,
    context: str | None = None,
    include_synonyms: bool = True,
    on_unresolved: Literal["raise", "warn", "ignore"] = "ignore",
    on_ambiguous: Literal["ignore", "first", "raise"] = "first",
    on_duplicate: Literal["ignore", "warn", "raise"] = "warn",
    return_unresolved: bool = False,
) -> pd.DataFrame:
    """Resolve taxonomic names through OTOL TNRS.

    Parameters
    ----------
    query : Sequence[str] or Mapping[str, str]
        Taxon-name strings to resolve. If a mapping is provided then its
        values are used as TNRS queries and its keys are stored in the
        returned ``key`` column.
    approximate : bool, default=False
        If True, enable approximate matching in TNRS.
    context : str or None, default=None
        Optional TNRS context.
    include_synonyms : bool, default=True
        If False, synonym matches are filtered before status assignment.
    on_unresolved : {"raise", "warn", "ignore"}, default="ignore"
        Behavior when unmatched or ambiguous rows remain.
    on_ambiguous : {"ignore", "first", "raise"}, default="first"
        Behavior when a query has multiple TNRS matches.
    on_duplicate : {"ignore", "warn", "raise"}, default="warn"
        Behavior when multiple matched queries resolve to the same OTT id.
    return_unresolved : bool, default=False
        If True, return only rows whose status is not ``"matched"``.

    Returns
    -------
    pandas.DataFrame
        Standardized resolution table with columns ``key``, ``query``,
        ``status``, ``matched_name``, ``rank``, ``taxon_name``, ``ott_id``,
        ``ncbi_id``, ``is_synonym``, and ``reason``. Rows kept as ambiguous
        leave taxon-specific fields missing. Duplicate matched OTT ids are
        handled according to ``on_duplicate``. For sequence input, ``key``
        values are missing. If ``return_unresolved=True``, only unresolved
        rows are returned.
    """
    return _get_default_client().resolve_taxonomic_names(
        query=query,
        approximate=approximate,
        context=context,
        include_synonyms=include_synonyms,
        on_unresolved=on_unresolved,
        on_ambiguous=on_ambiguous,
        on_duplicate=on_duplicate,
        return_unresolved=return_unresolved,
    )


def fetch_tree_from_taxonomy(
    resolved: pd.DataFrame,
    label_template: str = "{matched_name}_ott{ott_id}",
    force_as_tips: bool = True,
) -> ToyTree:
    """Build a taxonomy topology and return it as a ToyTree.

    Parameters
    ----------
    resolved : pandas.DataFrame
        Matched rows returned by :func:`resolve_taxonomic_names`. Every row
        must have ``status == 'matched'`` and a unique, non-missing ``ott_id``.
    label_template : str, default="{matched_name}_ott{ott_id}"
        Python format template for query tip names. Supported fields are
        ``key``, ``query``, ``matched_name``, ``ott_id``, ``ncbi_id``,
        ``query_id``, and ``ncbi_suffix``. Generated names must be unique.
    force_as_tips : bool, default=True
        If True, a queried taxon that is an ancestor of another query is
        represented by an added terminal child. If False, it remains only as
        its natural internal taxonomy node.

    Returns
    -------
    ToyTree
        A rooted taxonomy tree. Nodes store ``ott_id``, ``ncbi_id``, and
        ``taxonomic_rank`` features. Edge lengths are arbitrary unit lengths:
        OpenTree taxonomy provides ancestry but no divergence-time metric.

    Raises
    ------
    ToytreeError
        If rows are unresolved or duplicated, labels collide, or OpenTree
        returns incomplete or inconsistent lineage data.

    Notes
    -----
    The topology is built by merging ancestor identities into a lineage trie;
    taxonomic ranks are never converted into pseudo-distances.
    """
    return _get_default_client().fetch_tree_from_taxonomy(
        resolved,
        label_template=label_template,
        force_as_tips=force_as_tips,
    )


def fetch_tree_from_synthesis(
    resolved: pd.DataFrame,
    label_template: str = "{matched_name}_ott{ott_id}",
    constrain_by_taxonomy: bool = True,
    force_as_tips: bool = True,
) -> ToyTree:
    """Build an OpenTree synthesis topology and return it as a ToyTree.

    Parameters
    ----------
    resolved : pandas.DataFrame
        Matched rows returned by :func:`resolve_taxonomic_names`. Every row
        must have ``status == 'matched'`` and a unique, non-missing ``ott_id``.
    label_template : str, default="{matched_name}_ott{ott_id}"
        Python format template for query tip names. Supported fields are
        ``key``, ``query``, ``matched_name``, ``ott_id``, ``ncbi_id``,
        ``query_id``, and ``ncbi_suffix``. Generated names must be unique.
    constrain_by_taxonomy : bool, default=True
        If True, taxonomy clades are hard constraints and compatible synthesis
        clades refine their polytomies. If False, use the synthetic induced
        tree directly and attach taxa reported as broken under their supplied
        synthesis anchor.
    force_as_tips : bool, default=True
        If True, queried ancestors are represented by terminal children so all
        queries occur as tips. If False, ancestor queries may remain internal.

    Returns
    -------
    ToyTree
        A rooted tree with ``ott_id`` and ``ncbi_id`` node features and tip
        names generated from ``label_template``. Edge lengths are topological,
        not divergence times.

    Raises
    ------
    ToytreeError
        If resolution rows, labels, API payloads, or lineage data are invalid.
    """
    return _get_default_client().fetch_tree_from_synthesis(
        resolved,
        label_template=label_template,
        constrain_by_taxonomy=constrain_by_taxonomy,
        force_as_tips=force_as_tips,
    )


def fetch_newick_subtree_from_taxonomy(
    resolved: pd.DataFrame,
    label_template: str = "{matched_name}_ott{ott_id}",
) -> str:
    """Return deprecated Newick serialization of an OpenTree taxonomy tree.

    Parameters
    ----------
    resolved : pandas.DataFrame
        Output table from ``resolve_taxonomic_names`` with one matched row per
        unique OTOL taxon.
    label_template : str, default="{matched_name}_ott{ott_id}"
        Python format string applied to each resolved row to generate final
        output tip labels. Available fields include ``key``, ``query``,
        ``matched_name``, ``ott_id``, ``ncbi_id``, ``query_id``, and
        ``ncbi_suffix``.

    Returns
    -------
    str
        Rooted Newick with lineage-derived internal labels and NHX identifier
        metadata. Edge lengths are arbitrary topological units.

    Raises
    ------
    ToytreeError
        If rows, labels, or lineage records are invalid.

    Notes
    -----
    This compatibility wrapper emits ``DeprecationWarning``. New code should
    call :func:`fetch_tree_from_taxonomy` and serialize the returned ToyTree
    explicitly when needed.

    Examples
    --------
    >>> resolved = toytree.otol.resolve_taxonomic_names(
    ...     ["Homo sapiens", "Pan troglodytes", "Gorilla gorilla"],
    ...     on_ambiguous="first",
    ...     on_unresolved="raise",
    ... )
    >>> nwk = toytree.otol.fetch_newick_subtree_from_taxonomy(resolved)

    API Call (curl)
    ---------------
    ``curl -X POST https://api.opentreeoflife.org/v3/taxonomy/taxon_info -H "content-type: application/json" -d '{"ott_id": 770315, "include_lineage": true, "include_children": false, "include_terminal_descendants": false}'``
    """
    return _get_default_client().fetch_newick_subtree_from_taxonomy(
        resolved=resolved,
        label_template=label_template,
    )


def fetch_newick_induced_tree_otol(
    resolved: pd.DataFrame,
    label_template: str = "{matched_name}",
    constrain_by_taxonomy: bool = True,
    force_as_tips: bool = True,
) -> str:
    """Return induced OTOL Newick with optional taxonomy constraints.

    Parameters
    ----------
    resolved : pandas.DataFrame
        Output table from ``resolve_taxonomic_names`` with one matched row per
        OTOL taxon.
    label_template : str, default="{matched_name}"
        Python format string applied to each resolved row to generate final
        output tip labels. If output includes additional OTT IDs not present in
        ``resolved`` (for example from broken-node insertion), those labels are
        filled from taxonomy names as ``{name}_ott{ott_id}``. Available fields
        include ``key``, ``query``, ``matched_name``, ``ott_id``, ``ncbi_id``,
        ``query_id``, and ``ncbi_suffix``.
    constrain_by_taxonomy : bool, default=True
        If True, taxonomy scaffolding is enforced and induced topology is used
        to resolve compatible polytomies. If False, the induced OTOL topology
        is used directly.
    force_as_tips : bool, default=True
        If True, queried ancestor taxa are represented as terminal children.

    Returns
    -------
    str
        Newick string for induced OTOL tree with broken taxa inserted.

    Raises
    ------
    ToytreeError
        If query is empty, payload/lineage data are malformed, or selected tip
        label formatting yields duplicate names.

    Examples
    --------
    >>> resolved = toytree.otol.resolve_taxonomic_names(
    ...     ["Homo sapiens", "Pan troglodytes", "Gorilla gorilla"],
    ...     on_ambiguous="first",
    ...     on_unresolved="raise",
    ... )
    >>> nwk = toytree.otol.fetch_newick_induced_tree_otol(resolved)
    >>> nwk_unconstrained = toytree.otol.fetch_newick_induced_tree_otol(
    ...     resolved,
    ...     constrain_by_taxonomy=False,
    ... )
    """
    return _get_default_client().fetch_newick_induced_tree_otol(
        resolved=resolved,
        label_template=label_template,
        constrain_by_taxonomy=constrain_by_taxonomy,
        force_as_tips=force_as_tips,
    )


if __name__ == "__main__":
    SUBTREE_SPP_LIST = [
        "Castilleja caudata",
        "Castilleja campestris",
        "Orobanche cumana",
        "Pedicularis anas",
        "Pedicularis groenlandica",
        "Pedicularis latituba",
        # "Mimulus guttatus",
        "Erythranthe guttata",
        "Aquilegia coerulea",
        "Delphinium exaltatum",
        "Amaranthus greggii",
        "Quercus minima",
        # "Quercus macrocarpa",
        "Quercus virginiana",
        "Quercus alba",
        "Boswellia sacra",
    ]

    SUBTREE_GEN_LIST = [
        "Castilleja",
        "Orobanche",
        "Phelipanche",
        "Lindenbergia",
        "Rehmannia",
        "Pedicularis",
        "Mimulus",
        "Erythranthe",
        "Aquilegia",
        "Quercus",
        "Fagus",
        "Boswellia",
        "Delphinium",
    ]

    names = resolve_taxonomic_names(
        SUBTREE_GEN_LIST,
        approximate=True,
        context="Angiosperms",
        on_ambiguous="first",
        on_unresolved="warn",
    )

    nwk = fetch_newick_subtree_from_taxonomy(names)

    import toytree

    t = toytree.tree(nwk)
    t._draw_browser("s", node_hover=True)
