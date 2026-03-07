from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from public_jobs_tracker.models import ChangeType, JobPosting, JobPostingSnapshot, PostingChangeLog, SourceJobRun
from public_jobs_tracker.utils import utcnow


@dataclass(slots=True)
class ChangeDetectionResult:
    run_id: int
    change_count: int


def _latest_previous_run_id(session: Session, *, source_name: str, run_id: int) -> int | None:
    return session.scalar(
        select(SourceJobRun.id)
        .where(and_(SourceJobRun.source_name == source_name, SourceJobRun.id < run_id))
        .order_by(SourceJobRun.id.desc())
        .limit(1)
    )


def detect_changes(session: Session, *, run_id: int, source_name: str = "cido") -> ChangeDetectionResult:
    now = utcnow()
    run = session.get(SourceJobRun, run_id)
    if run is None:
        raise ValueError(f"Run not found: {run_id}")

    previous_run_id = _latest_previous_run_id(session, source_name=source_name, run_id=run_id)

    current_snapshots = session.scalars(select(JobPostingSnapshot).where(JobPostingSnapshot.run_id == run_id)).all()
    previous_by_posting: dict[int, JobPostingSnapshot] = {}

    if previous_run_id is not None:
        prev_snapshots = session.scalars(select(JobPostingSnapshot).where(JobPostingSnapshot.run_id == previous_run_id)).all()
        previous_by_posting = {item.posting_id: item for item in prev_snapshots}

    change_count = 0

    for curr in current_snapshots:
        prev = previous_by_posting.get(curr.posting_id)

        if prev is None:
            session.add(
                PostingChangeLog(
                    run_id=run_id,
                    posting_id=curr.posting_id,
                    change_type=ChangeType.NEW,
                    details={"reason": "first_snapshot_for_posting"},
                    detected_at=now,
                )
            )
            change_count += 1
            continue

        if curr.hash_content != prev.hash_content:
            session.add(
                PostingChangeLog(
                    run_id=run_id,
                    posting_id=curr.posting_id,
                    change_type=ChangeType.UPDATED,
                    details={"prev_hash": prev.hash_content, "curr_hash": curr.hash_content},
                    detected_at=now,
                )
            )
            change_count += 1

        if curr.deadline_date != prev.deadline_date:
            session.add(
                PostingChangeLog(
                    run_id=run_id,
                    posting_id=curr.posting_id,
                    change_type=ChangeType.DEADLINE_CHANGED,
                    field_name="deadline_date",
                    old_value=str(prev.deadline_date) if prev.deadline_date else None,
                    new_value=str(curr.deadline_date) if curr.deadline_date else None,
                    detected_at=now,
                )
            )
            change_count += 1

    stale_postings = session.scalars(
        select(JobPosting).where(
            JobPosting.source_name == source_name,
            JobPosting.is_active.is_(True),
            JobPosting.last_seen_at < run.started_at,
        )
    ).all()

    for posting in stale_postings:
        posting.is_active = False
        posting.closed_at = now
        session.add(
            PostingChangeLog(
                run_id=run_id,
                posting_id=posting.id,
                change_type=ChangeType.CLOSED,
                details={"reason": "not_seen_in_current_run"},
                detected_at=now,
            )
        )
        change_count += 1

    session.flush()
    return ChangeDetectionResult(run_id=run_id, change_count=change_count)
