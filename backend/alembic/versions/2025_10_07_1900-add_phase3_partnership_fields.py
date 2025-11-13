"""add_phase3_partnership_fields

Add Phase 3 LOGOS partnership enhancement fields:
- decision_making_authority: Track who makes decisions
- decision_timeline: Track decision speed
- accepts_60_40_ownership: Track ownership split acceptance
- willing_to_pay_deposit: Track financial commitment

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-10-07 19:00:00.000000+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Phase 3 partnership enhancement fields to assessments table"""
    
    # Add decision-making tracking
    op.add_column('assessments', sa.Column('decision_making_authority', sa.String(50), nullable=True))
    op.add_column('assessments', sa.Column('decision_timeline', sa.String(50), nullable=True))
    
    # Add ownership and financial commitment tracking
    op.add_column('assessments', sa.Column('accepts_60_40_ownership', sa.Boolean(), nullable=True))
    op.add_column('assessments', sa.Column('willing_to_pay_deposit', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Remove Phase 3 partnership enhancement fields"""
    
    # Remove ownership and financial commitment fields
    op.drop_column('assessments', 'willing_to_pay_deposit')
    op.drop_column('assessments', 'accepts_60_40_ownership')
    
    # Remove decision-making fields
    op.drop_column('assessments', 'decision_timeline')
    op.drop_column('assessments', 'decision_making_authority')
