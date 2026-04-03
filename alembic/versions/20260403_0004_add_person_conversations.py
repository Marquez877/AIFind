"""Add person conversations and messages tables

Revision ID: 20260403_0004
Revises: 20260403_0003
Create Date: 2026-04-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260403_0004'
down_revision: Union[str, None] = '20260403_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create person_conversations table
    op.create_table(
        'person_conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('person_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_person_conversations_person_id', 'person_conversations', ['person_id'])
    op.create_index('ix_person_conversations_created_at', 'person_conversations', ['created_at'])

    # Create person_messages table
    op.create_table(
        'person_messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),  # 'user' or 'assistant'
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=True),  # Store source references as JSON
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['person_conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_person_messages_conversation_id', 'person_messages', ['conversation_id'])
    op.create_index('ix_person_messages_created_at', 'person_messages', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_person_messages_created_at', table_name='person_messages')
    op.drop_index('ix_person_messages_conversation_id', table_name='person_messages')
    op.drop_table('person_messages')
    
    op.drop_index('ix_person_conversations_created_at', table_name='person_conversations')
    op.drop_index('ix_person_conversations_person_id', table_name='person_conversations')
    op.drop_table('person_conversations')
