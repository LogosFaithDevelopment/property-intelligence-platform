"""convert_admin_users_to_clerk

Convert admin_users table from custom auth to Clerk-based auth
- Remove password_hash column
- Add clerk_user_id column
- Keep email for reference

Revision ID: c273519300a9
Revises: ef2bce464a78
Create Date: 2025-10-07 03:28:19.668009+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c273519300a9'
down_revision = 'ef2bce464a78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add clerk_user_id column
    op.add_column('admin_users', sa.Column('clerk_user_id', sa.String(length=255), nullable=True))
    
    # Create index on clerk_user_id
    op.create_index(op.f('ix_admin_users_clerk_user_id'), 'admin_users', ['clerk_user_id'], unique=True)
    
    # Drop password_hash column (no longer needed with Clerk)
    op.drop_column('admin_users', 'password_hash')
    
    # Make clerk_user_id NOT NULL after migration
    op.execute("UPDATE admin_users SET clerk_user_id = 'TEMP_' || email WHERE clerk_user_id IS NULL")
    op.alter_column('admin_users', 'clerk_user_id', nullable=False)


def downgrade() -> None:
    # Restore password_hash column
    op.add_column('admin_users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    
    # Drop clerk_user_id
    op.drop_index(op.f('ix_admin_users_clerk_user_id'), table_name='admin_users')
    op.drop_column('admin_users', 'clerk_user_id')
