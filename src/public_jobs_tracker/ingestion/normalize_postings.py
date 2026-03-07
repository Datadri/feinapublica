from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from public_jobs_tracker.config import get_settings
from public_jobs_tracker.models import JobPosting, JobPostingSnapshot, JobPostingRaw, SourceJobRun
from public_jobs_tracker.sources import get_source_client
from public_jobs_tracker.utils import compute_hash_content, utcnow

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class NormalizeResult:
    run_id: int
    normalized_count: int


def _material_payload(mapped: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": mapped.get("title"),
        "organization": mapped.get("organization"),
        "territory": mapped.get("territory"),
        "staff_type": mapped.get("staff_type"),
        "status": mapped.get("status"),
        "publication_date": str(mapped.get("publication_date")) if mapped.get("publication_date") else None,
        "deadline_date": str(mapped.get("deadline_date")) if mapped.get("deadline_date") else None,
        "detail_url": mapped.get("detail_url"),
        "summary": mapped.get("summary"),
        "institucio_desenvolupat": mapped.get("institucio_desenvolupat"),
        "ambit": mapped.get("ambit"),
        "titol": mapped.get("titol"),
        "num_places": mapped.get("num_places"),
        "tipus_personal": mapped.get("tipus_personal"),
        "grup_titulacio": mapped.get("grup_titulacio"),
        "sistema_seleccio": mapped.get("sistema_seleccio"),
        "data_finalitzacio": str(mapped.get("data_finalitzacio")) if mapped.get("data_finalitzacio") else None,
        "estat": mapped.get("estat"),
        "expedient": mapped.get("expedient"),
        "url_web": mapped.get("url_web"),
    }


def _parse_min_publication_date(raw: str) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        logger.warning("Invalid MIN_PUBLICATION_DATE=%s, ignoring filter", raw)
        return None


def normalize_postings(session: Session, *, run_id: int, source_name: str = "cido") -> NormalizeResult:
    client = get_source_client(source_name)
    now = utcnow()
    settings = get_settings()
    min_publication_date = _parse_min_publication_date(settings.min_publication_date)

    run = session.get(SourceJobRun, run_id)
    if run is None:
        raise ValueError(f"Run not found: {run_id}")

    raws = session.scalars(select(JobPostingRaw).where(JobPostingRaw.run_id == run_id)).all()
    normalized_count = 0

    for raw in raws:
        mapped = client.map_raw_to_normalized(raw.payload)
        source_record_id = mapped.get("source_record_id")
        if not source_record_id:
            logger.warning("Skipping raw id=%s without source_record_id", raw.id)
            continue

        publication_date = mapped.get("publication_date")
        if min_publication_date and publication_date and publication_date < min_publication_date:
            continue

        material_payload = _material_payload(mapped)
        hash_content = compute_hash_content(material_payload)

        posting = session.scalar(
            select(JobPosting).where(
                JobPosting.source_name == source_name,
                JobPosting.source_record_id == source_record_id,
            )
        )

        is_new = posting is None
        if posting is None:
            posting = JobPosting(
                source_name=source_name,
                source_record_id=source_record_id,
                first_seen_at=now,
                last_changed_at=now,
            )
            session.add(posting)

        prev_hash = posting.hash_content if posting.hash_content else None

        posting.title = mapped.get("title")
        posting.organization = mapped.get("organization")
        posting.territory = mapped.get("territory")
        posting.staff_type = mapped.get("staff_type")
        posting.status = mapped.get("status")
        posting.publication_date = publication_date
        posting.deadline_date = mapped.get("deadline_date")
        posting.detail_url = mapped.get("detail_url")
        posting.summary = mapped.get("summary")

        posting.institucio_desenvolupat = mapped.get("institucio_desenvolupat")
        posting.ambit = mapped.get("ambit")
        posting.titol = mapped.get("titol")
        posting.num_places = mapped.get("num_places")
        posting.tipus_personal = mapped.get("tipus_personal")
        posting.grup_titulacio = mapped.get("grup_titulacio")
        posting.sistema_seleccio = mapped.get("sistema_seleccio")
        posting.data_finalitzacio = mapped.get("data_finalitzacio")
        posting.estat = mapped.get("estat")
        posting.expedient = mapped.get("expedient")
        posting.url_web = mapped.get("url_web")

        posting.hash_content = hash_content
        posting.last_seen_at = now
        posting.is_active = True
        posting.closed_at = None

        if is_new or prev_hash != hash_content:
            posting.last_changed_at = now

        session.flush()

        snapshot = JobPostingSnapshot(
            run_id=run_id,
            posting_id=posting.id,
            hash_content=hash_content,
            status=posting.status,
            deadline_date=posting.deadline_date,
            snapshot_payload=material_payload,
        )
        session.add(snapshot)

        normalized_count += 1

    run.normalized_count = normalized_count
    session.flush()

    return NormalizeResult(run_id=run_id, normalized_count=normalized_count)
