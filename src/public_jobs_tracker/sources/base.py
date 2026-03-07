from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class FetchResult:
    records: list[dict[str, Any]]
    next_offset: int | None
    total: int | None = None


class SourceClient(Protocol):
    source_name: str

    def fetch_page(self, *, limit: int, offset: int, filters: dict[str, Any] | None = None) -> FetchResult:
        ...

    def map_raw_to_normalized(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...
