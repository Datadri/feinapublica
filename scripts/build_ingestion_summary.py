from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, text

from public_jobs_tracker.config import normalize_database_url


def _fmt_dt(value):
    if value is None:
        return "-"
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def main() -> None:
    database_url = normalize_database_url(os.getenv("DATABASE_URL"))
    engine = create_engine(database_url)

    with engine.connect() as conn:
        run = conn.execute(
            text(
                """
                select id, source_name, status, fetched_count, normalized_count, started_at, finished_at, error_message
                from source_job_run
                order by id desc
                limit 1
                """
            )
        ).mappings().first()

        if run is None:
            print("No ingestion run found in source_job_run.")
            return

        change_rows = conn.execute(
            text(
                """
                select change_type, count(*) as cnt
                from posting_change_log
                where run_id = :run_id
                group by change_type
                order by change_type
                """
            ),
            {"run_id": run["id"]},
        ).mappings().all()

        counts = {row["change_type"]: int(row["cnt"]) for row in change_rows}

        total_postings = conn.execute(text("select count(*) from job_posting")).scalar_one()

    duration = "-"
    if run["started_at"] and run["finished_at"]:
        duration = str(run["finished_at"] - run["started_at"])

    lines = [
        "Public Jobs Tracker - Daily ingestion summary",
        "",
        f"run_id: {run['id']}",
        f"source: {run['source_name']}",
        f"status: {run['status']}",
        f"started_at_utc: {_fmt_dt(run['started_at'])}",
        f"finished_at_utc: {_fmt_dt(run['finished_at'])}",
        f"duration: {duration}",
        f"fetched_count: {run['fetched_count']}",
        f"normalized_count: {run['normalized_count']}",
        f"change_NEW: {counts.get('NEW', 0)}",
        f"change_UPDATED: {counts.get('UPDATED', 0)}",
        f"change_DEADLINE_CHANGED: {counts.get('DEADLINE_CHANGED', 0)}",
        f"change_CLOSED: {counts.get('CLOSED', 0)}",
        f"total_active_dataset: {total_postings}",
    ]

    if run.get("error_message"):
        lines.extend(["", f"error_message: {run['error_message']}"])

    print("\n".join(lines))


if __name__ == "__main__":
    main()
