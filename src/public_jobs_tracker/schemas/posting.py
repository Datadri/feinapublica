from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class NormalizedPosting:
    source_record_id: str
    title: str | None = None
    organization: str | None = None
    territory: str | None = None
    staff_type: str | None = None
    status: str | None = None
    publication_date: date | None = None
    deadline_date: date | None = None
    detail_url: str | None = None
    summary: str | None = None
    raw_attributes: dict | None = None
