from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from public_jobs_tracker.config import configure_logging
from public_jobs_tracker.ingestion.detect_changes import detect_changes
from public_jobs_tracker.ingestion.fetch_postings import fetch_postings
from public_jobs_tracker.ingestion.normalize_postings import normalize_postings
from public_jobs_tracker.models import RunStatus
from public_jobs_tracker.utils import utcnow

logger = logging.getLogger(__name__)


def run_ingestion(session: Session, *, source_name: str = "cido", filters: dict | None = None) -> int:
    configure_logging()
    run = fetch_postings(session, source_name=source_name, filters=filters)

    try:
        normalize_result = normalize_postings(session, run_id=run.id, source_name=source_name)
        detect_changes(session, run_id=run.id, source_name=source_name)

        run = session.get(type(run), run.id)
        run.status = RunStatus.SUCCESS
        run.finished_at = utcnow()
        run.normalized_count = normalize_result.normalized_count
        session.commit()
        logger.info("Run %s completed", run.id)
        return run.id
    except Exception as exc:
        run = session.get(type(run), run.id)
        run.status = RunStatus.FAILED
        run.finished_at = utcnow()
        run.error_message = str(exc)
        session.commit()
        raise
