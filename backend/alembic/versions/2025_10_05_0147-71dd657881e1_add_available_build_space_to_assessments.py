"""add_available_build_space_to_assessments

Revision ID: 71dd657881e1
Revises: add_user_tracking_001
Create Date: 2025-10-05 01:47:13.472860+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "71dd657881e1"
down_revision = "add_user_tracking_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add available build space fields to assessments table
    op.add_column("assessments", sa.Column("available_build_sqft", sa.Float(), nullable=True))
    op.add_column("assessments", sa.Column("available_build_acres", sa.Float(), nullable=True))
    op.add_column("assessments", sa.Column("build_area_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove available build space fields from assessments table
    op.drop_column("assessments", "build_area_notes")
    op.drop_column("assessments", "available_build_acres")
    op.drop_column("assessments", "available_build_sqft")
