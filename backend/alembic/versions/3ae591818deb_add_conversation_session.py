"""add_conversation_session

Revision ID: 3ae591818deb
Revises: a11e29de6dcd
Create Date: 2026-02-20 01:01:35.775297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ae591818deb'
down_revision: Union[str, None] = 'a11e29de6dcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('conversation_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('current_step', sa.String(length=50), nullable=False),
    sa.Column('context', sa.JSON(), nullable=True),
    sa.Column('step_summaries', sa.JSON(), nullable=True),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_sessions_created_at'), 'conversation_sessions', ['created_at'], unique=False)
    op.create_index(op.f('ix_conversation_sessions_id'), 'conversation_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_sessions_user_id'), 'conversation_sessions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_conversation_sessions_user_id'), table_name='conversation_sessions')
    op.drop_index(op.f('ix_conversation_sessions_id'), table_name='conversation_sessions')
    op.drop_index(op.f('ix_conversation_sessions_created_at'), table_name='conversation_sessions')
    op.drop_table('conversation_sessions')
