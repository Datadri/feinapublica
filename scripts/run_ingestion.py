import os

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.ingestion.run_ingestion import run_ingestion


def _build_filters() -> dict:
    filters: dict[str, str] = {}
    publication_from = os.getenv("CIDO_FILTER_PUBLICATION_FROM", "").strip()
    if publication_from:
        # Builds query string key: filter[maxDataPublicacioDocument][ge]
        filters["maxDataPublicacioDocument][ge"] = publication_from
    return filters


if __name__ == "__main__":
    with SessionLocal() as session:
        run_id = run_ingestion(session, filters=_build_filters() or None)
        print(f"ingestion completed run_id={run_id}")