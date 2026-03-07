from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from public_jobs_tracker.config import configure_logging, get_settings
from public_jobs_tracker.models import JobPostingRaw, RunStatus, SourceJobRun
from public_jobs_tracker.sources import get_source_client
from public_jobs_tracker.utils import compute_hash_content, utcnow

logger = logging.getLogger(__name__)


def fetch_postings(session: Session, *, source_name: str = "cido", filters: dict[str, Any] | None = None) -> SourceJobRun:
    configure_logging()
    settings = get_settings()
    client = get_source_client(source_name)

    run = SourceJobRun(source_name=source_name, status=RunStatus.RUNNING)
    session.add(run)
    session.flush()

    try:
        offset = 0
        limit = settings.cido_page_limit
        max_pages = settings.cido_max_pages
        pages_processed = 0
        fetched = 0

        while True:
            result = client.fetch_page(limit=limit, offset=offset, filters=filters)
            if not result.records:
                break

            for record in result.records:
                payload_hash = compute_hash_content(record)
                raw = JobPostingRaw(
                    run_id=run.id,
                    source_name=source_name,
                    source_record_id=str(record.get("id")) if record.get("id") is not None else None,
                    payload=record,
                    payload_hash=payload_hash,
                )
                session.add(raw)
                fetched += 1

            session.flush()
            pages_processed += 1
            logger.info("Fetched page offset=%s count=%s pages=%s", offset, len(result.records), pages_processed)

            if max_pages > 0 and pages_processed >= max_pages:
                logger.info("Stopping fetch due to CIDO_MAX_PAGES=%s", max_pages)
                break

            if result.next_offset is None:
                break
            offset = result.next_offset

        run.fetched_count = fetched
        run.status = RunStatus.SUCCESS
        run.finished_at = utcnow()
        session.flush()
        return run
    except Exception as exc:
        logger.exception("Failed during fetch step")
        run.status = RunStatus.FAILED
        run.error_message = str(exc)
        run.finished_at = utcnow()
        session.flush()
        raise
