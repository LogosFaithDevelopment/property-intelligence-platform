"""
Routers package initialization
Import all routers for FastAPI application
"""

from app.routers import assessments, auth, churches, properties, reports

__all__ = [
    "auth",
    "churches", 
    "properties",
    "assessments",
    "reports"
]
