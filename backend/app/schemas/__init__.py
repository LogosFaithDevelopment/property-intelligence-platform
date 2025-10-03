"""
Pydantic Schemas
Export all schemas for easy imports
"""

from app.schemas.assessment import (AssessmentBase, AssessmentCreate,
                                    AssessmentProcessRequest,
                                    AssessmentProcessResponse,
                                    AssessmentResponse, AssessmentScores,
                                    AssessmentUpdate)
from app.schemas.base import (AddressSchema, BaseSchema, LocationSchema,
                              TimestampMixin, UUIDMixin)
from app.schemas.church import (ChurchBase, ChurchCreate, ChurchResponse,
                                ChurchUpdate)
from app.schemas.property import (PropertyBase, PropertyCreate,
                                  PropertyResponse, PropertyUpdate)
from app.schemas.report import (ReportBase, ReportCreate,
                                ReportDownloadResponse, ReportGenerateRequest,
                                ReportGenerateResponse, ReportResponse,
                                ReportUpdate)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampMixin",
    "UUIDMixin",
    "AddressSchema",
    "LocationSchema",
    # Church
    "ChurchBase",
    "ChurchCreate",
    "ChurchUpdate",
    "ChurchResponse",
    # Property
    "PropertyBase",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyResponse",
    # Assessment
    "AssessmentBase",
    "AssessmentCreate",
    "AssessmentUpdate",
    "AssessmentResponse",
    "AssessmentScores",
    "AssessmentProcessRequest",
    "AssessmentProcessResponse",
    # Report
    "ReportBase",
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportGenerateRequest",
    "ReportGenerateResponse",
    "ReportDownloadResponse",
]
