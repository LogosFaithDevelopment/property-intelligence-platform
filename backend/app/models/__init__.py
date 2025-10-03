"""
Models package initialization
Import all models to ensure they're registered with SQLAlchemy
"""

from app.models.base import BaseModel, UUIDMixin, SoftDeleteMixin
from app.models.church import Church, ChurchStatus
from app.models.property import Property, PropertyType, ZoningType
from app.models.assessment import Assessment, AssessmentStatus, AssessmentPriority
from app.models.report import Report, ReportType, ReportFormat, ReportStatus
from app.models.api_cache import APICache

# Export all models for easy imports
__all__ = [
    # Base classes
    "BaseModel",
    "UUIDMixin", 
    "SoftDeleteMixin",
    
    # Models
    "Church",
    "Property", 
    "Assessment",
    "Report",
    "APICache",
    
    # Enums
    "ChurchStatus",
    "PropertyType",
    "ZoningType", 
    "AssessmentStatus",
    "AssessmentPriority",
    "ReportType",
    "ReportFormat",
    "ReportStatus",
]
