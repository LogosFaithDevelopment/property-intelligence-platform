"""add churchstatus enum type

Revision ID: z9y8x7w6v5u4
Revises: t0u1v2w3x4y5
Create Date: 2025-10-19

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'z9y8x7w6v5u4'
down_revision = 't0u1v2w3x4y5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ChurchStatus enum type"""
    # Create the enum type
    churchstatus_enum = postgresql.ENUM('pending', 'verified', 'rejected', 'suspended', name='churchstatus', create_type=True)
    churchstatus_enum.create(op.get_bind(), checkfirst=True)
    
    # Drop the default value temporarily
    op.execute("ALTER TABLE churches ALTER COLUMN verification_status DROP DEFAULT")
    
    # Convert the verification_status column from VARCHAR to the enum type
    op.execute("ALTER TABLE churches ALTER COLUMN verification_status TYPE churchstatus USING verification_status::churchstatus")
    
    # Re-add the default value
    op.execute("ALTER TABLE churches ALTER COLUMN verification_status SET DEFAULT 'pending'::churchstatus")


def downgrade() -> None:
    """Remove ChurchStatus enum type"""
    # Convert back to VARCHAR
    op.execute("ALTER TABLE churches ALTER COLUMN verification_status TYPE VARCHAR(50)")
    
    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS churchstatus")
