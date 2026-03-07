from __future__ import annotations

import logging
from typing import Any

import httpx

from public_jobs_tracker.config import get_settings
from public_jobs_tracker.sources.base import FetchResult
from public_jobs_tracker.sources.cido.mapping import map_cido_payload

logger = logging.getLogger(__name__)


class CidoClient:
    source_name = "cido"

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.cido_base_url.rstrip("/")
        self.timeout = settings.cido_timeout_seconds

    def _build_params(self, *, limit: int, offset: int, filters: dict[str, Any] | None) -> dict[str, Any]:
        params: dict[str, Any] = {
            "page[limit]": limit,
            "page[offset]": offset,
            "sort": "-maxDataPublicacioDocument",
        }
        for key, value in (filters or {}).items():
            params[f"filter[{key}]"] = value
        return params

    def fetch_page(self, *, limit: int, offset: int, filters: dict[str, Any] | None = None) -> FetchResult:
        url = f"{self.base_url}/oposicions"
        params = self._build_params(limit=limit, offset=offset, filters=filters)
        try:
            response = httpx.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            logger.exception("HTTP error while calling CIDO")
            raise RuntimeError(f"CIDO HTTP error: {exc}") from exc
        except ValueError as exc:
            logger.exception("JSON parse error while calling CIDO")
            raise RuntimeError(f"CIDO parse error: {exc}") from exc

        data = payload.get("data", []) or []
        meta = payload.get("meta", {}) or {}

        total = meta.get("total")
        if total is None:
            total = meta.get("count")

        next_offset: int | None = None
        if total is not None and (offset + limit) < int(total):
            next_offset = offset + limit
        elif total is None and len(data) == limit:
            next_offset = offset + limit

        return FetchResult(records=data, next_offset=next_offset, total=total)

    def map_raw_to_normalized(self, payload: dict[str, Any]) -> dict[str, Any]:
        return map_cido_payload(payload)
