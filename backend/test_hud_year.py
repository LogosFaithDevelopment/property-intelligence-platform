#!/usr/bin/env python3
"""
HUD API - Correct Format with Year
HUD APIs require year in the URL path
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
HUD_API_KEY = os.getenv("HUD_API_KEY")

async def test_with_year():
    """Test HUD APIs with year in URL path"""
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    print("\n" + "="*80)
    print("Testing HUD APIs with Year in URL Path")
    print("="*80)
    
    # Income Limits - /il/data/2024/78701
    print("\n🧪 INCOME LIMITS - /il/data/{year}/{zip}")
    for year in [2024, 2023, 2025]:
        print(f"\n   Trying year {year}...")
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://www.huduser.gov/hudapi/public/il/data/{year}/78701"
                response = await client.get(url, headers=headers, timeout=15.0)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS with year {year}!")
                    print(f"   Year: {data['data']['year']}")
                    print(f"   Area: {data['data']['area_name']}")
                    print(f"   Median: ${data['data']['median']:,}")
                    print(f"\n   80% AMI Limits:")
                    print(f"   1 Person: ${data['data']['income']['l80_1']:,}")
                    print(f"   2 Person: ${data['data']['income']['l80_2']:,}")
                    print(f"   3 Person: ${data['data']['income']['l80_3']:,}")
                    print(f"   4 Person: ${data['data']['income']['l80_4']:,}")
                    break
                elif response.status_code != 404:
                    print(f"   Error: {response.text[:200]}")
        except Exception as e:
            print(f"   Exception: {str(e)}")
        await asyncio.sleep(0.3)
    
    # FMR - /fmr/data/2024/78701
    print("\n🧪 FAIR MARKET RENT - /fmr/data/{year}/{zip}")
    for year in [2024, 2023, 2025]:
        print(f"\n   Trying year {year}...")
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://www.huduser.gov/hudapi/public/fmr/data/{year}/78701"
                response = await client.get(url, headers=headers, timeout=15.0)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS with year {year}!")
                    print(f"   Year: {data['data']['basicdata']['year']}")
                    print(f"   Area: {data['data']['basicdata']['area_name']}")
                    print(f"\n   Fair Market Rents:")
                    print(f"   Studio:    ${data['data']['basicdata']['rent_0br']:,}")
                    print(f"   1 Bedroom: ${data['data']['basicdata']['rent_1br']:,}")
                    print(f"   2 Bedroom: ${data['data']['basicdata']['rent_2br']:,}")
                    print(f"   3 Bedroom: ${data['data']['basicdata']['rent_3br']:,}")
                    print(f"   4 Bedroom: ${data['data']['basicdata']['rent_4br']:,}")
                    break
                elif response.status_code != 404:
                    print(f"   Error: {response.text[:200]}")
        except Exception as e:
            print(f"   Exception: {str(e)}")
        await asyncio.sleep(0.3)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_with_year())
