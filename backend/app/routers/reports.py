"""
Reports Router
Handle investment report generation and delivery
"""

import io
import logging
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.assessment import Assessment
from app.models.report import Report, ReportFormat, ReportStatus, ReportType
from app.schemas.base import SuccessResponse
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{assessment_id}", status_code=status.HTTP_201_CREATED)
async def generate_report(
    assessment_id: int,
    report_type: ReportType,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    report_format: ReportFormat = ReportFormat.PDF
):
    """
    Generate an investment report for an assessment
    """
    try:
        # Verify assessment exists and is completed
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        if not assessment.is_completed:
            raise HTTPException(
                status_code=400,
                detail="Assessment must be completed before generating report"
            )
        
        # Create report record
        report = Report(
            assessment_id=assessment_id,
            report_type=report_type,
            report_format=report_format,
            title=f"{report_type.value.replace('_', ' ').title()} Report",
            status=ReportStatus.PENDING
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        # Schedule background report generation
        background_tasks.add_task(generate_report_content, report.id)
        
        return {
            "id": report.id,
            "uuid": report.uuid,
            "status": report.status,
            "message": "Report generation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting report generation: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to start report generation"
        )


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get report information
    """
    try:
        stmt = select(Report).where(Report.id == report_id)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        return {
            "id": report.id,
            "uuid": report.uuid,
            "report_type": report.report_type,
            "report_format": report.report_format,
            "status": report.status,
            "title": report.title,
            "file_size_mb": report.file_size_mb,
            "page_count": report.page_count,
            "created_at": report.created_at,
            "is_ready": report.is_ready
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve report"
        )


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Download report file
    """
    try:
        stmt = select(Report).where(Report.id == report_id)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        if not report.is_ready:
            raise HTTPException(
                status_code=400,
                detail="Report is not ready for download"
            )
        
        # Increment download count
        report.download_count += 1
        await db.commit()
        
        # Prepare file for download
        file_content = io.BytesIO(report.file_content)
        
        # Set appropriate content type
        content_type = "application/pdf" if report.report_format == ReportFormat.PDF else "text/html"
        file_extension = "pdf" if report.report_format == ReportFormat.PDF else "html"
        filename = f"{report.title.replace(' ', '_')}_{report.uuid[:8]}.{file_extension}"
        
        return StreamingResponse(
            file_content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to download report"
        )


@router.get("/assessment/{assessment_id}")
async def get_assessment_reports(
    assessment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all reports for a specific assessment
    """
    try:
        # Verify assessment exists
        assessment_stmt = select(Assessment).where(Assessment.id == assessment_id)
        assessment_result = await db.execute(assessment_stmt)
        assessment = assessment_result.scalar_one_or_none()
        
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        # Get reports
        stmt = select(Report).where(Report.assessment_id == assessment_id).order_by(Report.created_at.desc())
        result = await db.execute(stmt)
        reports = result.scalars().all()
        
        return [
            {
                "id": report.id,
                "uuid": report.uuid,
                "report_type": report.report_type,
                "report_format": report.report_format,
                "status": report.status,
                "title": report.title,
                "file_size_mb": report.file_size_mb,
                "download_count": report.download_count,
                "created_at": report.created_at,
                "is_ready": report.is_ready
            }
            for report in reports
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reports for assessment {assessment_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve assessment reports"
        )


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a report
    """
    try:
        stmt = select(Report).where(Report.id == report_id)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        await db.delete(report)
        await db.commit()
        
        logger.info(f"Deleted report: {report.title} (ID: {report.id})")
        return SuccessResponse(message="Report deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete report"
        )


async def generate_report_content(report_id: int):
    """
    Background task to generate report content using AI
    This will integrate with the AI services layer
    """
    logger.info(f"Starting report content generation for report {report_id}")
    
    # TODO: Implement actual report generation:
    # 1. Load assessment data
    # 2. Generate executive summary with AI
    # 3. Create market analysis section
    # 4. Build financial projections
    # 5. Compile risk assessment
    # 6. Generate PDF/HTML output
    # 7. Store file content in database
    # 8. Update report status to completed
    
    logger.info(f"Report content generation completed for report {report_id}")


@router.get("/assessment/{assessment_id}/pdf")
async def generate_pdf_report(
    assessment_id: int,
    include_detailed_analysis: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and download a PDF report for an assessment
    
    Args:
        assessment_id: ID of the assessment
        include_detailed_analysis: Include detailed market/financial analysis
        
    Returns:
        PDF file download
    """
    try:
        # Verify assessment exists and is completed
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        if not assessment.is_completed:
            raise HTTPException(
                status_code=400,
                detail="Assessment must be completed before generating report"
            )
        
        # Generate PDF using synchronous session
        # (ReportLab requires sync operations)
        from app.database import SyncSessionLocal
        from app.services.report_generator_v3 import ReportGeneratorV3

        # Create sync session for ReportLab
        sync_db = SyncSessionLocal()
        
        try:
            # Get assessment, property, and church data from sync session
            from app.models.church import Church
            from app.models.property import Property

            # IMPORTANT: Get assessment from sync session to ensure JSON fields are properly loaded
            sync_assessment = sync_db.query(Assessment).filter(Assessment.id == assessment_id).first()
            property_obj = sync_db.query(Property).filter(Property.id == sync_assessment.property_id).first()
            church = sync_db.query(Church).filter(Church.id == sync_assessment.church_id).first()
            
            # Generate PDF using V3 generator
            generator = ReportGeneratorV3()
            pdf_buffer = generator.generate_report(sync_assessment, property_obj, church)
            pdf_bytes = pdf_buffer.getvalue()
        finally:
            sync_db.close()
        
        # Update report record
        # (Record that a report was generated)
        report = Report(
            assessment_id=assessment_id,
            report_type=ReportType.INVESTMENT,
            report_format=ReportFormat.PDF,
            status=ReportStatus.COMPLETED,
            title=f"Investment Report - Assessment {assessment_id}",
            file_name=f"assessment_{assessment_id}_report.pdf",
            file_size_bytes=len(pdf_bytes),
            generation_completed_at=datetime.utcnow()
        )
        db.add(report)
        await db.commit()
        
        # Return PDF as download
        filename = f"assessment_{assessment_id}_report.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/assessment/{assessment_id}/download-v2")
async def download_assessment_report_v2(
    assessment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Download professional 3-page assessment report (V2 Generator)
    Generates and streams PDF directly without saving to database
    """
    try:
        # Verify assessment exists
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail=f"Assessment {assessment_id} not found"
            )
        
        # Import V3 generator (clean implementation matching web page)
        # Get synchronous session for report generator
        from app.database import SyncSessionLocal
        from app.services.report_generator_v3 import ReportGeneratorV3
        sync_db = SyncSessionLocal()
        
        try:
            # Get assessment, property, and church data from sync session
            from app.models.church import Church
            from app.models.property import Property

            # IMPORTANT: Get assessment from sync session to ensure JSON fields are properly loaded
            sync_assessment = sync_db.query(Assessment).filter(Assessment.id == assessment_id).first()
            property_obj = sync_db.query(Property).filter(Property.id == sync_assessment.property_id).first()
            church = sync_db.query(Church).filter(Church.id == sync_assessment.church_id).first()
            
            # Generate PDF using V3 generator
            generator = ReportGeneratorV3()
            pdf_buffer = generator.generate_report(sync_assessment, property_obj, church)
            pdf_bytes = pdf_buffer.getvalue()
            
            # Generate filename with property address
            from app.models.property import Property
            property_obj = sync_db.query(Property).filter(Property.id == assessment.property_id).first()
            
            if property_obj and property_obj.street_address:
                safe_address = property_obj.street_address.replace(' ', '_').replace(',', '')
                filename = f"Logos_Assessment_{safe_address}.pdf"
            else:
                filename = f"Logos_Assessment_{assessment_id}.pdf"
            
            # Return PDF as download
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(pdf_bytes))
                }
            )
            
        finally:
            sync_db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating V2 PDF report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )
