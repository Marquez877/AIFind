"""add original file path to documents

Revision ID: 20260403_0008
Revises: 20260403_0007
Create Date: 2026-04-03 20:20:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260403_0008"
down_revision: str | None = "20260403_0007"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("original_file_path", sa.String(length=1024), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "original_file_path")
