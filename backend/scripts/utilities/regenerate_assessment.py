#!/usr/bin/env python3
"""
Regenerate assessment for a specific church and property
"""
import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.ai_assessment import AIAssessmentService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL and ensure it uses asyncpg
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/property_intel')
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
elif not DATABASE_URL.startswith('postgresql+asyncpg://'):
    DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@postgres:5432/property_intel'

async def regenerate_assessment(church_id: int, property_id: int):
    """Regenerate assessment for given church and property"""
    
    print(f"🔄 Regenerating assessment for Church ID {church_id}, Property ID {property_id}...")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if church and property exist
            church_result = await session.execute(select(Church).where(Church.id == church_id))
            church = church_result.scalar_one_or_none()
            
            if not church:
                print(f"❌ Church ID {church_id} not found")
                return
            
            property_result = await session.execute(select(Property).where(Property.id == property_id))
            property_obj = property_result.scalar_one_or_none()
            
            if not property_obj:
                print(f"❌ Property ID {property_id} not found")
                return
            
            print(f"✓ Found church: {church.name}")
            print(f"✓ Found property: {property_obj.street_address}")
            
            # Check if assessment already exists
            assessment_result = await session.execute(
                select(Assessment)
                .where(Assessment.church_id == church_id)
                .where(Assessment.property_id == property_id)
            )
            existing = assessment_result.scalar_one_or_none()
            
            if existing:
                print(f"⚠️  Assessment ID {existing.id} already exists - will update it")
            
            # Create assessment service and run assessment
            service = AIAssessmentService(session)
            
            print("\n🚀 Starting AI assessment...")
            print("   This will:")
            print("   - Calculate 3/4/5 story scenarios")
            print("   - Use $325K per unit cost")
            print("   - Use 425 sqft average unit size")
            print("   - Use 20% equity / 80% debt")
            print("   - Fetch market data (HUD, Census, FEMA)")
            print("")
            
            # Get or create assessment
            assessment_id = existing.id if existing else None
            
            if not assessment_id:
                print("❌ No assessment found - please create one first")
                return
            
            result = await service.process_assessment(
                assessment_id=assessment_id
            )
            
            print(f"\n✅ Assessment completed!")
            print(f"   Assessment ID: {result.get('assessment_id')}")
            print(f"   Overall Score: {result.get('overall_score', 'N/A')}")
            print(f"   Status: {result.get('status')}")
            
            # Fetch the generated assessment to show scenarios
            if result.get('assessment_id'):
                assessment_result = await session.execute(
                    select(Assessment).where(Assessment.id == result['assessment_id'])
                )
                assessment = assessment_result.scalar_one_or_none()
                
                if assessment and assessment.financial_projections:
                    fp = assessment.financial_projections
                    
                    print("\n📊 Multi-Story Scenarios:")
                    scenarios = fp.get('multi_story_scenarios', {}).get('scenarios', {})
                    
                    for scenario_name in ['3_story', '4_story', '5_story']:
                        if scenario_name in scenarios:
                            s = scenarios[scenario_name]
                            print(f"\n   {scenario_name.replace('_', ' ').title()}:")
                            print(f"      Units: {s.get('units')}")
                            print(f"      Dev Cost: ${s.get('total_development_cost', 0):,.0f}")
                            print(f"      Equity (20%): ${s.get('equity_required', 0):,.0f}")
                            print(f"      IRR: {s.get('irr_percent', 0):.1f}%")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
    await engine.dispose()
    print("\n✅ Done!")

if __name__ == "__main__":
    # Default to Manchester property (church 42, property 30)
    church_id = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    property_id = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    asyncio.run(regenerate_assessment(church_id, property_id))
