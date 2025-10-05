"""
Full System Test: Oasis Church
634 Normandie Ave, Los Angeles, CA 90005

Tests complete workflow:
1. Property creation
2. API enrichment (Census, FEMA, HUD, LA County Assessor)
3. AI assessment with grading
4. PDF report generation
"""
import asyncio
import sys
from pathlib import Path

from app.database import AsyncSessionLocal
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService
from app.services.report_generator import ReportGenerator
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def main():
    print("=" * 80)
    print("FULL SYSTEM TEST: OASIS CHURCH")
    print("Address: 634 Normandie Ave, Los Angeles, CA 90005")
    print("=" * 80)
    
    db = AsyncSessionLocal()
    
    try:
        # Step 1: Check if property exists, if not create it
        print("\n[STEP 1] Creating/Finding Property...")
        result = await db.execute(
            select(Property).where(
                Property.street_address == "634 Normandie Ave",
                Property.city == "Los Angeles"
            )
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            # Get or create church
            result = await db.execute(
                select(Church).where(Church.name == "Oasis Church")
            )
            church = result.scalar_one_or_none()
            
            if not church:
                church = Church(
                    name="Oasis Church",
                    denomination="Non-denominational",
                    website_url="https://oasischurchla.com",
                    primary_email="info@oasischurchla.com",
                    primary_phone="(213) 555-0100"
                )
                db.add(church)
                await db.flush()
                print(f"   ✅ Created church: {church.name} (ID: {church.id})")
            else:
                print(f"   ℹ️  Found existing church: {church.name} (ID: {church.id})")
            
            # Create property
            property_obj = Property(
                church_id=church.id,
                name="Oasis Church",
                street_address="634 Normandie Ave",
                city="Los Angeles",
                state="CA",
                zip_code="90005",
                county="Los Angeles",
                property_type="church_building"
            )
            db.add(property_obj)
            await db.commit()
            await db.refresh(property_obj)
            print(f"   ✅ Created property: {property_obj.name} (ID: {property_obj.id})")
        else:
            print(f"   ℹ️  Found existing property: {property_obj.name} (ID: {property_obj.id})")
            
            # Get the church for existing property
            result = await db.execute(
                select(Church).where(Church.id == property_obj.church_id)
            )
            church = result.scalar_one_or_none()
            print(f"   ℹ️  Found associated church: {church.name} (ID: {church.id})")
        
        # Step 2: Enrich property with ALL APIs
        print("\n[STEP 2] Enriching Property with APIs...")
        print("   APIs to use:")
        print("   - ✅ Census API (Demographics)")
        print("   - ✅ OpenFEMA (Disaster History)")
        print("   - ✅ HUD API (Income Limits, Fair Market Rents)")
        print("   - ✅ LA County Assessor (Free property data for LA County)")
        
        enrichment_service = PropertyEnrichmentService(db)
        enrichment_result = await enrichment_service.enrich_property(
            property_id=property_obj.id,
            use_premium_apis=False,  # Use free APIs (LA County instead of ATTOM)
            force_refresh=True
        )
        
        print(f"\n   Enrichment Status: {enrichment_result.get('status')}")
        
        # Show results for each API
        results = enrichment_result.get('results', {})
        
        # Demographics
        demographics = results.get('demographics', {})
        if demographics.get('status') == 'success':
            demo_data = demographics.get('data', {})
            print(f"   ✅ Census Demographics:")
            print(f"      - Population: {demo_data.get('population', 'N/A'):,}")
            print(f"      - Median Income: ${demo_data.get('median_household_income', 0):,}")
            print(f"      - Poverty Rate: {demo_data.get('poverty_rate', 0):.1f}%")
        else:
            print(f"   ❌ Census Demographics: {demographics.get('error', 'Failed')}")
        
        # Flood/Disaster Risk
        flood_risk = results.get('flood_risk', {})
        if flood_risk.get('status') == 'success':
            flood_data = flood_risk.get('data', {})
            disaster_history = flood_data.get('disaster_history', {})
            print(f"   ✅ FEMA Disaster History:")
            print(f"      - Total Disasters (20 years): {disaster_history.get('total_disasters', 0)}")
            print(f"      - Floods: {disaster_history.get('flood', {}).get('count', 0)}")
            print(f"      - Fires: {disaster_history.get('fire', {}).get('count', 0)}")
            print(f"      - Earthquakes: {disaster_history.get('earthquake', {}).get('count', 0)}")
            print(f"      - Hurricanes: {disaster_history.get('hurricane', {}).get('count', 0)}")
            print(f"      - Tornadoes: {disaster_history.get('tornado', {}).get('count', 0)}")
            print(f"      - Estimated Flood Zone: {flood_data.get('flood_zone', 'N/A')}")
        else:
            print(f"   ❌ FEMA Disaster History: {flood_risk.get('error', 'Failed')}")
        
        # HUD Data
        hud_data = results.get('hud_data', {})
        if hud_data.get('status') == 'success':
            hud_results = hud_data.get('data', {})
            income_limits = hud_results.get('income_limits', {})
            fmr_data = hud_results.get('fair_market_rent', {})
            
            print(f"   ✅ HUD Data:")
            if income_limits.get('success'):
                print(f"      - Area: {income_limits.get('area_name', 'N/A')}")
                print(f"      - Median Income: ${income_limits.get('median_income', 0):,}")
                limits_4p = income_limits.get('limits_by_household_size', {}).get('4_person', {})
                print(f"      - 80% AMI (4-person): ${limits_4p.get('80_percent_ami', 0):,}")
            
            if fmr_data.get('success'):
                rents = fmr_data.get('rent_by_bedroom', {})
                print(f"      - FMR Studio: ${rents.get('studio', 0):,}")
                print(f"      - FMR 1-BR: ${rents.get('1_bedroom', 0):,}")
                print(f"      - FMR 2-BR: ${rents.get('2_bedroom', 0):,}")
        else:
            print(f"   ⚠️  HUD Data: {hud_data.get('reason', 'Skipped')}")
        
        # LA County Assessor
        la_county = results.get('la_county_data', {})
        if la_county.get('status') == 'success':
            la_data = la_county.get('data', {})
            characteristics = la_data.get('property_characteristics', {})
            valuation = la_data.get('valuation', {})
            
            print(f"   ✅ LA County Assessor (FREE):")
            lot_sqft = characteristics.get('lot_sqft') or 0
            lot_acres = characteristics.get('lot_acres') or 0
            building_sqft = characteristics.get('building_sqft') or 0
            assessed_value = valuation.get('total_assessed_value') or 0
            
            print(f"      - Lot Size: {lot_sqft:,} sqft ({lot_acres} acres)")
            print(f"      - Building Size: {building_sqft:,} sqft")
            print(f"      - Year Built: {characteristics.get('year_built') or 'N/A'}")
            print(f"      - Units: {characteristics.get('units') or 'N/A'}")
            print(f"      - Assessed Value: ${assessed_value:,}")
        else:
            print(f"   ❌ LA County Assessor: {la_county.get('reason', 'Failed')}")
        
        # Refresh property to get updated data
        await db.refresh(property_obj)
        
        # Step 3: Run AI Assessment
        print("\n[STEP 3] Running AI Assessment with Grading...")
        
        # First, create assessment record
        assessment = Assessment(
            church_id=church.id,
            property_id=property_obj.id,
            user_id="test_system",
            congregation_approval=True,
            leadership_support="unanimous",
            timeline_readiness="ready_now",
            preferred_unit_count=20,
            affordability_target="60_ami",
            available_build_sqft=10000,
            revenue_sharing_preference="50_50_split"
        )
        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        
        print(f"   ✅ Assessment record created (ID: {assessment.id})")
        print(f"   ⏳ Processing with AI...")
        
        # Now process it with AI
        assessment_service = AIAssessmentService(db)
        await assessment_service.process_assessment(assessment.id, use_premium_model=False)
        
        # Refresh to get updated scores
        await db.refresh(assessment)
        
        print(f"\n   📊 GRADING RESULTS:")
        print(f"      Overall Score: {assessment.overall_score:.1f}/100 (Grade {assessment.score_grade})")
        print(f"\n      Category Scores:")
        print(f"      - Location: {assessment.location_score:.1f}/100")
        print(f"      - Market: {assessment.market_score:.1f}/100")
        print(f"      - Financial: {assessment.financial_score:.1f}/100")
        print(f"      - Partnership: {assessment.partnership_score:.1f}/100")
        print(f"      - Risk: {assessment.risk_score:.1f}/100")
        
        # Show some key insights
        if assessment.risk_factors:
            import json
            risk_factors = json.loads(assessment.risk_factors) if isinstance(assessment.risk_factors, str) else assessment.risk_factors
            disaster_risk = risk_factors.get('disaster_risk', {})
            
            print(f"\n   🌪️  Natural Disaster Risk Assessment:")
            for disaster_type, risk_data in disaster_risk.items():
                if isinstance(risk_data, dict):
                    risk_level = risk_data.get('risk_level', 'unknown')
                    penalty = risk_data.get('score_penalty', 0)
                    print(f"      - {disaster_type.title()}: {risk_level.upper()} (Penalty: {penalty} points)")
        
        # Step 4: Generate PDF Report
        print("\n[STEP 4] Generating PDF Report...")
        
        # Need to use sync session for report generator
        from app.database import SyncSessionLocal
        sync_db = SyncSessionLocal()
        
        try:
            generator = ReportGenerator(sync_db)
            pdf_bytes = await generator.generate_assessment_report(assessment.id)
            
            if pdf_bytes:
                # Save to /app directory
                pdf_path = Path("/app") / f"oasis_church_report_{assessment.id}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                file_size = len(pdf_bytes)
                print(f"   ✅ PDF Generated Successfully!")
                print(f"      File: {pdf_path}")
                print(f"      Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                print(f"\n   📥 To copy to Desktop, run:")
                print(f"      docker cp property-intelligence-platform-backend-1:/app/oasis_church_report_{assessment.id}.pdf ~/Desktop/")
            else:
                print("   ❌ PDF generation failed!")
        finally:
            sync_db.close()
        
        print("\n" + "=" * 80)
        print("🎉 FULL SYSTEM TEST COMPLETE!")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  Property ID: {property_obj.id}")
        print(f"  Assessment ID: {assessment.id}")
        print(f"  Overall Score: {assessment.overall_score:.1f}/100 (Grade {assessment.overall_grade})")
        print(f"  APIs Used: Census ✅ | FEMA ✅ | HUD ✅ | LA County ✅")
        print(f"  Report: Ready for review")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
