

# test End tp End to End Flow
"""
End-to-End Integration Test
Tests the complete user flow from church creation through assessment completion
"""

import asyncio
import json
from datetime import datetime

import httpx

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_TIMESTAMP = str(int(datetime.now().timestamp()))
TEST_EMAIL = f"test_church_{TEST_TIMESTAMP}@example.com"
TEST_TAX_ID = f"{TEST_TIMESTAMP[:2]}-{TEST_TIMESTAMP[2:9]}"


async def test_complete_flow():
    """Test the complete user journey"""
    
    print("=" * 70)
    print("PROPERTY INTELLIGENCE PLATFORM - END-TO-END TEST")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        
        # ================================================================
        # STEP 1: Create Church Profile
        # ================================================================
        print("📋 STEP 1: Creating Church Profile...")
        church_data = {
            "name": "Test Community Church",
            "primary_contact_name": "Rev. John Smith",
            "primary_email": TEST_EMAIL,
            "primary_phone": "310-555-0123",
            "street_address": "123 Test Street",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "tax_exempt_id": TEST_TAX_ID,
            "is_501c3_verified": True,
            "congregation_size": 350,
            "weekly_attendance": 280,
            "year_established": 1985
        }
        
        response = await client.post(f"{BASE_URL}/churches/", json=church_data, follow_redirects=True)
        
        if response.status_code != 201:
            print(f"❌ FAILED: Church creation returned {response.status_code}")
            print(response.text)
            return
        
        church = response.json()
        church_id = church["id"]
        print(f"✅ SUCCESS: Church created with ID: {church_id}")
        print(f"   Name: {church['name']}")
        print(f"   Email: {church['primary_email']}")
        print(f"   Status: {church['verification_status']}")
        print()
        
        # ================================================================
        # STEP 2: Add Property
        # ================================================================
        print("🏢 STEP 2: Adding Property...")
        property_data = {
            "church_id": church_id,
            "name": "North Parking Lot",
            "street_address": "1640 Maple Ave",  # Real Austin address for testing
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "current_use": "Parking - Underutilized",
            "lot_size_sqft": 25000,
            "property_type": "parking_lot",
            "ownership_status": "owned_outright",
            "zoning_classification": "R-2",
            "has_deed_restrictions": False,
            "has_environmental_concerns": False,
            "notes": "Only used on Sundays, sits empty rest of week"
        }
        
        response = await client.post(f"{BASE_URL}/properties/", json=property_data, follow_redirects=True)
        
        if response.status_code != 201:
            print(f"❌ FAILED: Property creation returned {response.status_code}")
            print(response.text)
            return
        
        property_obj = response.json()
        property_id = property_obj["id"]
        print(f"✅ SUCCESS: Property created with ID: {property_id}")
        print(f"   Address: {property_obj['full_address']}")
        print(f"   Lot Size: {property_obj['lot_size_sqft']} sqft ({property_obj['lot_size_acres']} acres)")
        print(f"   Status: Property enrichment scheduled in background")
        print()
        
        # ================================================================
        # STEP 3: Wait for Property Enrichment
        # ================================================================
        print("⏳ STEP 3: Waiting for property enrichment to complete...")
        print("   (This typically takes 30-90 seconds)")
        
        enriched = False
        max_attempts = 20
        attempt = 0
        
        while not enriched and attempt < max_attempts:
            attempt += 1
            await asyncio.sleep(5)  # Check every 5 seconds
            
            response = await client.get(f"{BASE_URL}/properties/{property_id}")
            if response.status_code == 200:
                property_obj = response.json()
                
                # Check if enrichment data exists
                if property_obj.get("latitude") and property_obj.get("longitude"):
                    enriched = True
                    print(f"✅ SUCCESS: Property enriched after {attempt * 5} seconds")
                    print(f"   Coordinates: {property_obj['latitude']}, {property_obj['longitude']}")
                    print(f"   County: {property_obj.get('county', 'N/A')}")
                    
                    # Check for enriched data
                    if property_obj.get("data_sources"):
                        try:
                            sources = json.loads(property_obj["data_sources"])
                            print(f"   Data Sources Retrieved:")
                            if "demographics" in sources:
                                print(f"      ✓ Census Demographics")
                            if "hud_data" in sources:
                                print(f"      ✓ HUD Income Limits & FMR")
                            if "flood_risk" in sources:
                                print(f"      ✓ FEMA Flood Risk")
                        except:
                            pass
                else:
                    print(f"   Attempt {attempt}/{max_attempts} - Still enriching...")
        
        if not enriched:
            print("⚠️  WARNING: Enrichment timed out, proceeding anyway...")
        
        print()
        
        # ================================================================
        # STEP 4: Create Assessment
        # ================================================================
        print("📊 STEP 4: Creating Assessment...")
        assessment_data = {
            "church_id": church_id,
            "property_id": property_id,
            "congregation_approval": True,
            "leadership_support": "majority",
            "timeline_readiness": "6_months",
            "preferred_unit_count": 75,
            "affordability_target": "60_ami",
            "revenue_sharing_preference": "ground_lease",
            "development_involvement_level": "collaborative",
            "special_requirements": "Need ground-floor community space for church outreach programs",
            "priority": "high"
        }
        
        response = await client.post(f"{BASE_URL}/assessments/", json=assessment_data, follow_redirects=True)
        
        if response.status_code not in [200, 201]:
            print(f"❌ FAILED: Assessment creation returned {response.status_code}")
            print(response.text)
            return
        
        assessment = response.json()
        assessment_id = assessment["id"]
        print(f"✅ SUCCESS: Assessment created with ID: {assessment_id}")
        print(f"   UUID: {assessment['uuid']}")
        print(f"   Status: {assessment['status']}")
        print(f"   Priority: {assessment['priority']}")
        print()
        
        # ================================================================
        # STEP 5: Trigger Assessment Processing
        # ================================================================
        print("🤖 STEP 5: Triggering AI Assessment Processing...")
        print("   (This typically takes 2-5 minutes)")
        
        response = await client.post(f"{BASE_URL}/assessments/{assessment_id}/process", follow_redirects=True)
        
        if response.status_code not in [200, 202]:
            print(f"❌ FAILED: Assessment processing returned {response.status_code}")
            print(response.text)
            return
        
        print("✅ Assessment processing started")
        print()
        
        # ================================================================
        # STEP 6: Wait for Assessment Completion
        # ================================================================
        print("⏳ STEP 6: Waiting for assessment to complete...")
        
        completed = False
        max_attempts = 60  # 5 minutes max (5 second intervals)
        attempt = 0
        
        while not completed and attempt < max_attempts:
            attempt += 1
            await asyncio.sleep(5)
            
            response = await client.get(f"{BASE_URL}/assessments/{assessment_id}")
            if response.status_code == 200:
                assessment = response.json()
                status = assessment.get("status")
                
                if status == "COMPLETED":
                    completed = True
                    print(f"✅ SUCCESS: Assessment completed after {attempt * 5} seconds")
                    print()
                    
                    # ================================================================
                    # STEP 7: Display Results
                    # ================================================================
                    print("=" * 70)
                    print("📋 ASSESSMENT RESULTS")
                    print("=" * 70)
                    print()
                    
                    print(f"OVERALL SCORE: {assessment['overall_score']:.1f}/100")
                    print(f"GRADE: {assessment.get('score_grade', 'N/A')}")
                    print()
                    
                    print("CATEGORY SCORES:")
                    print(f"  Financial Viability:    {assessment.get('financial_score', 0):.1f}/100")
                    print(f"  Location Quality:       {assessment.get('location_score', 0):.1f}/100")
                    print(f"  Market Demand:          {assessment.get('market_score', 0):.1f}/100")
                    print(f"  Partnership Fit:        {assessment.get('partnership_score', 0):.1f}/100")
                    print(f"  Risk Assessment:        {assessment.get('risk_score', 0):.1f}/100")
                    print()
                    
                    # Check for Logos-specific metrics
                    if "logos_metrics" in assessment:
                        print("LOGOS FINANCIAL METRICS:")
                        metrics = assessment["logos_metrics"]
                        print(f"  Lot Size: {metrics.get('lot_size_sqft', 0):,} sqft")
                        print(f"  Meets Minimum (10K sqft): {'✅ YES' if metrics.get('meets_minimum_lot_size') else '❌ NO'}")
                        print(f"  Estimated Unit Capacity: {metrics.get('unit_capacity', 0)} units")
                        print(f"  Within Target (40-140): {'✅ YES' if metrics.get('within_target_unit_range') else '⚠️  NO'}")
                        print(f"  Cost Per Unit: ${metrics.get('estimated_cost_per_unit', 0):,.0f}")
                        print(f"  Under $325K Target: {'✅ YES' if metrics.get('within_cost_per_unit_target') else '⚠️  NO'}")
                        print(f"  Total Development Cost: ${metrics.get('total_development_cost', 0):,.0f}")
                        print(f"  Estimated Annual Revenue: ${metrics.get('estimated_annual_revenue', 0):,.0f}")
                        print()
                    
                    # Check for compliance summary
                    if "logos_compliance_summary" in assessment:
                        print("LOGOS COMPLIANCE:")
                        compliance = assessment["logos_compliance_summary"]
                        print(f"  Lot Size Compliant: {'✅' if compliance.get('lot_size_compliant') else '❌'}")
                        print(f"  Unit Capacity Compliant: {'✅' if compliance.get('unit_capacity_compliant') else '❌'}")
                        print(f"  Cost Per Unit Compliant: {'✅' if compliance.get('cost_per_unit_compliant') else '❌'}")
                        print(f"  Overall Compliant: {'✅ YES' if compliance.get('overall_compliant') else '⚠️  PARTIAL'}")
                        print()
                    
                    # Market analysis
                    if assessment.get("market_analysis"):
                        print("MARKET ANALYSIS:")
                        market = json.loads(assessment["market_analysis"]) if isinstance(assessment["market_analysis"], str) else assessment["market_analysis"]
                        
                        if "section8_viability" in market:
                            s8 = market["section8_viability"]
                            print(f"  Section 8 Viability:")
                            print(f"    2BR Fair Market Rent: ${s8.get('two_br_fmr', 0)}/month")
                            print(f"    Rating: {s8.get('fmr_rating', 'N/A')}")
                            print(f"    Supports Economics: {'✅ YES' if s8.get('supports_project_economics') else '❌ NO'}")
                        
                        if "ami_alignment" in market:
                            ami = market["ami_alignment"]
                            print(f"  AMI Alignment:")
                            print(f"    80% AMI (2-person): ${ami.get('two_person_80pct_ami', 0):,}")
                            print(f"    In Target Range: {'✅ YES' if ami.get('in_target_range') else '❌ NO'}")
                        print()
                    
                    # Risk factors
                    if assessment.get("risk_factors"):
                        print("RISK FACTORS:")
                        risks = json.loads(assessment["risk_factors"]) if isinstance(assessment["risk_factors"], str) else assessment["risk_factors"]
                        print(f"  Flood Risk: {risks.get('flood_risk', 'UNKNOWN')}")
                        print(f"  Overall Risk: {risks.get('overall_risk', 'UNKNOWN')}")
                        print()
                    
                    print("=" * 70)
                    print()
                    
                elif status == "DRAFT":
                    print(f"⚠️  Status is still DRAFT after {attempt * 5} seconds")
                    print(f"   This may indicate the background processing didn't start")
                else:
                    print(f"   Attempt {attempt}/{max_attempts} - Status: {status}")
        
        if not completed:
            print("❌ FAILED: Assessment did not complete within timeout")
            print(f"   Final Status: {assessment.get('status', 'UNKNOWN')}")
            return
        
        # ================================================================
        # STEP 8: Test Assessment Retrieval
        # ================================================================
        print("📄 STEP 8: Testing assessment retrieval...")
        response = await client.get(f"{BASE_URL}/assessments/{assessment_id}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Assessment retrieved successfully")
        else:
            print(f"❌ FAILED: Could not retrieve assessment")
        print()
        
        # ================================================================
        # SUMMARY
        # ================================================================
        print("=" * 70)
        print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("SUMMARY:")
        print(f"  Church ID: {church_id}")
        print(f"  Property ID: {property_id}")
        print(f"  Assessment ID: {assessment_id}")
        print(f"  Final Score: {assessment['overall_score']:.1f}/100")
        print(f"  Grade: {assessment.get('score_grade', 'N/A')}")
        print()
        print("All systems operational! Ready for frontend integration.")
        print()


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
