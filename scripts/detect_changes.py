from sqlalchemy import func, select

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.ingestion.detect_changes import detect_changes
from public_jobs_tracker.models import SourceJobRun


if __name__ == "__main__":
    with SessionLocal() as session:
        run_id = session.scalar(select(func.max(SourceJobRun.id)))
        if run_id is None:
            raise SystemExit("No run available")
        result = detect_changes(session, run_id=run_id)
        session.commit()
        print(f"changes run_id={result.run_id} count={result.change_count}")
