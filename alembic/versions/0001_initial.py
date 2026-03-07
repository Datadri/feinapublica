"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    run_status = sa.Enum("RUNNING", "SUCCESS", "FAILED", name="runstatus")
    change_type = sa.Enum("NEW", "UPDATED", "CLOSED", "DEADLINE_CHANGED", name="changetype")
    user_posting_status = sa.Enum("pendent", "revisada", "interessa", "descartada", "aplicada", name="userpostingstatus")


    op.create_table(
        "source_job_run",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", run_status, nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("fetched_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalized_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_job_run_source_name", "source_job_run", ["source_name"])

    op.create_table(
        "job_posting_raw",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("source_job_run.id"), nullable=False),
        sa.Column("source_name", sa.String(length=64), nullable=False),
        sa.Column("source_record_id", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_job_posting_raw_run_id", "job_posting_raw", ["run_id"])
    op.create_index("ix_job_posting_raw_source_name", "job_posting_raw", ["source_name"])
    op.create_index("ix_job_posting_raw_source_record_id", "job_posting_raw", ["source_record_id"])

    op.create_table(
        "job_posting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=64), nullable=False),
        sa.Column("source_record_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("organization", sa.String(length=255), nullable=True),
        sa.Column("territory", sa.String(length=255), nullable=True),
        sa.Column("staff_type", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=100), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("deadline_date", sa.Date(), nullable=True),
        sa.Column("detail_url", sa.String(length=1000), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("hash_content", sa.String(length=64), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_name", "source_record_id", name="uq_job_posting_source_record"),
    )
    for c in ["source_name", "title", "organization", "territory", "staff_type", "status", "deadline_date", "hash_content", "last_seen_at"]:
        op.create_index(f"ix_job_posting_{c}", "job_posting", [c])

    op.create_table(
        "job_posting_snapshot",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("source_job_run.id"), nullable=False),
        sa.Column("posting_id", sa.Integer(), sa.ForeignKey("job_posting.id"), nullable=False),
        sa.Column("hash_content", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=100), nullable=True),
        sa.Column("deadline_date", sa.Date(), nullable=True),
        sa.Column("snapshot_payload", sa.JSON(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "posting_id", name="uq_snapshot_run_posting"),
    )
    for c in ["run_id", "posting_id", "hash_content"]:
        op.create_index(f"ix_job_posting_snapshot_{c}", "job_posting_snapshot", [c])

    op.create_table(
        "posting_change_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("source_job_run.id"), nullable=False),
        sa.Column("posting_id", sa.Integer(), sa.ForeignKey("job_posting.id"), nullable=False),
        sa.Column("change_type", change_type, nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
    )
    for c in ["run_id", "posting_id", "change_type"]:
        op.create_index(f"ix_posting_change_log_{c}", "posting_change_log", [c])

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "user_saved_search",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("filters_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_user_saved_search_user_id", "user_saved_search", ["user_id"])

    op.create_table(
        "user_followed_posting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("posting_id", sa.Integer(), sa.ForeignKey("job_posting.id"), nullable=False),
        sa.Column("user_status", user_posting_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "posting_id", name="uq_user_followed_posting"),
    )
    op.create_index("ix_user_followed_posting_user_id", "user_followed_posting", ["user_id"])
    op.create_index("ix_user_followed_posting_posting_id", "user_followed_posting", ["posting_id"])


def downgrade() -> None:
    for table in [
        "user_followed_posting",
        "user_saved_search",
        "user",
        "posting_change_log",
        "job_posting_snapshot",
        "job_posting",
        "job_posting_raw",
        "source_job_run",
    ]:
        op.drop_table(table)

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        sa.Enum(name="userpostingstatus").drop(bind, checkfirst=True)
        sa.Enum(name="changetype").drop(bind, checkfirst=True)
        sa.Enum(name="runstatus").drop(bind, checkfirst=True)
