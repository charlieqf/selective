"""Add previous_status to items

Revision ID: 35e8f293f4e8
Revises: 6a8246654d0f
Create Date: 2025-12-09 22:43:43.546512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35e8f293f4e8'
down_revision = '6a8246654d0f'
branch_labels = None
depends_on = None


def upgrade():
    # Only add the previous_status column
    op.add_column('items', sa.Column('previous_status', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('items', 'previous_status')
