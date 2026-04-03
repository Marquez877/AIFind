"""add duplicate detection support

Revision ID: 20260403_0007
Revises: 20260403_0006
Create Date: 2026-04-03 19:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "20260403_0007"
down_revision = "20260403_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.add_column(
        "persons",
        sa.Column("biography_embedding", Vector(1536), nullable=True),
    )

    op.execute(
        """
        CREATE INDEX ix_persons_full_name_trgm
        ON persons USING gin (lower(full_name) gin_trgm_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX ix_persons_biography_embedding_hnsw
        ON persons
        USING hnsw (biography_embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_persons_biography_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_persons_full_name_trgm")
    op.drop_column("persons", "biography_embedding")
