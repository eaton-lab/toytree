#!/usr/bin/env python
# ruff: noqa: E501,D401

"""TimeTree REST API helpers for divergence-time queries.

This module provides low-level JSON fetch methods for TimeTree endpoints and a
high-level helper, ``get_timetree_node_ages``, that estimates divergence times
for internal nodes on a ``ToyTree``.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import sys
import tempfile
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path
from typing import Any, Literal, Sequence
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from toytree import ToyTree
from toytree.utils import ToytreeError

URI = "http://timetree.temple.edu/api/"
HEADERS = {"User-Agent": "toytree"}

__all__ = [
    "configure_timetree_client",
    "reset_timetree_client",
    "fetch_json_timetree_pairwise",
    "fetch_json_timetree_mrca",
    "get_timetree_node_ages",
]


class _TimeTreeClient:
    """Private TimeTree client for transport, retries, and cache."""

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
            else Path(tempfile.gettempdir()) / "toytree_timetree_cache"
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
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.headers.update(HEADERS)
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
            f"TimeTree request failed at endpoint '{endpoint}'. "
            f"status={status!r}. error={exc}. response_snippet={snippet!r}"
        )

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        """Return deterministic hash of cache metadata."""
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
        use_cache: bool = True,
        cache_namespace: str = "json",
    ) -> dict[str, Any]:
        """GET endpoint and return parsed JSON payload."""
        cache_path = self._cache_path(cache_namespace, {"endpoint": endpoint})
        if use_cache:
            cached = self._cache_read(cache_path)
            if cached is not None:
                return cached

        response: requests.Response | None = None
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        try:
            response = self.session.get(url=url, timeout=self.timeout)
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
    def _coerce_ncbi_ids(ncbi_ids: Sequence[int], min_items: int = 2) -> list[int]:
        """Return ordered unique NCBI IDs validated as positive integers."""
        seen: set[int] = set()
        out: list[int] = []
        for raw in ncbi_ids:
            try:
                val = int(raw)
            except Exception as exc:
                raise ToytreeError(f"invalid NCBI ID value: {raw!r}") from exc
            if val <= 0:
                raise ToytreeError(f"NCBI IDs must be positive integers, got {val!r}.")
            if val in seen:
                continue
            seen.add(val)
            out.append(val)
        if len(out) < min_items:
            raise ToytreeError(
                f"at least {min_items} unique NCBI IDs are required, got {len(out)}."
            )
        return out

    def fetch_json_timetree_pairwise(
        self,
        taxon_a_id: int,
        taxon_b_id: int,
        endpoint: Literal["summaryjson", "json"] = "summaryjson",
    ) -> dict[str, Any]:
        """Fetch raw pairwise TimeTree response."""
        a_id, b_id = self._coerce_ncbi_ids([taxon_a_id, taxon_b_id], min_items=2)
        path = f"pairwise/{a_id}/{b_id}/{endpoint}"
        return self._request_json(path, use_cache=True, cache_namespace="pairwise")

    def fetch_json_timetree_mrca(
        self,
        ncbi_ids: Sequence[int],
        endpoint: Literal["json", "summaryjson"] = "json",
    ) -> dict[str, Any]:
        """Fetch raw TimeTree MRCA response for a set of NCBI IDs."""
        ids = self._coerce_ncbi_ids(ncbi_ids, min_items=2)
        query = "+".join(str(i) for i in ids)
        path = f"mrca/id/{query}/{endpoint}"
        return self._request_json(path, use_cache=True, cache_namespace="mrca")

    @staticmethod
    def _as_float(value: Any) -> float:
        """Return value cast to float or NaN if conversion fails."""
        if value is None or pd.isna(value):
            return float("nan")
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return float("nan")
        try:
            return float(value)
        except Exception:
            return float("nan")

    @staticmethod
    def _as_int(value: Any) -> int | pd.NA:
        """Return value cast to int or pandas.NA if conversion fails."""
        if value is None or pd.isna(value):
            return pd.NA
        try:
            return int(value)
        except Exception:
            return pd.NA

    def _extract_age_data(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return standardized age/metadata fields from a TimeTree payload."""
        age = self._as_float(payload.get("precomputed_age"))
        if pd.isna(age) or age <= 0:
            adjusted = self._as_float(payload.get("adjusted_age"))
            if not pd.isna(adjusted) and adjusted > 0:
                age = adjusted
            else:
                age = float("nan")
        return {
            "age": age,
            "ci_low": self._as_float(payload.get("precomputed_ci_low")),
            "ci_high": self._as_float(payload.get("precomputed_ci_high")),
            "all_total": self._as_int(payload.get("all_total")),
            "taxon_id": self._as_int(payload.get("taxon_id")),
            "mrca_ttid": self._as_int(payload.get("mrca_ttid")),
        }

    @staticmethod
    def _coerce_ncbi_id(value: Any, context: str) -> int:
        """Return one positive integer NCBI ID or raise ToytreeError."""
        if value is None or pd.isna(value):
            raise ToytreeError(f"{context} has missing ncbi_id.")
        try:
            ncbi_id = int(value)
        except Exception as exc:
            raise ToytreeError(f"{context} has invalid ncbi_id: {value!r}") from exc
        if ncbi_id <= 0:
            raise ToytreeError(f"{context} has non-positive ncbi_id: {ncbi_id!r}")
        return ncbi_id

    def _get_tree_ncbi_map(self, tree: ToyTree) -> dict[int, int]:
        """Return {node_idx: ncbi_id} parsed from tree feature data."""
        if "ncbi_id" not in tree.features:
            raise ToytreeError(
                "tree is missing required 'ncbi_id' feature. "
                "Provide this feature on nodes before calling this method."
            )
        series = tree.get_node_data("ncbi_id")
        out: dict[int, int] = {}
        for nidx, value in enumerate(series.tolist()):
            if value is None or pd.isna(value):
                continue
            out[nidx] = self._coerce_ncbi_id(value, f"node idx {nidx}")
        return out

    def _coerce_override_series(
        self,
        tree: ToyTree,
        data: pd.Series | None,
    ) -> dict[int, int]:
        """Return call-scoped override mapping from Series indexed by node idx."""
        if data is None:
            return {}
        if not isinstance(data, pd.Series):
            raise ToytreeError("data must be a pandas Series indexed by node idx.")
        if data.index.has_duplicates:
            raise ToytreeError("data Series index contains duplicate node idx values.")

        out: dict[int, int] = {}
        for raw_idx, value in data.items():
            try:
                nidx = int(raw_idx)
            except Exception as exc:
                raise ToytreeError(
                    f"data Series index must contain integer node idx labels, got {raw_idx!r}."
                ) from exc
            if nidx < 0 or nidx >= tree.nnodes:
                raise ToytreeError(
                    f"data Series index contains out-of-range node idx: {nidx!r}."
                )
            if value is None or pd.isna(value):
                continue
            out[nidx] = self._coerce_ncbi_id(value, f"override node idx {nidx}")
        return out

    def _get_node_ncbi_map(
        self,
        tree: ToyTree,
        data: pd.Series | None,
    ) -> dict[int, int]:
        """Return merged node map, with data overrides replacing tree feature values."""
        node_to_ncbi = self._get_tree_ncbi_map(tree)
        overrides = self._coerce_override_series(tree, data)
        node_to_ncbi.update(overrides)
        return node_to_ncbi

    def _get_child_candidate_ids(
        self,
        child,
        node_to_ncbi: dict[int, int],
        limit: int,
    ) -> list[int]:
        """Return ordered candidate IDs for one child clade.

        If the child node itself has an ID it is used exclusively; descendant
        sampling is skipped for that child.
        """
        if child.idx in node_to_ncbi:
            return [node_to_ncbi[child.idx]]

        seen: set[int] = set()
        out: list[int] = []
        # levelorder traversal gives nearest descendants first.
        for desc in child.iter_descendants("levelorder"):
            ncbi_id = node_to_ncbi.get(desc.idx)
            if ncbi_id is None or ncbi_id in seen:
                continue
            seen.add(ncbi_id)
            out.append(ncbi_id)
            if len(out) >= max(1, int(limit)):
                break
        return out

    @staticmethod
    def _build_pair_candidates(
        child_groups: list[list[int]],
        max_pairs: int,
    ) -> list[tuple[int, int]]:
        """Return deterministic cross-child pair candidates capped at max_pairs."""
        out: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        for i, j in combinations(range(len(child_groups)), 2):
            for left, right in product(child_groups[i], child_groups[j]):
                if left == right:
                    continue
                pair = (left, right) if left < right else (right, left)
                if pair in seen:
                    continue
                seen.add(pair)
                out.append(pair)
                if len(out) >= max_pairs:
                    return out
        return out

    def _query_pairwise_node(
        self,
        node_idx: int,
        child_groups: list[list[int]],
        max_pairs: int,
    ) -> dict[str, Any]:
        """Query pairwise endpoint for one node and return standardized row."""
        row = {
            "node_idx": node_idx,
            "endpoint": "pairwise",
            "query_ncbi_ids": tuple(),
            "n_query_ids": 0,
            "age": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
            "all_total": pd.NA,
            "taxon_id": pd.NA,
            "mrca_ttid": pd.NA,
            "status": "unresolved",
            "reason": "insufficient_child_ids",
            "n_pairs_attempted": 0,
            "n_pairs_success": 0,
            "query_pairs_used": tuple(),
            "pairwise_ages": tuple(),
        }

        if len(child_groups) < 2:
            return row

        pairs = self._build_pair_candidates(child_groups, max_pairs=max_pairs)
        if not pairs:
            return row
        row["query_ncbi_ids"] = pairs[0]
        row["n_query_ids"] = 2

        success_pairs: list[tuple[int, int]] = []
        success_ages: list[float] = []
        success_lows: list[float] = []
        success_highs: list[float] = []
        success_all_total: list[int] = []

        for pair in pairs[:max_pairs]:
            row["n_pairs_attempted"] += 1
            try:
                payload = self.fetch_json_timetree_pairwise(
                    pair[0],
                    pair[1],
                    endpoint="summaryjson",
                )
                parsed = self._extract_age_data(payload)
                age = parsed["age"]
                if pd.isna(age):
                    continue

                success_pairs.append(pair)
                success_ages.append(float(age))
                if not pd.isna(parsed["ci_low"]):
                    success_lows.append(float(parsed["ci_low"]))
                if not pd.isna(parsed["ci_high"]):
                    success_highs.append(float(parsed["ci_high"]))
                if parsed["all_total"] is not pd.NA:
                    success_all_total.append(int(parsed["all_total"]))
            except Exception:
                continue

        if not success_ages:
            row["reason"] = "missing_age"
            return row

        row["status"] = "ok"
        row["reason"] = "ok"
        row["n_pairs_success"] = len(success_ages)
        row["query_pairs_used"] = tuple(success_pairs)
        row["pairwise_ages"] = tuple(success_ages)
        row["age"] = float(np.median(np.asarray(success_ages, dtype=float)))
        if success_lows:
            row["ci_low"] = float(np.min(np.asarray(success_lows, dtype=float)))
        if success_highs:
            row["ci_high"] = float(np.max(np.asarray(success_highs, dtype=float)))
        if success_all_total:
            row["all_total"] = int(np.sum(np.asarray(success_all_total, dtype=int)))
        return row

    def _query_mrca_node(
        self,
        node_idx: int,
        child_groups: list[list[int]],
    ) -> dict[str, Any]:
        """Query MRCA endpoint for one node and return standardized row."""
        query_ids: list[int] = []
        for group in child_groups:
            if not group:
                continue
            query_ids.append(group[0])
        query_ids = list(dict.fromkeys(query_ids))

        row = {
            "node_idx": node_idx,
            "endpoint": "mrca",
            "query_ncbi_ids": tuple(query_ids),
            "n_query_ids": len(query_ids),
            "age": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
            "all_total": pd.NA,
            "taxon_id": pd.NA,
            "mrca_ttid": pd.NA,
            "status": "unresolved",
            "reason": "insufficient_child_ids",
            "n_pairs_attempted": 0,
            "n_pairs_success": 0,
            "query_pairs_used": tuple(),
            "pairwise_ages": tuple(),
        }

        if len(query_ids) < 2:
            return row

        try:
            payload = self.fetch_json_timetree_mrca(query_ids, endpoint="json")
            parsed = self._extract_age_data(payload)
            row.update(parsed)
            if pd.isna(row["age"]):
                row["reason"] = "missing_age"
            else:
                row["status"] = "ok"
                row["reason"] = "ok"
        except Exception as exc:
            row["status"] = "error"
            row["reason"] = str(exc)
        return row

    @staticmethod
    def _is_imputed_method(value: Any) -> bool:
        """Return True when an age_set_method indicates imputation."""
        return str(value).startswith("imputed")

    def _initialize_age_columns(self, table: pd.DataFrame) -> None:
        """Initialize age provenance columns from raw retrieval output."""
        table["age_raw"] = table["age"]
        is_calibrated = table["status"].eq("ok") & table["age"].notna()
        table["age_set_method"] = np.where(is_calibrated, "calibrated", "unresolved")

    def _resolve_conflicting_ages(
        self,
        tree: ToyTree,
        table: pd.DataFrame,
        atol: float = 1e-9,
        eps: float = 1e-6,
    ) -> None:
        """Clip descendant ages so they do not exceed their parent ages.

        If a calibrated descendant conflicts with its parent, this method first
        tries to clip within descendant CI bounds when possible. Otherwise it
        applies a deterministic forced clip just below the parent age.
        """
        ages = table["age"]
        for parent in tree.treenode.traverse("levelorder"):
            if parent.is_leaf() or parent.idx not in table.index:
                continue
            parent_age = self._as_float(ages.at[parent.idx])
            if pd.isna(parent_age):
                continue
            for child in parent.children:
                if child.is_leaf() or child.idx not in table.index:
                    continue
                child_age = self._as_float(ages.at[child.idx])
                if pd.isna(child_age):
                    continue
                if child_age <= parent_age + atol:
                    continue

                # Deterministic target is strictly below parent to avoid ties.
                max_below_parent = max(0.0, parent_age - eps)
                method = table.at[child.idx, "age_set_method"]

                # CI clipping is used only for calibrated nodes with at least one
                # finite CI bound and a feasible overlap below the parent age.
                ci_low = self._as_float(table.at[child.idx, "ci_low"])
                ci_high = self._as_float(table.at[child.idx, "ci_high"])
                ci_present = (not pd.isna(ci_low)) or (not pd.isna(ci_high))
                candidate = max_below_parent
                if not pd.isna(ci_high):
                    candidate = min(candidate, ci_high)
                ci_feasible = ci_present and (
                    pd.isna(ci_low) or (candidate + atol >= ci_low)
                )
                if self._is_imputed_method(method):
                    ci_feasible = False

                if ci_feasible:
                    ages.at[child.idx] = max(0.0, candidate)
                    table.at[child.idx, "age_set_method"] = "calibrated_ci_clipped"
                else:
                    ages.at[child.idx] = max_below_parent
                    if self._is_imputed_method(method):
                        table.at[child.idx, "age_set_method"] = "imputed_forced_clip"
                    else:
                        table.at[child.idx, "age_set_method"] = "calibrated_forced_clip"

    def _get_default_root_step(self, tree: ToyTree, ages: pd.Series) -> float:
        """Return fallback increment used when root age must be imputed."""
        deltas: list[float] = []
        for node in tree[tree.ntips :]:
            if node.up is None or node.up.idx not in ages.index:
                continue
            parent_age = self._as_float(ages.at[node.up.idx])
            child_age = self._as_float(ages.at[node.idx])
            if pd.isna(parent_age) or pd.isna(child_age):
                continue
            if parent_age > child_age:
                deltas.append(parent_age - child_age)
        if deltas:
            return float(np.median(np.asarray(deltas, dtype=float)))

        finite_ages = pd.to_numeric(ages, errors="coerce")
        finite_ages = finite_ages[np.isfinite(finite_ages.to_numpy())]
        if finite_ages.empty:
            return 1.0
        return max(1.0, float(np.median(finite_ages.to_numpy(dtype=float))) * 0.05)

    def _impute_missing_internal_ages(self, tree: ToyTree, table: pd.DataFrame) -> None:
        """Fill unresolved internal ages by edge-count interpolation."""
        if table.empty:
            return
        ages = table["age"]
        root_idx = tree.treenode.idx
        if root_idx in ages.index and pd.isna(ages.at[root_idx]):
            finite = pd.to_numeric(ages, errors="coerce")
            finite = finite[np.isfinite(finite.to_numpy())]
            step = self._get_default_root_step(tree, ages)
            if finite.empty:
                ages.at[root_idx] = step
            else:
                ages.at[root_idx] = float(finite.max()) + step
            table.at[root_idx, "age_set_method"] = "imputed_root"

        candidates: dict[int, list[float]] = defaultdict(list)
        for tip in tree[: tree.ntips]:
            chain = []
            node = tip
            while node is not None:
                chain.append(node)
                node = node.up
            chain.reverse()  # root -> ... -> tip

            chain_ages: list[float] = []
            for node in chain:
                if node.is_leaf():
                    chain_ages.append(0.0)
                else:
                    chain_ages.append(self._as_float(ages.at[node.idx]))

            anchor_pos = [i for i, age in enumerate(chain_ages) if not pd.isna(age)]
            for left_pos, right_pos in zip(anchor_pos[:-1], anchor_pos[1:]):
                if right_pos - left_pos <= 1:
                    continue
                left_age = float(chain_ages[left_pos])
                right_age = float(chain_ages[right_pos])
                edge_count = right_pos - left_pos
                step = (left_age - right_age) / edge_count
                for pos in range(left_pos + 1, right_pos):
                    node = chain[pos]
                    if node.is_leaf():
                        continue
                    if not pd.isna(ages.at[node.idx]):
                        continue
                    interp = left_age - ((pos - left_pos) * step)
                    candidates[node.idx].append(max(0.0, float(interp)))

        for nidx, values in candidates.items():
            if not values or not pd.isna(ages.at[nidx]):
                continue
            ages.at[nidx] = float(np.median(np.asarray(values, dtype=float)))
            table.at[nidx, "age_set_method"] = "imputed_edge_count"

    def get_timetree_node_ages(
        self,
        tree: ToyTree,
        endpoint: Literal["mrca", "pairwise"] = "pairwise",
        data: pd.Series | None = None,
        max_pairs: int = 3,
    ) -> pd.DataFrame:
        """Return TimeTree ages for internal nodes of a tree.

        Parameters
        ----------
        tree : ToyTree
            A tree with ``ncbi_id`` stored as node data.
        endpoint : {"pairwise", "mrca"}, default="pairwise"
            Strategy used for each internal node:
            - ``"pairwise"`` queries one or more pairwise combinations across
              child clades and combines successful age estimates.
            - ``"mrca"`` queries one MRCA request using one representative ID
              per child clade.
        data : pandas.Series or None, default=None
            Optional override mapping from node idx (Series index) to NCBI ID
            (Series values). These overrides are used for this call only and
            do not mutate tree features.
        max_pairs : int, default=3
            Maximum number of pairwise queries attempted per internal node when
            ``endpoint="pairwise"``.

        Returns
        -------
        pandas.DataFrame
            DataFrame indexed by internal-node idx labels with columns:
            ``age``, ``age_raw``, ``age_set_method``, ``ci_low``, ``ci_high``,
            ``status``, ``reason``,
            ``endpoint``, ``query_ncbi_ids``, ``n_query_ids``,
            ``all_total``, ``taxon_id``, ``mrca_ttid``,
            ``n_pairs_attempted``, ``n_pairs_success``,
            ``query_pairs_used``, and ``pairwise_ages``.
            Final ``age`` values are post-processed to avoid parent-child
            conflicts, and unresolved nodes are imputed by edge-count linear
            interpolation between calibrated anchors.

        Raises
        ------
        ToytreeError
            If inputs are malformed or node ``ncbi_id`` values are invalid.
        """
        if not isinstance(tree, ToyTree):
            raise ToytreeError("tree must be a ToyTree instance.")
        if endpoint not in ("mrca", "pairwise"):
            raise ToytreeError(f"invalid endpoint option: {endpoint!r}")
        if max_pairs < 1:
            raise ToytreeError("max_pairs must be >= 1.")
        node_to_ncbi = self._get_node_ncbi_map(tree, data)

        rows: list[dict[str, Any]] = []
        for node in tree[tree.ntips :]:
            child_groups: list[list[int]] = []
            for child in node.children:
                cands = self._get_child_candidate_ids(
                    child=child,
                    node_to_ncbi=node_to_ncbi,
                    limit=max_pairs,
                )
                if cands:
                    child_groups.append(cands)
            if endpoint == "mrca":
                row = self._query_mrca_node(
                    node_idx=node.idx, child_groups=child_groups
                )
            else:
                row = self._query_pairwise_node(
                    node_idx=node.idx,
                    child_groups=child_groups,
                    max_pairs=max_pairs,
                )
            rows.append(row)

        table = pd.DataFrame(rows)
        if table.empty:
            return pd.DataFrame(
                columns=[
                    "age",
                    "age_raw",
                    "age_set_method",
                    "ci_low",
                    "ci_high",
                    "status",
                    "reason",
                    "endpoint",
                    "query_ncbi_ids",
                    "n_query_ids",
                    "all_total",
                    "taxon_id",
                    "mrca_ttid",
                    "n_pairs_attempted",
                    "n_pairs_success",
                    "query_pairs_used",
                    "pairwise_ages",
                ]
            )

        table = table.set_index("node_idx").sort_index()
        self._initialize_age_columns(table)
        self._resolve_conflicting_ages(tree=tree, table=table)
        self._impute_missing_internal_ages(tree=tree, table=table)
        self._resolve_conflicting_ages(tree=tree, table=table)
        n_non_ok = int((table["status"] != "ok").sum())
        if n_non_ok:
            n_unresolved = int((table["status"] == "unresolved").sum())
            n_error = int((table["status"] == "error").sum())
            print(
                "TimeTree node-age retrieval completed with non-ok nodes: "
                f"{n_non_ok} total ({n_unresolved} unresolved, {n_error} errors).",
                file=sys.stderr,
            )
        return table


_DEFAULT_CLIENT: _TimeTreeClient | None = None


def _get_default_client() -> _TimeTreeClient:
    """Return module-level default TimeTree client, lazily initialized."""
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = _TimeTreeClient()
    return _DEFAULT_CLIENT


def configure_timetree_client(
    base_url: str = URI,
    timeout: float = 20.0,
    max_retries: int = 4,
    backoff_factor: float = 0.5,
    cache: bool = True,
    cache_dir: str | Path | None = None,
    session: Session | None = None,
) -> None:
    """Configure the module-level TimeTree client.

    Parameters
    ----------
    base_url : str, default="http://timetree.temple.edu/api/"
        Base URL for TimeTree requests.
    timeout : float, default=20.0
        Request timeout in seconds.
    max_retries : int, default=4
        Number of retry attempts for transient request failures.
    backoff_factor : float, default=0.5
        Retry backoff factor.
    cache : bool, default=True
        If True, enable local on-disk response caching.
    cache_dir : str | pathlib.Path | None, default=None
        Optional cache directory override.
    session : requests.Session | None, default=None
        Optional preconfigured session.

    Returns
    -------
    None

    Raises
    ------
    ToytreeError
        Not raised directly by this function.
    """
    global _DEFAULT_CLIENT
    _DEFAULT_CLIENT = _TimeTreeClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        cache=cache,
        cache_dir=cache_dir,
        session=session,
    )


def reset_timetree_client() -> None:
    """Reset module-level TimeTree client to default lazy initialization."""
    global _DEFAULT_CLIENT
    _DEFAULT_CLIENT = None


def fetch_json_timetree_pairwise(
    taxon_a_id: int,
    taxon_b_id: int,
    endpoint: Literal["summaryjson", "json"] = "summaryjson",
) -> dict[str, Any]:
    """Fetch raw pairwise JSON from TimeTree.

    Parameters
    ----------
    taxon_a_id : int
        NCBI identifier for the first taxon.
    taxon_b_id : int
        NCBI identifier for the second taxon.
    endpoint : {"summaryjson", "json"}, default="summaryjson"
        Pairwise endpoint variant.

    Returns
    -------
    dict[str, Any]
        Raw JSON response payload from TimeTree.

    Raises
    ------
    ToytreeError
        If IDs are invalid or the request fails.
    """
    return _get_default_client().fetch_json_timetree_pairwise(
        taxon_a_id=taxon_a_id,
        taxon_b_id=taxon_b_id,
        endpoint=endpoint,
    )


def fetch_json_timetree_mrca(
    ncbi_ids: Sequence[int],
    endpoint: Literal["json", "summaryjson"] = "json",
) -> dict[str, Any]:
    """Fetch raw MRCA JSON from TimeTree.

    Parameters
    ----------
    ncbi_ids : Sequence[int]
        NCBI identifiers defining the MRCA query set.
    endpoint : {"json", "summaryjson"}, default="json"
        MRCA endpoint variant.

    Returns
    -------
    dict[str, Any]
        Raw JSON response payload from TimeTree.

    Raises
    ------
    ToytreeError
        If IDs are invalid or the request fails.
    """
    return _get_default_client().fetch_json_timetree_mrca(
        ncbi_ids=ncbi_ids,
        endpoint=endpoint,
    )


def get_timetree_node_ages(
    tree: ToyTree,
    endpoint: Literal["mrca", "pairwise"] = "pairwise",
    data: pd.Series | None = None,
    max_pairs: int = 3,
) -> pd.DataFrame:
    """Return reconciled TimeTree divergence ages for internal nodes on a tree.

    Parameters
    ----------
    tree : ToyTree
        Tree object with ``ncbi_id`` saved as node feature data.
    endpoint : {"pairwise", "mrca"}, default="pairwise"
        TimeTree query strategy for each internal node.
    data : pandas.Series or None, default=None
        Optional Series override of NCBI IDs with node idx as index.
    max_pairs : int, default=3
        Maximum number of pairwise queries attempted per internal node.

    Returns
    -------
    pandas.DataFrame
        Internal-node age table indexed by ``node_idx``.
        Includes ``age_raw`` and ``age_set_method`` columns describing raw
        TimeTree retrieval values and deterministic reconciliation/imputation.

    Raises
    ------
    ToytreeError
        If required ``ncbi_id`` data are missing or malformed.
    """
    return _get_default_client().get_timetree_node_ages(
        tree=tree,
        endpoint=endpoint,
        data=data,
        max_pairs=max_pairs,
    )


if __name__ == "__main__":
    pass
