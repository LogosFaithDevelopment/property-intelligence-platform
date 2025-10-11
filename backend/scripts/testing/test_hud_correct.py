#!/usr/bin/env python3
"""
HUD API - Try Correct Endpoints
Based on HUD User API documentation
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
HUD_API_KEY = os.getenv("HUD_API_KEY")

async def test_correct_endpoints():
    """Test with correct HUD API endpoints"""
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    print("\n" + "="*80)
    print("Testing Correct HUD API Endpoints")
    print("="*80)
    
    # Income Limits - Try data/ prefix
    print("\n🧪 INCOME LIMITS - Testing /il/data/{zip}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/il/data/78701",
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Year: {data['data']['year']}")
                print(f"   Area: {data['data']['area_name']}")
                print(f"   Median: ${data['data']['median']:,}")
                print(f"\n   80% AMI Limits:")
                print(f"   1 Person: ${data['data']['income']['l80_1']:,}")
                print(f"   2 Person: ${data['data']['income']['l80_2']:,}")
                print(f"   3 Person: ${data['data']['income']['l80_3']:,}")
                print(f"   4 Person: ${data['data']['income']['l80_4']:,}")
            else:
                print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # FMR - Test with ZIP in path
    print("\n🧪 FAIR MARKET RENT - Testing /fmr/data/{zip}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/fmr/data/78701",
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Year: {data['data']['basicdata']['year']}")
                print(f"   Area: {data['data']['basicdata']['area_name']}")
                print(f"\n   Fair Market Rents:")
                print(f"   Studio:    ${data['data']['basicdata']['rent_0br']:,}")
                print(f"   1 Bedroom: ${data['data']['basicdata']['rent_1br']:,}")
                print(f"   2 Bedroom: ${data['data']['basicdata']['rent_2br']:,}")
                print(f"   3 Bedroom: ${data['data']['basicdata']['rent_3br']:,}")
                print(f"   4 Bedroom: ${data['data']['basicdata']['rent_4br']:,}")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    await asyncio.sleep(0.5)
    
    # FMR - Try with year in path
    print("\n🧪 FAIR MARKET RENT - Testing /fmr/data/{zip}?year=2024")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.huduser.gov/hudapi/public/fmr/data/78701",
                params={"year": 2024},
                headers=headers,
                timeout=15.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
            else:
                print(f"   ❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_correct_endpoints())
