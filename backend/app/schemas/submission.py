"""
Submission Pydantic Schemas
Request/response schemas for complete church property submissions
"""

from enum import Enum
from typing import List, Optional

from app.models.property import PropertyType
from app.schemas.base import BaseSchema
from pydantic import EmailStr, Field, HttpUrl, validator


# Enums for new fields
class DenominationalAffiliationEnum(str, Enum):
    """Denominational affiliation options"""
    NON_DENOMINATIONAL = "non_denominational"
    AME = "ame"
    BAPTIST = "baptist"
    COGIC = "cogic"
    UMC = "umc"
    OTHER = "other"


class BuildingConditionEnum(str, Enum):
    """Building condition rating"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


class PartnershipStructureEnum(str, Enum):
    """Partnership structure options"""
    GROUND_LEASE = "ground_lease"
    LIMITED_PARTNERSHIP = "limited_partnership"
    FEE_DEVELOPMENT = "fee_development"
    UNSURE = "unsure"


class TimelinePreferenceEnum(str, Enum):
    """Timeline preference options"""
    ZERO_TO_SIX_MONTHS = "0_6_months"
    SIX_TO_TWELVE_MONTHS = "6_12_months"
    TWELVE_PLUS_MONTHS = "12_plus_months"


class ChurchSubmissionData(BaseSchema):
    """Church data from submission form"""
    # Basic Information
    name: str = Field(..., min_length=3, max_length=255, description="Church name")
    legal_name: Optional[str] = Field(None, max_length=255, description="Legal organization name")
    denomination: Optional[str] = Field(None, max_length=100, description="Religious denomination")
    denominational_affiliation: Optional[DenominationalAffiliationEnum] = Field(None, description="Structured denominational affiliation")
    founded_year: Optional[int] = Field(None, ge=1600, le=2025, description="Year church was founded")
    member_count: Optional[int] = Field(None, ge=1, le=100000, description="Number of church members")
    
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
    
    # Property Condition & Site Assessment (NEW)
    building_condition: Optional[BuildingConditionEnum] = Field(None, description="Current building condition rating")
    site_condition_issues: Optional[List[str]] = Field(None, description="Site condition issues")
    exploration_reasons: Optional[List[str]] = Field(None, description="Reasons for exploring redevelopment")
    ministries_using_property: Optional[str] = Field(None, description="Which ministries use the property")
    
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
    
    # Multi-Address Support
    demolish_all_structures: Optional[bool] = Field(default=False, description="Plan to demolish all existing structures")
    additional_addresses: Optional[list] = Field(default=None, description="Additional addresses for multi-parcel properties")
    
    # Geospatial Data
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    
    # Property Details
    property_type: Optional[PropertyType] = Field(default=PropertyType.OTHER, description="Type of property")
    lot_size_sqft: Optional[float] = Field(None, ge=0, description="Lot size in square feet")
    current_usage: Optional[str] = Field(None, max_length=255, description="Current property usage")
    zoning_description: Optional[str] = Field(None, max_length=255, description="Zoning classification")
    
    # Financial Information (owner-provided estimate, separate from public assessed_value)
    market_value_estimate: Optional[float] = Field(None, ge=0, description="Owner's estimate of current market value")


class AssessmentSubmissionData(BaseSchema):
    """Assessment/preferences data from submission form"""
    # Ownership
    owns_property_free_clear: Optional[bool] = Field(None, description="Owns property free and clear")
    willing_to_ground_lease: Optional[bool] = Field(None, description="Willing to ground lease")
    existing_debt_amount: Optional[float] = Field(None, ge=0, description="Existing debt amount on the property in USD")
    
    # Property Debt & Restrictions (NEW)
    has_property_debt: Optional[bool] = Field(None, description="Does property have debt?")
    property_debt_amount: Optional[float] = Field(None, ge=0, description="Debt amount if yes")
    property_debt_terms: Optional[str] = Field(None, description="Debt terms/description if yes")
    has_transfer_restrictions: Optional[bool] = Field(None, description="Transfer/lease restrictions?")
    transfer_restrictions_description: Optional[str] = Field(None, description="Restriction description if yes")
    has_long_term_leases: Optional[bool] = Field(None, description="Existing leases/commitments?")
    long_term_leases_description: Optional[str] = Field(None, description="Lease description if yes")
    
    # Congregation Approval
    congregation_voted: Optional[bool] = Field(None, description="Has congregation voted")
    vote_percentage: Optional[float] = Field(None, ge=0, le=100, description="Vote percentage")
    leadership_support: Optional[str] = Field(None, max_length=50, description="Leadership support level")
    denomination_approval_needed: Optional[bool] = Field(None, description="Needs denomination approval")
    
    # Parking
    current_parking_spaces: Optional[int] = Field(None, ge=0, description="Current parking spaces")
    parking_spaces_needed_after: Optional[int] = Field(None, ge=0, description="Parking needed after development")
    sunday_parking_needed: Optional[int] = Field(None, ge=0, description="Parking needed on Sunday")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    
    # Timeline & Preferences
    timeline_readiness: Optional[str] = Field(None, max_length=50, description="Timeline readiness")
    preferred_unit_count: Optional[int] = Field(None, ge=1, le=1000, description="Preferred unit count")
    affordability_target: Optional[str] = Field(None, max_length=50, description="Affordability target")
    revenue_sharing_preference: Optional[str] = Field(None, max_length=50, description="Revenue sharing preference")
    development_involvement_level: Optional[str] = Field(None, max_length=50, description="Development involvement level")
    
    # Available Build Space
    available_build_sqft: Optional[float] = Field(None, ge=0, description="Available build space in sqft")
    build_area_notes: Optional[str] = Field(None, description="Build area constraints/notes")
    
    # Property Improvement & Financing Needs
    property_improvement_needs: Optional[List[str]] = Field(None, description="Property improvement needs checklist")
    capital_financing_need: Optional[str] = Field(None, max_length=100, description="Capital or financing need description")
    
    # Project Components & Priorities (NEW)
    project_components_wanted: Optional[List[str]] = Field(None, description="Wanted project components (housing, sanctuary, fellowship hall, etc.)")
    priority_ranking: Optional[List[str]] = Field(None, description="Ordered list of project priorities")
    
    # Partnership & Timeline (NEW)
    partnership_structure_preferences: Optional[List[str]] = Field(None, description="Partnership structure preferences")
    decision_making_structure: Optional[List[str]] = Field(None, description="Who makes decisions (pastor, board, trustees, congregation)")
    timeline_preference_new: Optional[TimelinePreferenceEnum] = Field(None, description="Structured timeline preference")
    reinvestment_preference: Optional[str] = Field(None, max_length=50, description="Reinvestment preference (yes/maybe/unsure)")
    
    @validator('property_debt_amount')
    def validate_debt_amount(cls, v, values):
        """Require debt amount if has_property_debt is True"""
        if values.get('has_property_debt') is True and v is None:
            raise ValueError('property_debt_amount is required when has_property_debt is True')
        return v
    
    @validator('transfer_restrictions_description')
    def validate_transfer_restrictions(cls, v, values):
        """Require description if has_transfer_restrictions is True"""
        if values.get('has_transfer_restrictions') is True and not v:
            raise ValueError('transfer_restrictions_description is required when has_transfer_restrictions is True')
        return v
    
    @validator('long_term_leases_description')
    def validate_leases(cls, v, values):
        """Require description if has_long_term_leases is True"""
        if values.get('has_long_term_leases') is True and not v:
            raise ValueError('long_term_leases_description is required when has_long_term_leases is True')
        return v


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
