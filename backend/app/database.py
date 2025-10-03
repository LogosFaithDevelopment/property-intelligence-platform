"""
Database Configuration and Setup
SQLAlchemy 2.0 with async support and PostGIS for geospatial queries
"""

import logging

from app.config import get_settings
from sqlalchemy import MetaData, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.is_development,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create declarative base with naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        # Enable PostGIS extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        
        # Import all models to ensure they're registered
        from app.models import api_cache, assessment, church, property, report

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# SQLite specific configuration (for testing)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite"""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Database utility functions
async def check_db_connection() -> bool:
    """Check if database connection is working"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def get_db_info() -> dict:
    """Get database information for health checks"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            
            # Check PostGIS
            try:
                result = await conn.execute("SELECT PostGIS_Version()")
                postgis_version = result.scalar()
            except:
                postgis_version = "Not available"
            
            return {
                "status": "connected",
                "version": version,
                "postgis_version": postgis_version,
                "url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "localhost"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
