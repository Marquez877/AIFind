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
    # Create user_role enum (safe - won't fail if already exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('user', 'moderator', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create users table
    op.create_table(
        'users',
        __sa__.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        __sa__.Column('email', __sa__.String(length=255), nullable=False, unique=True),
        __sa__.Column('password_hash', __sa__.String(length=255), nullable=False),
        __sa__.Column('role', __sa__.Enum('user', 'moderator', 'admin', name='user_role', create_type=False), nullable=False, server_default='user'),
        __sa__.Column('is_active', __sa__.Boolean(), nullable=False, server_default='true'),
        __sa__.Column('created_at', __sa__.DateTime(timezone=True), nullable=False, server_default=__sa__.func.now()),
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
