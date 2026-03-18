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

import hashlib
import json
import pickle
import re
import sys
import tempfile
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, Sequence
from urllib.parse import urljoin

import pandas as pd
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from toytree.utils import ToytreeError

from . import induced_tree

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
    "fetch_newick_subtree_from_taxonomy",
    "fetch_newick_induced_tree_otol",
]


class _OTOLClient:
    """Private OTOL client for transport, retries, and cache."""

    def __init__(
        self,
        base_url: str = URI,
        timeout: float = 20.0,
        max_retries: int = 4,
        backoff_factor: float = 0.5,
        cache: bool = True,
        cache_dir: str | Path | None = None,
        session: Session | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout = float(timeout)
        self.max_retries = int(max_retries)
        self.backoff_factor = float(backoff_factor)
        self.cache = bool(cache)
        self.cache_dir = (
            Path(cache_dir).expanduser()
            if cache_dir is not None
            else Path(tempfile.gettempdir()) / "toytree_otol_cache"
        )
        self._session = session

    @staticmethod
    def _build_session(max_retries: int, backoff_factor: float) -> Session:
        """Create a requests session with retry and backoff."""
        retry = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "POST"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.headers.update(HEADERS_JSON)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @staticmethod
    def _error_from_response(
        endpoint: str,
        exc: Exception,
        response: requests.Response | None,
    ) -> ToytreeError:
        """Construct a standardized ToytreeError from an HTTP failure."""
        status = None if response is None else response.status_code
        snippet = ""
        if response is not None:
            snippet = response.text[:500].replace("\n", " ")
        return ToytreeError(
            f"OTOL request failed at endpoint '{endpoint}'. "
            f"status={status!r}. error={exc}. response_snippet={snippet!r}"
        )

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        """Return deterministic hash of request payload."""
        dumped = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

    def _cache_path(self, namespace: str, payload: dict[str, Any]) -> Path:
        """Return cache path for namespace + payload hash."""
        return self.cache_dir / namespace / f"{self._hash_payload(payload)}.pkl"

    def _cache_read(self, path: Path) -> Any | None:
        """Read cache entry if available."""
        if not self.cache or not path.exists():
            return None
        with path.open("rb") as ihandle:
            return pickle.load(ihandle)

    def _cache_write(self, path: Path, data: Any) -> None:
        """Write cache entry if caching is enabled."""
        if not self.cache:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as ohandle:
            pickle.dump(data, ohandle, protocol=pickle.HIGHEST_PROTOCOL)

    def _request_json(
        self,
        endpoint: str,
        payload: dict[str, Any],
        use_cache: bool = False,
        cache_namespace: str = "json",
    ) -> dict[str, Any]:
        """POST JSON payload and return parsed JSON."""
        cache_path = self._cache_path(
            cache_namespace,
            {"endpoint": endpoint, "payload": payload},
        )
        if use_cache:
            cached = self._cache_read(cache_path)
            if cached is not None:
                return cached

        response: requests.Response | None = None
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.post(url=url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if use_cache:
                self._cache_write(cache_path, data)
            return data
        except Exception as exc:
            raise self._error_from_response(endpoint, exc, response) from exc

    @property
    def session(self) -> Session:
        """Return active requests session, creating lazily when needed."""
        if self._session is None:
            self._session = self._build_session(
                self.max_retries,
                self.backoff_factor,
            )
        return self._session

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

    def fetch_newick_subtree_from_taxonomy(
        self,
        resolved: pd.DataFrame,
        label_template: str = "{matched_name}_ott{ott_id}",
    ) -> str:
        """Infer a Newick subtree from taxonomic lineage similarity.

        This method fetches taxonomic information for each tip builds a rank
        distance matrix, where lower values representing a lower taxon rank
        MRCA, and then builds a UPGMA tree from this matrix. Taxon names are
        assigned to internal nodes as well.

        Parameters
        ----------
        resolved : pandas.DataFrame
            Output table from ``resolve_taxonomic_names`` with one matched row
            per OTOL taxon. Duplicate ``ott_id`` rows are allowed here.
        label_template : str, default="{matched_name}_ott{ott_id}"
            Python format string applied to each resolved row to generate the
            final output tip labels. Available fields include ``key``,
            ``query``, ``matched_name``, ``ott_id``, ``ncbi_id``,
            ``query_id``, and ``ncbi_suffix``.

        Returns
        -------
        str
            A rooted Newick string inferred from pairwise lineage-rank
            distances and rooted using taxonomy-informed clades when possible.
            If no compatible taxonomy-informed outgroup clade is monophyletic
            in the inferred topology, midpoint rooting is used as fallback.
            When an input taxon is reassigned to an internal node, it is not
            also retained as a terminal tip. When duplicate matched rows share
            a terminal ``ott_id``, the returned tree inserts an artificial
            ``{taxon_name}_ott{ott_id}_group`` parent with missing ``ott_id``.
            Duplicate surviving tip labels are allowed but warned on.

        Raises
        ------
        ToytreeError
            Raised if query is empty or lineage records are malformed.

        Notes
        -----
        **Distance Metric Calculation:**
        This function uses **absolute MRCA depth** rather than cophenetic distance.
        UPGMA assumes an ultrametric tree (all tips represent the present and are
        equidistant from the root). Because taxonomic lineages often have uneven
        resolutions (e.g., missing intermediate ranks), cophenetic path lengths
        artificially shorten branches for sparsely resolved taxa, distorting the
        topology. Absolute MRCA depth acts as a proxy for divergence time, aligning
        splits purely by their highest shared rank. This correctly satisfies UPGMA's
        ultrametric requirement and yields a biologically accurate tree.

        If one or more matched input taxa also label inferred internal nodes,
        those taxa are retained only on the internal nodes and a summary
        warning is printed to stderr because the returned tree will have fewer
        tips than matched input rows.
        """
        import toytree

        resolved = self._validate_resolved_taxa_table(resolved)
        resolved_rows: list[dict[str, Any]] = []
        ott_to_rows: dict[int, list[dict[str, Any]]] = {}
        unique_ott_ids: list[int] = []
        for idx, row in resolved.iterrows():
            record = row.to_dict()
            ott = int(record["ott_id"])
            record["ott_id"] = ott
            record["row_index"] = idx
            resolved_rows.append(record)
            if ott not in ott_to_rows:
                ott_to_rows[ott] = []
                unique_ott_ids.append(ott)
            ott_to_rows[ott].append(record)

        # Build the topology on unique OTT ids first so duplicate matched rows
        # can later be expanded only where they survive as terminal taxa.
        ott_to_label = {ott: f"ott{ott}" for ott in unique_ott_ids}
        label_to_ott = {j: i for (i, j) in ott_to_label.items()}

        # get list[dict[str,Any]] of lineage maps from each taxon to root.
        # TODO: for very large queries does this need to be broken into multiple calls?
        lineages = self.fetch_json_taxon_info(
            unique_ott_ids,
            include_lineage=True,
        )

        # fill dict[str,str] mapping label to taxon lineage map
        label_to_lineage: dict[str, tuple[str, str]] = {}
        ott_to_taxon_name: dict[int, str] = {}
        for rec in lineages:
            ott = rec.get("ott_id")
            if ott is None:
                raise ToytreeError("lineage record missing required key 'ott_id'.")
            ott = int(ott)
            label = ott_to_label[ott]
            ott_to_taxon_name[ott] = str(rec.get("name", f"ott{ott}"))
            lineage = []
            for tax in rec.get("lineage", []):
                ncbi = [i for i in tax.get("tax_sources", []) if i.startswith("ncbi:")]
                ncbi = int(ncbi[0][5:]) if ncbi else float("nan")
                lineage.append(
                    (tax["name"], tax["rank"], tax["ott_id"], ncbi),
                )
            label_to_lineage[label] = lineage

        # get taxonomy cophenetic distance matrix and infer UPGMA distance tree.
        dist, _ = induced_tree.build_cophenetic_distance_matrix_from_taxonomy(
            label_to_lineage
        )
        tree = toytree.infer.upgma_tree(dist)

        def _get_mrca_taxon(label_to_lineage, tnames):
            """Return lowest shared ancestor info among tips 'tnames."""
            base_path = label_to_lineage[tnames[0]]
            for t, _, ott, ncbi in base_path:
                if all([t in [i[0] for i in label_to_lineage[j]] for j in tnames[1:]]):
                    return t, ott, ncbi

        # assign names to internal nodes
        for node in tree:
            if node.is_leaf():
                node.ott_id = label_to_ott[node.name]
                node.ncbi_id = ott_to_rows[node.ott_id][0]["ncbi_id"]
                continue

            # get name and IDs for internal nodes
            tnames = node.get_leaf_names()
            _name, _ott, _ncbi = _get_mrca_taxon(label_to_lineage, tnames)
            node.name = _name
            node.ott_id = _ott
            node.ncbi_id = _ncbi

            # if name is same as a child, keep here and set child to OTT
            for child in node.children:
                if child.name == node.name:
                    child.name = f"ott{_ott}"
            node._dist = 1.0
        tree._update()

        # Mixed-rank inputs can include ancestor taxa that are also inferred
        # as internal nodes; keep those taxa once as internals, not as tips.
        internal_ott_ids = {
            int(node.ott_id)
            for node in tree[tree.ntips :]
            if pd.notna(getattr(node, "ott_id", pd.NA))
        }

        # Only labels that survive as tips are checked for collisions. Rows
        # reassigned to internal nodes do not materialize as terminal labels.
        final_tip_labels = []
        for ott, rows in ott_to_rows.items():
            if ott in internal_ott_ids:
                continue
            for row in rows:
                row["tip_label"] = self._format_resolved_taxon_label(
                    row=row,
                    label_template=label_template,
                    idx=row["row_index"],
                )
                final_tip_labels.append(row["tip_label"])
        duplicate_tip_labels = {
            label: count
            for label, count in Counter(final_tip_labels).items()
            if count > 1
        }
        if duplicate_tip_labels:
            duplicates = ", ".join(
                f"{label!r} ({count})"
                for label, count in sorted(duplicate_tip_labels.items())
            )
            print(
                "WARNING: label_template formatting produced duplicate tip labels: "
                f"{duplicates}. Choose a more specific label_template if you need "
                "unique tip names.",
                file=sys.stderr,
            )

        assigned_to_internal = 0
        for node in list(tree[: tree.ntips]):
            node_ott = getattr(node, "ott_id", pd.NA)
            if pd.isna(node_ott):
                continue
            node_ott = int(node_ott)
            rows = ott_to_rows[node_ott]
            if node_ott in internal_ott_ids:
                assigned_to_internal += len(rows)
                continue
            if len(rows) == 1:
                node.name = rows[0]["tip_label"]
                node.ncbi_id = rows[0]["ncbi_id"]
                continue

            # Preserve a single taxonomy-backed attachment point, then expand
            # duplicate matched rows into child tips underneath that parent.
            taxon_name = ott_to_taxon_name.get(node_ott, rows[0]["matched_name"])
            node.name = self._normalize_label_token(f"{taxon_name}_ott{node_ott}_group")
            node.ott_id = pd.NA
            node.ncbi_id = pd.NA
            for row in rows:
                child = toytree.Node(name=row["tip_label"], dist=0.0)
                child.ott_id = node_ott
                child.ncbi_id = row["ncbi_id"]
                node._add_child(child)
        tree._update()

        if assigned_to_internal:
            tip_labels_to_keep = [
                node.name
                for node in tree[: tree.ntips]
                if not (
                    pd.notna(getattr(node, "ott_id", pd.NA))
                    and int(node.ott_id) in internal_ott_ids
                )
            ]
            ndups = assigned_to_internal
            ntips = len(tip_labels_to_keep)
            ntaxa = len(resolved_rows)
            assigned = "taxon was" if ndups == 1 else "taxa were"
            node_word = "node" if ndups == 1 else "nodes"
            tip_word = "tip" if ntips == 1 else "tips"
            print(
                f"WARNING: {ndups} matched input {assigned} assigned to internal "
                f"{node_word}; returning {ntips} {tip_word} for {ntaxa} matched taxa.",
                file=sys.stderr,
            )
            tree = tree.mod.prune(*tip_labels_to_keep, require_root=False)

        tree.mod.edges_extend_tips_to_align(inplace=True)

        # write with internal node IDs as NHX metadata
        return tree
        # if store_ids:
        #     return tree.write(
        #         internal_labels="name", dist_formatter=None,
        #         features=["ott_id", "ncbi_id"]
        #         )
        # return tree.write(internal_labels="name", dist_formatter=None)

    def get_induced_subtree_from_otol(
        self,
        resolved: pd.DataFrame,
        label_template: str = "{matched_name}",
        constrain_by_taxonomy: bool = True,
        force_as_tips: bool = True,
    ) -> str:
        """Return induced OTOL Newick with optional taxonomy constraints.

        Parameters
        ----------
        resolved : pandas.DataFrame
            Output table from ``resolve_taxonomic_names`` with one matched row
            per OTOL taxon.
        label_template : str, default="{matched_name}"
            Python format string applied to each resolved row to generate the
            final output tip labels. If output includes additional OTT IDs not
            present in ``resolved`` (for example from broken-node insertion),
            those labels are filled from taxonomy names as ``{name}_ott{ott_id}``.
            Available fields include ``key``, ``query``, ``matched_name``,
            ``ott_id``, ``ncbi_id``, ``query_id``, and ``ncbi_suffix``.
        constrain_by_taxonomy : bool, default=True
            If True, enforce taxonomy scaffold constraints and use induced
            topology only to resolve compatible polytomies. If False, use the
            induced OTOL topology directly and insert broken tips on that tree.
        force_as_tips : bool, default=True
            Queries are forced as tip nodes, even if they are internal in
            the induced tree. This ensures the returned tree will have the
            same number of tips and the number of queries. If False, a query
            that is an ancestor of another node will not appear as a tip.

        See Also
        --------
        :func:`toytree.otol.get_timetree_node_ages`
        """
        import toytree

        # get dict[int,str] mapping ott<id> to template style label str
        ott_to_label = self._coerce_resolved_taxa(
            resolved=resolved,
            label_template=label_template,
        )
        # label_to_ott = {j: i for (i, j) in ott_to_label.items()}
        ott_to_ncbi = {i["ott_id"]: i["ncbi_id"] for i in resolved.to_dict("records")}

        # get newick and broken from API call to induced tree
        payload = self.fetch_json_induced_subtree(
            list(ott_to_label), label_format="name_and_id"
        )
        newick = payload.get("newick", "")
        broken = payload.get("broken", {})
        if (not newick) or (not isinstance(broken, dict)):
            raise ToytreeError("induced subtree payload malformed")

        # we do not support broken nodes currently
        if broken:
            raise ToytreeError(
                "broken nodes present. This method does not currently support "
                "splitting non-monophyletic higher-level taxa. Enter species "
                "input names to avoid this problem."
            )

        # build the induced tree from newick
        itree = toytree.tree(newick)
        # return itree

        # assign names and IDs to nodes
        internal_tips = []
        for node in itree:
            # nothing to do for generic mrca nodes
            if node.name.startswith("mrcaott"):
                continue
            # get OTT ID
            ott_id = int(node.name.strip("'").strip('"').rsplit("ott")[-1])
            # set label and IDs to resolved queries
            if ott_id in ott_to_label:
                node.name = ott_to_label[ott_id]
                node.ott_id = ott_id
                node.ncbi_id = ott_to_ncbi[ott_id]

                # store if the query was imputed as internal
                if not node.is_leaf():
                    internal_tips.append(node)

        # optionally enforce resolved queries as tips
        if force_as_tips:
            for node in internal_tips:
                tmp = toytree.Node(name=node.name)
                tmp.ott_id = node.ott_id
                tmp.ncbi_id = node.ncbi_id
                node.name = "null"
                node.ott_id = pd.NA
                node.ncbi_id = pd.NA
                node._add_child(tmp)
                itree._update()

        # clean up the tree
        itree.mod.remove_unary_nodes(inplace=True).ladderize(inplace=True)

        # optionally constrain by taxonomy.
        if constrain_by_taxonomy:
            ttree = fetch_newick_subtree_from_taxonomy(resolved, label_template)

            # iteratively resolve polytomies in taxon tree using resolved
            # splits in the synthetic otol tree.
            while 1:
                nnodes_start = ttree.nnodes

                # get nodes to resolve
                to_resolve = []
                for node in ttree:
                    tchilds = len(node.children)
                    if tchilds > 2:
                        tips = node.get_leaf_names()
                        snode = itree.get_mrca_node(*tips)
                        schilds = len(snode.children)
                        if schilds < tchilds:
                            ctips = []
                            for child in snode.children:
                                ctips.append(
                                    [i for i in child.get_leaf_names() if i in tips]
                                )  # noqa
                            to_resolve.append((tips, ctips))

                # resolve polytomy nodes
                for clade, split in to_resolve:
                    # skip if clade in taxonomy tree
                    try:
                        ttree.mod.resolve_node(*clade, splits=split, inplace=True)
                    except ToytreeError:
                        pass
                if ttree.nnodes == nnodes_start:
                    break
            itree = ttree

        itree.mod.edges_extend_tips_to_align(inplace=True).ladderize(inplace=True)
        return itree


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
    _DEFAULT_CLIENT = _OTOLClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        cache=cache,
        cache_dir=cache_dir,
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


def fetch_newick_subtree_from_taxonomy(
    resolved: pd.DataFrame,
    label_template: str = "{matched_name}_ott{ott_id}",
) -> str:
    """Infer a Newick subtree from taxonomic lineage similarity.

    This helper is designed for taxonomy-informed tree construction from a
    list of resolved taxa. It fetches lineage-enriched taxon records from
    OTOL, converts shared lineage ranks into a pairwise distance matrix,
    infers a distance tree (UPGMA), labels internal nodes from shared lineage
    taxa, and returns a Newick string.

    Parameters
    ----------
    resolved : pandas.DataFrame
        Output table from ``resolve_taxonomic_names`` with one matched row per
        OTOL taxon. Duplicate ``ott_id`` rows are allowed here.
    label_template : str, default="{matched_name}_ott{ott_id}"
        Python format string applied to each resolved row to generate final
        output tip labels. Available fields include ``key``, ``query``,
        ``matched_name``, ``ott_id``, ``ncbi_id``, ``query_id``, and
        ``ncbi_suffix``.

    Returns
    -------
    str
        Newick string with internal node labels set to lineage-derived
        ``{name}_ott{ott_id}`` when available. If a matched input taxon is
        reassigned to an internal node then the returned tree has fewer tips
        than matched input rows, and a summary warning is printed to stderr.
        Duplicate matched rows that remain as terminal taxa are expanded under
        an artificial ``{taxon_name}_ott{ott_id}_group`` parent with missing
        ``ott_id``. Duplicate surviving tip labels are allowed but warned on.

    Raises
    ------
    ToytreeError
        If query is empty or lineage records are malformed.

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
