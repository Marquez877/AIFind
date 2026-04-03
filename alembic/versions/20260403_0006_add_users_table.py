"""add users table

Revision ID: 20260403_0006
Revises: 20260403_0005
Create Date: 2026-04-03 19:26:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260403_0006'
down_revision = '20260403_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_role enum
    op.execute("CREATE TYPE user_role AS ENUM ('user', 'moderator', 'admin')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('user', 'moderator', 'admin', name='user_role'), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop table
    op.drop_table('users')
    
    # Drop enum
    op.execute("DROP TYPE user_role")
