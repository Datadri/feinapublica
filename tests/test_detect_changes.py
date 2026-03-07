from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from public_jobs_tracker.ingestion.detect_changes import detect_changes
from public_jobs_tracker.models import ChangeType, JobPosting, JobPostingSnapshot, PostingChangeLog, SourceJobRun


def test_detect_changes_updated_deadline_and_closed(session):
    t0 = datetime(2026, 3, 1, tzinfo=timezone.utc)
    t1 = t0 + timedelta(days=1)

    run1 = SourceJobRun(source_name="cido", started_at=t0)
    session.add(run1)
    session.flush()

    p1 = JobPosting(
        source_name="cido",
        source_record_id="1",
        title="A",
        hash_content="hash-a-1",
        first_seen_at=t0,
        last_seen_at=t0,
        last_changed_at=t0,
        is_active=True,
    )
    p2 = JobPosting(
        source_name="cido",
        source_record_id="2",
        title="B",
        hash_content="hash-b-1",
        first_seen_at=t0,
        last_seen_at=t0,
        last_changed_at=t0,
        is_active=True,
    )
    session.add_all([p1, p2])
    session.flush()

    s1 = JobPostingSnapshot(run_id=run1.id, posting_id=p1.id, hash_content="hash-a-1", status="open", deadline_date=None, snapshot_payload={"title": "A"})
    s2 = JobPostingSnapshot(run_id=run1.id, posting_id=p2.id, hash_content="hash-b-1", status="open", deadline_date=None, snapshot_payload={"title": "B"})
    session.add_all([s1, s2])
    session.commit()

    run2 = SourceJobRun(source_name="cido", started_at=t1)
    session.add(run2)
    session.flush()

    p1.last_seen_at = t1
    p1.hash_content = "hash-a-2"

    s1_new = JobPostingSnapshot(
        run_id=run2.id,
        posting_id=p1.id,
        hash_content="hash-a-2",
        status="open",
        deadline_date=None,
        snapshot_payload={"title": "A2"},
    )
    session.add(s1_new)
    session.commit()

    result = detect_changes(session, run_id=run2.id)
    session.commit()

    assert result.change_count == 2

    logs = session.scalars(select(PostingChangeLog).where(PostingChangeLog.run_id == run2.id)).all()
    types = sorted([l.change_type for l in logs], key=lambda x: x.value)
    assert types == [ChangeType.CLOSED, ChangeType.UPDATED]

    closed_p2 = session.get(JobPosting, p2.id)
    assert closed_p2.is_active is False
