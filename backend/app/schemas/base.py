"""
Base Pydantic Schemas
Common base classes and utilities for all schemas
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    
    created_at: datetime
    updated_at: datetime


class UUIDMixin(BaseModel):
    """Mixin for UUID fields"""
    
    uuid: str = Field(..., description="Unique identifier")


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Page size (max 100)")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Standard paginated response format"""
    
    items: List[BaseSchema]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    @classmethod
    def create(cls, items: List[BaseSchema], total: int, page: int, size: int):
        """Create paginated response"""
        import math
        pages = math.ceil(total / size) if total > 0 else 1
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class ErrorResponse(BaseModel):
    """Standard error response format"""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Standard success response format"""
    
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")


class LocationSchema(BaseModel):
    """Geographic location information"""
    
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    
    @property
    def coordinates(self) -> Optional[tuple]:
        """Get coordinates as tuple"""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None


class AddressSchema(BaseModel):
    """Standard address format"""
    
    street_address: str = Field(..., min_length=5, max_length=255, description="Street address")
    city: str = Field(..., min_length=2, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=50, description="State or province")
    zip_code: str = Field(..., min_length=5, max_length=20, description="ZIP or postal code")
    county: Optional[str] = Field(None, max_length=100, description="County name")
    country: str = Field(default="United States", max_length=100, description="Country name")
    
    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = [self.street_address, self.city, f"{self.state} {self.zip_code}"]
        return ", ".join(parts)
