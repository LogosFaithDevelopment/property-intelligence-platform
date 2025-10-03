"""
Routers package initialization
Import all routers for FastAPI application
"""

from app.routers import auth, churches, properties, assessments, reports

__all__ = [
    "auth",
    "churches", 
    "properties",
    "assessments",
    "reports"
]
