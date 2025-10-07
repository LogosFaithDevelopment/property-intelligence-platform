#!/usr/bin/env python3
"""
Test Enrichment via API
Tests enrichment speed and data quality through the API endpoint
"""

import asyncio
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

# Get auth token (you'll need to replace this with a valid token)
# For testing, we'll skip auth and hit the endpoint directly in Docker

async def test_enrichment():
    """Test enrichment speed via API"""
    
    print("\n" + "="*80)
    print("🧪 ENRICHMENT SPEED & DATA QUALITY TEST")
    print("="*80)
    
    # We'll test property ID 9 (the one from Phase 4 test)
    property_id = 9
    base_url = "http://localhost:8000/api"
    
    print(f"\n📍 Testing with Property ID: {property_id}")
    
    # Get current property data
    async with httpx.AsyncClient() as client:
        try:
            # First, get current property status
            print(f"\n📊 Checking Current Data Status...")
            response = await client.get(f"{base_url}/properties/{property_id}")
            
            if response.status_code != 200:
                print(f"❌ Could not fetch property: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return
            
            property_data = response.json()
            print(f"   Property: {property_data['name']}")
            print(f"   Location: {property_data['city']}, {property_data['state']} {property_data['zip_code']}")
            
            # Check current enrichment status
            data_sources = property_data.get('data_sources', {})
            print(f"\n   Current Enrichment:")
            print(f"   Census: {'✅' if data_sources.get('census_demographics') else '❌'}")
            print(f"   FEMA: {'✅' if data_sources.get('fema_flood') else '❌'}")
            hud_data = data_sources.get('hud_data', {})
            print(f"   HUD Income Limits: {'✅' if hud_data.get('income_limits') else '❌'}")
            print(f"   HUD FMR: {'✅' if hud_data.get('fair_market_rent') else '❌'}")
            print(f"   HUD Crosswalk: {'✅' if data_sources.get('hud_usps_crosswalk') else '❌'}")
            
            # Now trigger enrichment
            print(f"\n⏱️  Starting Enrichment...")
            start_time = time.time()
            
            response = await client.post(
                f"{base_url}/properties/{property_id}/enrich",
                timeout=90.0  # Allow up to 90 seconds
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code != 200:
                print(f"\n❌ Enrichment Failed: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return
            
            result = response.json()
            
            print(f"\n✅ Enrichment Complete!")
            print(f"   ⚡ Time: {elapsed:.1f} seconds")
            
            # Get updated property data
            response = await client.get(f"{base_url}/properties/{property_id}")
            if response.status_code == 200:
                property_data = response.json()
                data_sources = property_data.get('data_sources', {})
                
                print(f"\n📊 Enrichment Results:")
                
                # Census
                census_data = data_sources.get('census_demographics', {})
                if census_data and census_data.get('status') == 'success':
                    census_result = census_data.get('data', {})
                    print(f"   ✅ Census Demographics:")
                    print(f"      - Poverty Rate: {census_result.get('poverty_rate', 'N/A')}")
                    print(f"      - Renter %: {census_result.get('renter_percentage', 'N/A')}")
                    if census_result.get('median_income'):
                        print(f"      - Median Income: ${census_result.get('median_income'):,}")
                else:
                    error = census_data.get('error', 'No data')
                    print(f"   ❌ Census Demographics: {error}")
                
                # FEMA
                fema_data = data_sources.get('fema_flood', {})
                if fema_data and fema_data.get('status') == 'success':
                    fema_result = fema_data.get('data', {})
                    print(f"   ✅ FEMA Flood Risk:")
                    print(f"      - Flood Zone: {fema_result.get('flood_zone', 'N/A')}")
                    print(f"      - Risk Level: {fema_result.get('risk_level', 'N/A')}")
                else:
                    error = fema_data.get('error', 'No data')
                    print(f"   ⚠️  FEMA Flood Risk: {error}")
                
                # HUD Income Limits
                hud_data = data_sources.get('hud_data', {})
                income_limits = hud_data.get('income_limits', {})
                if income_limits and income_limits.get('status') == 'success':
                    il_data = income_limits.get('data', {})
                    print(f"   ✅ HUD Income Limits:")
                    print(f"      - Year: {il_data.get('year', 'N/A')}")
                    print(f"      - Area: {il_data.get('area_name', 'N/A')}")
                    if il_data.get('median'):
                        print(f"      - Median: ${il_data.get('median'):,}")
                    ami_data = il_data.get('income', {})
                    if ami_data and ami_data.get('l80_2'):
                        print(f"      - 80% AMI (2-person): ${ami_data.get('l80_2'):,}")
                else:
                    error = income_limits.get('error', 'No data')
                    print(f"   ❌ HUD Income Limits: {error}")
                
                # HUD Fair Market Rent
                fmr = hud_data.get('fair_market_rent', {})
                if fmr and fmr.get('status') == 'success':
                    fmr_data = fmr.get('data', {})
                    print(f"   ✅ HUD Fair Market Rent:")
                    print(f"      - Year: {fmr_data.get('year', 'N/A')}")
                    rent_by_bedroom = fmr_data.get('rent_by_bedroom', {})
                    if rent_by_bedroom.get('2_bedroom'):
                        print(f"      - 2BR FMR: ${rent_by_bedroom.get('2_bedroom'):,}")
                else:
                    error = fmr.get('error', 'No data')
                    print(f"   ❌ HUD Fair Market Rent: {error}")
                
                # HUD USPS Crosswalk
                crosswalk = data_sources.get('hud_usps_crosswalk', {})
                if crosswalk and crosswalk.get('status') == 'success':
                    print(f"   ✅ HUD USPS Crosswalk")
                else:
                    error = crosswalk.get('error', 'No data')
                    print(f"   ⚠️  HUD USPS Crosswalk: {error}")
                
                # Speed assessment
                print(f"\n🚀 Performance:")
                if elapsed < 15:
                    print(f"   ✅ EXCELLENT - {elapsed:.1f}s (Parallel API calls working!)")
                elif elapsed < 30:
                    print(f"   ✅ GOOD - {elapsed:.1f}s")
                elif elapsed < 60:
                    print(f"   ⚠️  SLOW - {elapsed:.1f}s (Should be <30s)")
                else:
                    print(f"   ❌ TOO SLOW - {elapsed:.1f}s (Sequential calls detected?)")
                
                print("\n" + "="*80)
            
        except httpx.TimeoutException:
            elapsed = time.time() - start_time
            print(f"\n❌ Request Timed Out after {elapsed:.1f}s")
            print(f"   APIs are taking too long to respond")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n❌ Test Failed after {elapsed:.1f}s")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enrichment())
