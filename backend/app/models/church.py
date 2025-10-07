"""
Church/Organization Model
Represents faith-based organizations and their details
"""

import enum

from app.models.base import BaseModel, SoftDeleteMixin, UUIDMixin
from sqlalchemy import (Boolean, Column, DateTime, Enum, Float, Integer,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ChurchStatus(str, enum.Enum):
    """Church verification status"""
    PENDING = "pending"
    VERIFIED = "verified" 
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class Church(BaseModel, UUIDMixin, SoftDeleteMixin):
    """Church/Organization model"""
    
    __tablename__ = "churches"
    
    # User Tracking (for authentication)
    user_id = Column(String(255), nullable=True, index=True)  # Clerk user ID
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255), nullable=True)  # Official legal name if different
    denomination = Column(String(100), nullable=True)
    founded_year = Column(Integer, nullable=True)
    
    # Tax-Exempt Status
    tax_exempt_id = Column(String(50), nullable=True, unique=True)  # EIN or other tax ID
    tax_exempt_status = Column(String(50), nullable=True)  # 501(c)(3), etc.
    verification_status = Column(Enum(ChurchStatus), default=ChurchStatus.PENDING, nullable=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Contact Information
    primary_email = Column(String(255), nullable=False)
    primary_phone = Column(String(50), nullable=True)
    website_url = Column(String(255), nullable=True)
    
    # Physical Address
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), default="United States", nullable=False)
    
    # Organization Details
    congregation_size = Column(Integer, nullable=True)
    annual_budget = Column(Float, nullable=True)  # Optional financial info
    staff_count = Column(Integer, nullable=True)
    
    # Programs and Services
    community_programs = Column(Text, nullable=True)  # JSON string of programs
    current_ministries = Column(Text, nullable=True)  # Current ministry activities
    
    # Development Experience
    previous_development_experience = Column(Boolean, default=False, nullable=False)
    development_experience_notes = Column(Text, nullable=True)
    
    # Partnership Preferences
    partnership_goals = Column(Text, nullable=True)  # What they hope to achieve
    timeline_preference = Column(String(50), nullable=True)  # "immediate", "6-months", "1-year", etc.
    
    # Internal Notes (not visible to church)
    admin_notes = Column(Text, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    
    # Relationships
    properties = relationship("Property", back_populates="church", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="church", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Church(id={self.id}, name='{self.name}', status='{self.verification_status}')>"
    
    @property
    def is_verified(self) -> bool:
        """Check if church is verified"""
        return self.verification_status == ChurchStatus.VERIFIED
    
    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = [self.street_address, self.city, self.state, self.zip_code]
        return ", ".join(part for part in parts if part)
    
    @property
    def display_name(self) -> str:
        """Get display name (legal name if available, otherwise name)"""
        return self.legal_name or self.name
