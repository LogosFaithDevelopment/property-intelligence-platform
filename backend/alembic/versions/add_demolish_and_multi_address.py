"""add demolish and multi-address support

Revision ID: c4d5e6f7g8h9
Revises: b2c3d4e5f6g7
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c4d5e6f7g8h9'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # Add demolish_all_structures boolean column
    op.add_column('properties', 
        sa.Column('demolish_all_structures', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Add additional_addresses JSON column for multi-parcel developments
    op.add_column('properties',
        sa.Column('additional_addresses', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )


def downgrade():
    # Remove columns in reverse order
    op.drop_column('properties', 'additional_addresses')
    op.drop_column('properties', 'demolish_all_structures')
