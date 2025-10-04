"""
Properties Router
CRUD operations for property management and data enrichment
"""

import logging
from typing import List, Optional

from app.database import get_db
from app.middleware.auth import (CurrentUser, get_current_user,
                                 get_optional_user)
from app.models.church import Church
from app.models.property import Property, PropertyType, ZoningType
from app.schemas.base import (PaginatedResponse, PaginationParams,
                              SuccessResponse)
from app.schemas.property import (PropertyAnalytics, PropertyCreate,
                                  PropertyEnrichment, PropertyResponse,
                                  PropertySummary, PropertyUpdate)
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Query,
                     status)
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create a new property and trigger data enrichment (requires authentication)
    """
    try:
        # Verify church exists and is active
        church_stmt = select(Church).where(
            and_(Church.id == property_data.church_id, Church.is_active == True)
        )
        church_result = await db.execute(church_stmt)
        church = church_result.scalar_one_or_none()
        
        if not church:
            raise HTTPException(
                status_code=404,
                detail="Church not found"
            )
        
        # Verify user owns the church (or is admin)
        if church.user_id != current_user.user_id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to add properties to this church"
            )
        
        # Check for duplicate address for this church
        existing_stmt = select(Property).where(
            and_(
                Property.church_id == property_data.church_id,
                Property.street_address == property_data.street_address,
                Property.is_active == True
            )
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Property with this address already exists for this church"
            )
        
        # Create property
        property_dict = property_data.model_dump(exclude_unset=True)
        property_obj = Property(**property_dict)
        property_obj.user_id = current_user.user_id  # Track ownership
        
        # Auto-calculate acres if not provided
        if property_obj.lot_size_sqft and not property_obj.lot_size_acres:
            property_obj.lot_size_acres = round(property_obj.lot_size_sqft / 43560, 4)
        
        db.add(property_obj)
        await db.commit()
        await db.refresh(property_obj)
        
        # Schedule background data enrichment
        background_tasks.add_task(enrich_property_data, property_obj.id)
        
        logger.info(f"Created property: {property_obj.full_address} (ID: {property_obj.id}) by user: {current_user.user_id}")
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating property: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create property"
        )


@router.get("/", response_model=PaginatedResponse)
async def list_properties(
    pagination: PaginationParams = Depends(),
    church_id: Optional[int] = Query(None, description="Filter by church ID"),
    property_type: Optional[PropertyType] = Query(None, description="Filter by property type"),
    state: Optional[str] = Query(None, description="Filter by state"),
    min_lot_size: Optional[float] = Query(None, description="Minimum lot size in acres"),
    search: Optional[str] = Query(None, description="Search by address or name"),
    db: AsyncSession = Depends(get_db)
):
    """
    List properties with filtering and pagination
    """
    try:
        # Build base query
        stmt = select(Property).where(Property.is_active == True)
        count_stmt = select(func.count(Property.id)).where(Property.is_active == True)
        
        # Apply filters
        if church_id:
            stmt = stmt.where(Property.church_id == church_id)
            count_stmt = count_stmt.where(Property.church_id == church_id)
        
        if property_type:
            stmt = stmt.where(Property.property_type == property_type)
            count_stmt = count_stmt.where(Property.property_type == property_type)
        
        if state:
            stmt = stmt.where(Property.state.ilike(f"%{state}%"))
            count_stmt = count_stmt.where(Property.state.ilike(f"%{state}%"))
        
        if min_lot_size:
            stmt = stmt.where(Property.lot_size_acres >= min_lot_size)
            count_stmt = count_stmt.where(Property.lot_size_acres >= min_lot_size)
        
        if search:
            search_filter = or_(
                Property.street_address.ilike(f"%{search}%"),
                Property.city.ilike(f"%{search}%"),
                Property.name.ilike(f"%{search}%")
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
        
        # Get total count
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(Property.created_at.desc())
        stmt = stmt.offset(pagination.offset).limit(pagination.size)
        
        # Execute query
        result = await db.execute(stmt)
        properties = result.scalars().all()
        
        # Convert to summary format
        property_summaries = [
            PropertySummary(
                id=prop.id,
                uuid=prop.uuid,
                name=prop.name,
                property_type=prop.property_type,
                street_address=prop.street_address,
                city=prop.city,
                state=prop.state,
                lot_size_display=prop.lot_size_display,
                assessed_value=prop.assessed_value,
                created_at=prop.created_at
            )
            for prop in properties
        ]
        
        return PaginatedResponse.create(
            items=property_summaries,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
        
    except Exception as e:
        logger.error(f"Error listing properties: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve properties"
        )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific property by ID
    """
    try:
        stmt = select(Property).where(
            and_(Property.id == property_id, Property.is_active == True)
        )
        result = await db.execute(stmt)
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            raise HTTPException(
                status_code=404,
                detail="Property not found"
            )
        
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving property {property_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve property"
        )


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Update property information
    """
    try:
        # Get existing property
        stmt = select(Property).where(
            and_(Property.id == property_id, Property.is_active == True)
        )
        result = await db.execute(stmt)
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            raise HTTPException(
                status_code=404,
                detail="Property not found"
            )
        
        # Update property with provided data
        update_data = property_data.model_dump(exclude_unset=True)
        address_changed = False
        
        for field, value in update_data.items():
            if field in ['street_address', 'city', 'state', 'zip_code'] and getattr(property_obj, field) != value:
                address_changed = True
            setattr(property_obj, field, value)
        
        # Auto-recalculate acres if lot size changed
        if 'lot_size_sqft' in update_data and property_obj.lot_size_sqft:
            property_obj.lot_size_acres = round(property_obj.lot_size_sqft / 43560, 4)
        
        await db.commit()
        await db.refresh(property_obj)
        
        # Re-enrich data if address changed
        if address_changed:
            background_tasks.add_task(enrich_property_data, property_obj.id)
        
        logger.info(f"Updated property: {property_obj.full_address} (ID: {property_obj.id})")
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating property {property_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update property"
        )


@router.post("/{property_id}/enrich", response_model=SuccessResponse)
async def enrich_property(
    property_id: int,
    force_refresh: bool = Query(False, description="Force refresh cached data"),
    use_premium_apis: bool = Query(False, description="Use premium APIs (Google, ATTOM)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger property data enrichment from external APIs
    
    Fetches additional data from Census, FEMA, HUD, and optionally Google Maps/ATTOM Data
    """
    try:
        # Import service
        from app.services.property_enrichment import PropertyEnrichmentService

        # Verify property exists
        stmt = select(Property).where(
            and_(Property.id == property_id, Property.is_active == True)
        )
        result = await db.execute(stmt)
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            raise HTTPException(
                status_code=404,
                detail="Property not found"
            )
        
        # Run enrichment service
        enrichment_service = PropertyEnrichmentService(db)
        enrichment_results = await enrichment_service.enrich_property(
            property_id=property_id,
            use_premium_apis=use_premium_apis,
            force_refresh=force_refresh
        )
        
        return SuccessResponse(
            message="Property enrichment completed",
            data=enrichment_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting property enrichment {property_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to start property enrichment"
        )


@router.get("/{property_id}/enrichment", response_model=PropertyEnrichment)
async def get_property_enrichment(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get enriched property data from APIs
    """
    try:
        # This would return processed data from API cache and assessments
        # For now, return placeholder
        return PropertyEnrichment(
            estimated_value=None,
            comparable_sales=[],
            rental_estimates={},
            demographics={},
            income_levels={},
            housing_demand={},
            flood_risk={},
            environmental_risks=[],
            walkability_score=None,
            transit_score=None,
            nearby_amenities=[],
            max_units_estimate=None,
            development_costs={},
            zoning_restrictions=[]
        )
        
    except Exception as e:
        logger.error(f"Error getting property enrichment {property_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve property enrichment data"
        )


@router.delete("/{property_id}", response_model=SuccessResponse)
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a property
    """
    try:
        # Get property
        stmt = select(Property).where(
            and_(Property.id == property_id, Property.is_active == True)
        )
        result = await db.execute(stmt)
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            raise HTTPException(
                status_code=404,
                detail="Property not found"
            )
        
        # Soft delete
        property_obj.soft_delete()
        await db.commit()
        
        logger.info(f"Soft deleted property: {property_obj.full_address} (ID: {property_obj.id})")
        return SuccessResponse(message="Property deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting property {property_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete property"
        )


@router.get("/stats/analytics", response_model=PropertyAnalytics)
async def get_property_analytics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get property analytics for admin dashboard
    """
    try:
        # Total properties
        total_stmt = select(func.count(Property.id)).where(Property.is_active == True)
        total_result = await db.execute(total_stmt)
        total_properties = total_result.scalar()
        
        # Properties by type
        type_stmt = select(Property.property_type, func.count(Property.id)).where(
            Property.is_active == True
        ).group_by(Property.property_type)
        type_result = await db.execute(type_stmt)
        by_type = {row[0]: row[1] for row in type_result}
        
        # Properties by state
        state_stmt = select(Property.state, func.count(Property.id)).where(
            Property.is_active == True
        ).group_by(Property.state)
        state_result = await db.execute(state_stmt)
        by_state = {row[0]: row[1] for row in state_result}
        
        # Value statistics
        value_stmt = select(func.sum(Property.assessed_value)).where(
            and_(Property.is_active == True, Property.assessed_value.isnot(None))
        )
        value_result = await db.execute(value_stmt)
        total_assessed_value = value_result.scalar()
        
        # Average lot size
        lot_size_stmt = select(func.avg(Property.lot_size_acres)).where(
            and_(Property.is_active == True, Property.lot_size_acres.isnot(None))
        )
        lot_size_result = await db.execute(lot_size_stmt)
        average_lot_size = lot_size_result.scalar()
        
        # Developable properties (basic heuristic)
        developable_stmt = select(func.count(Property.id)).where(
            and_(
                Property.is_active == True,
                Property.lot_size_sqft >= 5000,  # Minimum developable size
                or_(Property.flood_zone.is_(None), ~Property.flood_zone.startswith('A'))  # Not high flood risk
            )
        )
        developable_result = await db.execute(developable_stmt)
        developable_properties = developable_result.scalar()
        
        # Monthly stats
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        new_properties_stmt = select(func.count(Property.id)).where(
            and_(Property.is_active == True, Property.created_at >= thirty_days_ago)
        )
        new_properties_result = await db.execute(new_properties_stmt)
        new_properties_this_month = new_properties_result.scalar()
        
        updated_properties_stmt = select(func.count(Property.id)).where(
            and_(Property.is_active == True, Property.updated_at >= thirty_days_ago)
        )
        updated_properties_result = await db.execute(updated_properties_stmt)
        updated_properties_this_month = updated_properties_result.scalar()
        
        return PropertyAnalytics(
            total_properties=total_properties,
            by_type=by_type,
            by_state=by_state,
            total_assessed_value=total_assessed_value,
            average_lot_size=float(average_lot_size) if average_lot_size else None,
            developable_properties=developable_properties,
            estimated_total_units=None,  # Would calculate based on lot sizes and zoning
            new_properties_this_month=new_properties_this_month,
            updated_properties_this_month=updated_properties_this_month
        )
        
    except Exception as e:
        logger.error(f"Error getting property analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve property analytics"
        )


async def enrich_property_data(property_id: int, force_refresh: bool = False):
    """
    Background task to enrich property data from external APIs
    This will be implemented with actual API calls in the services layer
    """
    logger.info(f"Starting property enrichment for property {property_id} (force_refresh={force_refresh})")
    
    # TODO: Implement actual API calls to:
    # - Census API for demographics
    # - HUD Exchange for housing data
    # - FEMA for flood risk
    # - ATTOM Data for property details (when available)
    # - Google Maps for location data
    
    # For now, just log the task
    logger.info(f"Property enrichment completed for property {property_id}")
