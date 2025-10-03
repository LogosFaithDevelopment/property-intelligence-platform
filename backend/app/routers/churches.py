"""
Churches Router
CRUD operations for church/organization management
"""

import logging
from typing import List, Optional

from app.database import get_db
from app.models.assessment import Assessment
from app.models.church import Church, ChurchStatus
from app.models.property import Property
from app.schemas.base import (PaginatedResponse, PaginationParams,
                              SuccessResponse)
from app.schemas.church import (ChurchCreate, ChurchResponse, ChurchStats,
                                ChurchSummary, ChurchUpdate,
                                ChurchVerification)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChurchResponse, status_code=status.HTTP_201_CREATED)
async def create_church(
    church_data: ChurchCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new church/organization
    """
    try:
        # Check for duplicate email
        existing_stmt = select(Church).where(Church.primary_email == church_data.primary_email)
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Church with this email already exists"
            )
        
        # Check for duplicate tax ID if provided
        if church_data.tax_exempt_id:
            tax_id_stmt = select(Church).where(Church.tax_exempt_id == church_data.tax_exempt_id)
            tax_id_result = await db.execute(tax_id_stmt)
            if tax_id_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Church with this tax-exempt ID already exists"
                )
        
        # Create new church
        church = Church(**church_data.model_dump(exclude_unset=True))
        church.verification_status = ChurchStatus.PENDING
        
        db.add(church)
        await db.commit()
        await db.refresh(church)
        
        logger.info(f"Created new church: {church.name} (ID: {church.id})")
        return church
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating church: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create church"
        )


@router.get("/", response_model=PaginatedResponse)
async def list_churches(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[ChurchStatus] = Query(None, description="Filter by verification status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    state: Optional[str] = Query(None, description="Filter by state"),  
    db: AsyncSession = Depends(get_db)
):
    """
    List churches with filtering and pagination
    """
    try:
        # Build base query
        stmt = select(Church).where(Church.is_active == True)
        count_stmt = select(func.count(Church.id)).where(Church.is_active == True)
        
        # Apply filters
        if status_filter:
            stmt = stmt.where(Church.verification_status == status_filter)
            count_stmt = count_stmt.where(Church.verification_status == status_filter)
        
        if search:
            search_filter = or_(
                Church.name.ilike(f"%{search}%"),
                Church.primary_email.ilike(f"%{search}%"),
                Church.legal_name.ilike(f"%{search}%")
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
        
        if state:
            stmt = stmt.where(Church.state.ilike(f"%{state}%"))
            count_stmt = count_stmt.where(Church.state.ilike(f"%{state}%"))
        
        # Get total count
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(Church.created_at.desc())
        stmt = stmt.offset(pagination.offset).limit(pagination.size)
        
        # Execute query
        result = await db.execute(stmt)
        churches = result.scalars().all()
        
        # Convert to summary format
        church_summaries = [
            ChurchSummary(
                id=church.id,
                uuid=church.uuid,
                name=church.name,
                verification_status=church.verification_status,
                city=church.city,
                state=church.state,
                congregation_size=church.congregation_size,
                created_at=church.created_at
            )
            for church in churches
        ]
        
        return PaginatedResponse.create(
            items=church_summaries,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error listing churches: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve churches"
        )


@router.get("/{church_id}", response_model=ChurchResponse)
async def get_church(
    church_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific church by ID
    """
    try:
        stmt = select(Church).where(
            and_(Church.id == church_id, Church.is_active == True)
        )
        result = await db.execute(stmt)
        church = result.scalar_one_or_none()
        
        if not church:
            raise HTTPException(
                status_code=404,
                detail="Church not found"
            )
        
        return church
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving church {church_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve church"
        )


@router.put("/{church_id}", response_model=ChurchResponse)
async def update_church(
    church_id: int,
    church_data: ChurchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update church information
    """
    try:
        # Get existing church
        stmt = select(Church).where(
            and_(Church.id == church_id, Church.is_active == True)
        )
        result = await db.execute(stmt)
        church = result.scalar_one_or_none()
        
        if not church:
            raise HTTPException(
                status_code=404,
                detail="Church not found"
            )
        
        # Check for email conflicts if email is being updated
        if church_data.primary_email and church_data.primary_email != church.primary_email:
            email_stmt = select(Church).where(
                and_(
                    Church.primary_email == church_data.primary_email,
                    Church.id != church_id
                )
            )
            email_result = await db.execute(email_stmt)
            if email_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Another church with this email already exists"
                )
        
        # Update church with provided data
        update_data = church_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(church, field, value)
        
        await db.commit()
        await db.refresh(church) 
        
        logger.info(f"Updated church: {church.name} (ID: {church.id})")
        return church
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating church {church_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update church"
        )


@router.post("/{church_id}/verify", response_model=SuccessResponse)
async def verify_church(
    church_id: int,
    verification_data: ChurchVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Update church verification status (admin only)
    """
    try:
        # Get church
        stmt = select(Church).where(
            and_(Church.id == church_id, Church.is_active == True)
        )
        result = await db.execute(stmt)
        church = result.scalar_one_or_none()
        
        if not church:
            raise HTTPException(
                status_code=404,
                detail="Church not found"
            )
        
        # Update verification status
        church.verification_status = verification_data.verification_status
        church.verification_notes = verification_data.verification_notes
        
        if verification_data.verification_status == ChurchStatus.VERIFIED:
            church.verification_date = func.now()
        
        await db.commit()
        
        logger.info(f"Updated verification status for church {church.name}: {verification_data.verification_status}")
        return SuccessResponse(message=f"Church verification status updated to {verification_data.verification_status}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying church {church_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update verification status"
        )


@router.delete("/{church_id}", response_model=SuccessResponse)
async def delete_church(
    church_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a church (admin only)
    """
    try:
        # Get church
        stmt = select(Church).where(
            and_(Church.id == church_id, Church.is_active == True)
        )
        result = await db.execute(stmt)
        church = result.scalar_one_or_none()
        
        if not church:
            raise HTTPException(
                status_code=404,
                detail="Church not found"
            )
        
        # Soft delete
        church.soft_delete()
        await db.commit()
        
        logger.info(f"Soft deleted church: {church.name} (ID: {church.id})")
        return SuccessResponse(message="Church deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting church {church_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete church"
        )


@router.get("/{church_id}/properties", response_model=List[dict])
async def get_church_properties(
    church_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all properties for a specific church
    """
    try:
        # Verify church exists
        church_stmt = select(Church).where(
            and_(Church.id == church_id, Church.is_active == True)
        )
        church_result = await db.execute(church_stmt)
        church = church_result.scalar_one_or_none()
        
        if not church:
            raise HTTPException(
                status_code=404,
                detail="Church not found"
            )
        
        # Get properties
        stmt = select(Property).where(
            and_(Property.church_id == church_id, Property.is_active == True)
        ).order_by(Property.created_at.desc())
        
        result = await db.execute(stmt)
        properties = result.scalars().all()
        
        return [
            {
                "id": prop.id,
                "uuid": prop.uuid,
                "name": prop.name,
                "property_type": prop.property_type,
                "full_address": prop.full_address,
                "lot_size_display": prop.lot_size_display,
                "assessed_value": prop.assessed_value,
                "created_at": prop.created_at
            }
            for prop in properties
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting properties for church {church_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve church properties"
        )


@router.get("/stats/overview", response_model=ChurchStats)
async def get_church_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get church statistics for admin dashboard
    """
    try:
        # Total churches
        total_stmt = select(func.count(Church.id)).where(Church.is_active == True)
        total_result = await db.execute(total_stmt)
        total_churches = total_result.scalar()
        
        # Verified churches
        verified_stmt = select(func.count(Church.id)).where(
            and_(Church.is_active == True, Church.verification_status == ChurchStatus.VERIFIED)
        )
        verified_result = await db.execute(verified_stmt)
        verified_churches = verified_result.scalar()
        
        # Pending verification
        pending_stmt = select(func.count(Church.id)).where(
            and_(Church.is_active == True, Church.verification_status == ChurchStatus.PENDING)
        )
        pending_result = await db.execute(pending_stmt)
        pending_verification = pending_result.scalar()
        
        # Total properties
        properties_stmt = select(func.count(Property.id)).where(Property.is_active == True)
        properties_result = await db.execute(properties_stmt)
        total_properties = properties_result.scalar()
        
        # Active assessments
        assessments_stmt = select(func.count(Assessment.id)).where(Assessment.status.in_(["processing", "completed"]))
        assessments_result = await db.execute(assessments_stmt)
        active_assessments = assessments_result.scalar()
        
        # Monthly stats (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        new_churches_stmt = select(func.count(Church.id)).where(
            and_(Church.is_active == True, Church.created_at >= thirty_days_ago)
        )
        new_churches_result = await db.execute(new_churches_stmt)
        new_churches_this_month = new_churches_result.scalar()
        
        completed_assessments_stmt = select(func.count(Assessment.id)).where(
            and_(Assessment.status == "completed", Assessment.processing_completed_at >= thirty_days_ago)
        )
        completed_assessments_result = await db.execute(completed_assessments_stmt)
        completed_assessments_this_month = completed_assessments_result.scalar()
        
        return ChurchStats(
            total_churches=total_churches,
            verified_churches=verified_churches,
            pending_verification=pending_verification,
            total_properties=total_properties,
            active_assessments=active_assessments,
            new_churches_this_month=new_churches_this_month,
            completed_assessments_this_month=completed_assessments_this_month
        )
        
    except Exception as e:
        logger.error(f"Error getting church stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )
