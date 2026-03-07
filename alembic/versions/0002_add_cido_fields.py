"""add explicit cido fields to job_posting

Revision ID: 0002_add_cido_fields
Revises: 0001_initial
Create Date: 2026-03-07
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_cido_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("job_posting", sa.Column("institucio_desenvolupat", sa.String(length=255), nullable=True))
    op.add_column("job_posting", sa.Column("ambit", sa.String(length=255), nullable=True))
    op.add_column("job_posting", sa.Column("titol", sa.String(length=500), nullable=True))
    op.add_column("job_posting", sa.Column("num_places", sa.Integer(), nullable=True))
    op.add_column("job_posting", sa.Column("tipus_personal", sa.String(length=255), nullable=True))
    op.add_column("job_posting", sa.Column("grup_titulacio", sa.String(length=255), nullable=True))
    op.add_column("job_posting", sa.Column("sistema_seleccio", sa.String(length=255), nullable=True))
    op.add_column("job_posting", sa.Column("data_finalitzacio", sa.Date(), nullable=True))
    op.add_column("job_posting", sa.Column("estat", sa.String(length=100), nullable=True))
    op.add_column("job_posting", sa.Column("expedient", sa.String(length=255), nullable=True))
    op.add_column("job_posting", sa.Column("url_web", sa.String(length=1000), nullable=True))

    op.create_index("ix_job_posting_institucio_desenvolupat", "job_posting", ["institucio_desenvolupat"])
    op.create_index("ix_job_posting_ambit", "job_posting", ["ambit"])
    op.create_index("ix_job_posting_titol", "job_posting", ["titol"])
    op.create_index("ix_job_posting_tipus_personal", "job_posting", ["tipus_personal"])
    op.create_index("ix_job_posting_data_finalitzacio", "job_posting", ["data_finalitzacio"])
    op.create_index("ix_job_posting_estat", "job_posting", ["estat"])


def downgrade() -> None:
    op.drop_index("ix_job_posting_estat", table_name="job_posting")
    op.drop_index("ix_job_posting_data_finalitzacio", table_name="job_posting")
    op.drop_index("ix_job_posting_tipus_personal", table_name="job_posting")
    op.drop_index("ix_job_posting_titol", table_name="job_posting")
    op.drop_index("ix_job_posting_ambit", table_name="job_posting")
    op.drop_index("ix_job_posting_institucio_desenvolupat", table_name="job_posting")

    op.drop_column("job_posting", "url_web")
    op.drop_column("job_posting", "expedient")
    op.drop_column("job_posting", "estat")
    op.drop_column("job_posting", "data_finalitzacio")
    op.drop_column("job_posting", "sistema_seleccio")
    op.drop_column("job_posting", "grup_titulacio")
    op.drop_column("job_posting", "tipus_personal")
    op.drop_column("job_posting", "num_places")
    op.drop_column("job_posting", "titol")
    op.drop_column("job_posting", "ambit")
    op.drop_column("job_posting", "institucio_desenvolupat")
