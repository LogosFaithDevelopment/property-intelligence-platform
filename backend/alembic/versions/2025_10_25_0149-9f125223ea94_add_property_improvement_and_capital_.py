"""Add property improvement and capital financing need fields

Revision ID: 9f125223ea94
Revises: z9y8x7w6v5u4
Create Date: 2025-10-25 01:49:30.955820+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '9f125223ea94'
down_revision = 'z9y8x7w6v5u4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add property improvement needs and capital financing need fields to assessments table
    # Using raw SQL with IF NOT EXISTS to safely handle if columns already exist in production
    op.execute("""
        ALTER TABLE assessments 
        ADD COLUMN IF NOT EXISTS property_improvement_needs JSON,
        ADD COLUMN IF NOT EXISTS capital_financing_need VARCHAR(100)
    """)


def downgrade() -> None:
    # Remove the columns if downgrading
    op.execute("""
        ALTER TABLE assessments 
        DROP COLUMN IF EXISTS capital_financing_need,
        DROP COLUMN IF EXISTS property_improvement_needs
    """)
