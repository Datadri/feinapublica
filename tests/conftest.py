from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from public_jobs_tracker.db.base import Base


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    with SessionLocal() as db:
        yield db


@pytest.fixture()
def fixed_now(monkeypatch):
    instant = datetime(2026, 3, 7, 10, 0, 0, tzinfo=timezone.utc)

    def _utcnow():
        return instant

    monkeypatch.setattr("public_jobs_tracker.utils.utcnow", _utcnow)
    return instant
