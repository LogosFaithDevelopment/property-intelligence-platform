"""sync churches table structure

Revision ID: t0u1v2w3x4y5
Revises: h8i9j0k1l2m3
Create Date: 2025-10-19

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 't0u1v2w3x4y5'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add all missing columns to churches table to match current model"""
    
    # Add new columns that don't exist in original schema
    op.add_column('churches', sa.Column('legal_name', sa.String(255), nullable=True))
    op.add_column('churches', sa.Column('founded_year', sa.Integer(), nullable=True))
    op.add_column('churches', sa.Column('tax_exempt_id', sa.String(50), nullable=True))
    op.add_column('churches', sa.Column('tax_exempt_status', sa.String(50), nullable=True))
    op.add_column('churches', sa.Column('verification_status', sa.String(50), nullable=False, server_default='pending'))
    op.add_column('churches', sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('churches', sa.Column('verification_notes', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('primary_email', sa.String(255), nullable=True))
    op.add_column('churches', sa.Column('primary_phone', sa.String(50), nullable=True))
    op.add_column('churches', sa.Column('website_url', sa.String(255), nullable=True))
    op.add_column('churches', sa.Column('street_address', sa.String(255), nullable=True))
    op.add_column('churches', sa.Column('country', sa.String(100), nullable=False, server_default='United States'))
    op.add_column('churches', sa.Column('congregation_size', sa.Integer(), nullable=True))
    op.add_column('churches', sa.Column('annual_budget', sa.Float(), nullable=True))
    op.add_column('churches', sa.Column('staff_count', sa.Integer(), nullable=True))
    op.add_column('churches', sa.Column('community_programs', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('current_ministries', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('previous_development_experience', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('churches', sa.Column('development_experience_notes', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('partnership_goals', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('timeline_preference', sa.String(50), nullable=True))
    op.add_column('churches', sa.Column('admin_notes', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('risk_assessment', sa.Text(), nullable=True))
    op.add_column('churches', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('churches', sa.Column('uuid', sa.String(), nullable=True))
    op.add_column('churches', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Rename old columns to match new naming convention
    op.alter_column('churches', 'contact_email', new_column_name='_old_contact_email', nullable=True)
    op.alter_column('churches', 'contact_phone', new_column_name='_old_contact_phone', nullable=True)
    op.alter_column('churches', 'address', new_column_name='_old_address', nullable=True)
    
    # Migrate data from old columns to new ones
    op.execute("""
        UPDATE churches 
        SET primary_email = _old_contact_email,
            primary_phone = _old_contact_phone,
            street_address = _old_address
        WHERE _old_contact_email IS NOT NULL OR _old_contact_phone IS NOT NULL OR _old_address IS NOT NULL
    """)
    
    # Create indexes
    op.create_index('ix_churches_name', 'churches', ['name'])
    op.create_index('ix_churches_primary_email', 'churches', ['primary_email'])
    
    # Create unique constraint on tax_exempt_id
    op.create_index('ix_churches_tax_exempt_id', 'churches', ['tax_exempt_id'], unique=True)


def downgrade() -> None:
    """Remove added columns and restore original schema"""
    
    # Drop indexes
    op.drop_index('ix_churches_tax_exempt_id', table_name='churches')
    op.drop_index('ix_churches_primary_email', table_name='churches')
    op.drop_index('ix_churches_name', table_name='churches')
    
    # Restore old column names
    op.alter_column('churches', '_old_address', new_column_name='address')
    op.alter_column('churches', '_old_contact_phone', new_column_name='contact_phone')
    op.alter_column('churches', '_old_contact_email', new_column_name='contact_email')
    
    # Drop added columns
    op.drop_column('churches', 'is_deleted')
    op.drop_column('churches', 'uuid')
    op.drop_column('churches', 'is_active')
    op.drop_column('churches', 'risk_assessment')
    op.drop_column('churches', 'admin_notes')
    op.drop_column('churches', 'timeline_preference')
    op.drop_column('churches', 'partnership_goals')
    op.drop_column('churches', 'development_experience_notes')
    op.drop_column('churches', 'previous_development_experience')
    op.drop_column('churches', 'current_ministries')
    op.drop_column('churches', 'community_programs')
    op.drop_column('churches', 'staff_count')
    op.drop_column('churches', 'annual_budget')
    op.drop_column('churches', 'congregation_size')
    op.drop_column('churches', 'country')
    op.drop_column('churches', 'street_address')
    op.drop_column('churches', 'website_url')
    op.drop_column('churches', 'primary_phone')
    op.drop_column('churches', 'primary_email')
    op.drop_column('churches', 'verification_notes')
    op.drop_column('churches', 'verification_date')
    op.drop_column('churches', 'verification_status')
    op.drop_column('churches', 'tax_exempt_status')
    op.drop_column('churches', 'tax_exempt_id')
    op.drop_column('churches', 'founded_year')
