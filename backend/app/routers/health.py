"""
Health Check Endpoints
For monitoring application and database health in production (AWS ECS, etc.)
"""

from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint
    Returns 200 OK if the application is running
    Used by AWS ECS/load balancers for basic health monitoring
    """
    return {
        "status": "healthy",
        "service": "property-intelligence-platform-backend"
    }


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check endpoint
    Returns 200 OK if database connection is working
    Used for monitoring database connectivity in production
    """
    try:
        # Execute a simple query to check database connectivity
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
        
        return {
            "status": "healthy",
            "service": "property-intelligence-platform-backend",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
