from datetime import date

from sqlalchemy import select

from public_jobs_tracker.ingestion.normalize_postings import normalize_postings
from public_jobs_tracker.models import JobPosting, JobPostingRaw, SourceJobRun


def test_normalize_upsert_updates_existing_posting(session):
    run1 = SourceJobRun(source_name="cido")
    session.add(run1)
    session.flush()

    payload_1 = {
        "id": "abc",
        "attributes": {
            "titol": "Tecnic/a",
            "ensConvocant": "Ajuntament X",
            "dataFiPresentacio": "2026-03-20",
        },
    }
    session.add(JobPostingRaw(run_id=run1.id, source_name="cido", source_record_id="abc", payload=payload_1, payload_hash="h1"))
    session.commit()

    normalize_postings(session, run_id=run1.id)
    session.commit()

    posting = session.scalar(select(JobPosting).where(JobPosting.source_record_id == "abc"))
    assert posting is not None
    assert posting.title == "Tecnic/a"
    assert posting.deadline_date == date(2026, 3, 20)

    run2 = SourceJobRun(source_name="cido")
    session.add(run2)
    session.flush()

    payload_2 = {
        "id": "abc",
        "attributes": {
            "titol": "Tecnic/a actualitzat",
            "ensConvocant": "Ajuntament X",
            "dataFiPresentacio": "2026-03-25",
        },
    }
    session.add(JobPostingRaw(run_id=run2.id, source_name="cido", source_record_id="abc", payload=payload_2, payload_hash="h2"))
    session.commit()

    normalize_postings(session, run_id=run2.id)
    session.commit()

    updated = session.scalar(select(JobPosting).where(JobPosting.source_record_id == "abc"))
    assert updated.title == "Tecnic/a actualitzat"
    assert updated.deadline_date == date(2026, 3, 25)
