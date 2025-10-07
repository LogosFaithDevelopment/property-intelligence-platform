"""add manual overrides tracking

Revision ID: manual_overrides_2025
Revises: 71dd657881e1
Create Date: 2025-10-05 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'manual_overrides_2025'
down_revision = '71dd657881e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add JSON field to track manual overrides vs API values
    op.add_column('properties', sa.Column('manual_overrides', sa.JSON(), nullable=True))
    
    # Add comment explaining the field
    op.execute("""
        COMMENT ON COLUMN properties.manual_overrides IS 
        'Tracks fields where user manually entered data that differs from API values. 
        Format: {"lot_size_sqft": {"manual": 50000, "api": 48500, "source": "LA County", "date": "2025-10-05"}}'
    """)


def downgrade() -> None:
    op.drop_column('properties', 'manual_overrides')
