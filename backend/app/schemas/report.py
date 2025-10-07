"""
Report Pydantic Schemas
Request/response schemas for generated reports
"""

from datetime import datetime
from typing import Optional

from app.models.report import ReportFormat, ReportStatus, ReportType
from app.schemas.base import BaseSchema, TimestampMixin, UUIDMixin
from pydantic import Field, HttpUrl


class ReportBase(BaseSchema):
    """Base report schema with common fields"""
    
    title: str = Field(..., min_length=3, max_length=255, description="Report title")
    report_type: ReportType = Field(..., description="Type of report")
    report_format: ReportFormat = Field(default=ReportFormat.PDF, description="Output format")
    
    # Optional customization
    include_maps: bool = Field(default=True, description="Include location maps")
    include_demographics: bool = Field(default=True, description="Include demographic analysis")
    include_financials: bool = Field(default=True, description="Include financial projections")
    include_comparables: bool = Field(default=True, description="Include comparable projects")
    
    # Branding
    custom_branding: Optional[str] = Field(None, description="Custom branding/logo URL")
    recipient_name: Optional[str] = Field(None, max_length=255, description="Report recipient name")
    recipient_organization: Optional[str] = Field(None, max_length=255, description="Recipient organization")


class ReportCreate(ReportBase):
    """Schema for creating/generating a new report"""
    
    church_id: int = Field(..., description="Church ID")
    property_id: int = Field(..., description="Property ID")
    assessment_id: int = Field(..., description="Assessment ID to generate report from")


class ReportUpdate(BaseSchema):
    """Schema for updating report metadata"""
    
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    status: Optional[ReportStatus] = None
    recipient_name: Optional[str] = Field(None, max_length=255)
    recipient_organization: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class ReportResponse(ReportBase, TimestampMixin, UUIDMixin):
    """Full report response with all data"""
    
    id: int
    church_id: int
    property_id: int
    assessment_id: int
    
    status: ReportStatus
    
    # File Information
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    
    # Generation Metadata
    generated_at: Optional[datetime] = None
    generated_by: Optional[str] = None
    generation_duration_seconds: Optional[int] = None
    
    # Access Information
    download_count: int = 0
    last_downloaded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # AI Generation Details
    ai_model_used: Optional[str] = None
    ai_tokens_used: Optional[int] = None
    ai_cost_usd: Optional[float] = None
    
    # Additional Notes
    notes: Optional[str] = None
    
    # Computed Properties
    is_ready: bool = Field(False, description="Report is ready for download")
    is_expired: bool = Field(False, description="Report has expired")
    file_size_display: str = Field("N/A", description="Human-readable file size")
    download_url: Optional[str] = Field(None, description="Download URL if ready")
    
    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseSchema):
    """Request to generate a report"""
    
    assessment_id: int = Field(..., description="Assessment to generate report from")
    report_type: ReportType = Field(
        default=ReportType.INVESTMENT,
        description="Type of report to generate"
    )
    report_format: ReportFormat = Field(
        default=ReportFormat.PDF,
        description="Output format"
    )
    
    # Customization options
    include_maps: bool = Field(default=True)
    include_demographics: bool = Field(default=True)
    include_financials: bool = Field(default=True)
    include_comparables: bool = Field(default=True)
    
    recipient_name: Optional[str] = Field(None, max_length=255)
    recipient_organization: Optional[str] = Field(None, max_length=255)
    
    # AI Model Selection
    ai_model: str = Field(
        default="gpt-4o",
        description="AI model to use for generation (gpt-4o, gpt-4o-mini)"
    )


class ReportGenerateResponse(BaseSchema):
    """Response from report generation request"""
    
    success: bool
    message: str
    report_id: int
    status: ReportStatus
    estimated_completion_seconds: Optional[int] = Field(
        default=120,
        description="Estimated time to generate report"
    )


class ReportDownloadResponse(BaseSchema):
    """Response with download information"""
    
    report_id: int
    filename: str
    file_size_bytes: int
    download_url: str
    expires_at: Optional[datetime] = None
