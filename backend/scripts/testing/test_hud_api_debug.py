#!/usr/bin/env python3
"""
HUD API Debug Script
Tests different query formats to fix 404 errors
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUD_API_KEY = os.getenv("HUD_API_KEY")

print("\n" + "="*80)
print("HUD API DEBUG TEST SUITE")
print("="*80)
print(f"API Key: {HUD_API_KEY[:20]}..." if HUD_API_KEY else "❌ NO API KEY")
print("="*80)


async def test_income_limits_variations(zip_code="78701"):
    """Test different query formats for Income Limits API"""
    print(f"\n{'='*80}")
    print(f"TESTING INCOME LIMITS API - Multiple Query Formats")
    print(f"{'='*80}")
    
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    # Test 1: Just ZIP code
    print(f"\n🧪 Test 1: ZIP Code Only")
    print(f"   URL: https://www.huduser.gov/hudapi/public/il")
    print(f"   Params: zip={zip_code}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/il",
                params={"zip": zip_code},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Year: {data['data']['year']}")
                print(f"   Area: {data['data']['area_name']}")
                print(f"   Median Income: ${data['data']['median']:,}")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 2: ZIP code with year
    print(f"\n🧪 Test 2: ZIP Code + Year")
    print(f"   URL: https://www.huduser.gov/hudapi/public/il")
    print(f"   Params: zip={zip_code}, year=2024")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/il",
                params={"zip": zip_code, "year": 2024},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Year: {data['data']['year']}")
                print(f"   Area: {data['data']['area_name']}")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 3: County FIPS (Travis County = 48453)
    print(f"\n🧪 Test 3: County FIPS (entityid)")
    print(f"   URL: https://www.huduser.gov/hudapi/public/il")
    print(f"   Params: entityid=48453")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/il",
                params={"entityid": "48453"},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 4: Metro code (Austin MSA = 12420)
    print(f"\n🧪 Test 4: Metro Code")
    print(f"   URL: https://www.huduser.gov/hudapi/public/il")
    print(f"   Params: entityid=METRO12420M12420")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/il",
                params={"entityid": "METRO12420M12420"},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 5: State + County format
    print(f"\n🧪 Test 5: State + County")
    print(f"   URL: https://www.huduser.gov/hudapi/public/il")
    print(f"   Params: statecd=TX, countycd=453")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/il",
                params={"statecd": "TX", "countycd": "453"},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    return False


async def test_fmr_variations(zip_code="78701"):
    """Test different query formats for Fair Market Rent API"""
    print(f"\n{'='*80}")
    print(f"TESTING FAIR MARKET RENT API - Multiple Query Formats")
    print(f"{'='*80}")
    
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    # Test 1: ZIP in params
    print(f"\n🧪 Test 1: ZIP Code in Params")
    print(f"   URL: https://www.huduser.gov/hudapi/public/fmr/data")
    print(f"   Params: zip={zip_code}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/fmr/data",
                params={"zip": zip_code},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Year: {data['data']['basicdata']['year']}")
                print(f"   Area: {data['data']['basicdata']['area_name']}")
                print(f"   2BR Rent: ${data['data']['basicdata']['rent_2br']:,}")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 2: ZIP in URL path
    print(f"\n🧪 Test 2: ZIP Code in URL Path")
    print(f"   URL: https://www.huduser.gov/hudapi/public/fmr/data/{zip_code}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.huduser.gov/hudapi/public/fmr/data/{zip_code}",
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 3: ZIP + year in params
    print(f"\n🧪 Test 3: ZIP Code + Year in Params")
    print(f"   URL: https://www.huduser.gov/hudapi/public/fmr/data")
    print(f"   Params: zip={zip_code}, year=2024")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/fmr/data",
                params={"zip": zip_code, "year": 2024},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 4: Different endpoint - statedata
    print(f"\n🧪 Test 4: State Data Endpoint")
    print(f"   URL: https://www.huduser.gov/hudapi/public/fmr/statedata/TX")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/fmr/statedata/TX",
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   (Returns all TX data - would need to filter by ZIP)")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # Test 5: Metro code
    print(f"\n🧪 Test 5: Metro Code")
    print(f"   URL: https://www.huduser.gov/hudapi/public/fmr/data")
    print(f"   Params: entityid=METRO12420M12420")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/fmr/data",
                params={"entityid": "METRO12420M12420"},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                return True
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    return False


async def run_all_tests():
    """Run all HUD API debug tests"""
    if not HUD_API_KEY:
        print("❌ ERROR: HUD_API_KEY not found in environment variables")
        return
    
    # Test Income Limits
    il_success = await test_income_limits_variations()
    
    await asyncio.sleep(1)
    
    # Test Fair Market Rent
    fmr_success = await test_fmr_variations()
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Income Limits API: {'✅ WORKING' if il_success else '❌ ALL TESTS FAILED'}")
    print(f"Fair Market Rent API: {'✅ WORKING' if fmr_success else '❌ ALL TESTS FAILED'}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
