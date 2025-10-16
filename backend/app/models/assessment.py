"""
Assessment Model  
Represents the evaluation process and results for a property
"""

import enum

from app.models.base import BaseModel, UUIDMixin
from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AssessmentStatus(str, enum.Enum):
    """Assessment workflow status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class AssessmentPriority(str, enum.Enum):
    """Assessment priority for review queue"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Assessment(BaseModel, UUIDMixin):
    """Property assessment and evaluation results"""
    
    __tablename__ = "assessments"
    
    # Relationships
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    
    church = relationship("Church", back_populates="assessments")
    property_obj = relationship("Property", back_populates="assessments")
    
    # User Tracking (for authentication)
    user_id = Column(String(255), nullable=True, index=True)  # Clerk user ID
    
    # Assessment Metadata
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    priority = Column(Enum(AssessmentPriority), default=AssessmentPriority.MEDIUM, nullable=False)
    
    # Church Readiness Information
    congregation_approval = Column(Boolean, nullable=True)  # Has congregation voted?
    congregation_voted = Column(Boolean, nullable=True)  # Alias for congregation_approval
    vote_percentage = Column(Float, nullable=True)  # Percentage of congregation that voted yes
    leadership_support = Column(String(50), nullable=True)  # unanimous, majority, mixed, etc.
    denomination_approval_needed = Column(Boolean, nullable=True)  # Needs denomination approval
    timeline_readiness = Column(String(50), nullable=True)  # ready_now, 6_months, 1_year, exploring
    
    # Ownership and Property
    owns_property_free_clear = Column(Boolean, nullable=True)  # Owns property without debt
    willing_to_ground_lease = Column(Boolean, nullable=True)  # Willing to ground lease the property
    
    # Parking Requirements
    current_parking_spaces = Column(Integer, nullable=True)  # Current number of parking spaces
    parking_spaces_needed_after = Column(Integer, nullable=True)  # Parking needed after development
    
    # Development Preferences
    preferred_unit_count = Column(Integer, nullable=True)
    preferred_unit_types = Column(Text, nullable=True)  # JSON: ["studio", "1br", "2br"]
    affordability_target = Column(String(50), nullable=True)  # "30_ami", "60_ami", "80_ami"
    
    # Available Space for Development (Client-Provided)
    available_build_sqft = Column(Float, nullable=True)  # Square footage available for housing development
    available_build_acres = Column(Float, nullable=True)  # Acres available for housing (auto-calculated from sqft)
    build_area_notes = Column(Text, nullable=True)  # Additional context about available space (e.g., "Southeast corner of parking lot")
    
    # Partnership Terms
    revenue_sharing_preference = Column(String(50), nullable=True)
    development_involvement_level = Column(String(50), nullable=True)
    special_requirements = Column(Text, nullable=True)
    
    # Phase 2: Deal Breaker Fields (LOGOS Requirements)
    existing_debt_amount = Column(Float, nullable=True)  # Current church debt amount
    debt_to_value_ratio = Column(Float, nullable=True)  # Calculated: debt / assessed_value (deal breaker if >20%)
    expects_sanctuary_replacement = Column(Boolean, nullable=True)  # Does church expect new sanctuary?
    sanctuary_replacement_cost_estimate = Column(Float, nullable=True)  # Estimated cost if yes
    
    # Phase 3: Partnership Enhancement Fields (LOGOS Requirements)
    decision_making_authority = Column(String(50), nullable=True)  # "pastor", "board", "congregation", "denomination"
    decision_timeline = Column(String(50), nullable=True)  # "immediate", "1-3_months", "3-6_months", "6-12_months", "unsure"
    accepts_60_40_ownership = Column(Boolean, nullable=True)  # Willing to accept 60% LOGOS / 40% Church split
    willing_to_pay_deposit = Column(Boolean, nullable=True)  # Willing to pay $5K refundable deposit
    
    # AI Scoring Results (0-100 scale)
    overall_score = Column(Float, nullable=True)
    location_score = Column(Float, nullable=True)
    market_score = Column(Float, nullable=True)
    financial_score = Column(Float, nullable=True)
    partnership_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    
    # Detailed Analysis (JSON fields)
    market_analysis = Column(JSON, nullable=True)  # Demographics, demand, competition
    financial_projections = Column(JSON, nullable=True)  # Development costs, ROI, cash flow
    risk_factors = Column(JSON, nullable=True)  # Identified risks and mitigation
    comparable_projects = Column(JSON, nullable=True)  # Similar successful projects
    
    # API Data Cache
    api_data_census = Column(JSON, nullable=True)
    api_data_hud = Column(JSON, nullable=True)  
    api_data_fema = Column(JSON, nullable=True)
    api_data_attom = Column(JSON, nullable=True)  # Premium API data
    api_data_google = Column(JSON, nullable=True)
    
    # Processing Metadata
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration_seconds = Column(Integer, nullable=True)
    
    # Review Information
    reviewed_by = Column(String(255), nullable=True)  # Admin user who reviewed
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    # AI Report Generation
    report_generated = Column(Boolean, default=False, nullable=False)
    report_generated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships to reports
    reports = relationship("Report", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, property_id={self.property_id}, score={self.overall_score}, status='{self.status}')>"
    
    @property
    def is_high_opportunity(self) -> bool:
        """Check if this is a high-opportunity assessment"""
        return bool(self.overall_score and self.overall_score >= 75)
    
    @property
    def is_completed(self) -> bool:
        """Check if assessment is completed"""
        return self.status in [AssessmentStatus.COMPLETED, AssessmentStatus.REVIEWED, AssessmentStatus.APPROVED]
    
    @property
    def processing_time(self) -> int:
        """Get processing time in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            delta = self.processing_completed_at - self.processing_started_at
            return int(delta.total_seconds())
        return 0
    
    @property
    def score_grade(self) -> str:
        """
        Convert numeric score to letter grade
        
        Updated Oct 2025: Passing score raised to 70%
        Financial viability is now 100% of score (other factors informational only)
        """
        if not self.overall_score:
            return "N/A"
        
        # Passing grades (70%+)
        if self.overall_score >= 90:
            return "A+ (Excellent)"
        elif self.overall_score >= 85:
            return "A (Excellent)"
        elif self.overall_score >= 80:
            return "A- (Very Good)"
        elif self.overall_score >= 75:
            return "B+ (Good)"
        elif self.overall_score >= 70:
            return "B (Pass)"
        
        # Failing grades (<70%)
        elif self.overall_score >= 65:
            return "C+ (Below Target)"
        elif self.overall_score >= 60:
            return "C (Marginal)"
        elif self.overall_score >= 55:
            return "C- (Weak)"
        elif self.overall_score >= 50:
            return "D+ (Poor)"
        elif self.overall_score >= 40:
            return "D (Fail)"
        else:
            return "F (Reject)"
    
    @property
    def passes_threshold(self) -> bool:
        """
        Check if assessment passes the 70% threshold (Oct 2025)
        Based on financial viability only
        """
        return self.overall_score is not None and self.overall_score >= 70.0
    
    def start_processing(self):
        """Mark assessment as processing"""
        self.status = AssessmentStatus.PROCESSING
        self.processing_started_at = func.now()
    
    def complete_processing(self, overall_score: float):
        """Mark assessment as completed with score"""
        self.status = AssessmentStatus.COMPLETED
        self.processing_completed_at = func.now()
        self.overall_score = overall_score
        
        # Calculate processing duration
        if self.processing_started_at:
            delta = self.processing_completed_at - self.processing_started_at
            self.processing_duration_seconds = int(delta.total_seconds())
