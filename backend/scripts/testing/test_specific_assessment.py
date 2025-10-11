#!/usr/bin/env python3
"""
Re-run assessment for specific assessment ID
"""

import asyncio
import sys
from app.database import AsyncSessionLocal
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService


async def rerun_assessment(assessment_id: int):
    """Re-run assessment for specific ID"""
    
    async with AsyncSessionLocal() as db:
        try:
            print(f"\n🔄 Re-running assessment {assessment_id}...")
            
            # Run AI assessment
            assessment_service = AIAssessmentService(db)
            await assessment_service.process_assessment(assessment_id)
            
            # Commit changes
            await db.commit()
            
            print(f"\n🎉 SUCCESS! Assessment {assessment_id} has been re-processed")
            print(f"   Check the admin dashboard to see updated results")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    assessment_id = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    print("=" * 60)
    print(f"Re-running Assessment ID: {assessment_id}")
    print("=" * 60)
    asyncio.run(rerun_assessment(assessment_id))
