"""
FastAPI Application Entry Point
Property Intelligence Platform Backend
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import get_settings
from app.database import connect_with_retry, engine
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import (admin_actions, admin_auth, admin_stats, assessments,
                         auth, churches, health, properties, reports,
                         submissions)
# Import logging configuration
from app.utils.logging_config import get_logger, setup_logging

# Get settings
settings = get_settings()

# Configure logging (JSON format in production)
# Ensure early logging to stdout for CloudWatch
logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True)
setup_logging(
    log_level=settings.log_level,
    environment=settings.environment
)
logger = get_logger(__name__)

# Readiness state
_ready = {"db": False}

# Log missing environment variables (don't exit)
logger.info("🔍 Checking environment variables...")
required_env_vars = [
    "SECRET_KEY", "DATABASE_URL", "REDIS_URL", "CLERK_SECRET_KEY", 
    "OPENAI_API_KEY", "ATTOM_API_KEY", "GOOGLE_MAPS_API_KEY", 
    "SMARTY_AUTH_ID", "SMARTY_AUTH_TOKEN", "HUD_API_KEY"
]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
else:
    logger.info("✅ All required environment variables present")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Property Intelligence Platform...")
    
    # Don't block on database connection - let app start immediately
    # Database will be connected lazily on first use
    logger.info("⏭️  Skipping database connection during startup - will connect on first use")
    _ready["db"] = False
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down Property Intelligence Platform...")


# Create FastAPI application
app = FastAPI(
    title="Property Intelligence Platform API",
    description="AI-powered platform for church property evaluation and affordable housing development",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# Health check endpoints are now in routers/health.py


# Root endpoint - simple liveness probe (always returns 200)
@app.get("/")
async def root():
    """
    Liveness probe - returns 200 OK if application is running.
    Used by ALB health checks. Always returns success even if dependencies are unavailable.
    """
    return {"status": "ok"}


# Readiness endpoint - checks if all dependencies are ready
@app.get("/readyz")
async def readiness():
    """
    Readiness probe - returns status of dependencies.
    Returns 200 if all dependencies are ready, 503 if any are not ready.
    """
    if all(_ready.values()):
        return {"ready": True, "db": _ready["db"]}
    else:
        return JSONResponse(
            status_code=503,
            content={"ready": False, "db": _ready["db"]}
        )


# Info endpoint with API information
@app.get("/info")
async def info():
    """API information endpoint"""
    return {
        "message": "Welcome to Property Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs" if settings.environment == "development" else "Contact admin for API documentation",
        "health": "/health",
        "readiness": "/readyz"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.environment == "development":
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# Include routers
# Health checks (no prefix for ECS compatibility)
app.include_router(health.router, tags=["Health"])

# API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin_auth.router, prefix="/api/v1", tags=["Admin Auth"])
app.include_router(admin_stats.router)  # Admin stats (includes /api/v1 prefix)
app.include_router(admin_actions.router)  # Admin actions (includes /api/v1 prefix)
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["Submissions"])
app.include_router(churches.router, prefix="/api/v1/churches", tags=["Churches"])
app.include_router(properties.router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )
