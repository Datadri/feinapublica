from __future__ import annotations

import os
from datetime import date, datetime, timedelta

from public_jobs_tracker.db.session import SessionLocal
from public_jobs_tracker.ingestion.run_ingestion import run_ingestion


def _parse_date(raw: str, *, default: date) -> date:
    raw = (raw or "").strip()
    if not raw:
        return default
    return datetime.strptime(raw, "%Y-%m-%d").date()


def _daterange_chunks(start: date, end: date, chunk_days: int) -> list[tuple[date, date]]:
    chunks: list[tuple[date, date]] = []
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=chunk_days - 1), end)
        chunks.append((cur, chunk_end))
        cur = chunk_end + timedelta(days=1)
    return chunks


if __name__ == "__main__":
    start_date = _parse_date(os.getenv("BACKFILL_START_DATE", "2025-01-01"), default=date(2025, 1, 1))
    end_date = _parse_date(os.getenv("BACKFILL_END_DATE", date.today().isoformat()), default=date.today())
    chunk_days = int(os.getenv("BACKFILL_CHUNK_DAYS", "31"))

    if end_date < start_date:
        raise ValueError("BACKFILL_END_DATE must be >= BACKFILL_START_DATE")

    chunks = _daterange_chunks(start_date, end_date, chunk_days)
    print(f"running backfill chunks={len(chunks)} range={start_date}..{end_date} chunk_days={chunk_days}")

    with SessionLocal() as session:
        for idx, (from_d, to_d) in enumerate(chunks, start=1):
            filters = {
                "maxDataPublicacioDocument][ge": from_d.isoformat(),
                "maxDataPublicacioDocument][le": to_d.isoformat(),
            }
            print(f"[{idx}/{len(chunks)}] ingest {from_d}..{to_d}")
            run_id = run_ingestion(session, filters=filters)
            print(f"[{idx}/{len(chunks)}] done run_id={run_id}")

    print("backfill complete")
