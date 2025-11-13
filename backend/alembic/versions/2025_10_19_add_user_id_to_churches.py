"""add user_id to churches

Revision ID: add_user_id_churches
Revises: 2025_10_09_1615_add_demolish_and_multi_address
Create Date: 2025-10-19

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'h8i9j0k1l2m3'
down_revision = 'd3e4f5g6h7i8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add user_id column to churches table"""
    # Add user_id column (nullable for existing records)
    op.add_column('churches', sa.Column('user_id', sa.String(255), nullable=True))
    
    # Add index for performance
    op.create_index('ix_churches_user_id', 'churches', ['user_id'])


def downgrade() -> None:
    """Remove user_id column from churches table"""
    op.drop_index('ix_churches_user_id', table_name='churches')
    op.drop_column('churches', 'user_id')
