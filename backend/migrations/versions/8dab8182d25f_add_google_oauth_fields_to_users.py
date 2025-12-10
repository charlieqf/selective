"""Add Google OAuth fields to users

Revision ID: 8dab8182d25f
Revises: a1b2c3d4e5f6
Create Date: 2025-12-10 10:20:53.106369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8dab8182d25f'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add OAuth columns to users table
    op.add_column('users', sa.Column('google_id', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(length=20), nullable=False, server_default='local'))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    
    # Create unique index for google_id
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    
    # Backfill existing users with auth_provider='local'
    op.execute("UPDATE users SET auth_provider = 'local' WHERE auth_provider IS NULL")


def downgrade():
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'google_id')
