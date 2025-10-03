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
    
    # Assessment Metadata
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.DRAFT, nullable=False)
    priority = Column(Enum(AssessmentPriority), default=AssessmentPriority.MEDIUM, nullable=False)
    
    # Church Readiness Information
    congregation_approval = Column(Boolean, nullable=True)  # Has congregation voted?
    leadership_support = Column(String(50), nullable=True)  # unanimous, majority, mixed, etc.
    timeline_readiness = Column(String(50), nullable=True)  # ready_now, 6_months, 1_year, exploring
    
    # Development Preferences
    preferred_unit_count = Column(Integer, nullable=True)
    preferred_unit_types = Column(Text, nullable=True)  # JSON: ["studio", "1br", "2br"]
    affordability_target = Column(String(50), nullable=True)  # "30_ami", "60_ami", "80_ami"
    
    # Partnership Terms
    revenue_sharing_preference = Column(String(50), nullable=True)
    development_involvement_level = Column(String(50), nullable=True)
    special_requirements = Column(Text, nullable=True)
    
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
        """Convert numeric score to letter grade"""
        if not self.overall_score:
            return "N/A"
        
        if self.overall_score >= 90:
            return "A+"
        elif self.overall_score >= 85:
            return "A"
        elif self.overall_score >= 80:
            return "A-"
        elif self.overall_score >= 75:
            return "B+"
        elif self.overall_score >= 70:
            return "B"
        elif self.overall_score >= 65:
            return "B-"
        elif self.overall_score >= 60:
            return "C+"
        elif self.overall_score >= 55:
            return "C"
        elif self.overall_score >= 50:
            return "C-"
        else:
            return "D"
    
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
