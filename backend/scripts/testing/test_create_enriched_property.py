#!/usr/bin/env python3
"""
Create Fully Enriched Test Property
Creates a complete property with all API enrichment data and generates assessment
"""

import asyncio
import json
import sys

# Add app to path
sys.path.insert(0, '/app')

from app.database import AsyncSessionLocal
from app.models.assessment import (Assessment, AssessmentPriority,
                                   AssessmentStatus)
from app.models.church import Church
from app.models.property import Property, PropertyType
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def create_enriched_property_and_assessment():
    """Create a fully enriched property and generate assessment"""
    
    print("\n" + "="*80)
    print("🚀 CREATING FULLY ENRICHED TEST PROPERTY")
    print("="*80 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Create test church
            print("📍 Step 1: Creating test church...")
            church = Church(
                name="Grace Community Church - Enrichment Test",
                legal_name="Grace Community Church of Los Angeles",
                denomination="Non-denominational",
                founded_year=1995,
                primary_email="contact@gracecommunityla.org",
                primary_phone="(323) 555-0100",
                street_address="500 Church Street",
                city="Los Angeles",
                state="CA",
                zip_code="90012",
                congregation_size=450,
                annual_budget=850000.0,
                staff_count=8,
                previous_development_experience=False,
                partnership_goals="Develop affordable housing to serve our community",
                timeline_preference="6-12 months",
                user_id="test_enrichment_user_001"
            )
            db.add(church)
            await db.flush()
            print(f"   ✅ Created church: {church.name} (ID: {church.id})")
            
            # Step 2: Create property with realistic details
            print("\n📍 Step 2: Creating property with complete details...")
            
            # Using a real Los Angeles property for enrichment testing
            # 1234 S Hope St, Los Angeles, CA 90015
            property_obj = Property(
                church_id=church.id,
                name="Hope Street Parcel",
                property_type=PropertyType.VACANT_LAND,
                street_address="1234 S Hope St",
                city="Los Angeles",
                state="CA",
                zip_code="90015",
                county="Los Angeles County",
                latitude=34.0407,  # Real coordinates for downtown LA
                longitude=-118.2662,
                lot_size_sqft=35000,  # ~0.8 acres
                lot_size_acres=0.803,
                zoning_description="R4-2 (High Density Residential)",
                assessed_value=450000.0,
                market_value_estimate=525000.0,
                annual_property_tax=5625.0,
                current_usage="Vacant land, previously church parking",
                usage_frequency="vacant",
                has_water=True,
                has_sewer=True,
                has_electricity=True,
                has_gas=True,
                internet_available=True,
                parking_spaces=0,
                user_id="test_enrichment_user_001"
            )
            db.add(property_obj)
            await db.flush()
            print(f"   ✅ Created property: {property_obj.name} (ID: {property_obj.id})")
            print(f"      Address: {property_obj.street_address}, {property_obj.city}, {property_obj.state}")
            print(f"      Coordinates: {property_obj.latitude}, {property_obj.longitude}")
            print(f"      Lot Size: {property_obj.lot_size_sqft:,} sqft ({property_obj.lot_size_acres} acres)")
            
            # Step 3: Run enrichment APIs
            print("\n📍 Step 3: Running enrichment APIs...")
            print("   This will call: Census, HUD, FEMA, Google Places")
            print("   ⏳ Please wait 10-15 seconds...\n")
            
            enrichment_service = PropertyEnrichmentService(db)
            enrichment_results = await enrichment_service.enrich_property(property_obj.id)
            
            print(f"\n   📊 Enrichment Results:")
            print(f"      Status: {enrichment_results.get('status')}")
            print(f"      APIs Called: {len(enrichment_results.get('api_results', []))}")
            
            # Display API results summary
            for api_result in enrichment_results.get('api_results', []):
                api_name = api_result.get('api_name')
                success = api_result.get('success')
                status_icon = "✅" if success else "❌"
                print(f"      {status_icon} {api_name}: {api_result.get('message', 'No message')}")
            
            # Refresh property to get updated enrichment data
            await db.refresh(property_obj)
            
            # Step 4: Create assessment
            print("\n📍 Step 4: Creating assessment...")
            assessment = Assessment(
                church_id=church.id,
                property_id=property_obj.id,
                user_id="test_enrichment_user_001",
                status=AssessmentStatus.DRAFT,
                priority=AssessmentPriority.HIGH,
                
                # Church preferences
                congregation_approval=True,  # Boolean: has congregation approved?
                leadership_support="strong",
                timeline_readiness="6_months",
                preferred_unit_count=45,  # Good size for this lot
                affordability_target="60_ami",  # 60% AMI
                revenue_sharing_preference="50_50_split",
                development_involvement_level="active",
                special_requirements="Community room for church programs, some units for seniors"
            )
            db.add(assessment)
            await db.flush()
            print(f"   ✅ Created assessment (ID: {assessment.id})")
            
            # Step 5: Run AI Assessment
            print("\n📍 Step 5: Running AI Assessment with enriched data...")
            print("   ⏳ Analyzing property with GPT-4... (30-60 seconds)\n")
            
            ai_service = AIAssessmentService(db)
            ai_results = await ai_service.process_assessment(assessment.id)
            
            # Refresh to get updated scores
            await db.refresh(assessment)
            
            print(f"\n   📊 AI Assessment Complete!")
            print(f"      Overall Score: {assessment.overall_score:.1f}/100")
            print(f"      Location Score: {assessment.location_score:.1f}/100")
            print(f"      Market Score: {assessment.market_score:.1f}/100")
            print(f"      Financial Score: {assessment.financial_score:.1f}/100")
            print(f"      Partnership Score: {assessment.partnership_score:.1f}/100")
            print(f"      Risk Score: {assessment.risk_score:.1f}/100")
            print(f"      Status: {assessment.status.value}")
            
            # Commit all changes
            await db.commit()
            
            # Step 6: Display enrichment data summary
            print("\n" + "="*80)
            print("📋 ENRICHMENT DATA SUMMARY")
            print("="*80 + "\n")
            
            # Check data_sources field which has the enrichment data
            if property_obj.data_sources:
                data_sources = property_obj.data_sources
                if isinstance(data_sources, dict):
                    # Demographics
                    if 'demographics' in data_sources and data_sources['demographics'].get('status') == 'success':
                        demo_data = data_sources['demographics'].get('data', {})
                        print("✅ Census Demographics:")
                        print(f"   Population: {demo_data.get('population', 'N/A')}")
                        print(f"   Median Income: ${demo_data.get('median_income', 'N/A'):,}" if demo_data.get('median_income') else "   Median Income: N/A")
                        print(f"   Median Age: {demo_data.get('median_age', 'N/A')}")
                    else:
                        print("❌ Census Demographics: Not available")
                    
                    # HUD data
                    if 'hud_income_limits' in data_sources and data_sources['hud_income_limits'].get('status') == 'success':
                        print("\n✅ HUD Income Limits: Available")
                    
                    if 'hud_fair_market_rent' in data_sources and data_sources['hud_fair_market_rent'].get('status') == 'success':
                        print("✅ HUD Fair Market Rent: Available")
                    
                    # FEMA data
                    if property_obj.flood_zone:
                        print(f"\n✅ FEMA Flood Zone: {property_obj.flood_zone}")
                    else:
                        print("\n❌ FEMA Flood Data: Not available")
            else:
                print("❌ No enrichment data available")
            
            # Final summary
            print("\n" + "="*80)
            print("✅ PROPERTY CREATION COMPLETE!")
            print("="*80)
            print(f"\n📌 Assessment ID: {assessment.id}")
            print(f"📌 Property ID: {property_obj.id}")
            print(f"📌 Church ID: {church.id}")
            print(f"\n🎯 Next Step: Generate PDF Report")
            print(f"   Run: docker exec property-intelligence-platform-backend-1 python test_pdf_generation.py")
            print(f"   Or use API: curl -o ~/Desktop/enriched_report.pdf http://localhost:8000/api/v1/reports/assessment/{assessment.id}/pdf")
            print("\n" + "="*80 + "\n")
            
            return assessment.id, property_obj.id, church.id
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise


if __name__ == "__main__":
    assessment_id, property_id, church_id = asyncio.run(create_enriched_property_and_assessment())
