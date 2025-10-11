#!/usr/bin/env python3
"""
HUD API Integration Test Script
Tests the HUD API endpoints directly
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUD_API_KEY = os.getenv("HUD_API_KEY")

async def test_usps_crosswalk(zip_code="78701"):
    """Test HUD USPS Crosswalk API"""
    print(f"\n{'='*60}")
    print(f"TEST 1: USPS ZIP-to-Tract Crosswalk")
    print(f"{'='*60}")
    print(f"ZIP Code: {zip_code}")
    
    url = "https://www.huduser.gov/hudapi/public/usps"
    params = {"type": 1, "query": zip_code}
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Year: {data['data']['year']}")
            print(f"Quarter: {data['data']['quarter']}")
            print(f"Results: {len(data['data']['results'])} tracts found")
            
            # Show top 3 tracts by residential ratio
            results = sorted(data['data']['results'], key=lambda x: x['res_ratio'], reverse=True)[:3]
            print(f"\nTop 3 Tracts (by residential address ratio):")
            for r in results:
                print(f"  - GEOID: {r['geoid']} | Res Ratio: {r['res_ratio']:.2%}")
        else:
            print(f"❌ Error: {response.text}")

async def test_income_limits(zip_code="78701"):
    """Test HUD Income Limits API"""
    print(f"\n{'='*60}")
    print(f"TEST 2: Income Limits API")
    print(f"{'='*60}")
    print(f"ZIP Code: {zip_code}")
    
    url = "https://www.huduser.gov/hudapi/public/il"
    params = {"zip": zip_code}
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Year: {data['data']['year']}")
            print(f"Area: {data['data']['area_name']}")
            print(f"Median Income: ${data['data']['median']:,}")
            
            print(f"\n80% AMI Limits (Logos Target):")
            print(f"  1 Person: ${data['data']['income']['l80_1']:,}")
            print(f"  2 Person: ${data['data']['income']['l80_2']:,}")
            print(f"  3 Person: ${data['data']['income']['l80_3']:,}")
            print(f"  4 Person: ${data['data']['income']['l80_4']:,}")
            
            print(f"\n60% AMI Limits:")
            print(f"  2 Person: ${data['data']['income']['l60_2']:,}")
            print(f"  4 Person: ${data['data']['income']['l60_4']:,}")
        else:
            print(f"❌ Error: {response.text}")

async def test_fair_market_rent(zip_code="78701"):
    """Test HUD Fair Market Rent API"""
    print(f"\n{'='*60}")
    print(f"TEST 3: Fair Market Rent API")
    print(f"{'='*60}")
    print(f"ZIP Code: {zip_code}")
    
    url = "https://www.huduser.gov/hudapi/public/fmr/data"
    params = {"zip": zip_code}
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Year: {data['data']['basicdata']['year']}")
            print(f"Area: {data['data']['basicdata']['area_name']}")
            print(f"County: {data['data']['basicdata']['county_name']}")
            
            print(f"\nFair Market Rents (Section 8 Payment Standards):")
            print(f"  Studio:    ${data['data']['basicdata']['rent_0br']:,}/month")
            print(f"  1 Bedroom: ${data['data']['basicdata']['rent_1br']:,}/month")
            print(f"  2 Bedroom: ${data['data']['basicdata']['rent_2br']:,}/month ⭐ Logos Focus")
            print(f"  3 Bedroom: ${data['data']['basicdata']['rent_3br']:,}/month")
            print(f"  4 Bedroom: ${data['data']['basicdata']['rent_4br']:,}/month")
            
            # Calculate annual rent for 2BR
            fmr_2br = data['data']['basicdata']['rent_2br']
            annual_rent = fmr_2br * 12
            estimated_cost = annual_rent * 15  # Rough heuristic
            
            print(f"\nLogos Analysis (2BR Unit):")
            print(f"  Annual Rent: ${annual_rent:,}")
            print(f"  Estimated Supportable Cost: ${estimated_cost:,}")
            print(f"  Logos Target Cost: $325,000")
            print(f"  Meets Threshold: {'✅ YES' if estimated_cost >= 250000 else '❌ NO'}")
        else:
            print(f"❌ Error: {response.text}")

async def run_all_tests():
    """Run all HUD API tests"""
    print("\n" + "="*60)
    print("HUD API INTEGRATION TEST SUITE")
    print("="*60)
    
    if not HUD_API_KEY:
        print("❌ ERROR: HUD_API_KEY not found in environment variables")
        return
    
    print(f"✅ HUD API Key Found: {HUD_API_KEY[:20]}...")
    
    # Test different ZIP codes
    test_zips = [
        "78701",  # Austin, TX (high market)
        "90012",  # Los Angeles, CA (very high market)
        "85001",  # Phoenix, AZ (moderate market)
    ]
    
    for zip_code in test_zips:
        print(f"\n\n{'#'*60}")
        print(f"Testing ZIP: {zip_code}")
        print(f"{'#'*60}")
        
        await test_usps_crosswalk(zip_code)
        await asyncio.sleep(0.5)  # Be respectful to API
        
        await test_income_limits(zip_code)
        await asyncio.sleep(0.5)
        
        await test_fair_market_rent(zip_code)
        await asyncio.sleep(0.5)
    
    print(f"\n\n{'='*60}")
    print("✅ ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
