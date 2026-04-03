"""add_persons_and_documents

Revision ID: 20260403_0002
Revises: 20260403_0001
Create Date: 2026-04-03 15:40:00

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260403_0002"
down_revision: str | None = "20260403_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Таблица репрессированных
    op.create_table(
        "persons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False, index=True),
        sa.Column("birth_year", sa.Integer(), nullable=False),
        sa.Column("death_year", sa.Integer(), nullable=True),
        sa.Column("region", sa.String(length=255), nullable=False, index=True),
        sa.Column("accusation", sa.String(length=500), nullable=False),
        sa.Column("biography", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Индекс для проверки дублей (имя + год рождения)
    op.create_index(
        "ix_persons_name_birth_year",
        "persons",
        ["full_name", "birth_year"],
    )

    # Таблица документов
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_index("ix_persons_name_birth_year", table_name="persons")
    op.drop_table("persons")
