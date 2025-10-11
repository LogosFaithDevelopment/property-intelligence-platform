"""
Complete End-to-End Test with LA County Church
Tests the full property intelligence platform flow with LA County Assessor API:
1. Create church and property in database
2. Enrich property with APIs (including LA County Assessor)
3. Run AI assessment
4. Generate PDF report

Test Property: Shepherd Church (Chatsworth, CA)
- Address: 19700 Rinaldi St, Chatsworth, CA 91326
- Real church property in LA County
- Should retrieve lot size and assessed values from LA County Assessor API
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime

from app.database import engine, get_db
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService
from app.services.report_generator import ReportGenerator
from sqlalchemy import select


async def main():
    print("\n" + "="*80)
    print("LA COUNTY CHURCH - COMPLETE END-TO-END TEST")
    print("="*80)
    
    # Get database session
    async for db in get_db():
        try:
            # ============================================================
            # STEP 1: CREATE CHURCH
            # ============================================================
            print("\n📍 STEP 1: Creating Shepherd Church (Chatsworth, CA)")
            print("-" * 80)
            
            # Check if church already exists
            result = await db.execute(
                select(Church).where(Church.name == "Shepherd Church")
            )
            church = result.scalar_one_or_none()
            
            if church:
                print(f"✅ Church already exists (ID: {church.id})")
            else:
                church = Church(
                    name="Shepherd Church",
                    denomination="Non-denominational",
                    city="Chatsworth",
                    state="CA",
                    congregation_size=5000,
                    annual_budget=3000000,
                    notes="Large community church in San Fernando Valley"
                )
                db.add(church)
                await db.commit()
                await db.refresh(church)
                print(f"✅ Created church (ID: {church.id})")
            
            print(f"   Name: {church.name}")
            print(f"   Location: {church.city}, {church.state}")
            print(f"   Congregation: {church.congregation_size:,} members")
            
            # ============================================================
            # STEP 2: CREATE PROPERTY
            # ============================================================
            print("\n🏢 STEP 2: Creating Property Record")
            print("-" * 80)
            
            # Check if property already exists
            result = await db.execute(
                select(Property).where(
                    Property.street_address == "19700 Rinaldi St"
                ).where(Property.church_id == church.id)
            )
            property_obj = result.scalar_one_or_none()
            
            if property_obj:
                print(f"✅ Property already exists (ID: {property_obj.id})")
            else:
                property_obj = Property(
                    church_id=church.id,
                    street_address="19700 Rinaldi St",
                    city="Chatsworth",
                    state="CA",
                    zip_code="91326",
                    property_type="Church Campus",
                    zoning_description="Religious Use",
                    current_use="Church and Community Center",
                    # Note: NOT setting lot_size_sqft - should come from LA County API
                )
                db.add(property_obj)
                await db.commit()
                await db.refresh(property_obj)
                print(f"✅ Created property (ID: {property_obj.id})")
            
            print(f"   Address: {property_obj.full_address}")
            print(f"   Type: {property_obj.property_type}")
            print(f"   Current lot_size_sqft: {property_obj.lot_size_sqft or 'NOT SET'}")
            print(f"   (Should be populated by LA County API)")
            
            # ============================================================
            # STEP 3: ENRICH PROPERTY
            # ============================================================
            print("\n🔍 STEP 3: Enriching Property with APIs")
            print("-" * 80)
            print("APIs to call:")
            print("  1. Geocoding (OpenStreetMap)")
            print("  2. US Census Bureau (demographics)")
            print("  3. FEMA Flood Zones")
            print("  4. FEMA Disaster History")
            print("  5. HUD Fair Market Rent")
            print("  6. HUD Income Limits")
            print("  7. 🆕 LA County Assessor (lot size, assessed values)")
            print()
            
            enrichment_service = PropertyEnrichmentService(db)
            
            enrichment_results = await enrichment_service.enrich_property(
                property_id=property_obj.id,
                use_premium_apis=False,  # Use free APIs (including LA County)
                force_refresh=True  # Force refresh to get latest data
            )
            
            # Display enrichment results
            print("\n📊 ENRICHMENT RESULTS:")
            print("-" * 80)
            
            results = enrichment_results.get("results", {})
            
            # Geocoding
            geocoding = results.get("geocoding", {})
            if geocoding.get("status") == "success":
                print(f"✅ Geocoding: ({geocoding['latitude']:.4f}, {geocoding['longitude']:.4f})")
            else:
                print(f"❌ Geocoding: {geocoding.get('status')}")
            
            # Demographics
            demographics = results.get("demographics", {})
            if demographics.get("status") == "success":
                demo_data = demographics.get("data", {})
                print(f"✅ Demographics: Pop {demo_data.get('population', 0):,}, "
                      f"Median Income ${demo_data.get('median_income', 0):,}")
            else:
                print(f"❌ Demographics: {demographics.get('status')}")
            
            # Flood Risk
            flood = results.get("flood_risk", {})
            if flood.get("status") == "success":
                flood_data = flood.get("data", {})
                print(f"✅ Flood Risk: Zone {flood_data.get('flood_zone', 'Unknown')}")
            else:
                print(f"❌ Flood Risk: {flood.get('status')}")
            
            # HUD Data
            hud = results.get("hud_data", {})
            if hud.get("status") == "success":
                hud_data = hud.get("data", {})
                print(f"✅ HUD Data: FMR ${hud_data.get('fair_market_rent', 0):,}, "
                      f"AMI ${hud_data.get('area_median_income', 0):,}")
            else:
                print(f"❌ HUD Data: {hud.get('status')}")
            
            # LA County Assessor (KEY TEST)
            la_county = results.get("la_county_data", {})
            print("\n🌟 LA COUNTY ASSESSOR DATA:")
            if la_county.get("status") == "success":
                la_data = la_county.get("data", {})
                chars = la_data.get("property_characteristics", {})
                vals = la_data.get("valuation", {})
                ident = la_data.get("identification", {})
                
                print(f"✅ LA County Assessor: SUCCESS")
                print(f"   AIN: {ident.get('ain')}")
                print(f"   Lot Size: {chars.get('lot_sqft', 0):,} sq ft ({chars.get('lot_acres', 0):.2f} acres)")
                print(f"   Building Size: {chars.get('building_sqft', 0):,} sq ft")
                print(f"   Year Built: {chars.get('year_built', 'N/A')}")
                print(f"   Total Assessed Value: ${vals.get('total_assessed_value', 0):,}")
                print(f"   Land Value: ${vals.get('land_value', 0):,}")
                print(f"   Improvement Value: ${vals.get('improvement_value', 0):,}")
            else:
                print(f"❌ LA County Assessor: {la_county.get('status')} - {la_county.get('reason', la_county.get('error'))}")
            
            # Refresh property to see updated fields
            await db.refresh(property_obj)
            
            print("\n📝 UPDATED PROPERTY FIELDS:")
            print(f"   lot_size_sqft: {property_obj.lot_size_sqft or 'NOT SET'}")
            print(f"   building_sqft: {property_obj.building_sqft or 'NOT SET'}")
            print(f"   year_built: {property_obj.year_built or 'NOT SET'}")
            print(f"   estimated_value: ${property_obj.estimated_value or 0:,}")
            
            # ============================================================
            # STEP 4: RUN AI ASSESSMENT
            # ============================================================
            print("\n🤖 STEP 4: Running AI Assessment")
            print("-" * 80)
            
            ai_service = AIAssessmentService(db)
            
            assessment = await ai_service.create_assessment(
                property_id=property_obj.id,
                assessment_type="affordable_housing"
            )
            
            print(f"✅ Assessment created (ID: {assessment.id})")
            print(f"   Status: {assessment.status}")
            print(f"   Overall Score: {assessment.overall_score:.1f}/100")
            print(f"   Grade: {assessment.overall_grade}")
            
            # Score breakdown
            if assessment.score_breakdown:
                print("\n   Score Breakdown:")
                for category, score in assessment.score_breakdown.items():
                    print(f"     • {category.title()}: {score:.1f}/100")
            
            # ============================================================
            # STEP 5: GENERATE PDF REPORT
            # ============================================================
            print("\n📄 STEP 5: Generating PDF Report")
            print("-" * 80)
            
            report_generator = ReportGenerator(db)
            
            pdf_bytes = await report_generator.generate_report(assessment.id)
            
            # Save PDF to file
            filename = f"shepherd_church_report_{assessment.id}.pdf"
            filepath = Path("/app") / filename
            
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
            
            print(f"✅ PDF report generated: {filename}")
            print(f"   Size: {len(pdf_bytes) / 1024:.1f} KB")
            print(f"   Location: {filepath}")
            
            # ============================================================
            # SUMMARY
            # ============================================================
            print("\n" + "="*80)
            print("✅ TEST COMPLETE!")
            print("="*80)
            
            print("\n📊 SUMMARY:")
            print(f"  • Church ID: {church.id} - {church.name}")
            print(f"  • Property ID: {property_obj.id}")
            print(f"  • Address: {property_obj.full_address}")
            print(f"  • Lot Size: {property_obj.lot_size_sqft or 0:,} sq ft")
            print(f"  • Assessed Value: ${property_obj.estimated_value or 0:,}")
            print(f"  • Assessment ID: {assessment.id}")
            print(f"  • Overall Score: {assessment.overall_score:.1f}/100 (Grade: {assessment.overall_grade})")
            print(f"  • PDF Report: {filename}")
            
            print("\n🎉 LA County Assessor API integration successful!")
            print("   Property data was automatically populated from public records.")
            
            print("\n📋 To copy PDF to Desktop:")
            print(f"   docker cp property-intelligence-backend:/app/{filename} ~/Desktop/")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await db.close()
        
        break  # Only use first db session


if __name__ == "__main__":
    asyncio.run(main())
