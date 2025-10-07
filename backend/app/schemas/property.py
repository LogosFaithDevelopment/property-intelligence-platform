"""
Property Pydantic Schemas
Request/response schemas for property-related endpoints
"""

from datetime import datetime
from typing import List, Optional, Tuple

from app.models.property import PropertyType, ZoningType
from app.schemas.base import (AddressSchema, BaseSchema, LocationSchema,
                              TimestampMixin, UUIDMixin)
from pydantic import Field, validator


class PropertyBase(BaseSchema):
    """Base property schema with common fields"""
    
    name: Optional[str] = Field(None, max_length=255, description="Property name or identifier")
    property_type: PropertyType = Field(..., description="Type of property")
    
    # Current usage
    current_usage: Optional[str] = Field(None, description="How church currently uses the property")
    usage_frequency: Optional[str] = Field(None, description="How often property is used")
    
    # Basic property details
    lot_size_sqft: Optional[float] = Field(None, ge=0, description="Lot size in square feet")
    lot_size_acres: Optional[float] = Field(None, ge=0, description="Lot size in acres")
    building_sqft: Optional[float] = Field(None, ge=0, description="Building square footage")
    year_built: Optional[int] = Field(None, ge=1800, le=2024, description="Year building was constructed")
    
    # Utilities and infrastructure
    has_water: bool = Field(default=True, description="Has water service")
    has_sewer: bool = Field(default=True, description="Has sewer service")
    has_electricity: bool = Field(default=True, description="Has electrical service")
    has_gas: bool = Field(default=False, description="Has gas service")
    internet_available: bool = Field(default=True, description="Internet service available")
    
    # Church-specific features
    parking_spaces: Optional[int] = Field(None, ge=0, description="Number of parking spaces")
    accessibility_features: Optional[str] = Field(None, description="ADA accessibility features")
    
    @validator('lot_size_acres')
    def calculate_acres_from_sqft(cls, v, values):
        """Auto-calculate acres from square feet if not provided"""
        if v is None and 'lot_size_sqft' in values and values['lot_size_sqft']:
            return round(values['lot_size_sqft'] / 43560, 4)  # 43,560 sq ft per acre
        return v


class PropertyCreate(PropertyBase, AddressSchema, LocationSchema):
    """Schema for creating a new property"""
    
    church_id: int = Field(..., description="ID of the church that owns this property")
    
    # Additional creation fields
    environmental_concerns: Optional[str] = Field(None, description="Known environmental concerns")
    access_road_type: Optional[str] = Field(None, description="Type of road access")


class PropertyUpdate(BaseSchema):
    """Schema for updating property information"""
    
    name: Optional[str] = Field(None, max_length=255)
    property_type: Optional[PropertyType] = None
    current_usage: Optional[str] = None
    usage_frequency: Optional[str] = None
    
    lot_size_sqft: Optional[float] = Field(None, ge=0)
    lot_size_acres: Optional[float] = Field(None, ge=0)
    building_sqft: Optional[float] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2024)
    
    # Utilities
    has_water: Optional[bool] = None
    has_sewer: Optional[bool] = None
    has_electricity: Optional[bool] = None
    has_gas: Optional[bool] = None
    internet_available: Optional[bool] = None
    
    # Features
    parking_spaces: Optional[int] = Field(None, ge=0)
    accessibility_features: Optional[str] = None
    environmental_concerns: Optional[str] = None


class PropertyResponse(PropertyBase, TimestampMixin, UUIDMixin, AddressSchema, LocationSchema):
    """Schema for property responses"""
    
    id: int = Field(..., description="Property ID")
    church_id: int = Field(..., description="Owning church ID")
    
    # Zoning information
    zoning_classification: ZoningType = Field(..., description="Zoning classification")
    zoning_description: Optional[str] = Field(None, description="Detailed zoning description")
    parcel_id: Optional[str] = Field(None, description="Parcel/APN number")
    
    # Financial information
    assessed_value: Optional[float] = Field(None, description="Assessed property value")
    market_value_estimate: Optional[float] = Field(None, description="Estimated market value")
    annual_property_tax: Optional[float] = Field(None, description="Annual property tax")
    
    # Risk factors
    flood_zone: Optional[str] = Field(None, description="FEMA flood zone")
    environmental_concerns: Optional[str] = None
    access_road_type: Optional[str] = None
    
    # Data metadata  
    data_sources: Optional[str] = Field(None, description="API sources used for data")
    last_data_update: Optional[datetime] = Field(None, description="When property data was last updated")
    
    # Computed properties
    full_address: str = Field(..., description="Formatted full address")
    coordinates: Optional[Tuple[float, float]] = Field(None, description="Latitude, longitude coordinates")
    lot_size_display: str = Field(..., description="Human-readable lot size")
    is_developable: bool = Field(..., description="Basic developability assessment")


class PropertySummary(BaseSchema):
    """Lightweight property summary for lists"""
    
    id: int
    uuid: str
    name: Optional[str] = None
    property_type: PropertyType
    street_address: str
    city: str
    state: str
    lot_size_display: str
    assessed_value: Optional[float] = None
    created_at: datetime


class PropertyEnrichment(BaseSchema):
    """Schema for property data enrichment from APIs"""
    
    # Market data
    estimated_value: Optional[float] = Field(None, description="AI estimated property value")
    comparable_sales: Optional[List[dict]] = Field(None, description="Recent comparable sales")
    rental_estimates: Optional[dict] = Field(None, description="Rental market estimates")
    
    # Demographics
    demographics: Optional[dict] = Field(None, description="Census demographic data")
    income_levels: Optional[dict] = Field(None, description="Area income statistics")
    housing_demand: Optional[dict] = Field(None, description="Housing demand indicators")
    
    # Risk assessment
    flood_risk: Optional[dict] = Field(None, description="Flood risk assessment")
    environmental_risks: Optional[List[str]] = Field(None, description="Environmental risk factors")
    seismic_risk: Optional[dict] = Field(None, description="Earthquake risk data")
    
    # Transit and amenities
    walkability_score: Optional[int] = Field(None, ge=0, le=100, description="Walk Score rating")
    transit_score: Optional[int] = Field(None, ge=0, le=100, description="Transit accessibility score")
    nearby_amenities: Optional[List[dict]] = Field(None, description="Nearby amenities and services")
    
    # Development potential
    max_units_estimate: Optional[int] = Field(None, ge=0, description="Estimated maximum housing units")
    development_costs: Optional[dict] = Field(None, description="Estimated development costs")
    zoning_restrictions: Optional[List[str]] = Field(None, description="Zoning restrictions")


class PropertyAnalytics(BaseSchema):
    """Property analytics and insights"""
    
    total_properties: int = Field(..., description="Total number of properties")
    by_type: dict = Field(..., description="Properties grouped by type")
    by_state: dict = Field(..., description="Properties grouped by state")
    
    # Value statistics
    total_assessed_value: Optional[float] = Field(None, description="Total assessed value of all properties")
    average_lot_size: Optional[float] = Field(None, description="Average lot size in acres")
    
    # Development potential
    developable_properties: int = Field(..., description="Number of potentially developable properties")
    estimated_total_units: Optional[int] = Field(None, description="Estimated total housing units possible")
    
    # Recent activity
    new_properties_this_month: int = Field(..., description="Properties added this month")
    updated_properties_this_month: int = Field(..., description="Properties updated this month")
