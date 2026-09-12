"""Shared HTTP transport and JSON cache support for remote tree services."""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from toytree.utils import ToytreeError


class JSONServiceClient:
    """Reusable requests client with retries and an expiring JSON cache."""

    service_name = "remote service"
    default_headers = {"User-Agent": "toytree"}

    def __init__(
        self,
        base_url: str,
        timeout: float = 20.0,
        max_retries: int = 4,
        backoff_factor: float = 0.5,
        cache: bool = True,
        cache_dir: str | Path | None = None,
        cache_ttl: float | None = 7 * 24 * 60 * 60,
        session: Session | None = None,
    ) -> None:
        base_url = str(base_url).strip()
        if not base_url.startswith(("https://", "http://")):
            raise ValueError("base_url must start with 'https://' or 'http://'.")
        if not base_url.endswith("/"):
            base_url += "/"
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout):
            raise ValueError("timeout must be a finite positive number.")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")
        if isinstance(max_retries, bool) or not isinstance(max_retries, int):
            raise TypeError("max_retries must be a non-negative integer.")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative.")
        if not isinstance(backoff_factor, (int, float)) or backoff_factor < 0:
            raise ValueError("backoff_factor must be a non-negative number.")
        if cache_ttl is not None:
            if not isinstance(cache_ttl, (int, float)) or cache_ttl < 0:
                raise ValueError("cache_ttl must be None or a non-negative number.")

        self.base_url = base_url
        self.timeout = float(timeout)
        self.max_retries = max_retries
        self.backoff_factor = float(backoff_factor)
        self.cache = bool(cache)
        self.cache_dir = (
            Path(cache_dir).expanduser()
            if cache_dir is not None
            else Path(tempfile.gettempdir()) / f"toytree_{self.service_name}_cache"
        )
        self.cache_ttl = None if cache_ttl is None else float(cache_ttl)
        self._session = session
        self._owns_session = session is None

    @classmethod
    def _build_session(cls, max_retries: int, backoff_factor: float) -> Session:
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
        session.headers.update(cls.default_headers)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @property
    def session(self) -> Session:
        """Return the active session, creating an owned session lazily."""
        if self._session is None:
            self._session = self._build_session(
                self.max_retries,
                self.backoff_factor,
            )
        return self._session

    def close(self) -> None:
        """Close a session created by this client, leaving injected sessions open."""
        if self._session is not None and self._owns_session:
            self._session.close()
            self._session = None

    def __enter__(self) -> JSONServiceClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def _hash_metadata(metadata: dict[str, Any]) -> str:
        dumped = json.dumps(
            metadata,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(dumped.encode()).hexdigest()

    def _cache_path(self, namespace: str, metadata: dict[str, Any]) -> Path:
        key = {
            "base_url": self.base_url,
            "namespace": namespace,
            **metadata,
        }
        return self.cache_dir / namespace / f"{self._hash_metadata(key)}.json"

    def _cache_read(self, path: Path) -> Any | None:
        if not self.cache or not path.exists():
            return None
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            created = float(envelope["created_at"])
            if self.cache_ttl is not None and time.time() - created > self.cache_ttl:
                return None
            return envelope["data"]
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            # A truncated or legacy cache entry is a miss, never an API result.
            return None

    def _cache_write(self, path: Path, data: Any) -> None:
        if not self.cache:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        envelope = {"created_at": time.time(), "data": data}
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(envelope, stream, sort_keys=True, separators=(",", ":"))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def _error_from_response(
        self,
        endpoint: str,
        exc: Exception,
        response: requests.Response | None,
    ) -> ToytreeError:
        status = None if response is None else response.status_code
        snippet = "" if response is None else response.text[:500].replace("\n", " ")
        return ToytreeError(
            f"{self.service_name} request failed at endpoint {endpoint!r}; "
            f"status={status!r}; error={exc}; response_snippet={snippet!r}"
        )

    def _request_json(
        self,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        *,
        method: Literal["GET", "POST"] = "POST",
        use_cache: bool = False,
        cache_namespace: str = "json",
    ) -> Any:
        """Request and decode JSON with optional deterministic disk caching."""
        payload = {} if payload is None else payload
        metadata = {"method": method, "endpoint": endpoint, "payload": payload}
        path = self._cache_path(cache_namespace, metadata)
        if use_cache:
            cached = self._cache_read(path)
            if cached is not None:
                return cached

        response: requests.Response | None = None
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        try:
            if method == "GET":
                response = self.session.get(url, params=payload, timeout=self.timeout)
            else:
                response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if use_cache:
                self._cache_write(path, data)
            return data
        except Exception as exc:
            raise self._error_from_response(endpoint, exc, response) from exc
