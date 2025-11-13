"""
Submissions Router
Handles complete church property submissions (Church + Property + Assessment)
"""

import logging
from typing import Optional

from app.database import get_db
from app.middleware.auth import CurrentUser, get_current_user
from app.models.assessment import Assessment
from app.models.church import Church, ChurchStatus
from app.models.property import Property, PropertyType
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


async def trigger_property_enrichment_and_assessment(property_id: int, assessment_id: int):
    """
    Background task to trigger property enrichment AND AI assessment
    This runs asynchronously after the submission is created
    
    Steps:
    1. Enrich property data from external APIs
    2. Run AI assessment scoring
    
    NOTE: Creates its own database session since this runs in background
    """
    try:
        # Create a NEW database session for this background task
        async for db in get_db():
            try:
                # STEP 1: Property Enrichment
                from app.services.property_enrichment import \
                    PropertyEnrichmentService
                
                logger.info(f"🔄 Starting background enrichment for property {property_id}")
                
                enrichment_service = PropertyEnrichmentService(db)
                await enrichment_service.enrich_property(property_id)
                
                logger.info(f"✅ Enrichment completed for property {property_id}")
                
                # STEP 2: AI Assessment Scoring
                from app.services.ai_assessment import AIAssessmentService
                
                logger.info(f"🤖 Starting AI assessment for assessment {assessment_id}")
                
                assessment_service = AIAssessmentService(db)
                await assessment_service.process_assessment(assessment_id)
                
                logger.info(f"✅ AI assessment completed for assessment {assessment_id}")
                
                # Commit the changes
                await db.commit()
                
            except Exception as e:
                await db.rollback()
                raise e
            finally:
                await db.close()
                
    except Exception as e:
        logger.error(f"❌ Enrichment/Assessment failed for property {property_id}: {e}", exc_info=True)
        # Don't raise - failure shouldn't block submission


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission_data: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Create complete church property submission
    
    This endpoint creates:
    1. Church record
    2. Property record (linked to church)
    3. Assessment record (linked to church and property)
    4. Triggers background enrichment (async)
    
    All operations are atomic - if any fail, none are committed.
    
    Requires authentication to prevent spam and track ownership.
    """
    
    try:
        # Start atomic transaction
        async with db.begin_nested():
            
            # ============================================================
            # STEP 1: Create Church
            # ============================================================
            logger.info(f"Creating church: {submission_data.church.name}")
            
            # Check for duplicate email
            from sqlalchemy import select
            existing_church = await db.execute(
                select(Church).where(Church.primary_email == submission_data.church.primary_email)
            )
            if existing_church.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail=f"Church with email {submission_data.church.primary_email} already exists"
                )
            
            # Create church
            church_data = submission_data.church.model_dump(exclude_unset=True)
            
            # Convert HttpUrl to string if present
            if 'website_url' in church_data and church_data['website_url']:
                church_data['website_url'] = str(church_data['website_url'])
            
            church = Church(**church_data)
            church.user_id = current_user.user_id
            church.verification_status = ChurchStatus.PENDING
            
            db.add(church)
            await db.flush()  # Get church.id without committing
            
            logger.info(f"✅ Church created with ID: {church.id}")
            
            # ============================================================
            # STEP 2: Create Property
            # ============================================================
            logger.info(f"Creating property for church {church.id}")
            
            property_data = submission_data.property.model_dump(exclude_unset=True)
            
            # DEBUG: Log what we received
            logger.info(f"🔍 Property data received: demolish_all_structures={property_data.get('demolish_all_structures')}, additional_addresses={property_data.get('additional_addresses')}")
            
            # Ensure property_type has a value (default to OTHER if not provided)
            if 'property_type' not in property_data or property_data['property_type'] is None:
                property_data['property_type'] = PropertyType.OTHER
            
            # Auto-generate property name if not provided (using church name + city)
            if 'name' not in property_data or not property_data.get('name'):
                property_data['name'] = f"{church.name} - {property_data.get('city', 'Property')}"
            
            # Remove fields that shouldn't be set during initial submission
            # These will be populated later by enrichment or admin edits
            property_data.pop('data_sources', None)
            property_data.pop('manual_overrides', None)
            property_data.pop('last_data_update', None)
            
            property_obj = Property(
                church_id=church.id,
                user_id=current_user.user_id,
                **property_data
            )
            
            db.add(property_obj)
            await db.flush()  # Get property_obj.id without committing
            
            logger.info(f"✅ Property created with ID: {property_obj.id}")
            
            # ============================================================
            # STEP 3: Create Assessment
            # ============================================================
            logger.info(f"Creating assessment for property {property_obj.id}")
            
            assessment = Assessment(
                church_id=church.id,
                property_id=property_obj.id,
                **submission_data.assessment.model_dump(exclude_unset=True)
            )
            
            db.add(assessment)
            await db.flush()  # Get assessment.id without committing
            
            logger.info(f"✅ Assessment created with ID: {assessment.id}")
        
        # Commit the transaction (all 3 records created successfully)
        await db.commit()
        
        logger.info(
            f"🎉 Submission complete! Church: {church.id}, "
            f"Property: {property_obj.id}, Assessment: {assessment.id}"
        )
        
        # ============================================================
        # STEP 4: Trigger Enrichment AND AI Assessment (Background Task)
        # ============================================================
        logger.info(f"Scheduling enrichment and AI assessment for property {property_obj.id}, assessment {assessment.id}")
        background_tasks.add_task(
            trigger_property_enrichment_and_assessment, 
            property_obj.id, 
            assessment.id
        )
        
        return SubmissionResponse(
            church_id=church.id,
            property_id=property_obj.id,
            assessment_id=assessment.id,
            message="Submission created successfully! Property enrichment and AI assessment started in background.",
            enrichment_started=True
        )
        
    except HTTPException:
        await db.rollback()
        raise
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Submission creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create submission: {str(e)}"
        )


@router.get("/my-status")
async def get_my_submission_status(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get submission status for the current authenticated user
    
    Returns list of user's church submissions with basic status info
    """
    from sqlalchemy import select

    # Get all churches for this user
    result = await db.execute(
        select(Church)
        .where(Church.user_id == current_user.user_id)
        .where(Church.is_deleted == False)
        .order_by(Church.created_at.desc())
    )
    churches = result.scalars().all()
    
    if not churches:
        return {
            "total_submissions": 0,
            "submissions": []
        }
    
    submissions = []
    for church in churches:
        # Get property count for this church
        property_result = await db.execute(
            select(Property)
            .where(Property.church_id == church.id)
            .where(Property.is_deleted == False)
        )
        properties = property_result.scalars().all()
        
        submissions.append({
            "church_id": church.id,
            "church_name": church.name,
            "verification_status": church.verification_status,
            "property_count": len(properties),
            "submitted_at": church.created_at.isoformat(),
        })
    
    return {
        "total_submissions": len(submissions),
        "submissions": submissions
    }
