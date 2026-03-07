from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.ingestion.fetch_postings import fetch_postings


if __name__ == "__main__":
    with SessionLocal() as session:
        run = fetch_postings(session)
        session.commit()
        print(f"fetch completed run_id={run.id} fetched={run.fetched_count}")
