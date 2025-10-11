"""
Admin Statistics Router
Provides aggregated statistics and analytics for the admin dashboard
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.database import get_db
from app.models.admin_user import AdminRole
from app.models.assessment import Assessment, AssessmentStatus
from app.models.church import Church
from app.models.property import Property
from app.routers.admin_auth import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/api/v1/admin/stats", tags=["admin-stats"])


# Response Models
class StatusCount(BaseModel):
    status: str
    count: int


class DashboardStats(BaseModel):
    total_submissions: int
    pending_submissions: int
    approved_submissions: int
    rejected_submissions: int
    processing_submissions: int
    total_churches: int
    total_properties: int
    avg_score: Optional[float]
    status_breakdown: List[StatusCount]


class RecentSubmission(BaseModel):
    id: int
    church_name: str
    property_address: str
    status: str
    overall_score: Optional[float]
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class TrendDataPoint(BaseModel):
    date: str
    count: int


class AdminTrends(BaseModel):
    submissions_by_day: List[TrendDataPoint]
    approvals_by_day: List[TrendDataPoint]


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    """
    Get aggregated statistics for admin dashboard
    Requires admin role
    """
    
    # Total submissions
    total_result = await db.execute(select(func.count(Assessment.id)))
    total_submissions = total_result.scalar() or 0
    
    # Pending submissions (submitted + processing)
    pending_result = await db.execute(
        select(func.count(Assessment.id)).where(
            Assessment.status.in_([AssessmentStatus.SUBMITTED, AssessmentStatus.PROCESSING])
        )
    )
    pending_submissions = pending_result.scalar() or 0
    
    # Approved submissions
    approved_result = await db.execute(
        select(func.count(Assessment.id)).where(Assessment.status == AssessmentStatus.APPROVED)
    )
    approved_submissions = approved_result.scalar() or 0
    
    # Rejected submissions
    rejected_result = await db.execute(
        select(func.count(Assessment.id)).where(Assessment.status == AssessmentStatus.REJECTED)
    )
    rejected_submissions = rejected_result.scalar() or 0
    
    # Processing submissions
    processing_result = await db.execute(
        select(func.count(Assessment.id)).where(Assessment.status == AssessmentStatus.PROCESSING)
    )
    processing_submissions = processing_result.scalar() or 0
    
    # Total churches
    churches_result = await db.execute(select(func.count(Church.id)))
    total_churches = churches_result.scalar() or 0
    
    # Total properties
    properties_result = await db.execute(select(func.count(Property.id)))
    total_properties = properties_result.scalar() or 0
    
    # Average score (only for completed assessments with scores)
    avg_score_result = await db.execute(
        select(func.avg(Assessment.overall_score)).where(
            and_(
                Assessment.overall_score.isnot(None),
                Assessment.status.in_([
                    AssessmentStatus.COMPLETED,
                    AssessmentStatus.REVIEWED,
                    AssessmentStatus.APPROVED
                ])
            )
        )
    )
    avg_score = avg_score_result.scalar()
    if avg_score:
        avg_score = round(float(avg_score), 1)
    
    # Status breakdown
    status_result = await db.execute(
        select(
            Assessment.status,
            func.count(Assessment.id)
        ).group_by(Assessment.status)
    )
    status_breakdown = [
        StatusCount(status=status.value, count=count)
        for status, count in status_result.all()
    ]
    
    return DashboardStats(
        total_submissions=total_submissions,
        pending_submissions=pending_submissions,
        approved_submissions=approved_submissions,
        rejected_submissions=rejected_submissions,
        processing_submissions=processing_submissions,
        total_churches=total_churches,
        total_properties=total_properties,
        avg_score=avg_score,
        status_breakdown=status_breakdown
    )


@router.get("/recent-submissions", response_model=List[RecentSubmission])
async def get_recent_submissions(
    request: Request,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    """
    Get recent submissions for dashboard
    Requires admin role
    """
    
    result = await db.execute(
        select(
            Assessment.id,
            Church.name.label("church_name"),
            Property.street_address.label("property_address"),
            Assessment.status,
            Assessment.overall_score,
            Assessment.created_at.label("submitted_at")
        )
        .join(Church, Assessment.church_id == Church.id)
        .join(Property, Assessment.property_id == Property.id)
        .order_by(desc(Assessment.created_at))
        .limit(limit)
    )
    
    rows = result.all()
    return [
        RecentSubmission(
            id=row.id,
            church_name=row.church_name,
            property_address=row.property_address,
            status=row.status.value,
            overall_score=row.overall_score,
            submitted_at=row.submitted_at
        )
        for row in rows
    ]


@router.get("/trends", response_model=AdminTrends)
async def get_admin_trends(
    request: Request,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    """
    Get trend data for charts
    Requires admin role
    """
    
    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    # Submissions by day
    submissions_result = await db.execute(
        select(
            func.date(Assessment.created_at).label("date"),
            func.count(Assessment.id).label("count")
        )
        .where(Assessment.created_at >= start_date)
        .group_by(func.date(Assessment.created_at))
        .order_by(func.date(Assessment.created_at))
    )
    
    submissions_by_day = [
        TrendDataPoint(date=str(row.date), count=row.count)
        for row in submissions_result.all()
    ]
    
    # Approvals by day
    approvals_result = await db.execute(
        select(
            func.date(Assessment.updated_at).label("date"),
            func.count(Assessment.id).label("count")
        )
        .where(
            and_(
                Assessment.status == AssessmentStatus.APPROVED,
                Assessment.updated_at >= start_date
            )
        )
        .group_by(func.date(Assessment.updated_at))
        .order_by(func.date(Assessment.updated_at))
    )
    
    approvals_by_day = [
        TrendDataPoint(date=str(row.date), count=row.count)
        for row in approvals_result.all()
    ]
    
    return AdminTrends(
        submissions_by_day=submissions_by_day,
        approvals_by_day=approvals_by_day
    )


class SubmissionListItem(BaseModel):
    id: int
    church_name: str
    property_address: str
    status: str
    overall_score: Optional[float]
    submitted_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionList(BaseModel):
    total: int
    submissions: List[SubmissionListItem]


@router.get("/submissions", response_model=SubmissionList)
async def list_all_submissions(
    request: Request,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    """
    List all submissions with optional filtering
    Requires admin role
    """
    
    # Build query
    query = (
        select(
            Assessment.id,
            Church.name.label("church_name"),
            Property.street_address.label("property_address"),
            Assessment.status,
            Assessment.overall_score,
            Assessment.created_at.label("submitted_at"),
            Assessment.updated_at
        )
        .join(Church, Assessment.church_id == Church.id)
        .join(Property, Assessment.property_id == Property.id)
    )
    
    # Apply status filter if provided
    if status:
        try:
            status_enum = AssessmentStatus(status.upper())
            query = query.where(Assessment.status == status_enum)
        except ValueError:
            pass  # Invalid status, ignore filter
    
    # Get total count
    count_query = select(func.count()).select_from(
        query.subquery()
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(desc(Assessment.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    submissions = [
        SubmissionListItem(
            id=row.id,
            church_name=row.church_name,
            property_address=row.property_address,
            status=row.status.value,
            overall_score=row.overall_score,
            submitted_at=row.submitted_at,
            updated_at=row.updated_at
        )
        for row in rows
    ]
    
    return SubmissionList(
        total=total,
        submissions=submissions
    )


class AssessmentDetail(BaseModel):
    id: int
    status: str
    overall_score: Optional[float]
    location_score: Optional[float]
    market_score: Optional[float]
    financial_score: Optional[float]
    partnership_score: Optional[float]
    risk_score: Optional[float]
    market_analysis: Optional[Dict[str, Any]]
    financial_projections: Optional[Dict[str, Any]]
    risk_factors: Optional[Dict[str, Any]]
    comparable_projects: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    reviewer_notes: Optional[str]
    
    # Church data
    church_id: int
    church_name: str
    church_legal_name: Optional[str]
    church_denomination: Optional[str]
    church_founded_year: Optional[int]
    church_tax_exempt_status: Optional[str]
    church_tax_exempt_id: Optional[str]
    church_primary_email: str
    church_primary_phone: Optional[str]
    church_website_url: Optional[str]
    church_street_address: Optional[str]
    church_city: Optional[str]
    church_state: Optional[str]
    church_zip_code: Optional[str]
    church_congregation_size: Optional[int]
    church_annual_budget: Optional[float]
    
    # Property data
    property_id: int
    property_street_address: Optional[str]
    property_city: Optional[str]
    property_state: Optional[str]
    property_zip_code: Optional[str]
    property_county: Optional[str]
    property_latitude: Optional[float]
    property_longitude: Optional[float]
    property_type: Optional[str]
    property_lot_size_sqft: Optional[int]
    property_lot_size_acres: Optional[float]
    property_current_usage: Optional[str]
    property_zoning_classification: Optional[str]
    property_zoning_description: Optional[str]
    property_assessed_value: Optional[float]
    property_data_sources: Optional[str]  # JSON string with enriched data from APIs
    property_building_sqft: Optional[float]
    property_year_built: Optional[int]
    property_additional_addresses: Optional[List[Dict[str, Any]]]  # Additional addresses with enriched data
    property_demolish_all_structures: Optional[bool]
    
    class Config:
        from_attributes = True


@router.get("/submissions/{submission_id}", response_model=AssessmentDetail)
async def get_submission_detail(
    submission_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    """
    Get full details of a single submission including church and property data
    Requires admin role
    """
    
    result = await db.execute(
        select(
            Assessment.id,
            Assessment.status,
            Assessment.overall_score,
            Assessment.location_score,
            Assessment.market_score,
            Assessment.financial_score,
            Assessment.partnership_score,
            Assessment.risk_score,
            Assessment.market_analysis,
            Assessment.financial_projections,
            Assessment.risk_factors,
            Assessment.comparable_projects,
            Assessment.created_at,
            Assessment.updated_at,
            Assessment.reviewer_notes,
            # Church data
            Church.id.label("church_id"),
            Church.name.label("church_name"),
            Church.legal_name.label("church_legal_name"),
            Church.denomination.label("church_denomination"),
            Church.founded_year.label("church_founded_year"),
            Church.tax_exempt_status.label("church_tax_exempt_status"),
            Church.tax_exempt_id.label("church_tax_exempt_id"),
            Church.primary_email.label("church_primary_email"),
            Church.primary_phone.label("church_primary_phone"),
            Church.website_url.label("church_website_url"),
            Church.street_address.label("church_street_address"),
            Church.city.label("church_city"),
            Church.state.label("church_state"),
            Church.zip_code.label("church_zip_code"),
            Church.congregation_size.label("church_congregation_size"),
            Church.annual_budget.label("church_annual_budget"),
            # Property data
            Property.id.label("property_id"),
            Property.street_address.label("property_street_address"),
            Property.city.label("property_city"),
            Property.state.label("property_state"),
            Property.zip_code.label("property_zip_code"),
            Property.county.label("property_county"),
            Property.latitude.label("property_latitude"),
            Property.longitude.label("property_longitude"),
            Property.property_type.label("property_type"),
            Property.lot_size_sqft.label("property_lot_size_sqft"),
            Property.lot_size_acres.label("property_lot_size_acres"),
            Property.current_usage.label("property_current_usage"),
            Property.zoning_classification.label("property_zoning_classification"),
            Property.zoning_description.label("property_zoning_description"),
            Property.assessed_value.label("property_assessed_value"),
            Property.data_sources.label("property_data_sources"),
            Property.building_sqft.label("property_building_sqft"),
            Property.year_built.label("property_year_built"),
            Property.additional_addresses.label("property_additional_addresses"),
            Property.demolish_all_structures.label("property_demolish_all_structures"),
        )
        .join(Church, Assessment.church_id == Church.id)
        .join(Property, Assessment.property_id == Property.id)
        .where(Assessment.id == submission_id)
    )
    
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {submission_id} not found"
        )
    
    return AssessmentDetail(
        id=row.id,
        status=row.status.value,
        overall_score=row.overall_score,
        location_score=row.location_score,
        market_score=row.market_score,
        financial_score=row.financial_score,
        partnership_score=row.partnership_score,
        risk_score=row.risk_score,
        market_analysis=row.market_analysis,
        financial_projections=row.financial_projections,
        risk_factors=row.risk_factors,
        comparable_projects=row.comparable_projects,
        created_at=row.created_at,
        updated_at=row.updated_at,
        reviewer_notes=row.reviewer_notes,
        # Church data
        church_id=row.church_id,
        church_name=row.church_name,
        church_legal_name=row.church_legal_name,
        church_denomination=row.church_denomination,
        church_founded_year=row.church_founded_year,
        church_tax_exempt_status=row.church_tax_exempt_status,
        church_tax_exempt_id=row.church_tax_exempt_id,
        church_primary_email=row.church_primary_email,
        church_primary_phone=row.church_primary_phone,
        church_website_url=row.church_website_url,
        church_street_address=row.church_street_address,
        church_city=row.church_city,
        church_state=row.church_state,
        church_zip_code=row.church_zip_code,
        church_congregation_size=row.church_congregation_size,
        church_annual_budget=row.church_annual_budget,
        # Property data
        property_id=row.property_id,
        property_street_address=row.property_street_address,
        property_city=row.property_city,
        property_state=row.property_state,
        property_zip_code=row.property_zip_code,
        property_county=row.property_county,
        property_latitude=row.property_latitude,
        property_longitude=row.property_longitude,
        property_type=row.property_type,
        property_lot_size_sqft=row.property_lot_size_sqft,
        property_lot_size_acres=row.property_lot_size_acres,
        property_current_usage=row.property_current_usage,
        property_zoning_classification=row.property_zoning_classification.value if row.property_zoning_classification else None,
        property_zoning_description=row.property_zoning_description,
        property_assessed_value=row.property_assessed_value,
        property_data_sources=row.property_data_sources,
        property_building_sqft=row.property_building_sqft,
        property_year_built=row.property_year_built,
        property_additional_addresses=row.property_additional_addresses,
        property_demolish_all_structures=row.property_demolish_all_structures,
    )
