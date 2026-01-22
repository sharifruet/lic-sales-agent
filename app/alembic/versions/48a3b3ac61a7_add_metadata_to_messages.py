"""add_metadata_to_messages

Revision ID: 48a3b3ac61a7
Revises: cfedcf1cb1c6
Create Date: 2025-11-24 11:08:28.422996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48a3b3ac61a7'
down_revision: Union[str, None] = 'cfedcf1cb1c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add metadata column to messages table
    op.add_column('messages', sa.Column('metadata', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove metadata column from messages table
    op.drop_column('messages', 'metadata')

