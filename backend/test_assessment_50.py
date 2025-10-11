#!/usr/bin/env python3
"""
Re-run Assessment 50 (St Rest Baptist Church) with NEW code
This is the ONLY property with Smarty enriched data
"""

import asyncio

from app.database import AsyncSessionLocal
from app.services.ai_assessment import AIAssessmentService


async def rerun_assessment_50():
    """Re-run assessment 50 with updated available build space logic"""
    
    async with AsyncSessionLocal() as db:
        try:
            assessment_id = 50
            
            print("=" * 80)
            print(f"Re-running Assessment 50 (St Rest Baptist Church)")
            print("This property has Smarty enriched data:")
            print("  - Lot: 13,708 sqft")
            print("  - Building: 2,488 sqft")
            print("  - Available: 11,220 sqft (Smarty calculated)")
            print("=" * 80)
            print()
            
            # Run AI assessment with NEW code
            assessment_service = AIAssessmentService(db)
            await assessment_service.process_assessment(assessment_id)
            
            # Commit changes
            await db.commit()
            
            print()
            print("=" * 80)
            print("✅ SUCCESS! Assessment 50 re-processed with updated code")
            print()
            print("Check the admin dashboard to see updated results:")
            print("  - Should show ~42 units feasible (not 4)")
            print("  - Should be APPROVED (not deal breaker)")
            print("  - Financial score should be much higher")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(rerun_assessment_50())
