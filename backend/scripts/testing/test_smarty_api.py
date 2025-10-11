"""
Test Smarty API for lot size data
Testing: 709 Manchester Ave, Los Angeles, CA 90044 (Church Property)

This script tests Smarty's US Street Address API to verify:
1. Address validation works for church properties
2. Lot size data is available (sqft and acres)
3. Property metadata includes zoning, land use, etc.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import httpx
from app.config import get_settings


async def test_smarty_street_api():
    """Test Smarty US Street Address API with church property"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY API TEST - Church Property Lot Size")
    print("="*80)
    
    # Test address
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    print(f"Auth ID: {settings.smarty_auth_id[:20]}...")
    print(f"Auth Token: {settings.smarty_auth_token[:10]}...")
    
    # Smarty US Street Address API endpoint
    url = "https://us-street.api.smarty.com/street-address"
    
    # Try with and without license parameter
    params = {
        "auth-id": settings.smarty_auth_id,
        "auth-token": settings.smarty_auth_token,
        "street": street,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "match": "invalid",  # Return best match even if not exact
        "license": "us-core-cloud"  # Try specifying the license explicitly
    }
    
    print("\n" + "-"*80)
    print("Calling Smarty API...")
    print("-"*80)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if not data or len(data) == 0:
                    print("\n❌ No results returned from Smarty API")
                    print("This could mean:")
                    print("  - Address not found in Smarty database")
                    print("  - Address format needs adjustment")
                    return
                
                print(f"\n✅ SUCCESS - Found {len(data)} result(s)")
                
                for idx, result in enumerate(data, 1):
                    print("\n" + "="*80)
                    print(f"RESULT #{idx}")
                    print("="*80)
                    
                    # Delivery line (formatted address)
                    delivery_line = result.get('delivery_line_1', 'N/A')
                    print(f"\n📍 Validated Address: {delivery_line}")
                    print(f"   City: {result.get('components', {}).get('city_name', 'N/A')}")
                    print(f"   State: {result.get('components', {}).get('state_abbreviation', 'N/A')}")
                    print(f"   ZIP: {result.get('components', {}).get('zipcode', 'N/A')}")
                    
                    # Metadata (includes property data)
                    metadata = result.get('metadata', {})
                    
                    print("\n" + "-"*80)
                    print("🏠 PROPERTY DATA")
                    print("-"*80)
                    
                    # Lot size data
                    lot_sqft = metadata.get('lot_sqft')
                    lot_acres = metadata.get('lot_acres')
                    
                    if lot_sqft:
                        print(f"✅ Lot Size (sqft):  {int(lot_sqft):,} sqft")
                        if lot_sqft >= 10000:
                            print(f"   ✅ MEETS LOGOS MINIMUM (10,000 sqft)")
                        else:
                            print(f"   ❌ Below LOGOS minimum (10,000 sqft)")
                    else:
                        print(f"❌ Lot Size (sqft):  NOT AVAILABLE")
                    
                    if lot_acres:
                        print(f"✅ Lot Size (acres): {float(lot_acres):.4f} acres")
                    else:
                        print(f"❌ Lot Size (acres): NOT AVAILABLE")
                    
                    # Building data
                    building_sqft = metadata.get('building_default_indicator')
                    print(f"\n📏 Building Area: {metadata.get('building_area', 'N/A')} sqft")
                    
                    # Property metadata
                    print("\n" + "-"*80)
                    print("📊 PROPERTY METADATA")
                    print("-"*80)
                    print(f"Land Use: {metadata.get('land_use', 'N/A')}")
                    print(f"Zoning: {metadata.get('zoning', 'N/A')}")
                    print(f"Property Type: {metadata.get('property_type', 'N/A')}")
                    print(f"Year Built: {metadata.get('year_built', 'N/A')}")
                    
                    # Geocoding
                    print("\n" + "-"*80)
                    print("🗺️  GEOCODING")
                    print("-"*80)
                    print(f"Latitude: {metadata.get('latitude', 'N/A')}")
                    print(f"Longitude: {metadata.get('longitude', 'N/A')}")
                    print(f"County FIPS: {metadata.get('county_fips', 'N/A')}")
                    print(f"County Name: {metadata.get('county_name', 'N/A')}")
                    
                    # Carrier route (delivery info)
                    print("\n" + "-"*80)
                    print("📮 DELIVERY INFO")
                    print("-"*80)
                    print(f"Carrier Route: {metadata.get('carrier_route', 'N/A')}")
                    print(f"Congressional District: {metadata.get('congressional_district', 'N/A')}")
                    print(f"RDI (Residential Delivery Indicator): {metadata.get('rdi', 'N/A')}")
                    
                    # Analysis
                    analysis = result.get('analysis', {})
                    print("\n" + "-"*80)
                    print("🔍 ADDRESS ANALYSIS")
                    print("-"*80)
                    print(f"DPV Match Code: {analysis.get('dpv_match_code', 'N/A')}")
                    print(f"DPV Footnotes: {analysis.get('dpv_footnotes', 'N/A')}")
                    print(f"Active: {analysis.get('active', 'N/A')}")
                
                # Final summary
                print("\n" + "="*80)
                print("📋 SUMMARY")
                print("="*80)
                
                first_result = data[0]
                metadata = first_result.get('metadata', {})
                lot_sqft = metadata.get('lot_sqft')
                
                if lot_sqft and float(lot_sqft) > 0:
                    print(f"✅ SMARTY HAS LOT SIZE DATA: {int(float(lot_sqft)):,} sqft")
                    print(f"✅ Smarty API is suitable for church properties!")
                    print(f"\n💡 Recommendation: Use Smarty as primary source for lot size data")
                else:
                    print(f"❌ Smarty does NOT have lot size data for this property")
                    print(f"⚠️  May need to investigate other APIs or manual data entry")
                
                print("\n" + "="*80)
                
            elif response.status_code == 401:
                print("\n❌ AUTHENTICATION FAILED")
                print("Error: Invalid auth-id or auth-token")
                print("\nPlease check your Smarty API credentials in .env file:")
                print("  SMARTY_AUTH_ID")
                print("  SMARTY_AUTH_TOKEN")
                
            elif response.status_code == 400:
                print("\n❌ BAD REQUEST")
                print(f"Error: {response.text}")
                print("\nPlease check the address format")
                
            else:
                print(f"\n❌ ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text[:500]}")
    
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_smarty_street_api())
