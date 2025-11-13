"""initial_schema

Revision ID: 000000000000
Revises: 
Create Date: 2025-10-01 00:00:00.000000

This is the initial migration that creates all base tables.
Generated from existing database schema.
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000000000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create api_cache table
    op.create_table('api_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_provider', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('params_hash', sa.String(length=64), nullable=False),
        sa.Column('request_params', sa.Text(), nullable=True),
        sa.Column('request_url', sa.Text(), nullable=True),
        sa.Column('response_data', sa.Text(), nullable=False),
        sa.Column('response_status', sa.Integer(), nullable=False),
        sa.Column('response_size_bytes', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('api_cost_estimate', sa.Float(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.Column('validation_errors', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_cache_api_provider'), 'api_cache', ['api_provider'], unique=False)
    op.create_index(op.f('ix_api_cache_id'), 'api_cache', ['id'], unique=False)
    op.create_index('ix_api_cache_lookup', 'api_cache', ['api_provider', 'endpoint', 'params_hash'], unique=False)
    
    # Create churches table
    op.create_table('churches',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('denomination', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_phone', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_churches_id'), 'churches', ['id'], unique=False)
    
    # Create properties table
    op.create_table('properties',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('apn', sa.String(), nullable=True),
        sa.Column('lot_size_sqft', sa.Integer(), nullable=True),
        sa.Column('lot_size_acres', sa.Float(), nullable=True),
        sa.Column('zoning', sa.String(), nullable=True),
        sa.Column('existing_building_sqft', sa.Integer(), nullable=True),
        sa.Column('year_built', sa.Integer(), nullable=True),
        sa.Column('number_of_units', sa.Integer(), nullable=True),
        sa.Column('owner_name', sa.String(), nullable=True),
        sa.Column('owner_address', sa.String(), nullable=True),
        sa.Column('smarty_key', sa.String(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('census_tract', sa.String(), nullable=True),
        sa.Column('census_block_group', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        # Note: Fields added by subsequent migrations are excluded:
        # - demolish_all_structures, additional_addresses, combined_lot_size_sqft (migration d3e4f5g6h7i8)
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_id'), 'properties', ['id'], unique=False)
    op.create_index(op.f('ix_properties_smarty_key'), 'properties', ['smarty_key'], unique=False)
    
    # Create assessments table
    op.create_table('assessments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('church_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('submission_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('ai_assessment', sa.Text(), nullable=True),
        sa.Column('ai_assessment_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('manual_notes', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        # Note: Fields added by subsequent migrations are excluded:
        # - available_build_sqft, available_build_acres, build_area_notes (migration 71dd657881e1)
        # - manual_overrides, override_reason, overridden_by, overridden_at (migration manual_overrides_2025)
        # - submitter_name, submitter_email, submitter_phone (migration 0e265bd5510a)
        # - deal_breaker_* fields (migration a1b2c3d4e5f6)
        # - jv_* fields (migration b2c3d4e5f6g7)
        sa.ForeignKeyConstraint(['church_id'], ['churches.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_id'), 'assessments', ['id'], unique=False)
    op.create_index(op.f('ix_assessments_property_id'), 'assessments', ['property_id'], unique=False)
    op.create_index(op.f('ix_assessments_status'), 'assessments', ['status'], unique=False)
    
    # Create reports table
    op.create_table('reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('assessment_id', sa.UUID(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('generated_by', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_assessment_id'), 'reports', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_assessment_id'), table_name='reports')
    op.drop_table('reports')
    
    op.drop_index(op.f('ix_assessments_status'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_property_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_id'), table_name='assessments')
    op.drop_table('assessments')
    
    op.drop_index(op.f('ix_properties_smarty_key'), table_name='properties')
    op.drop_index(op.f('ix_properties_id'), table_name='properties')
    op.drop_table('properties')
    
    op.drop_index(op.f('ix_churches_id'), table_name='churches')
    op.drop_table('churches')
    
    op.drop_index('ix_api_cache_lookup', table_name='api_cache')
    op.drop_index(op.f('ix_api_cache_id'), table_name='api_cache')
    op.drop_index(op.f('ix_api_cache_api_provider'), table_name='api_cache')
    op.drop_table('api_cache')
