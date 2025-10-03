"""add user tracking

Revision ID: add_user_tracking_001
Revises: 
Create Date: 2025-10-03 23:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_tracking_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_id column to churches table
    op.add_column('churches', sa.Column('user_id', sa.String(length=255), nullable=True))
    op.create_index('ix_churches_user_id', 'churches', ['user_id'])
    
    # Add user_id column to properties table
    op.add_column('properties', sa.Column('user_id', sa.String(length=255), nullable=True))
    op.create_index('ix_properties_user_id', 'properties', ['user_id'])
    
    # Add user_id column to assessments table
    op.add_column('assessments', sa.Column('user_id', sa.String(length=255), nullable=True))
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])
    
    # Add indexes for common queries
    op.create_index('ix_properties_church_id', 'properties', ['church_id'])
    op.create_index('ix_assessments_property_id', 'assessments', ['property_id'])
    op.create_index('ix_assessments_status', 'assessments', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_assessments_status', table_name='assessments')
    op.drop_index('ix_assessments_property_id', table_name='assessments')
    op.drop_index('ix_properties_church_id', table_name='properties')
    
    # Drop user_id columns
    op.drop_index('ix_assessments_user_id', table_name='assessments')
    op.drop_column('assessments', 'user_id')
    
    op.drop_index('ix_properties_user_id', table_name='properties')
    op.drop_column('properties', 'user_id')
    
    op.drop_index('ix_churches_user_id', table_name='churches')
    op.drop_column('churches', 'user_id')
