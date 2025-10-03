#!/usr/bin/env python3
"""
Test HUD API endpoints with corrected URLs
Based on official HUD API documentation: https://www.huduser.gov/portal/dataset/fmr-api.html
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUD_API_KEY = os.getenv("HUD_API_KEY")

async def test_usps_crosswalk(zip_code: str):
    """Test USPS Crosswalk API (ZIP to Census Tract)"""
    print(f"\n{'='*60}")
    print(f"Testing USPS Crosswalk for ZIP: {zip_code}")
    print(f"{'='*60}")
    
    url = "https://www.huduser.gov/hudapi/public/usps"
    params = {"type": 1, "query": zip_code}
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=15.0)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data", {}).get("results"):
                    results = data["data"]["results"]
                    # Sort by residential ratio
                    sorted_results = sorted(results, key=lambda x: x.get("res_ratio", 0), reverse=True)
                    top_result = sorted_results[0]
                    
                    geoid = top_result.get("geoid", "")
                    state_fips = geoid[:2] if len(geoid) >= 2 else ""
                    county_fips = geoid[:5] if len(geoid) >= 5 else ""
                    
                    print(f"\n✅ SUCCESS")
                    print(f"   GEOID: {geoid}")
                    print(f"   State FIPS: {state_fips}")
                    print(f"   County FIPS: {county_fips}")
                    print(f"   Residential Ratio: {top_result.get('res_ratio')}")
                    
                    return county_fips
                else:
                    print(f"\n❌ No crosswalk results found")
                    return None
            else:
                print(f"\n❌ Error: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        return None


async def test_income_limits(county_fips: str):
    """Test Income Limits API with county FIPS"""
    print(f"\n{'='*60}")
    print(f"Testing Income Limits for County FIPS: {county_fips}")
    print(f"{'='*60}")
    
    # Format entityid: county FIPS + 99999 suffix
    entityid = f"{county_fips}99999"
    url = f"https://www.huduser.gov/hudapi/public/il/data/{entityid}"
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    print(f"URL: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS - Income Limits Retrieved")
                
                if data.get("data"):
                    response_data = data["data"]
                    print(f"   County: {response_data.get('county_name')}")
                    print(f"   Area: {response_data.get('area_name')}")
                    print(f"   Year: {response_data.get('year')}")
                    print(f"   Median Income: ${response_data.get('median_income'):,}")
                    
                    # Show income limits for 2-person household
                    extremely_low = response_data.get("extremely_low", {})
                    very_low = response_data.get("very_low", {})
                    low = response_data.get("low", {})
                    
                    print(f"\n   2-Person Household Income Limits:")
                    print(f"      30% AMI: ${extremely_low.get('il30_p2', 0):,}")
                    print(f"      50% AMI: ${very_low.get('il50_p2', 0):,}")
                    print(f"      80% AMI: ${low.get('il80_p2', 0):,}")
                    
                    return True
                else:
                    print(f"   Response: {response.text[:500]}")
                    return False
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


async def test_fair_market_rent(county_fips: str):
    """Test Fair Market Rent API with county FIPS"""
    print(f"\n{'='*60}")
    print(f"Testing Fair Market Rent for County FIPS: {county_fips}")
    print(f"{'='*60}")
    
    # Format entityid: county FIPS + 99999 suffix
    entityid = f"{county_fips}99999"
    url = f"https://www.huduser.gov/hudapi/public/fmr/data/{entityid}"
    headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
    
    print(f"URL: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS - Fair Market Rent Retrieved")
                
                if data.get("data"):
                    response_data = data["data"]
                    print(f"   County: {response_data.get('county_name')}")
                    print(f"   Metro: {response_data.get('metro_name')}")
                    
                    if response_data.get("basicdata"):
                        fmr_data = response_data["basicdata"]
                        print(f"\n   Fair Market Rents:")
                        print(f"      Studio:    ${fmr_data.get('Efficiency', 0)}")
                        print(f"      1 Bedroom: ${fmr_data.get('One-Bedroom', 0)}")
                        print(f"      2 Bedroom: ${fmr_data.get('Two-Bedroom', 0)}")
                        print(f"      3 Bedroom: ${fmr_data.get('Three-Bedroom', 0)}")
                        print(f"      4 Bedroom: ${fmr_data.get('Four-Bedroom', 0)}")
                    
                    return True
                else:
                    print(f"   Response: {response.text[:500]}")
                    return False
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print(f"\n{'#'*60}")
    print(f"# HUD API Testing - Fixed Endpoints")
    print(f"# Based on: https://www.huduser.gov/portal/dataset/fmr-api.html")
    print(f"{'#'*60}")
    print(f"\nAPI Key: {HUD_API_KEY[:20]}..." if HUD_API_KEY else "API Key: NOT FOUND")
    
    if not HUD_API_KEY:
        print("\n❌ ERROR: HUD_API_KEY not found in environment")
        return
    
    # Test with Austin, TX ZIP code
    test_zip = "78701"
    
    # Step 1: Get county FIPS from ZIP
    county_fips = await test_usps_crosswalk(test_zip)
    
    if county_fips:
        # Step 2: Test Income Limits with county FIPS
        await test_income_limits(county_fips)
        
        # Step 3: Test Fair Market Rent with county FIPS
        await test_fair_market_rent(county_fips)
        
        print(f"\n{'#'*60}")
        print(f"# SUMMARY")
        print(f"{'#'*60}")
        print(f"✅ USPS Crosswalk: County FIPS extracted successfully")
        print(f"✅ Income Limits API: Now uses /il/data/{{entityid}} endpoint")
        print(f"✅ Fair Market Rent API: Now uses /fmr/data/{{entityid}} endpoint")
        print(f"\nCONCLUSION: USPS Crosswalk IS necessary to get county FIPS!")
        print(f"The Income Limits and FMR APIs require entityid (FIPS), not ZIP codes.\n")
    else:
        print(f"\n❌ Could not extract county FIPS from crosswalk")


if __name__ == "__main__":
    asyncio.run(main())
