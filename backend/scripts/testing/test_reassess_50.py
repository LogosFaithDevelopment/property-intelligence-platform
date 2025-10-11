#!/usr/bin/env python3
"""
Re-assess assessment ID 50 (St Rest Baptist Church)
"""

import asyncio

from app.database import AsyncSessionLocal
from app.services.ai_assessment import AIAssessmentService


async def reassess_50():
    """Re-run assessment 50"""
    
    async with AsyncSessionLocal() as db:
        try:
            assessment_id = 50
            
            print(f"🤖 Re-running AI assessment for assessment {assessment_id}...")
            assessment_service = AIAssessmentService(db)
            await assessment_service.process_assessment(assessment_id)
            print(f"✅ AI assessment completed")
            
            await db.commit()
            
            print(f"\n🎉 SUCCESS! Assessment {assessment_id} has been re-processed")
            print(f"   Check the admin dashboard to see the updated results")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    print("=" * 60)
    print("Re-assessing St Rest Baptist Church (Assessment 50)")
    print("=" * 60)
    asyncio.run(reassess_50())
