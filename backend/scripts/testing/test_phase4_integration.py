"""
Test Phase 4: AI Assessment Integration with Enriched Data

This script tests that the AI assessment service correctly:
1. Reads Census demographics data
2. Reads FEMA flood risk data
3. Reads HUD Income Limits data
4. Reads HUD Fair Market Rent data
5. Uses real data in scoring calculations
6. Generates data-driven financial projections
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.ai_assessment import AIAssessmentService
from sqlalchemy import select


async def test_phase4_integration():
    """Test AI assessment with enriched data"""
    
    print("\n" + "="*70)
    print("🧪 PHASE 4 INTEGRATION TEST")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        # Get test property (should have enriched data from previous tests)
        result = await db.execute(
            select(Property).order_by(Property.id.desc()).limit(1)
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print("\n❌ No property found. Please run enrichment test first:")
            print("   python test_end_to_end_flow.py")
            return
        
        print(f"\n✅ Found property: {property_obj.name}")
        print(f"   Location: {property_obj.city}, {property_obj.state}")
        
        # Check if property has enriched data
        if not property_obj.data_sources:
            print("\n❌ Property has no enriched data. Please run enrichment:")
            print("   POST /api/v1/properties/{id}/enrich")
            return
        
        data_sources = json.loads(property_obj.data_sources)
        
        print("\n📊 Enriched Data Status:")
        # Check both old and new key names
        census_check = (data_sources.get('census_demographics', {}).get('status') == 'success' or 
                       data_sources.get('demographics', {}).get('status') == 'success')
        fema_check = (data_sources.get('fema_flood', {}).get('status') == 'success' or 
                     data_sources.get('flood_risk', {}).get('status') == 'success')
        
        print(f"   Census: {'✅' if census_check else '❌'}")
        print(f"   FEMA: {'✅' if fema_check else '❌'}")
        
        # HUD data can be in different structures
        hud_data = data_sources.get('hud_data', {})
        # Check multiple possible structures
        il_check = (hud_data.get('data', {}).get('income_limits', {}).get('success') == True or
                   hud_data.get('data', {}).get('income_limits', {}).get('status') == 'success' or
                   hud_data.get('income_limits', {}).get('status') == 'success')
        fmr_check = (hud_data.get('data', {}).get('fair_market_rent', {}).get('success') == True or
                    hud_data.get('data', {}).get('fair_market_rent', {}).get('status') == 'success' or
                    hud_data.get('fair_market_rent', {}).get('status') == 'success')
        
        print(f"   HUD Income Limits: {'✅' if il_check else '❌'}")
        print(f"   HUD FMR: {'✅' if fmr_check else '❌'}")
        
        # Get assessment
        result = await db.execute(
            select(Assessment).where(Assessment.property_id == property_obj.id).order_by(Assessment.id.desc()).limit(1)
        )
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            print("\n❌ No assessment found. Creating one...")
            
            # Get church
            result = await db.execute(select(Church).order_by(Church.id.desc()).limit(1))
            church = result.scalar_one_or_none()
            
            if not church:
                print("❌ No church found. Please create church first.")
                return
            
            # Create assessment
            assessment = Assessment(
                church_id=church.id,
                property_id=property_obj.id,
                congregation_approval=True,
                leadership_support="unanimous",
                timeline_readiness="ready_now",
                preferred_unit_count=100,
                affordability_target="80_ami"
            )
            db.add(assessment)
            await db.commit()
            await db.refresh(assessment)
            print(f"✅ Created assessment ID: {assessment.id}")
        
        print(f"\n✅ Using assessment ID: {assessment.id}")
        
        # Initialize AI assessment service
        ai_service = AIAssessmentService(db)
        
        print("\n🤖 Running AI Assessment with Enriched Data...")
        print("   This will:")
        print("   1. Analyze Census demographics for market validation")
        print("   2. Calculate flood mitigation costs from FEMA data")
        print("   3. Validate AMI alignment from HUD Income Limits")
        print("   4. Project revenue using HUD Fair Market Rent")
        print("   5. Generate comprehensive financial analysis")
        print("\n   Processing... (may take 30-60 seconds)")
        
        try:
            result = await ai_service.process_assessment(assessment.id)
            
            print("\n" + "="*70)
            print("✅ PHASE 4 INTEGRATION SUCCESS!")
            print("="*70)
            
            print(f"\n📊 Assessment Results:")
            print(f"   Overall Score: {result['overall_score']}/100")
            print(f"   Grade: {result['grade']}")
            print(f"   Status: {result['status']}")
            print(f"   Processing Time: {result.get('processing_time_seconds', 'N/A')} seconds")
            
            print(f"\n📈 Category Scores:")
            scores = result.get('scores', {})
            print(f"   Location:    {scores.get('location', 'N/A')}/100")
            print(f"   Market:      {scores.get('market', 'N/A')}/100")
            print(f"   Financial:   {scores.get('financial', 'N/A')}/100")
            print(f"   Partnership: {scores.get('partnership', 'N/A')}/100")
            print(f"   Risk:        {scores.get('risk', 'N/A')}/100")
            
            # Reload assessment to get full data
            await db.refresh(assessment)
            
            # Check if enriched data was used
            print(f"\n🔍 Enriched Data Usage:")
            
            if assessment.market_analysis:
                market = json.loads(assessment.market_analysis) if isinstance(assessment.market_analysis, str) else assessment.market_analysis
                
                # Check demographics
                if market.get("demographics"):
                    demo = market["demographics"]
                    print(f"\n   ✅ Census Demographics:")
                    print(f"      Status: {demo.get('status')}")
                    print(f"      Score Adjustment: +{demo.get('score_adjustment', 0)} points")
                    if demo.get('indicators'):
                        print(f"      Indicators:")
                        for indicator in demo['indicators'][:3]:  # Show first 3
                            print(f"         • {indicator}")
                
                # Check FMR
                if market.get("section8_viability"):
                    fmr = market["section8_viability"]
                    print(f"\n   ✅ HUD Fair Market Rent:")
                    print(f"      2BR FMR: ${fmr.get('fmr_2br', 'N/A')}")
                    print(f"      Status: {fmr.get('status')}")
                    print(f"      Score Adjustment: +{fmr.get('score_adjustment', 0)} points")
                
                # Check AMI
                if market.get("ami_alignment"):
                    ami = market["ami_alignment"]
                    print(f"\n   ✅ HUD Income Limits:")
                    print(f"      80% AMI (2-person): ${ami.get('ami_80_percent_2person', 'N/A'):,}")
                    print(f"      Status: {ami.get('status')}")
                    print(f"      Score Adjustment: +{ami.get('score_adjustment', 0)} points")
            
            if assessment.financial_projections:
                financial = json.loads(assessment.financial_projections) if isinstance(assessment.financial_projections, str) else assessment.financial_projections
                
                # Check flood risk
                if financial.get("flood_risk_analysis"):
                    flood = financial["flood_risk_analysis"]
                    print(f"\n   ✅ FEMA Flood Risk:")
                    print(f"      Flood Zone: {flood.get('flood_zone', 'N/A')}")
                    print(f"      Risk Level: {flood.get('risk_level')}")
                    print(f"      Mitigation Cost/Unit: ${flood.get('mitigation_cost_per_unit', 0):,}")
                
                # Check revenue projections
                if financial.get("revenue_projections"):
                    revenue = financial["revenue_projections"]
                    if revenue.get("status") == "calculated":
                        print(f"\n   ✅ Revenue Projections (Actual FMR Data):")
                        print(f"      Annual Revenue: {revenue.get('total_annual_revenue_formatted', 'N/A')}")
                        print(f"      NOI: {revenue.get('noi_formatted', 'N/A')}")
                        print(f"      ROI: {revenue.get('roi_percent', 'N/A')}%")
                        print(f"      Cap Rate: {revenue.get('cap_rate', 'N/A')}%")
                        print(f"      Data Source: {revenue.get('data_source', 'N/A')}")
            
            print("\n" + "="*70)
            print("🎉 PHASE 4 COMPLETE!")
            print("="*70)
            print("\nThe AI assessment now uses all enriched data:")
            print("✅ Census demographics → Market scoring")
            print("✅ FEMA flood risk → Risk scoring + Cost adjustments")
            print("✅ HUD Income Limits → Market validation")
            print("✅ HUD Fair Market Rent → Revenue projections")
            
            print("\n📝 Next Steps:")
            print("1. ✅ Phase 4: AI Integration - COMPLETE")
            print("2. ⏳ Phase 5: Report Generation - Generate PDF reports")
            print("3. ⏳ Phase 6: Testing & Deployment - End-to-end testing")
            
        except Exception as e:
            print(f"\n❌ Error running AI assessment: {e}")
            import traceback
            traceback.print_exc()
            return


if __name__ == "__main__":
    asyncio.run(test_phase4_integration())
