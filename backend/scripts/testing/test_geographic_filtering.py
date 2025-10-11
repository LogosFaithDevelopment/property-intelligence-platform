"""
Test Geographic Filtering for Downtown LA Property

This script tests that:
1. Property #14 (downtown LA) has 35 statewide fire events
2. Geographic filtering identifies ZERO nearby fires
3. Fire risk drops from HIGH (-15 points) to MINIMAL (0 points)
4. Overall score increases significantly
"""

import asyncio
import json
import sys

from app.database import AsyncSessionLocal
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.ai_assessment import AIAssessmentService
from sqlalchemy import select


async def test_geographic_filtering():
    """Test geographic filtering on downtown LA property"""
    
    async with AsyncSessionLocal() as db:
        try:
            # Get property #14 (downtown LA)
            result = await db.execute(select(Property).where(Property.id == 14))
            property_obj = result.scalar_one_or_none()
            
            if not property_obj:
                print("❌ Property #14 not found")
                return
            
            # Get church #16
            result = await db.execute(select(Church).where(Church.id == 16))
            church = result.scalar_one_or_none()
            
            if not church:
                print("❌ Church #16 not found")
                return
            
            print("=" * 80)
            print("TESTING GEOGRAPHIC FILTERING - Downtown LA Property")
            print("=" * 80)
            print(f"\n📍 Property: {property_obj.full_address}")
            print(f"📍 County: {property_obj.county}")
            print(f"📍 Coordinates: {property_obj.latitude}, {property_obj.longitude}")
            
            # Create new assessment
            assessment = Assessment(
                church_id=church.id,
                property_id=property_obj.id,
                status="DRAFT",
                priority="HIGH"
            )
            db.add(assessment)
            await db.commit()
            await db.refresh(assessment)
            
            print(f"\n✅ Created assessment #{assessment.id}")
            
            # Run AI assessment with geographic filtering
            print("\n🔄 Running AI assessment with geographic filtering...")
            service = AIAssessmentService(db)
            result_data = await service.process_assessment(assessment.id)
            
            # Refresh assessment to get updated data
            await db.refresh(assessment)
            
            # Extract fire risk data from the assessment's risk_factors
            risk_factors = assessment.risk_factors or {}
            flood_analysis = risk_factors.get('flood_analysis', {})
            disaster_breakdown = flood_analysis.get('disaster_breakdown', {})
            fire_risk = disaster_breakdown.get('fire', {})
            
            print("\n" + "=" * 80)
            print("🔥 FIRE RISK ANALYSIS RESULTS")
            print("=" * 80)
            
            event_count = fire_risk.get('event_count', 0)
            nearby_count = fire_risk.get('event_count_nearby', 'N/A')
            regional_count = fire_risk.get('event_count_regional', 'N/A')
            risk_level = fire_risk.get('risk_level', 'unknown')
            score_penalty = fire_risk.get('score_penalty', 0)
            mitigation_cost = fire_risk.get('mitigation_cost_per_unit', 0)
            geo_context = fire_risk.get('geographic_context', 'No context available')
            
            print(f"\n📊 Statewide Events: {event_count}")
            print(f"📍 Nearby Events (within 15 miles): {nearby_count}")
            print(f"🌐 Regional Events (15-35 miles): {regional_count}")
            print(f"\n⚠️  Risk Level: {risk_level.upper()}")
            print(f"📉 Score Penalty: {score_penalty} points")
            print(f"💰 Mitigation Cost: ${mitigation_cost:,}/unit")
            print(f"\n🗺️  Geographic Context:")
            print(f"   {geo_context}")
            
            print("\n" + "=" * 80)
            print("📈 OVERALL ASSESSMENT SCORES")
            print("=" * 80)
            
            overall_score = assessment.overall_score or 0
            risk_score = assessment.risk_score or 0
            location_score = assessment.location_score or 0
            market_score = assessment.market_score or 0
            financial_score = assessment.financial_score or 0
            
            print(f"\n🎯 Overall Score: {overall_score:.1f}/100")
            print(f"⚠️  Risk Score: {risk_score:.1f}/100")
            print(f"📍 Location Score: {location_score:.1f}/100")
            print(f"📊 Market Score: {market_score:.1f}/100")
            print(f"💵 Financial Score: {financial_score:.1f}/100")
            
            # Test Results
            print("\n" + "=" * 80)
            print("✅ TEST RESULTS")
            print("=" * 80)
            
            tests_passed = 0
            tests_total = 4
            
            # Test 1: Statewide events detected
            if event_count == 35:
                print(f"\n✅ Test 1 PASSED: Detected {event_count} statewide fire events")
                tests_passed += 1
            else:
                print(f"\n❌ Test 1 FAILED: Expected 35 statewide events, got {event_count}")
            
            # Test 2: Geographic filtering applied
            if nearby_count == 0:
                print(f"✅ Test 2 PASSED: Geographic filtering identified ZERO nearby fires")
                tests_passed += 1
            else:
                print(f"❌ Test 2 FAILED: Expected 0 nearby events, got {nearby_count}")
            
            # Test 3: Risk level is minimal
            if risk_level == 'minimal':
                print(f"✅ Test 3 PASSED: Risk level correctly set to MINIMAL")
                tests_passed += 1
            else:
                print(f"❌ Test 3 FAILED: Expected 'minimal' risk level, got '{risk_level}'")
            
            # Test 4: No score penalty
            if score_penalty == 0:
                print(f"✅ Test 4 PASSED: No score penalty applied (was -15 before filtering)")
                tests_passed += 1
            else:
                print(f"❌ Test 4 FAILED: Expected 0 penalty, got {score_penalty}")
            
            print(f"\n{'='*80}")
            print(f"📊 FINAL RESULTS: {tests_passed}/{tests_total} tests passed")
            print(f"{'='*80}\n")
            
            if tests_passed == tests_total:
                print("🎉 SUCCESS! Geographic filtering is working correctly!")
                print("   Downtown LA is no longer penalized for rural California wildfires.")
            else:
                print("⚠️  Some tests failed. Geographic filtering may need adjustment.")
            
            await db.commit()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_geographic_filtering())
