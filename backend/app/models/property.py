"""
Property Model
Represents physical properties owned by churches
"""

from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.models.base import BaseModel, UUIDMixin, SoftDeleteMixin


class PropertyType(str, enum.Enum):
    """Property type classification"""
    VACANT_LAND = "vacant_land"
    CHURCH_BUILDING = "church_building"
    MIXED_USE = "mixed_use"
    PARKING_LOT = "parking_lot"
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    OTHER = "other"


class ZoningType(str, enum.Enum):
    """Common zoning classifications"""
    RESIDENTIAL_LOW = "residential_low_density"
    RESIDENTIAL_MEDIUM = "residential_medium_density"  
    RESIDENTIAL_HIGH = "residential_high_density"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    INSTITUTIONAL = "institutional"
    AGRICULTURAL = "agricultural"
    UNKNOWN = "unknown"


class Property(BaseModel, UUIDMixin, SoftDeleteMixin):
    """Property model for church-owned real estate"""
    
    __tablename__ = "properties"
    
    # Relationships
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    church = relationship("Church", back_populates="properties")
    
    # Basic Property Information
    name = Column(String(255), nullable=True)  # Property name/identifier
    property_type = Column(Enum(PropertyType), nullable=False)
    
    # Address Information
    street_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    county = Column(String(100), nullable=True)
    
    # Geospatial Data (PostGIS)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location = Column(Geography("POINT", srid=4326), nullable=True)  # PostGIS point
    
    # Property Details
    lot_size_sqft = Column(Float, nullable=True)
    lot_size_acres = Column(Float, nullable=True)
    building_sqft = Column(Float, nullable=True)
    year_built = Column(Integer, nullable=True)
    
    # Zoning and Legal
    zoning_classification = Column(Enum(ZoningType), default=ZoningType.UNKNOWN, nullable=False)
    zoning_description = Column(String(255), nullable=True)
    parcel_id = Column(String(100), nullable=True)  # APN/Parcel number
    
    # Financial Information
    assessed_value = Column(Float, nullable=True)
    market_value_estimate = Column(Float, nullable=True)
    annual_property_tax = Column(Float, nullable=True)
    
    # Current Usage
    current_usage = Column(Text, nullable=True)  # How church currently uses property
    usage_frequency = Column(String(50), nullable=True)  # daily, weekly, occasionally, vacant
    
    # Development Constraints
    flood_zone = Column(String(10), nullable=True)  # FEMA flood zone
    environmental_concerns = Column(Text, nullable=True)
    access_road_type = Column(String(50), nullable=True)  # paved, gravel, private, etc.
    
    # Utilities and Infrastructure
    has_water = Column(Boolean, default=True, nullable=False)
    has_sewer = Column(Boolean, default=True, nullable=False)
    has_electricity = Column(Boolean, default=True, nullable=False)
    has_gas = Column(Boolean, default=False, nullable=False)
    internet_available = Column(Boolean, default=True, nullable=False)
    
    # Church-Specific Information
    parking_spaces = Column(Integer, nullable=True)
    accessibility_features = Column(Text, nullable=True)  # ADA compliance, ramps, etc.
    
    # Data Sources and Timestamps
    data_sources = Column(Text, nullable=True)  # JSON of API sources used
    last_data_update = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assessments = relationship("Assessment", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property(id={self.id}, address='{self.street_address}', type='{self.property_type}')>"
    
    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
    
    @property
    def coordinates(self) -> tuple:
        """Get latitude, longitude as tuple"""
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        return None
    
    @property
    def lot_size_display(self) -> str:
        """Get human-readable lot size"""
        if self.lot_size_acres and self.lot_size_acres >= 0.1:
            return f"{self.lot_size_acres:.2f} acres"
        elif self.lot_size_sqft:
            return f"{self.lot_size_sqft:,.0f} sq ft"
        return "Size unknown"
    
    @property
    def is_developable(self) -> bool:
        """Basic check if property might be developable"""
        # Simple heuristic - can be improved with ML
        if not self.lot_size_sqft or self.lot_size_sqft < 5000:
            return False
        if self.flood_zone and self.flood_zone.startswith('A'):
            return False  # High flood risk
        return True
