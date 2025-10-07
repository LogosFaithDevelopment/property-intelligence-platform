"""Quick check of Assessment #38 results"""
import asyncio
import json
from app.database import AsyncSessionLocal
from app.models import Assessment
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        stmt = select(Assessment).where(Assessment.id == 38)
        result = await db.execute(stmt)
        assessment = result.scalar_one()
        
        print("=" * 80)
        print(f"ASSESSMENT #{assessment.id} - DETAILED RESULTS")
        print("=" * 80)
        print(f"\n✅ Overall Score: {assessment.overall_score}/100 ({assessment.score_grade})")
        print(f"   Status: {assessment.status.value}")
        
        print(f"\n📏 Available Build Space:")
        print(f"   Specified: {assessment.available_build_sqft:,} sqft ({assessment.available_build_acres} acres)")
        print(f"   Notes: {assessment.build_area_notes}")
        
        if assessment.financial_projections:
            if isinstance(assessment.financial_projections, str):
                fin = json.loads(assessment.financial_projections)
            else:
                fin = assessment.financial_projections
            
            print(f"\n💰 Financial Analysis (Score: {fin.get('score', 0):.1f}/100):")
            print(f"   Using Available Space: {fin.get('using_available_space', False)}")
            print(f"   Lot Size Used in Calc: {fin.get('lot_size_sqft', 0):,} sqft")
            
            if fin.get('available_build_sqft'):
                print(f"   ✅ Available Build: {fin.get('available_build_sqft', 0):,} sqft")
            
            print(f"   Total Property Lot: {fin.get('total_lot_size_sqft', 0):,} sqft")
            print(f"   Feasible Units: {fin.get('feasible_units', 0)}")
            print(f"   Within Target (40-140): {fin.get('within_target_range', False)}")
            print(f"   Cost Per Unit: {fin.get('adjusted_cost_per_unit_formatted', 'N/A')}")
            print(f"   Under Target Cost: {fin.get('under_target', False)}")
            
            if fin.get('disqualified'):
                print(f"\n   ⚠️ DISQUALIFIED: {fin.get('disqualification_reason', 'Unknown')}")
        
        print(f"\n📊 Score Breakdown:")
        print(f"   Financial:    {assessment.financial_score:.1f}/100")
        print(f"   Location:     {assessment.location_score:.1f}/100")
        print(f"   Market:       {assessment.market_score:.1f}/100")
        print(f"   Partnership:  {assessment.partnership_score:.1f}/100")
        print(f"   Risk:         {assessment.risk_score:.1f}/100")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
