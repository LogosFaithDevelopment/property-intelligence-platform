"""add_phase2_deal_breaker_fields

Add Phase 2 LOGOS deal breaker tracking fields:
- existing_debt_amount: Track church's current debt
- expects_sanctuary_replacement: Boolean for sanctuary replacement expectation

Revision ID: a1b2c3d4e5f6
Revises: c273519300a9
Create Date: 2025-10-07 18:45:00.000000+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'c273519300a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Phase 2 deal breaker fields to assessments table"""
    
    # Add existing debt tracking
    op.add_column('assessments', sa.Column('existing_debt_amount', sa.Float(), nullable=True))
    op.add_column('assessments', sa.Column('debt_to_value_ratio', sa.Float(), nullable=True))
    
    # Add sanctuary replacement tracking
    op.add_column('assessments', sa.Column('expects_sanctuary_replacement', sa.Boolean(), nullable=True))
    op.add_column('assessments', sa.Column('sanctuary_replacement_cost_estimate', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove Phase 2 deal breaker fields"""
    
    # Remove sanctuary replacement fields
    op.drop_column('assessments', 'sanctuary_replacement_cost_estimate')
    op.drop_column('assessments', 'expects_sanctuary_replacement')
    
    # Remove debt tracking fields
    op.drop_column('assessments', 'debt_to_value_ratio')
    op.drop_column('assessments', 'existing_debt_amount')
