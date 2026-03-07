from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from public_jobs_tracker.db.base import Base
from public_jobs_tracker.models.enums import ChangeType, RunStatus
from public_jobs_tracker.utils import utcnow

JSONType = JSON().with_variant(JSONB, "postgresql")


class SourceJobRun(Base):
    __tablename__ = "source_job_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(64), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.RUNNING, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    normalized_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class JobPostingRaw(Base):
    __tablename__ = "job_posting_raw"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("source_job_run.id"), index=True)
    source_name: Mapped[str] = mapped_column(String(64), index=True)
    source_record_id: Mapped[str | None] = mapped_column(String(255), index=True)
    payload: Mapped[dict] = mapped_column(JSONType, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class JobPosting(Base):
    __tablename__ = "job_posting"
    __table_args__ = (UniqueConstraint("source_name", "source_record_id", name="uq_job_posting_source_record"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(64), index=True)
    source_record_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Legacy normalized fields (kept for backward compatibility)
    title: Mapped[str | None] = mapped_column(String(500), index=True)
    organization: Mapped[str | None] = mapped_column(String(255), index=True)
    territory: Mapped[str | None] = mapped_column(String(255), index=True)
    staff_type: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[str | None] = mapped_column(String(100), index=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    detail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Requested CIDO fields
    institucio_desenvolupat: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    ambit: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    titol: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    num_places: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tipus_personal: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    grup_titulacio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sistema_seleccio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_finalitzacio: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    estat: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    expedient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url_web: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    hash_content: Mapped[str] = mapped_column(String(64), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    snapshots: Mapped[list[JobPostingSnapshot]] = relationship(back_populates="posting")


class JobPostingSnapshot(Base):
    __tablename__ = "job_posting_snapshot"
    __table_args__ = (UniqueConstraint("run_id", "posting_id", name="uq_snapshot_run_posting"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("source_job_run.id"), index=True)
    posting_id: Mapped[int] = mapped_column(ForeignKey("job_posting.id"), index=True)
    hash_content: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deadline_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    snapshot_payload: Mapped[dict] = mapped_column(JSONType, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    posting: Mapped[JobPosting] = relationship(back_populates="snapshots")


class PostingChangeLog(Base):
    __tablename__ = "posting_change_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("source_job_run.id"), index=True)
    posting_id: Mapped[int] = mapped_column(ForeignKey("job_posting.id"), index=True)
    change_type: Mapped[ChangeType] = mapped_column(Enum(ChangeType), index=True, nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)