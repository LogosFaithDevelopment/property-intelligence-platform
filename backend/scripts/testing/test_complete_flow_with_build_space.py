"""
Complete Test Flow with Available Build Space
Demonstrates full workflow with new client-provided build space data
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from app.database import AsyncSessionLocal, SyncSessionLocal
from app.models import Assessment, Church, Property
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService
from app.services.report_generator import ReportGenerator
from sqlalchemy import select


async def main():
    """Complete test flow with available build space"""
    print("=" * 80)
    print("COMPLETE TEST FLOW - WITH AVAILABLE BUILD SPACE")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        try:
            # ========================================================================
            # Step 1: Create Test Church
            # ========================================================================
            print("\n📍 Step 1: Creating Test Church...")
            
            church = Church(
                name="Shepherd of the Hills Church",
                street_address="19700 Rinaldi St",
                city="Los Angeles",
                state="CA",
                zip_code="91326",
                denomination="Evangelical",
                congregation_size=8500,
                founded_year=1974,
                primary_phone="(818) 882-7777",
                primary_email="info@theshepherd.org",
                website_url="https://theshepherd.org",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(church)
            await db.commit()
            await db.refresh(church)
            
            print(f"✅ Church Created: {church.name}")
            print(f"   ID: {church.id}")
            print(f"   Location: {church.city}, {church.state}")
            print(f"   Congregation: {church.congregation_size:,}")
            
            # ========================================================================
            # Step 2: Create Property (LA County - will use LA County Assessor API)
            # ========================================================================
            print("\n📍 Step 2: Creating Property...")
            
            property_obj = Property(
                church_id=church.id,
                name="Main Campus - Parking Lot Redevelopment",
                property_type="parking_lot",
                street_address="19700 Rinaldi St",
                city="Los Angeles",
                state="CA",
                zip_code="91326",
                county="Los Angeles",
                # Note: lot_size will be populated by LA County Assessor API
                zoning_classification="residential_medium_density",
                zoning_description="R3 - Multiple Dwelling Zone",
                current_usage="Parking lot - available for affordable housing development",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(property_obj)
            await db.commit()
            await db.refresh(property_obj)
            
            print(f"✅ Property Created: {property_obj.name}")
            print(f"   ID: {property_obj.id}")
            print(f"   Address: {property_obj.full_address}")
            print(f"   Type: {property_obj.property_type.value}")
            
            # ========================================================================
            # Step 3: Enrich Property with APIs
            # ========================================================================
            print("\n📍 Step 3: Enriching Property with API Data...")
            print("   (This will take 30-45 seconds...)")
            print("   • Geocoding address")
            print("   • LA County Assessor API (lot size, assessed value)")
            print("   • US Census Bureau (demographics)")
            print("   • FEMA Flood Risk")
            print("   • FEMA Disaster History")
            print("   • HUD Income Limits & Fair Market Rent")
            
            enrichment_service = PropertyEnrichmentService(db)
            enrichment_results = await enrichment_service.enrich_property(
                property_id=property_obj.id,
                use_premium_apis=False,  # Use free APIs
                force_refresh=True
            )
            
            # Reload property to see enriched data
            await db.refresh(property_obj)
            
            print(f"\n✅ Property Enrichment Complete!")
            print(f"\n📐 Property Details (from APIs):")
            if property_obj.latitude and property_obj.longitude:
                print(f"   Coordinates: ({property_obj.latitude:.4f}, {property_obj.longitude:.4f})")
            else:
                print(f"   Coordinates: Not available (geocoding failed)")
            if property_obj.lot_size_sqft:
                print(f"   Lot Size: {property_obj.lot_size_sqft:,.0f} sq ft")
            if property_obj.lot_size_acres:
                print(f"   Lot Size: {property_obj.lot_size_acres:.2f} acres")
            if property_obj.assessed_value:
                print(f"   Assessed Value: ${property_obj.assessed_value:,.0f}")
            if property_obj.flood_zone:
                print(f"   Flood Zone: {property_obj.flood_zone}")
            
            # Show data sources
            print(f"\n📡 Data Sources Used:")
            if property_obj.data_sources:
                sources = json.loads(property_obj.data_sources)
                for source_name, source_data in sources.items():
                    status = "✅" if source_data.get("status") == "success" else "❌"
                    print(f"   {status} {source_name}")
            
            # ========================================================================
            # Step 4: Create Assessment with Available Build Space
            # ========================================================================
            print("\n📍 Step 4: Creating Assessment with Build Space Specifications...")
            
            # Church has 2 acres total, but only wants to use 25,000 sq ft for housing
            available_sqft = 25000.0
            available_acres = available_sqft / 43560.0  # Convert to acres
            
            assessment = Assessment(
                church_id=church.id,
                property_id=property_obj.id,
                
                # Church Readiness
                congregation_approval=True,
                leadership_support="unanimous",
                timeline_readiness="ready_now",
                
                # Development Preferences
                preferred_unit_count=45,
                affordability_target="60_ami",
                
                # NEW FIELD: Available Build Space (client-provided)
                available_build_sqft=available_sqft,
                available_build_acres=available_acres,
                build_area_notes="Southeast corner of parking lot, preserving Sunday overflow parking",
                
                # Assessment Metadata
                priority="high",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(assessment)
            await db.commit()
            await db.refresh(assessment)
            
            print(f"✅ Assessment Created: ID {assessment.id}")
            print(f"   Status: {assessment.status.value}")
            print(f"   Priority: {assessment.priority.value}")
            print(f"\n   🏗️  Build Space Specifications:")
            print(f"   Available Build Area: {assessment.available_build_sqft:,.0f} sq ft")
            print(f"   Available Build Area: {assessment.available_build_acres:.2f} acres")
            print(f"   Build Area Notes: {assessment.build_area_notes}")
            print(f"   Preferred Units: {assessment.preferred_unit_count}")
            
            # Calculate density
            if assessment.available_build_sqft and assessment.preferred_unit_count:
                sqft_per_unit = assessment.available_build_sqft / assessment.preferred_unit_count
                print(f"   Target Density: {sqft_per_unit:,.0f} sq ft per unit")
            
            # ========================================================================
            # Step 5: Process Assessment with AI
            # ========================================================================
            print("\n📍 Step 5: Processing Assessment with AI...")
            print("   (This takes 15-20 seconds...)")
            
            ai_service = AIAssessmentService(db)
            result = await ai_service.process_assessment(assessment.id)
            
            if result["status"] == "completed":
                print(f"\n✅ AI Processing Complete!")
                print(f"   Overall Score: {result['overall_score']:.1f}/100")
                print(f"   Grade: {result.get('grade', 'N/A')}")
                print(f"   Duration: {result.get('processing_time_seconds', 0):.1f}s")
                
                print(f"\n📊 Score Breakdown:")
                scores = result.get('scores', {})
                print(f"   Financial:   {scores.get('financial_score', 0):5.1f}/100")
                print(f"   Location:    {scores.get('location_score', 0):5.1f}/100")
                print(f"   Market:      {scores.get('market_score', 0):5.1f}/100")
                print(f"   Partnership: {scores.get('partnership_score', 0):5.1f}/100")
                print(f"   Risk:        {scores.get('risk_score', 0):5.1f}/100")
            else:
                print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                return
            
            # ========================================================================
            # Step 6: Generate PDF Report
            # ========================================================================
            print("\n📍 Step 6: Generating PDF Report...")
            print("   (This takes 10-15 seconds...)")
            
            # Reload assessment with all relationships
            assessment_stmt = select(Assessment).where(Assessment.id == assessment.id)
            assessment_result = await db.execute(assessment_stmt)
            assessment = assessment_result.scalar_one()
            
            # Generate report (using sync session)
            sync_db = SyncSessionLocal()
            try:
                generator = ReportGenerator(sync_db)
                pdf_bytes = await generator.generate_assessment_report(assessment.id)
            finally:
                sync_db.close()
            
            if pdf_bytes:
                # Save PDF
                pdf_filename = f"grace_community_report_{assessment.id}.pdf"
                pdf_path = Path("/app") / pdf_filename
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                file_size = len(pdf_bytes)
                print(f"\n✅ PDF Report Generated!")
                print(f"   File: {pdf_path}")
                print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                print(f"\n📥 To copy to Desktop, run:")
                print(f"   docker cp property-intelligence-platform-backend-1:/app/{pdf_filename} ~/Desktop/")
            else:
                print(f"❌ PDF generation failed!")
                return
            
            # ========================================================================
            # Step 7: Summary
            # ========================================================================
            print("\n" + "=" * 80)
            print("✅ SUCCESS - COMPLETE TEST FLOW FINISHED")
            print("=" * 80)
            
            print(f"\n📋 Summary:")
            print(f"   Church ID: {church.id} - {church.name}")
            print(f"   Property ID: {property_obj.id} - {property_obj.name}")
            print(f"   Assessment ID: {assessment.id}")
            
            print(f"\n📐 Property Data (API-Enriched):")
            if property_obj.lot_size_sqft:
                print(f"   Total Lot: {property_obj.lot_size_sqft:,.0f} sq ft ({property_obj.lot_size_acres:.2f} acres)")
            else:
                print(f"   Total Lot: Not available from LA County API")
            if property_obj.assessed_value:
                print(f"   Assessed Value: ${property_obj.assessed_value:,.0f}")
            if property_obj.flood_zone:
                print(f"   Flood Zone: {property_obj.flood_zone}")
            
            print(f"\n🏗️  Build Space (Client-Provided):")
            print(f"   Available for Housing: {assessment.available_build_sqft:,.0f} sq ft ({assessment.available_build_acres:.2f} acres)")
            print(f"   Build Notes: {assessment.build_area_notes}")
            if property_obj.lot_size_sqft:
                print(f"   Utilization: {(assessment.available_build_sqft / property_obj.lot_size_sqft * 100):.1f}% of total lot")
            
            print(f"\n📊 Assessment Results:")
            print(f"   Overall Score: {assessment.overall_score:.1f}/100")
            print(f"   Grade: {assessment.score_grade}")
            print(f"   Preferred Units: {assessment.preferred_unit_count}")
            print(f"   Target Density: {(assessment.available_build_sqft / assessment.preferred_unit_count):,.0f} sq ft/unit")
            
            print(f"\n📄 Report:")
            print(f"   PDF: ~/Desktop/{pdf_filename}")
            
            print(f"\n🎉 Complete! Ready for review!\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
