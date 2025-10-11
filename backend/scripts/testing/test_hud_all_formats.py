#!/usr/bin/env python3
"""
HUD API - Try with County/State formats
Based on what we know works
"""

import asyncio
import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
HUD_API_KEY = os.getenv("HUD_API_KEY")

async def get_crosswalk_data(zip_code="78701"):
    """First get crosswalk data to extract county info"""
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.huduser.gov/hudapi/public/usps",
            params={"type": 1, "query": zip_code},
            headers=headers,
            timeout=15.0
        )
        if response.status_code == 200:
            data = response.json()
            if data['data']['results']:
                # Get first result's GEOID
                geoid = data['data']['results'][0]['geoid']
                state = geoid[:2]  # First 2 digits
                county = geoid[2:5]  # Next 3 digits
                return state, county, geoid
    return None, None, None

async def test_income_limits_formats():
    """Test Income Limits with different formats"""
    print("\n" + "="*80)
    print("INCOME LIMITS API - Testing All Formats")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    # Get county info from crosswalk
    state, county, geoid = await get_crosswalk_data()
    print(f"\nFrom Crosswalk: State={state} (TX), County={county}, Full GEOID={geoid}")
    
    # Test formats
    test_cases = [
        ("ZIP query param", "https://www.huduser.gov/hudapi/public/il", {"zip": "78701"}),
        ("State/County", "https://www.huduser.gov/hudapi/public/il", {"state": state, "county": county}),
        ("GEOID prefix", "https://www.huduser.gov/hudapi/public/il", {"entityid": f"{state}{county}"}),
        ("Full GEOID", "https://www.huduser.gov/hudapi/public/il", {"entityid": geoid}),
        ("COUNTY format", "https://www.huduser.gov/hudapi/public/il", {"entityid": f"COUNTY{state}{county}"}),
        ("State abbrev", "https://www.huduser.gov/hudapi/public/il", {"state": "TX", "county": county}),
    ]
    
    for name, url, params in test_cases:
        print(f"\n🧪 Testing: {name}")
        print(f"   Params: {params}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS!")
                    print(f"   Year: {data['data']['year']}")
                    print(f"   Area: {data['data']['area_name']}")
                    print(f"   Median: ${data['data']['median']:,}")
                    return True
                elif response.status_code == 400:
                    print(f"   ❌ 400: {response.json().get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        await asyncio.sleep(0.3)
    
    return False

async def test_fmr_formats():
    """Test Fair Market Rent with different formats"""
    print("\n" + "="*80)
    print("FAIR MARKET RENT API - Testing All Formats")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    # Get county info from crosswalk
    state, county, geoid = await get_crosswalk_data()
    
    test_cases = [
        ("ZIP query param", "https://www.huduser.gov/hudapi/public/fmr", {"zip": "78701"}),
        ("ZIP in subpath", "https://www.huduser.gov/hudapi/public/fmr/listzip/78701", {}),
        ("State/County", "https://www.huduser.gov/hudapi/public/fmr", {"state": state, "county": county}),
        ("StateData + filter", "https://www.huduser.gov/hudapi/public/fmr/statedata/TX", {}),
        ("Listcounties TX", "https://www.huduser.gov/hudapi/public/fmr/listcounties/TX", {}),
        ("County code", "https://www.huduser.gov/hudapi/public/fmr", {"entityid": f"{state}{county}"}),
    ]
    
    for name, url, params in test_cases:
        print(f"\n🧪 Testing: {name}")
        print(f"   URL: {url}")
        print(f"   Params: {params}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS!")
                    if 'data' in data and 'basicdata' in data['data']:
                        print(f"   Year: {data['data']['basicdata']['year']}")
                        print(f"   Area: {data['data']['basicdata']['area_name']}")
                        print(f"   2BR: ${data['data']['basicdata']['rent_2br']:,}")
                    else:
                        print(f"   (Returns list/collection data)")
                    return True
                elif response.status_code == 400:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"   ❌ 400: {error_data if isinstance(error_data, str) else error_data.get('error', 'Unknown')}")
                else:
                    print(f"   ❌ {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        await asyncio.sleep(0.3)
    
    return False

async def main():
    il_success = await test_income_limits_formats()
    await asyncio.sleep(1)
    fmr_success = await test_fmr_formats()
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Income Limits: {'✅ FOUND WORKING FORMAT' if il_success else '❌ NO WORKING FORMAT'}")
    print(f"Fair Market Rent: {'✅ FOUND WORKING FORMAT' if fmr_success else '❌ NO WORKING FORMAT'}")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
