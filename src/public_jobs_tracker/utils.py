import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def stable_json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash_content(material_payload: dict[str, Any]) -> str:
    serialized = stable_json_dumps(material_payload)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
