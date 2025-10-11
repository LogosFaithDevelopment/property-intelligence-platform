#!/usr/bin/env python3
"""
Manual Assessment Trigger Script
Run this to manually trigger AI assessment for a submission in DRAFT status
"""

import asyncio
import sys

from app.database import AsyncSessionLocal
from app.models.assessment import Assessment, AssessmentStatus
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def trigger_assessment_for_draft():
    """Find the most recent DRAFT assessment and process it"""
    
    async with AsyncSessionLocal() as db:
        try:
            # Find most recent DRAFT assessment
            result = await db.execute(
                select(Assessment)
                .where(Assessment.status == AssessmentStatus.DRAFT)
                .order_by(Assessment.created_at.desc())
                .limit(1)
            )
            assessment = result.scalar_one_or_none()
            
            if not assessment:
                print("❌ No DRAFT assessments found")
                return
            
            print(f"✅ Found DRAFT assessment: {assessment.id}")
            print(f"   Property ID: {assessment.property_id}")
            print(f"   Church ID: {assessment.church_id}")
            
            # Step 1: Enrich property
            print(f"\n🔄 Step 1: Enriching property {assessment.property_id}...")
            enrichment_service = PropertyEnrichmentService(db)
            await enrichment_service.enrich_property(assessment.property_id)
            print(f"✅ Property enrichment completed")
            
            # Step 2: Run AI assessment
            print(f"\n🤖 Step 2: Running AI assessment {assessment.id}...")
            assessment_service = AIAssessmentService(db)
            await assessment_service.process_assessment(assessment.id)
            print(f"✅ AI assessment completed")
            
            # Commit changes
            await db.commit()
            
            print(f"\n🎉 SUCCESS! Assessment {assessment.id} is now processed")
            print(f"   Check the admin dashboard to see the results")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    print("=" * 60)
    print("Manual Assessment Trigger")
    print("=" * 60)
    asyncio.run(trigger_assessment_for_draft())
