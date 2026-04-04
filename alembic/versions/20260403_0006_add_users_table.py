"""add users table

Revision ID: 20260403_0006
Revises: 20260403_0005
Create Date: 2026-04-03 19:26:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = '20260403_0006'
down_revision = '20260403_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Создаём ENUM (без падения, если уже есть)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('user', 'moderator', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # 2. Используем готовый ENUM (ВАЖНО: create_type=False)
    user_role_enum = ENUM(
        'user',
        'moderator',
        'admin',
        name='user_role',
        create_type=False
    )

    # 3. Создаём таблицу
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 4. Индекс
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    # Удаляем ENUM (если есть)
    op.execute("DROP TYPE IF EXISTS user_role")