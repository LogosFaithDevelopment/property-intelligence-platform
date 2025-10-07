"""
Submission Pydantic Schemas
Request/response schemas for complete church property submissions
"""

from typing import Optional

from app.models.property import PropertyType
from app.schemas.base import BaseSchema
from pydantic import EmailStr, Field, HttpUrl


class ChurchSubmissionData(BaseSchema):
    """Church data from submission form"""
    # Basic Information
    name: str = Field(..., min_length=3, max_length=255, description="Church name")
    legal_name: Optional[str] = Field(None, max_length=255, description="Legal organization name")
    denomination: Optional[str] = Field(None, max_length=100, description="Religious denomination")
    founded_year: Optional[int] = Field(None, ge=1600, le=2025, description="Year church was founded")
    
    # Tax-exempt information
    tax_exempt_status: Optional[str] = Field(None, max_length=50, description="Entity type")
    tax_exempt_id: Optional[str] = Field(None, max_length=50, description="EIN number")
    
    # Contact Information
    primary_email: EmailStr = Field(..., description="Primary contact email")
    primary_phone: Optional[str] = Field(None, max_length=50, description="Primary phone number")
    website_url: Optional[HttpUrl] = Field(None, description="Church website URL")
    
    # Address Information
    street_address: Optional[str] = Field(None, max_length=255, description="Church street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP code")
    
    # Organization Details
    congregation_size: Optional[int] = Field(None, ge=1, le=100000, description="Number of members")
    annual_budget: Optional[float] = Field(None, ge=0, description="Annual budget in USD")
    
    # Partnership Preferences
    partnership_goals: Optional[str] = Field(None, description="Goals for partnership")
    timeline_preference: Optional[str] = Field(None, max_length=50, description="Preferred timeline")


class PropertySubmissionData(BaseSchema):
    """Property data from submission form"""
    # Property Address
    street_address: str = Field(..., max_length=255, description="Property street address")
    city: str = Field(..., max_length=100, description="City")
    state: str = Field(..., max_length=50, description="State")
    zip_code: str = Field(..., max_length=20, description="ZIP code")
    
    # Geospatial Data
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    
    # Property Details
    property_type: Optional[PropertyType] = Field(default=PropertyType.OTHER, description="Type of property")
    lot_size_sqft: Optional[float] = Field(None, ge=0, description="Lot size in square feet")
    current_usage: Optional[str] = Field(None, max_length=255, description="Current property usage")
    zoning_description: Optional[str] = Field(None, max_length=255, description="Zoning classification")


class AssessmentSubmissionData(BaseSchema):
    """Assessment/preferences data from submission form"""
    # Ownership
    owns_property_free_clear: Optional[bool] = Field(None, description="Owns property free and clear")
    willing_to_ground_lease: Optional[bool] = Field(None, description="Willing to ground lease")
    
    # Congregation Approval
    congregation_voted: Optional[bool] = Field(None, description="Has congregation voted")
    vote_percentage: Optional[float] = Field(None, ge=0, le=100, description="Vote percentage")
    leadership_support: Optional[str] = Field(None, max_length=50, description="Leadership support level")
    denomination_approval_needed: Optional[bool] = Field(None, description="Needs denomination approval")
    
    # Parking
    current_parking_spaces: Optional[int] = Field(None, ge=0, description="Current parking spaces")
    parking_spaces_needed_after: Optional[int] = Field(None, ge=0, description="Parking needed after development")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    
    # Timeline & Preferences
    timeline_readiness: Optional[str] = Field(None, max_length=50, description="Timeline readiness")
    preferred_unit_count: Optional[int] = Field(None, ge=1, le=1000, description="Preferred unit count")
    affordability_target: Optional[str] = Field(None, max_length=50, description="Affordability target")
    revenue_sharing_preference: Optional[str] = Field(None, max_length=50, description="Revenue sharing preference")
    development_involvement_level: Optional[str] = Field(None, max_length=50, description="Development involvement level")
    
    # Available Build Space (NEW FIELDS)
    available_build_sqft: Optional[float] = Field(None, ge=0, description="Available build space in sqft")
    build_area_notes: Optional[str] = Field(None, description="Build area constraints/notes")


class SubmissionCreate(BaseSchema):
    """Complete submission payload with church, property, and assessment data"""
    church: ChurchSubmissionData
    property: PropertySubmissionData
    assessment: AssessmentSubmissionData


class SubmissionResponse(BaseSchema):
    """Response after creating a submission"""
    church_id: int = Field(..., description="Created church ID")
    property_id: int = Field(..., description="Created property ID")
    assessment_id: int = Field(..., description="Created assessment ID")
    message: str = Field(default="Submission created successfully")
    enrichment_started: bool = Field(default=False, description="Whether enrichment was triggered")
