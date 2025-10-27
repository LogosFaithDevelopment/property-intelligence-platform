"""
Fix Alembic version table in production database
This script stamps the database at the version before our new migration
so that only the new migration runs.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings
from sqlalchemy import create_engine, text


def fix_alembic_version():
    """Stamp the production database with the correct Alembic version."""
    
    # Create sync engine for production
    database_url = settings.DATABASE_URL
    
    # Convert to psycopg2 for sync operations
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if "ssl=require" in database_url:
        database_url = database_url.replace("ssl=require", "sslmode=require")
    
    print(f"Connecting to database...")
    engine = create_engine(database_url)
    
    # The version before our new migration
    # Our new migration is: 9f125223ea94
    # The previous head was: z9y8x7w6v5u4
    target_version = "z9y8x7w6v5u4"
    
    with engine.connect() as conn:
        # Check current version
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current = result.fetchone()
        
        if current:
            print(f"Current Alembic version: {current[0]}")
        else:
            print("No Alembic version found!")
        
        # Update to the correct version
        print(f"\nUpdating Alembic version to: {target_version}")
        conn.execute(text("UPDATE alembic_version SET version_num = :version"), {"version": target_version})
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        new_version = result.fetchone()
        print(f"New Alembic version: {new_version[0]}")
        print("\n✅ Alembic version updated successfully!")
        print("Now deploy the backend again and only the new migration will run.")


if __name__ == "__main__":
    fix_alembic_version()
