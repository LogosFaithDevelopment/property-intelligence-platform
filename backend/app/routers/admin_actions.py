"""
Admin Actions Router
Handles admin actions on submissions: approve, reject, add comments, change status
"""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from app.database import get_db
from app.models.admin_user import AdminRole, AdminUser
from app.models.assessment import Assessment, AssessmentStatus
from app.routers.admin_auth import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api/v1/admin/submissions", tags=["admin-actions"])


# Schemas
class ApproveRequest(BaseModel):
    notes: Optional[str] = Field(None, description="Admin notes for approval")


class RejectRequest(BaseModel):
    reason: str = Field(..., description="Reason for rejection")
    notes: Optional[str] = Field(None, description="Additional admin notes")


class CommentRequest(BaseModel):
    comment: str = Field(..., description="Admin comment")


class StatusChangeRequest(BaseModel):
    status: str = Field(..., description="New status (DRAFT, SUBMITTED, PROCESSING, COMPLETED, REVIEWED, APPROVED, REJECTED)")
    notes: Optional[str] = Field(None, description="Admin notes for status change")


class SubmissionResponse(BaseModel):
    id: int
    property_address: str
    status: str
    created_at: datetime
    updated_at: datetime
    reviewer_notes: Optional[str]


# Helper function to format timestamp in Pacific time
def get_pacific_timestamp() -> str:
    """Get current timestamp formatted in Pacific timezone (PST/PDT)"""
    pacific_tz = ZoneInfo("America/Los_Angeles")
    now_pacific = datetime.now(pacific_tz)
    # Determine if we're in PST or PDT
    tz_name = now_pacific.strftime('%Z')  # Will be PST or PDT
    return now_pacific.strftime(f'%Y-%m-%d %H:%M {tz_name}')


# Helper function to get submission
async def get_submission_or_404(
    submission_id: int,
    db: AsyncSession
) -> Assessment:
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.property_obj))
        .where(Assessment.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {submission_id} not found"
        )
    
    return submission


@router.post("/{submission_id}/approve", response_model=SubmissionResponse)
async def approve_submission(
    submission_id: int,
    request: ApproveRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Approve a submission
    Requires ADMIN or SUPERADMIN role
    """
    # Check permissions (viewers cannot approve)
    if admin.role == AdminRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot approve submissions"
        )
    
    submission = await get_submission_or_404(submission_id, db)
    
    # Update status
    submission.status = AssessmentStatus.APPROVED
    submission.updated_at = datetime.utcnow()
    
    # Add reviewer notes
    admin_note = f"✅ Approved by {admin.full_name or admin.email} on {get_pacific_timestamp()}"
    if request.notes:
        admin_note += f"\nNotes: {request.notes}"
    
    if submission.reviewer_notes:
        submission.reviewer_notes += f"\n\n{admin_note}"
    else:
        submission.reviewer_notes = admin_note
    
    await db.commit()
    await db.refresh(submission)
    
    return SubmissionResponse(
        id=submission.id,
        property_address=submission.property_obj.street_address if submission.property_obj else "N/A",
        status=submission.status.value,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
        reviewer_notes=submission.reviewer_notes
    )


@router.post("/{submission_id}/reject", response_model=SubmissionResponse)
async def reject_submission(
    submission_id: int,
    request: RejectRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Reject a submission
    Requires ADMIN or SUPERADMIN role
    """
    # Check permissions (viewers cannot reject)
    if admin.role == AdminRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot reject submissions"
        )
    
    submission = await get_submission_or_404(submission_id, db)
    
    # Update status
    submission.status = AssessmentStatus.REJECTED
    submission.updated_at = datetime.utcnow()
    
    # Add reviewer notes with rejection reason
    admin_note = f"❌ Rejected by {admin.full_name or admin.email} on {get_pacific_timestamp()}"
    admin_note += f"\nReason: {request.reason}"
    if request.notes:
        admin_note += f"\nNotes: {request.notes}"
    
    if submission.reviewer_notes:
        submission.reviewer_notes += f"\n\n{admin_note}"
    else:
        submission.reviewer_notes = admin_note
    
    await db.commit()
    await db.refresh(submission)
    
    return SubmissionResponse(
        id=submission.id,
        property_address=submission.property_obj.street_address if submission.property_obj else "N/A",
        status=submission.status.value,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
        reviewer_notes=submission.reviewer_notes
    )


@router.post("/{submission_id}/comment", response_model=SubmissionResponse)
async def add_comment(
    submission_id: int,
    request: CommentRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Add a comment to a submission
    All admin roles can comment
    """
    submission = await get_submission_or_404(submission_id, db)
    
    # Add comment
    comment = f"💬 {admin.full_name or admin.email} ({get_pacific_timestamp()}): {request.comment}"
    
    if submission.reviewer_notes:
        submission.reviewer_notes += f"\n\n{comment}"
    else:
        submission.reviewer_notes = comment
    
    submission.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(submission)
    
    return SubmissionResponse(
        id=submission.id,
        property_address=submission.property_obj.street_address if submission.property_obj else "N/A",
        status=submission.status.value,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
        reviewer_notes=submission.reviewer_notes
    )


@router.patch("/{submission_id}/status", response_model=SubmissionResponse)
async def change_status(
    submission_id: int,
    request: StatusChangeRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Change submission status
    Requires ADMIN or SUPERADMIN role
    """
    # Check permissions (viewers cannot change status)
    if admin.role == AdminRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot change submission status"
        )
    
    submission = await get_submission_or_404(submission_id, db)
    
    # Validate status
    try:
        new_status = AssessmentStatus(request.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {request.status}. Valid statuses: {[s.value for s in AssessmentStatus]}"
        )
    
    old_status = submission.status
    submission.status = new_status
    submission.updated_at = datetime.utcnow()
    
    # Add reviewer notes
    admin_note = f"🔄 Status changed by {admin.full_name or admin.email} on {get_pacific_timestamp()}"
    admin_note += f"\nFrom: {old_status.value} → To: {new_status.value}"
    if request.notes:
        admin_note += f"\nNotes: {request.notes}"
    
    if submission.reviewer_notes:
        submission.reviewer_notes += f"\n\n{admin_note}"
    else:
        submission.reviewer_notes = admin_note
    
    await db.commit()
    await db.refresh(submission)
    
    return SubmissionResponse(
        id=submission.id,
        property_address=submission.property_obj.street_address if submission.property_obj else "N/A",
        status=submission.status.value,
        created_at=submission.created_at,
        updated_at=submission.updated_at,
        reviewer_notes=submission.reviewer_notes
    )
