#!/usr/bin/env python3
"""
Test GPT-4o Market Analysis
Re-run AI assessment for existing enriched property with GPT-4o
"""

import asyncio
import sys

sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from app.models.assessment import Assessment
from app.services.ai_assessment import AIAssessmentService
from sqlalchemy import select, update


async def rerun_assessment_with_gpt4o():
    """Re-run assessment #8 with GPT-4o for complete market analysis"""
    
    print("\n" + "="*80)
    print("🔄 RE-RUNNING ASSESSMENT #8 WITH GPT-4o")
    print("="*80 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # Get assessment #8
            stmt = select(Assessment).where(Assessment.id == 8)
            result = await db.execute(stmt)
            assessment = result.scalar_one_or_none()
            
            if not assessment:
                print("❌ Assessment #8 not found")
                return
            
            print(f"✅ Found Assessment #8")
            print(f"   Property ID: {assessment.property_id}")
            print(f"   Church ID: {assessment.church_id}")
            print(f"   Current Overall Score: {assessment.overall_score}/100")
            
            # Reset scores to re-run
            print("\n📍 Resetting scores and re-running with GPT-4o...")
            assessment.overall_score = None
            assessment.market_score = None
            assessment.market_analysis = None
            
            # Run AI assessment
            ai_service = AIAssessmentService(db)
            await ai_service.process_assessment(assessment.id)
            
            # Refresh to get updated data
            await db.refresh(assessment)
            
            print("\n" + "="*80)
            print("✅ ASSESSMENT COMPLETE WITH GPT-4o!")
            print("="*80)
            print(f"\n📊 New Scores:")
            print(f"   Overall Score: {assessment.overall_score:.1f}/100")
            print(f"   Market Score: {assessment.market_score:.1f}/100")
            print(f"   Location Score: {assessment.location_score:.1f}/100")
            print(f"   Financial Score: {assessment.financial_score:.1f}/100")
            print(f"   Partnership Score: {assessment.partnership_score:.1f}/100")
            print(f"   Risk Score: {assessment.risk_score:.1f}/100")
            
            # Check if market analysis is complete
            if assessment.market_analysis:
                analysis_text = assessment.market_analysis.get('analysis', '')
                print(f"\n📝 Market Analysis Length: {len(analysis_text)} characters")
                
                # Check for truncation indicators
                if analysis_text.endswith('####') or analysis_text.endswith('...'):
                    print("   ⚠️  Analysis may still be truncated")
                else:
                    print("   ✅ Analysis appears complete!")
            
            print(f"\n🎯 Generate PDF:")
            print(f"   curl -o ~/Desktop/gpt4o_report.pdf http://localhost:8000/api/v1/reports/assessment/8/pdf")
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(rerun_assessment_with_gpt4o())
