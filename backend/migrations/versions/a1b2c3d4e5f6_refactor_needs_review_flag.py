"""Refactor: Add needs_review flag, remove NEED_REVIEW from status

Revision ID: a1b2c3d4e5f6
Revises: 35e8f293f4e8
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '35e8f293f4e8'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add needs_review column
    op.add_column('items', sa.Column('needs_review', sa.Boolean(), nullable=True))
    
    # Step 2: Backfill - set needs_review=True for items with status='NEED_REVIEW'
    # Also set their status to 'ANSWERED' (they were answered but got it wrong)
    op.execute("""
        UPDATE items 
        SET needs_review = TRUE, status = 'ANSWERED' 
        WHERE status = 'NEED_REVIEW'
    """)
    
    # Step 3: Set needs_review=False for all other items
    op.execute("""
        UPDATE items 
        SET needs_review = FALSE 
        WHERE needs_review IS NULL
    """)
    
    # Step 4: Make needs_review NOT NULL after backfill
    op.alter_column('items', 'needs_review', nullable=False, existing_type=sa.Boolean())
    
    # Step 5: Drop previous_status column (no longer needed)
    op.drop_column('items', 'previous_status')
    
    # Step 6: Update CHECK constraint (remove NEED_REVIEW)
    # Note: Constraint changes are complex in MySQL, may need to drop and recreate
    # For MySQL, we drop the old constraint and add a new one
    op.drop_constraint('check_status_valid', 'items', type_='check')
    op.create_check_constraint(
        'check_status_valid', 
        'items', 
        "status IN ('UNANSWERED', 'ANSWERED', 'MASTERED')"
    )


def downgrade():
    # Reverse the changes
    
    # Re-add NEED_REVIEW to constraint
    op.drop_constraint('check_status_valid', 'items', type_='check')
    op.create_check_constraint(
        'check_status_valid',
        'items',
        "status IN ('UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW')"
    )
    
    # Re-add previous_status column
    op.add_column('items', sa.Column('previous_status', sa.String(length=20), nullable=True))
    
    # Convert needs_review back to status
    op.execute("""
        UPDATE items 
        SET status = 'NEED_REVIEW' 
        WHERE needs_review = TRUE
    """)
    
    # Drop needs_review column
    op.drop_column('items', 'needs_review')
