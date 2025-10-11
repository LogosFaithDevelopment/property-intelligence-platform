#!/usr/bin/env python3
"""
Direct test of Census and FEMA APIs
Tests the actual API calls with the test property coordinates
"""

import asyncio

import httpx

# Test property coordinates (Austin, TX - from Phase 4 test)
TEST_LAT = 30.267153
TEST_LNG = -97.743061
TEST_ZIP = "78701"

async def test_census_api():
    """Test Census Geocoder and ACS APIs directly"""
    
    print("\n" + "="*80)
    print("🧪 CENSUS API DIRECT TEST")
    print("="*80)
    
    # Step 1: Get Census Tract from coordinates
    print(f"\n📍 Step 1: Getting Census Tract for coordinates {TEST_LAT}, {TEST_LNG}")
    
    try:
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": TEST_LNG,
            "y": TEST_LAT,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15.0)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result") and data["result"].get("geographies"):
                    tracts = data["result"]["geographies"].get("Census Tracts", [])
                    if tracts:
                        tract = tracts[0]
                        state_fips = tract["STATE"]
                        county_fips = tract["COUNTY"]
                        tract_code = tract["TRACT"]
                        
                        print(f"   ✅ Census Tract Found!")
                        print(f"      State FIPS: {state_fips}")
                        print(f"      County FIPS: {county_fips}")
                        print(f"      Tract: {tract_code}")
                        print(f"      Area: {tract.get('BASENAME', 'N/A')}")
                        
                        # Step 2: Fetch ACS demographic data
                        print(f"\n📊 Step 2: Fetching ACS Demographics Data")
                        
                        acs_url = "https://api.census.gov/data/2022/acs/acs5"
                        variables = [
                            "B01003_001E",  # Total population
                            "B19013_001E",  # Median household income
                            "B17001_002E",  # Below poverty level
                            "B25001_001E",  # Total housing units
                            "B25003_002E",  # Owner-occupied units
                            "B25003_003E",  # Renter-occupied units
                        ]
                        
                        acs_params = {
                            "get": ",".join(variables),
                            "for": f"tract:{tract_code}",
                            "in": f"state:{state_fips} county:{county_fips}"
                        }
                        
                        response2 = await client.get(acs_url, params=acs_params, timeout=15.0)
                        
                        print(f"   Status: {response2.status_code}")
                        
                        if response2.status_code == 200:
                            acs_data = response2.json()
                            
                            if len(acs_data) >= 2:
                                headers = acs_data[0]
                                values = acs_data[1]
                                result = dict(zip(headers, values))
                                
                                total_pop = int(result.get("B01003_001E", 0) or 0)
                                median_income = int(result.get("B19013_001E", -666666666) or -666666666)
                                poverty_pop = int(result.get("B17001_002E", 0) or 0)
                                owner_occ = int(result.get("B25003_002E", 0) or 0)
                                renter_occ = int(result.get("B25003_003E", 0) or 0)
                                
                                poverty_rate = round((poverty_pop / total_pop * 100), 2) if total_pop > 0 else 0
                                total_occ = owner_occ + renter_occ
                                renter_pct = round((renter_occ / total_occ * 100), 2) if total_occ > 0 else 0
                                
                                print(f"   ✅ Demographics Data Retrieved!")
                                print(f"      Population: {total_pop:,}")
                                print(f"      Median Income: ${median_income:,}" if median_income != -666666666 else "      Median Income: N/A")
                                print(f"      Poverty Rate: {poverty_rate}%")
                                print(f"      Renter Percentage: {renter_pct}%")
                                print(f"      Owner-Occupied: {owner_occ:,}")
                                print(f"      Renter-Occupied: {renter_occ:,}")
                            else:
                                print(f"   ❌ No ACS data returned")
                                print(f"      Response: {acs_data}")
                        else:
                            print(f"   ❌ ACS API Error: {response2.status_code}")
                            print(f"      Response: {response2.text[:200]}")
                    else:
                        print(f"   ❌ No census tracts found in response")
                else:
                    print(f"   ❌ No geographies in response")
                    print(f"      Response: {data}")
            else:
                print(f"   ❌ Geocoder Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_fema_api():
    """Test FEMA OpenFEMA v2 API directly"""
    
    print("\n" + "="*80)
    print("🧪 FEMA API DIRECT TEST")
    print("="*80)
    
    # Texas state code and Travis County (Austin)
    state_code = "48"  # Texas
    county_name = "Travis"
    
    print(f"\n🌊 Fetching Flood Disaster History for Travis County, TX")
    
    try:
        url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
        
        # Build filter
        filters = [
            f"state eq '{state_code}'",
            "(incidentType eq 'Flood' or incidentType eq 'Severe Storm(s)' or incidentType eq 'Hurricane')",
            "declarationDate ge '2004-01-01'"
        ]
        
        filter_string = " and ".join(filters)
        
        params = {
            "$filter": filter_string,
            "$select": "disasterNumber,declarationDate,incidentType,declarationTitle",
            "$orderby": "declarationDate desc",
            "$top": 10
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=15.0)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                disasters = data.get("DisasterDeclarationsSummaries", [])
                
                print(f"   ✅ Found {len(disasters)} flood-related disasters since 2004")
                
                if disasters:
                    print(f"\n   Recent Disasters:")
                    for i, disaster in enumerate(disasters[:5], 1):
                        print(f"      {i}. {disaster.get('declarationDate', 'N/A')}: {disaster.get('incidentType', 'N/A')}")
                        print(f"         {disaster.get('declarationTitle', 'N/A')[:60]}")
                
                flood_count = len([d for d in disasters if "Flood" in d.get("incidentType", "")])
                
                # Estimate risk
                if flood_count >= 5:
                    risk = "HIGH (5+ flood events)"
                    zone = "A"
                elif flood_count >= 2:
                    risk = "MODERATE (2-4 flood events)"
                    zone = "X (shaded)"
                elif flood_count >= 1:
                    risk = "LOW-MODERATE (1 flood event)"
                    zone = "X (unshaded)"
                else:
                    risk = "MINIMAL (no recorded floods)"
                    zone = "X"
                
                print(f"\n   📊 Flood Risk Assessment:")
                print(f"      Flood Events: {flood_count}")
                print(f"      Estimated Risk: {risk}")
                print(f"      Estimated Zone: {zone}")
                
            else:
                print(f"   ❌ FEMA API Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)


async def main():
    await test_census_api()
    await test_fema_api()
    
    print("\n" + "="*80)
    print("✅ DIAGNOSTIC COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
