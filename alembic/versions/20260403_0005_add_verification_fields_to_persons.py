"""add verification fields to persons

Revision ID: 20260403_0005
Revises: 20260403_0004
Create Date: 2026-04-03 19:21:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260403_0005'
down_revision = '20260403_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add verification fields to persons table
    op.add_column('persons', sa.Column('verification_status', sa.String(length=20), nullable=False, server_default='pending'))
    op.add_column('persons', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('persons', sa.Column('verified_by', sa.String(length=255), nullable=True))
    
    # Create index on verification_status for faster filtering
    op.create_index(op.f('ix_persons_verification_status'), 'persons', ['verification_status'], unique=False)


def downgrade() -> None:
    # Drop index and columns
    op.drop_index(op.f('ix_persons_verification_status'), table_name='persons')
    op.drop_column('persons', 'verified_by')
    op.drop_column('persons', 'verified_at')
    op.drop_column('persons', 'verification_status')
