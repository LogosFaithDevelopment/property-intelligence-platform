"""
Church Pydantic Schemas
Request/response schemas for church-related endpoints
"""

from pydantic import Field, EmailStr, HttpUrl, validator
from typing import Optional, List
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, UUIDMixin, AddressSchema
from app.models.church import ChurchStatus


class ChurchBase(BaseSchema):
    """Base church schema with common fields"""
    
    name: str = Field(..., min_length=3, max_length=255, description="Church name")
    legal_name: Optional[str] = Field(None, max_length=255, description="Legal organization name")
    denomination: Optional[str] = Field(None, max_length=100, description="Religious denomination")
    founded_year: Optional[int] = Field(None, ge=1600, le=2024, description="Year church was founded")
    
    # Contact Information
    primary_email: EmailStr = Field(..., description="Primary contact email")
    primary_phone: Optional[str] = Field(None, max_length=50, description="Primary phone number")
    website_url: Optional[HttpUrl] = Field(None, description="Church website URL")
    
    # Organization Details
    congregation_size: Optional[int] = Field(None, ge=1, le=100000, description="Number of congregation members")
    annual_budget: Optional[float] = Field(None, ge=0, description="Annual budget in USD")
    staff_count: Optional[int] = Field(None, ge=0, le=1000, description="Number of staff members")
    
    @validator('primary_phone')
    def validate_phone(cls, v):
        """Basic phone number validation"""
        if v is None:
            return v
        # Remove common separators
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v


class ChurchCreate(ChurchBase):
    """Schema for creating a new church"""
    
    # Tax-exempt information (required for verification)
    tax_exempt_id: Optional[str] = Field(None, max_length=50, description="Tax-exempt ID (EIN)")
    tax_exempt_status: Optional[str] = Field(None, max_length=50, description="Tax-exempt status type")
    
    # Address information
    street_address: Optional[str] = Field(None, max_length=255, description="Church street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP code")
    
    # Programs and experience
    community_programs: Optional[str] = Field(None, description="Community programs offered")
    current_ministries: Optional[str] = Field(None, description="Current ministry activities")
    previous_development_experience: bool = Field(default=False, description="Has previous development experience")
    development_experience_notes: Optional[str] = Field(None, description="Details about development experience")
    
    # Partnership preferences
    partnership_goals: Optional[str] = Field(None, description="Goals for development partnership")
    timeline_preference: Optional[str] = Field(None, description="Preferred development timeline")


class ChurchUpdate(BaseSchema):
    """Schema for updating church information"""
    
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    denomination: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1600, le=2024)
    
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = Field(None, max_length=50)
    website_url: Optional[HttpUrl] = None
    
    congregation_size: Optional[int] = Field(None, ge=1, le=100000)
    annual_budget: Optional[float] = Field(None, ge=0)
    staff_count: Optional[int] = Field(None, ge=0, le=1000)
    
    community_programs: Optional[str] = None
    current_ministries: Optional[str] = None
    partnership_goals: Optional[str] = None
    timeline_preference: Optional[str] = None


class ChurchResponse(ChurchBase, TimestampMixin, UUIDMixin):
    """Schema for church responses"""
    
    id: int = Field(..., description="Church ID")
    verification_status: ChurchStatus = Field(..., description="Verification status")
    verification_date: Optional[datetime] = Field(None, description="Date church was verified")
    
    # Address information
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "United States"
    
    # Computed properties
    is_verified: bool = Field(..., description="Whether church is verified")
    full_address: Optional[str] = Field(None, description="Formatted full address")
    display_name: str = Field(..., description="Display name for the church")
    
    # Development experience
    previous_development_experience: bool = False
    development_experience_notes: Optional[str] = None
    
    # Partnership info
    partnership_goals: Optional[str] = None
    timeline_preference: Optional[str] = None


class ChurchSummary(BaseSchema):
    """Lightweight church summary for lists"""
    
    id: int
    uuid: str
    name: str
    verification_status: ChurchStatus
    city: Optional[str] = None
    state: Optional[str] = None
    congregation_size: Optional[int] = None
    created_at: datetime


class ChurchVerification(BaseSchema):
    """Schema for church verification process"""
    
    verification_status: ChurchStatus = Field(..., description="New verification status")
    verification_notes: Optional[str] = Field(None, description="Verification notes")
    
    
class ChurchStats(BaseSchema):
    """Church statistics for dashboards"""
    
    total_churches: int = Field(..., description="Total number of churches")
    verified_churches: int = Field(..., description="Number of verified churches")
    pending_verification: int = Field(..., description="Churches pending verification")
    total_properties: int = Field(..., description="Total properties across all churches")
    active_assessments: int = Field(..., description="Active property assessments")
    
    # Recent activity
    new_churches_this_month: int = Field(..., description="New churches registered this month")
    completed_assessments_this_month: int = Field(..., description="Assessments completed this month")
