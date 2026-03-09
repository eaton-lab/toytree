#!/usr/bin/env python
# ruff: noqa: E501,D401

"""Open Tree of Life (OTOL) API utilities.

This module exposes a default OTOL client and module-level wrapper functions
for taxonomy, name-resolution, and synthetic-tree queries.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import re
import tempfile
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Sequence
from urllib.parse import urljoin

import pandas as pd
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from toytree.utils import ToytreeError

if TYPE_CHECKING:
    from toytree import ToyTree

URI = "https://api.opentreeoflife.org/v3/"
HEADERS_JSON = {"content-type": "application/json", "User-Agent": "toytree"}
NODE_ID_PATTERN = re.compile(r"^(ott\d+|mrcaott\d+(?:ott\d+)*)$")
RANKS = ["species", "genus", "family", "order", "class", "phylum", "kingdom"]

FLEX_QUERY = str | int | Sequence[str] | Sequence[int]

__all__ = [
    "FLEX_QUERY",
    "configure_client",
    "reset_client",
    "match_names",
    "taxon_id",
    "taxonomy",
    "taxon_info",
    "taxon_lineage",
    "taxon_parent",
    "taxon_descendants",
    "node_info",
    "node_id",
    "mrca",
    "mrca_node_id",
    "mrca_taxon_id",
    "synthetic_subtree",
    "induced_subtree",
    "taxonomy_subtree",
    "supporting_studies",
    "study_tree",
]


class _OTOLClient:
    """Client for Open Tree of Life API calls.

    Parameters
    ----------
    base_url : str, default=URI
        OTOL API base URL.
    timeout : float, default=20.0
        Request timeout in seconds.
    max_retries : int, default=4
        Number of transport retries for transient failures.
    backoff_factor : float, default=0.5
        Exponential backoff factor between retries.
    cache : bool, default=True
        Enable on-disk cache for selected read calls.
    cache_dir : str, pathlib.Path, or None, default=None
        Cache root directory. Defaults to a temporary-session location.
    session : requests.Session or None, default=None
        Optional custom requests session.
    """

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
        """Create a requests session with retry/backoff for transient failures."""
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
        """Build a standardized ToytreeError from an HTTP failure."""
        status = None if response is None else response.status_code
        snippet = ""
        if response is not None:
            snippet = response.text[:500].replace("\n", " ")
        msg = (
            f"OTOL request failed at endpoint '{endpoint}'. "
            f"status={status!r}. "
            f"error={exc}. response_snippet={snippet!r}"
        )
        return ToytreeError(msg)

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        """Return deterministic hash of a request payload."""
        dumped = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

    def _cache_path(self, namespace: str, payload: dict[str, Any]) -> Path:
        """Return cache path for namespace and payload."""
        key = self._hash_payload(payload)
        return self.cache_dir / namespace / f"{key}.pkl"

    def _cache_read(self, path: Path) -> Any | None:
        """Read cache entry if available."""
        if not self.cache or not path.exists():
            return None
        with path.open("rb") as ihandle:
            return pickle.load(ihandle)

    def _cache_write(self, path: Path, data: Any) -> None:
        """Write cache entry."""
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
        """POST JSON payload and return parsed JSON with consistent handling."""
        cache_path = self._cache_path(
            cache_namespace, {"endpoint": endpoint, "payload": payload}
        )
        if use_cache:
            cached = self._cache_read(cache_path)
            if cached is not None:
                return cached

        url = urljoin(self.base_url, endpoint)
        response: requests.Response | None = None
        try:
            response = self.session.post(url=url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if use_cache:
                self._cache_write(cache_path, data)
            return data
        except Exception as exc:
            raise self._error_from_response(endpoint, exc, response) from exc

    def _request_text(
        self, url: str, use_cache: bool = False, cache_namespace: str = "text"
    ) -> str:
        """GET text content with consistent handling."""
        cache_path = self._cache_path(cache_namespace, {"url": url})
        if use_cache:
            cached = self._cache_read(cache_path)
            if cached is not None:
                return str(cached)

        response: requests.Response | None = None
        try:
            response = self.session.get(url=url, timeout=self.timeout)
            response.raise_for_status()
            text = response.text
            if use_cache:
                self._cache_write(cache_path, text)
            return text
        except Exception as exc:
            raise self._error_from_response(url, exc, response) from exc

    @property
    def session(self) -> Session:
        """Return active requests session, lazily creating one if needed."""
        if self._session is None:
            self._session = self._build_session(
                self.max_retries,
                self.backoff_factor,
            )
        return self._session

    @staticmethod
    def _to_list(query: FLEX_QUERY) -> list[str | int]:
        """Normalize query argument to a list preserving order."""
        if isinstance(query, (str, int)):
            return [query]
        return list(query)

    def resolve_names(
        self,
        query: Sequence[str],
        do_approximate_matching: bool = False,
        context: str | None = None,
        include_synonyms: bool = True,
        on_unresolved: Literal["raise", "warn", "ignore"] = "ignore",
        on_ambiguous: Literal["keep", "first", "raise"] = "keep",
    ) -> pd.DataFrame:
        """Resolve taxon names through OTOL TNRS and return a standardized table.

        Parameters
        ----------
        query : Sequence[str]
            Taxon-name strings to resolve.
        do_approximate_matching : bool, default=False
            If True, enable fuzzy matching in TNRS.
        context : str or None, default=None
            Optional TNRS context.
        include_synonyms : bool, default=True
            If False, synonym matches are filtered before choosing status.
        on_unresolved : {"raise", "warn", "ignore"}, default="ignore"
            Behavior when any final row is unmatched or ambiguous.
        on_ambiguous : {"keep", "first", "raise"}, default="keep"
            Behavior when TNRS returns multiple matches for a query.

        Returns
        -------
        pandas.DataFrame
            Columns: ``query``, ``status``, ``matched_name``, ``ott_id``,
            ``is_synonym``, ``reason``. ``ott_id`` uses nullable integer dtype
            (``Int64``), with missing entries stored as ``pd.NA``.

        Raises
        ------
        ToytreeError
            If configured to raise on ambiguity or unresolved rows.

        Examples
        --------
        >>> client = _OTOLClient()
        >>> table = client.resolve_names(
        ...     ["Canis lupus", "Panthera leo"],
        ...     context="Animals",
        ... )
        >>> table = client.resolve_names(
        ...     ["A namestring that may be ambiguous"],
        ...     on_ambiguous="first",
        ...     on_unresolved="warn",
        ... )
        """
        if on_unresolved not in ("raise", "warn", "ignore"):
            raise ToytreeError(f"invalid on_unresolved option: {on_unresolved!r}")
        if on_ambiguous not in ("keep", "first", "raise"):
            raise ToytreeError(f"invalid on_ambiguous option: {on_ambiguous!r}")

        payload: dict[str, Any] = {"names": list(query)}
        if do_approximate_matching:
            payload["do_approximate_matching"] = True
        if context is not None:
            payload["context"] = context

        data = self._request_json(
            "tnrs/match_names",
            payload,
            use_cache=True,
            cache_namespace="matches",
        )
        if "results" not in data or not isinstance(data["results"], list):
            raise ToytreeError("unexpected response shape from tnrs/match_names")

        rows: list[dict[str, Any]] = []
        for item in data["results"]:
            qname = str(item.get("name", ""))
            matches = list(item.get("matches", []))
            # Apply synonym filtering before deciding if a query is unresolved
            # or ambiguous so downstream status reflects the user's intent.
            if not include_synonyms:
                matches = [m for m in matches if not bool(m.get("is_synonym", False))]

            if not matches:
                rows.append(
                    {
                        "query": qname,
                        "status": "unmatched",
                        "matched_name": None,
                        "ott_id": pd.NA,
                        "is_synonym": None,
                        "reason": "no_match",
                    }
                )
                continue

            if len(matches) > 1:
                if on_ambiguous == "raise":
                    raise ToytreeError(
                        f"TNRS ambiguous resolution failed for {qname!r}."
                    )
                # "first" resolves the row deterministically while preserving
                # traceability in `reason` (e.g., resolved_first_of_3).
                if on_ambiguous == "first":
                    match = matches[0]
                    taxon = match.get("taxon", {})
                    rows.append(
                        {
                            "query": qname,
                            "status": "matched",
                            "matched_name": match.get(
                                "matched_name", taxon.get("name")
                            ),
                            "ott_id": int(taxon["ott_id"])
                            if "ott_id" in taxon
                            else pd.NA,
                            "is_synonym": bool(match.get("is_synonym", False)),
                            "reason": f"resolved_first_of_{len(matches)}",
                        }
                    )
                    continue
                rows.append(
                    {
                        "query": qname,
                        "status": "ambiguous",
                        "matched_name": None,
                        "ott_id": pd.NA,
                        "is_synonym": None,
                        "reason": f"{len(matches)}_matches",
                    }
                )
                continue

            match = matches[0]
            taxon = match.get("taxon", {})
            rows.append(
                {
                    "query": qname,
                    "status": "matched",
                    "matched_name": match.get("matched_name", taxon.get("name")),
                    "ott_id": int(taxon["ott_id"]) if "ott_id" in taxon else pd.NA,
                    "is_synonym": bool(match.get("is_synonym", False)),
                    "reason": "ok",
                }
            )

        table = pd.DataFrame(rows)
        # Preserve integer IDs while allowing missing values for unresolved rows.
        table["ott_id"] = pd.array(table["ott_id"], dtype="Int64")

        if (table["status"] != "matched").any() and on_unresolved in ("raise", "warn"):
            amb = int((table["status"] == "ambiguous").sum())
            unm = int((table["status"] == "unmatched").sum())
            message = f"TNRS resolution has unresolved rows: {amb} ambiguous, {unm} unmatched."
            if on_unresolved == "raise":
                raise ToytreeError(message)
            warnings.warn(message, stacklevel=2)
        return table

    def _query_to_node_ids(self, query: FLEX_QUERY) -> list[str]:
        """Convert mixed queries to OTOL node IDs preserving input order."""
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
            table = self.resolve_names(names, on_unresolved="raise")
            for idx, ott_id in zip(name_positions, table["ott_id"].tolist()):
                out[idx] = f"ott{int(ott_id)}"
        return out

    def get_matched_names(
        self,
        query: str | Sequence[str],
        do_approximate_matching: bool = False,
        context: str | None = None,
    ) -> dict[str, Any]:
        """Return raw TNRS JSON for one or more taxon-name queries."""
        names = [query] if isinstance(query, str) else list(query)
        payload: dict[str, Any] = {"names": names}
        if do_approximate_matching:
            payload["do_approximate_matching"] = True
        if context is not None:
            payload["context"] = context
        return self._request_json("tnrs/match_names", payload)

    def get_taxon_id_table(
        self,
        query: str | Sequence[str],
        accept_synonym: bool = False,
    ) -> pd.DataFrame:
        """Return a table of matched taxa and OTT IDs."""
        names = [query] if isinstance(query, str) else list(query)
        return self.resolve_names(
            names,
            include_synonyms=accept_synonym,
            on_unresolved="ignore",
        )

    def get_taxonomy(self) -> dict[str, Any]:
        """Return metadata about the current OTOL taxonomy build."""
        return self._request_json(
            "taxonomy/about", {}, use_cache=True, cache_namespace="taxonomy"
        )

    def get_taxon_info(
        self,
        query: str | int | dict[str, int],
        include_lineage: bool = False,
        include_children: bool = False,
        include_terminal_descendants: bool = False,
    ) -> dict[str, Any]:
        """Return taxonomy information for one OTOL taxon."""
        if isinstance(query, dict):
            key = next(iter(query))
            payload: dict[str, Any] = {"source_id": f"{key}:{query[key]}"}
        elif isinstance(query, int):
            payload = {"ott_id": query}
        else:
            node_id = self._query_to_node_ids(query)[0]
            if node_id.startswith("ott"):
                payload = {"ott_id": int(node_id[3:])}
            else:
                nearest = self.get_node_info(node_id, include_lineage=False)[0].get(
                    "taxon"
                )
                if not nearest or "ott_id" not in nearest:
                    raise ToytreeError(
                        f"could not resolve taxon info from node ID: {node_id}"
                    )
                payload = {"ott_id": int(nearest["ott_id"])}

        payload.update(
            {
                "include_children": include_children,
                "include_lineage": include_lineage,
                "include_terminal_descendants": include_terminal_descendants,
            }
        )
        return self._request_json("taxonomy/taxon_info", payload)

    def get_taxon_lineage(
        self,
        query: str | int,
        full_json: bool = False,
        rank_only: bool = False,
        max_height: int | None = None,
        top: str | None = None,
    ) -> dict[str, str] | list[dict[str, Any]]:
        """Return lineage of a taxon query from OTOL."""
        info = self.get_taxon_info(query, include_lineage=True)
        lineage = list(info.get("lineage", []))

        # limit how far deep in evolution we show
        if top is not None:
            stop = str(top).lower()
            cropped: list[dict[str, Any]] = []
            for entry in lineage:
                cropped.append(entry)
                if (
                    str(entry.get("rank", "")).lower() == stop
                    or str(entry.get("unique_name", "")).lower() == stop
                ):
                    break
            lineage = cropped

        # prune out unranked lineages
        if rank_only:
            lineage = [entry for entry in lineage if entry.get("rank") != "no rank"]
        else:
            no_rank_idx = 1
            for entry in lineage:
                if entry.get("rank") == "no rank":
                    entry["rank"] = f"no_rank_{no_rank_idx}"
                    no_rank_idx += 1

        # of the remaining lineages optionally only show the last X hits
        if max_height is not None:
            lineage = lineage[:max_height]

        # return options
        if full_json:
            return lineage
        return {str(entry["rank"]): str(entry["unique_name"]) for entry in lineage}

    def get_taxon_parent(
        self,
        query: str | int,
        full_json: bool = False,
        rank_only: bool = False,
    ) -> dict[str, Any]:
        """Return the nearest parent lineage entry for a query."""
        lineage = self.get_taxon_lineage(query, full_json=True, rank_only=rank_only)
        if not lineage:
            raise ToytreeError(f"no lineage records found for query: {query!r}")
        parent = lineage[0]
        if full_json:
            return parent
        return {"rank": parent.get("rank"), "name": parent.get("unique_name")}

    def get_taxon_descendants(
        self,
        query: str | int,
        min_rank: str = "genus",
        terminal_only: bool = False,
    ) -> list[int]:
        """Return descendant OTT IDs at or above a minimum rank."""
        rank = str(min_rank).lower()
        if rank not in RANKS:
            raise ToytreeError(f"invalid min_rank: {min_rank!r}")

        node_id = self._query_to_node_ids(query)[0]
        queue: list[int | str] = [node_id]
        out: list[int] = []

        while queue:
            current = queue.pop(0)
            info = self.get_taxon_info(current, include_children=True)
            for child in info.get("children", []):
                if child.get("flags"):
                    continue
                ott_id = int(child["ott_id"])
                child_rank = str(child.get("rank", ""))
                if child_rank == rank:
                    out.append(ott_id)
                else:
                    queue.append(ott_id)
                    if not terminal_only:
                        out.append(ott_id)
        return out

    def get_taxon_id(self, query: str) -> int:
        """Return resolved OTT ID for a single taxon name."""
        table = self.resolve_names([query], on_unresolved="raise")
        return int(table.iloc[0]["ott_id"])

    def get_node_info(
        self,
        query: FLEX_QUERY,
        include_lineage: bool = False,
    ) -> list[dict[str, Any]]:
        """Return node-info payload for one or more OTOL node IDs."""
        node_ids = self._query_to_node_ids(query)
        data = self._request_json(
            "tree_of_life/node_info",
            {"node_ids": node_ids, "include_lineage": include_lineage},
        )
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "node_id" in data:
            return [data]
        if (
            isinstance(data, dict)
            and "results" in data
            and isinstance(data["results"], list)
        ):
            return data["results"]
        raise ToytreeError("unexpected response shape from tree_of_life/node_info")

    def get_node_id(self, query: str | int) -> str:
        """Return OTOL node ID for a single taxon query."""
        return str(self.get_node_info(query)[0]["node_id"])

    def get_mrca_info(self, query: FLEX_QUERY) -> dict[str, Any]:
        """Return MRCA payload for a query set."""
        node_ids = self._query_to_node_ids(query)
        return self._request_json("tree_of_life/mrca", {"node_ids": node_ids})

    def get_mrca_node_id(self, query: FLEX_QUERY) -> str:
        """Return MRCA node ID for a query set."""
        return str(self.get_mrca_info(query)["mrca"]["node_id"])

    @staticmethod
    def _extract_mrca_taxon_id(payload: dict[str, Any]) -> int:
        """Extract a taxon OTT ID from variable MRCA payload shapes."""
        # OTOL responses vary. Some include mrca.taxon (single query / named
        # node cases), while others include nearest_taxon (multi-query cases).
        mrca_taxon = payload.get("mrca", {}).get("taxon", {})
        if "ott_id" in mrca_taxon:
            return int(mrca_taxon["ott_id"])
        nearest = payload.get("nearest_taxon", {})
        if "ott_id" in nearest:
            return int(nearest["ott_id"])
        raise ToytreeError(
            "could not extract taxon ott_id from MRCA payload; expected "
            "mrca.taxon.ott_id or nearest_taxon.ott_id."
        )

    def get_mrca_taxon_id(self, query: FLEX_QUERY) -> int:
        """Return nearest taxon OTT ID to MRCA for a query set."""
        payload = self.get_mrca_info(query)
        return self._extract_mrca_taxon_id(payload)

    def get_synthetic_subtree(
        self,
        query: int | str,
        full_json: bool = False,
        **kwargs: Any,
    ) -> str | dict[str, Any]:
        """Return Newick subtree below one OTOL node."""
        node_id = self._query_to_node_ids(query)[0]
        info = self.get_node_info(node_id)[0]
        if int(info.get("num_tips", 0)) >= 25_000:
            raise ToytreeError(
                "OTOL subtree endpoint does not support >=25K tips; use induced subtree instead."
            )

        payload = {"node_id": node_id} | kwargs
        data = self._request_json("tree_of_life/subtree", payload)
        if "newick" not in data:
            raise ToytreeError("unexpected response shape from tree_of_life/subtree")
        if full_json:
            return data
        return str(data["newick"])

    def induced_subtree_from_ott_ids(
        self,
        ott_ids: Sequence[int],
        full_json: bool = False,
        label_format: str = "name_and_id",
        insert_broken_nodes: bool = False,
    ) -> str | dict[str, Any]:
        """Return induced subtree for OTT IDs."""
        node_ids = [f"ott{int(i)}" for i in ott_ids]
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

        if insert_broken_nodes and data.get("broken"):
            from toytree import tree as parse_tree
            from toytree.core import Node

            tre = parse_tree(data["newick"])
            for ott_key, val in data["broken"].items():
                node = tre.get_nodes("~" + str(val))[0]
                name = str(self.get_taxon_info(str(ott_key)).get("name", ott_key))
                child = Node(f"broken_{name}_{node.name}", dist=1.0)
                child.broken = True
                node._add_child(child)
            tre._update()
            data["newick"] = tre.write(internal_labels="name", dist_formatter=None)

        if full_json:
            return data
        return str(data["newick"])

    def get_synthetic_induced_subtree(
        self,
        query: Sequence[int | str],
        full_json: bool = False,
        label_format: str = "name_and_id",
        insert_broken_nodes: bool = False,
    ) -> str | dict[str, Any]:
        """Return induced subtree for a mixed query list."""
        node_ids = self._query_to_node_ids(query)
        ott_ids: list[int] = []
        for node_id in node_ids:
            if node_id.startswith("ott"):
                ott_ids.append(int(node_id[3:]))
            else:
                info = self.get_node_info(node_id)[0]
                taxon = info.get("taxon")
                if not taxon or "ott_id" not in taxon:
                    raise ToytreeError(f"could not map node ID to ott ID: {node_id}")
                ott_ids.append(int(taxon["ott_id"]))

        return self.induced_subtree_from_ott_ids(
            ott_ids=ott_ids,
            full_json=full_json,
            label_format=label_format,
            insert_broken_nodes=insert_broken_nodes,
        )

    @staticmethod
    def parse_ott_ids_from_tip_labels(labels: Sequence[str]) -> list[int]:
        """Extract OTT IDs from labels containing ``ott12345`` tokens."""
        patt = re.compile(r"ott(\d+)")
        out: list[int] = []
        for label in labels:
            match = patt.search(str(label))
            if match:
                out.append(int(match.group(1)))
        return out

    def get_taxonomy_induced_subtree(
        self,
        query: str | int,
        min_rank: str = "genus",
    ) -> ToyTree:
        """Return a taxonomy-derived subtree for descendants at/above min_rank."""
        rank = str(min_rank).lower()
        if rank not in RANKS:
            raise ToytreeError(f"invalid min_rank: {min_rank!r}")

        from toytree.core import Node, ToyTree

        # find the closest taxonomic named node to the query
        # mrca = self.get_mrca_info(query)
        # nearest = mrca.get("mrca", {}).get("taxon") or mrca.get("nearest_taxon")
        # if not nearest or "ott_id" not in nearest:
        #     raise ToytreeError(
        #         "could not infer root taxon for taxonomy-induced subtree."
        #     )

        # create root Node and name it with the mrca OTT_ID
        # ott_id = int(nearest["ott_id"])
        # Start from the API node query field to anchor descendants.
        ott_id = self.get_node_info(query)[0]["query"]
        root = Node(name=ott_id)
        nodes = {ott_id: root}
        queue = [ott_id]

        # add all its descendant nodes
        while queue:
            current = queue.pop(0)
            info = self.get_taxon_info(current, include_children=True)
            parent = nodes[current]
            parent._taxon = info.get("name")
            for child in info.get("children", []):
                if child.get("flags"):
                    continue
                c_ott = int(child["ott_id"])
                node = Node(name=c_ott, dist=1.0)
                node._taxon = child.get("name")
                parent._add_child(node)
                nodes[c_ott] = node
                if str(child.get("rank")) != rank:
                    queue.append(c_ott)

        # make into a ToyTree and set names
        tree = ToyTree(root)
        tree.set_node_data(
            "name", {i: f"{i._taxon}_{i._name}" for i in tree}, inplace=True
        )
        return tree

    def get_supporting_studies(self, query: FLEX_QUERY) -> list[str]:
        """Return study IDs supporting synthetic-tree relationships for query."""
        if isinstance(query, (str, int)):
            data = self.get_synthetic_subtree(query, full_json=True)
        else:
            data = self.get_synthetic_induced_subtree(query, full_json=True)
        return list(data.get("supporting_studies", []))

    def get_study_or_tree(
        self,
        study_id: str | int,
        tree_id: str | int | None = None,
        label_format: str | None = None,
    ) -> str:
        """Return Newick/Nexus content for an OTOL study or a specific tree."""
        suffix = ".tre"
        if label_format == "otttaxonname":
            label = "?tip_label=ot:otttaxonname"
        elif label_format == "ottid":
            label = "?tip_label=ot:ottid"
        else:
            label = "?tip_label=ot:originallabel"

        if tree_id is not None:
            tid = int(str(tree_id).lstrip("tree"))
            url = urljoin(
                self.base_url, f"study/{study_id}/tree/tree{tid}{suffix}/{label}"
            )
        else:
            url = urljoin(self.base_url, f"study/{study_id}{suffix}/{label}")

        text = self._request_text(url)
        if text.startswith("'") and text.endswith("'"):
            return text[1:-1]
        return text


_DEFAULT_CLIENT: _OTOLClient | None = None


def _get_default_client() -> _OTOLClient:
    """Return the module default client, creating it on first use."""
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
    """Configure the module-level OTOL client."""
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
    """Reset the module-level OTOL client to lazy defaults."""
    global _DEFAULT_CLIENT
    _DEFAULT_CLIENT = None


def match_names(
    query: Sequence[str],
    approximate: bool = False,
    context: str | None = None,
    include_synonyms: bool = True,
    on_unresolved: Literal["raise", "warn", "ignore"] = "ignore",
    on_ambiguous: Literal["keep", "first", "raise"] = "keep",
    output: Literal["table", "raw"] = "table",
) -> pd.DataFrame | dict[str, Any]:
    """Resolve taxon names against TNRS and return a table or raw JSON."""
    client = _get_default_client()
    if output == "raw":
        if (
            include_synonyms is not True
            or on_unresolved != "ignore"
            or on_ambiguous != "keep"
        ):
            raise ToytreeError(
                "include_synonyms/on_unresolved/on_ambiguous are only valid when output='table'."
            )
        return client.get_matched_names(
            query=query,
            do_approximate_matching=approximate,
            context=context,
        )
    if output != "table":
        raise ToytreeError(f"invalid output option: {output!r}")
    return client.resolve_names(
        query=query,
        do_approximate_matching=approximate,
        context=context,
        include_synonyms=include_synonyms,
        on_unresolved=on_unresolved,
        on_ambiguous=on_ambiguous,
    )


def taxon_id(query: str) -> int:
    """Return resolved OTT ID for one taxon-name query."""
    return _get_default_client().get_taxon_id(query=query)


def taxonomy() -> dict[str, Any]:
    """Return metadata about the current OTOL taxonomy."""
    return _get_default_client().get_taxonomy()


def taxon_info(
    query: str | int | dict[str, int],
    include_lineage: bool = False,
    include_children: bool = False,
    include_terminal_descendants: bool = False,
) -> dict[str, Any]:
    """Return taxonomy information for a single taxon query."""
    return _get_default_client().get_taxon_info(
        query=query,
        include_lineage=include_lineage,
        include_children=include_children,
        include_terminal_descendants=include_terminal_descendants,
    )


def taxon_lineage(
    query: str | int,
    full_json: bool = False,
    rank_only: bool = False,
    max_height: int | None = None,
    top: str | None = None,
) -> dict[str, str] | list[dict[str, Any]]:
    """Return lineage records for a taxon query."""
    return _get_default_client().get_taxon_lineage(
        query=query,
        full_json=full_json,
        rank_only=rank_only,
        max_height=max_height,
        top=top,
    )


def taxon_parent(
    query: str | int,
    full_json: bool = False,
    rank_only: bool = False,
) -> dict[str, Any]:
    """Return nearest parent lineage entry for a taxon query."""
    return _get_default_client().get_taxon_parent(
        query=query,
        full_json=full_json,
        rank_only=rank_only,
    )


def taxon_descendants(
    query: str | int,
    min_rank: str = "genus",
    terminal_only: bool = False,
) -> list[int]:
    """Return descendant OTT IDs for a taxon query."""
    return _get_default_client().get_taxon_descendants(
        query=query,
        min_rank=min_rank,
        terminal_only=terminal_only,
    )


def node_info(query: FLEX_QUERY, include_lineage: bool = False) -> list[dict[str, Any]]:
    """Return node-info payload for one or more queries."""
    return _get_default_client().get_node_info(
        query=query,
        include_lineage=include_lineage,
    )


def node_id(query: str | int) -> str:
    """Return OTOL node ID for one query."""
    return _get_default_client().get_node_id(query=query)


def mrca(query: FLEX_QUERY) -> dict[str, Any]:
    """Return MRCA payload for a set of queries."""
    return _get_default_client().get_mrca_info(query=query)


def mrca_node_id(query: FLEX_QUERY) -> str:
    """Return MRCA node ID for a set of queries."""
    return _get_default_client().get_mrca_node_id(query=query)


def mrca_taxon_id(query: FLEX_QUERY) -> int:
    """Return nearest taxon OTT ID to MRCA for a query set."""
    return _get_default_client().get_mrca_taxon_id(query=query)


def synthetic_subtree(
    query: int | str,
    full_json: bool = False,
    extra_params: dict[str, Any] | None = None,
) -> str | dict[str, Any]:
    """Return synthetic subtree below one OTOL node/taxon query."""
    return _get_default_client().get_synthetic_subtree(
        query=query,
        full_json=full_json,
        **({} if extra_params is None else extra_params),
    )


def induced_subtree(
    query: Sequence[int | str],
    full_json: bool = False,
    label_format: str = "name_and_id",
    insert_broken_nodes: bool = False,
) -> str | dict[str, Any]:
    """Return induced subtree for mixed query values."""
    return _get_default_client().get_synthetic_induced_subtree(
        query=query,
        full_json=full_json,
        label_format=label_format,
        insert_broken_nodes=insert_broken_nodes,
    )


def taxonomy_subtree(query: str | int, min_rank: str = "genus") -> ToyTree:
    """Return a taxonomy-derived subtree under a query."""
    return _get_default_client().get_taxonomy_induced_subtree(
        query=query,
        min_rank=min_rank,
    )


def supporting_studies(query: FLEX_QUERY) -> list[str]:
    """Return study IDs that support subtree relationships."""
    return _get_default_client().get_supporting_studies(query=query)


def study_tree(
    study_id: str | int,
    tree_id: str | int | None = None,
    label_format: str | None = None,
) -> str:
    """Return Newick/Nexus text for an OTOL study or one tree in that study."""
    return _get_default_client().get_study_or_tree(
        study_id=study_id,
        tree_id=tree_id,
        label_format=label_format,
    )
