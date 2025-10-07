"""
Report Model
Generated investment reports and documents
"""

import enum

from app.models.base import BaseModel, UUIDMixin
from sqlalchemy import (Boolean, Column, DateTime, Enum, Float, ForeignKey,
                        Integer, LargeBinary, String, Text)
from sqlalchemy.orm import relationship


class ReportType(str, enum.Enum):
    """Types of reports generated"""
    PRELIMINARY = "preliminary"  # Quick assessment for church
    INVESTMENT = "investment"    # Full investment analysis
    EXECUTIVE_SUMMARY = "executive_summary"
    MARKET_ANALYSIS = "market_analysis"
    FINANCIAL_MODEL = "financial_model"


class ReportFormat(str, enum.Enum):
    """Report output formats"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


class ReportStatus(str, enum.Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(BaseModel, UUIDMixin):
    """Generated investment reports"""
    
    __tablename__ = "reports"
    
    # Relationships
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    assessment = relationship("Assessment", back_populates="reports")
    
    # Report Metadata
    report_type = Column(Enum(ReportType), nullable=False)
    report_format = Column(Enum(ReportFormat), default=ReportFormat.PDF, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    
    # Content Information
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=True)
    
    # File Information
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_content = Column(LargeBinary, nullable=True)  # Store PDF/HTML content
    download_count = Column(Integer, default=0, nullable=False)
    
    # Generation Metadata
    generated_by = Column(String(100), default="AI", nullable=False)  # "AI" or user ID
    generation_started_at = Column(DateTime(timezone=True), nullable=True)
    generation_completed_at = Column(DateTime(timezone=True), nullable=True)
    generation_duration_seconds = Column(Integer, nullable=True)
    
    # AI Model Information
    ai_model_used = Column(String(50), nullable=True)  # "gpt-3.5-turbo", "gpt-4", etc.
    ai_prompt_tokens = Column(Integer, nullable=True)
    ai_completion_tokens = Column(Integer, nullable=True)
    ai_cost_estimate = Column(Float, nullable=True)
    
    # Report Quality Metrics
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    charts_count = Column(Integer, nullable=True)
    
    # Access Control
    is_public = Column(Boolean, default=False, nullable=False)
    password_protected = Column(Boolean, default=False, nullable=False)
    access_password_hash = Column(String(255), nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Report(id={self.id}, type='{self.report_type}', status='{self.status}')>"
    
    @property
    def is_ready(self) -> bool:
        """Check if report is ready for download"""
        return self.status == ReportStatus.COMPLETED and bool(self.file_content)
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return 0.0
    
    @property
    def generation_time(self) -> int:
        """Get generation time in seconds"""
        if self.generation_started_at and self.generation_completed_at:
            delta = self.generation_completed_at - self.generation_started_at
            return int(delta.total_seconds())
        return 0
