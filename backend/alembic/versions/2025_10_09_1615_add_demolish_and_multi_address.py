"""add demolish and multi address support

Revision ID: d3e4f5g6h7i8
Revises: b2c3d4e5f6g7
Create Date: 2025-10-09 16:15:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd3e4f5g6h7i8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add demolish_all_structures column to properties table
    op.add_column('properties', sa.Column('demolish_all_structures', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add additional_addresses column to properties table (JSONB array)
    op.add_column('properties', sa.Column('additional_addresses', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Add combined_lot_size_sqft column to properties table
    op.add_column('properties', sa.Column('combined_lot_size_sqft', sa.Integer(), nullable=True))
    
    # Add combined_building_size_sqft column to properties table
    op.add_column('properties', sa.Column('combined_building_size_sqft', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove added columns
    op.drop_column('properties', 'combined_building_size_sqft')
    op.drop_column('properties', 'combined_lot_size_sqft')
    op.drop_column('properties', 'additional_addresses')
    op.drop_column('properties', 'demolish_all_structures')
