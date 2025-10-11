"""
Test Smarty API using GEOCODE (lat/lon) approach instead of SmartyKey
Testing: 709 Manchester Ave, Los Angeles, CA 90044 (Church Property)

APPROACH: Use latitude/longitude from Street Address API to query property data
This is more reliable than constructing SmartyKeys manually
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import httpx
from app.config import get_settings


async def test_smarty_geocode():
    """Test Smarty Property API using geocode (lat/lon)"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY PROPERTY API TEST - GEOCODE APPROACH")
    print("="*80)
    
    # Test address
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    print(f"Auth ID: {settings.smarty_auth_id}")
    print(f"Auth Token: {settings.smarty_auth_token}")
    
    # STEP 1: Get Geocode (lat/lon) from US Street Address API
    print("\n" + "="*80)
    print("STEP 1: Getting Geocode from US Street Address API")
    print("="*80)
    
    street_url = "https://us-street.api.smarty.com/street-address"
    
    street_params = {
        "auth-id": settings.smarty_auth_id,
        "auth-token": settings.smarty_auth_token,
        "street": street,
        "city": city,
        "state": state,
        "zipcode": zipcode
    }
    
    print(f"\nURL: {street_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(street_url, params=street_params)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ ERROR: {response.text}")
                return
            
            street_data = response.json()
            
            if not street_data or len(street_data) == 0:
                print("\n❌ No address found")
                return
            
            # Extract geocode from metadata
            metadata = street_data[0].get('metadata', {})
            latitude = metadata.get('latitude')
            longitude = metadata.get('longitude')
            
            if not latitude or not longitude:
                print("\n❌ No geocode in response")
                return
            
            print(f"\n✅ SUCCESS - Got Geocode:")
            print(f"   Latitude: {latitude}")
            print(f"   Longitude: {longitude}")
            print(f"   Validated Address: {street_data[0].get('delivery_line_1')}")
            
            # STEP 2: Try Property Lookup using Geocode
            print("\n" + "="*80)
            print("STEP 2: Getting Property Data using Geocode")
            print("="*80)
            
            # Try the geocode-based endpoint
            # Format: /search/property/principal?latitude={lat}&longitude={lon}
            property_url = "https://us-enrichment.api.smarty.com/search/property/principal"
            
            property_params = {
                "auth-id": settings.smarty_auth_id,
                "auth-token": settings.smarty_auth_token,
                "latitude": latitude,
                "longitude": longitude
            }
            
            print(f"\nURL: {property_url}")
            print(f"Params: lat={latitude}, lon={longitude}")
            
            response = await client.get(property_url, params=property_params)
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 402:
                print("\n❌ ERROR 402: Payment Required")
                print("Your Smarty account needs an active subscription for Property Data")
                print("\nError details:", response.text)
                return
            
            if response.status_code == 404:
                print("\n❌ ERROR 404: Geocode endpoint not available")
                print("This endpoint may not be supported or property not found")
                print("\nError details:", response.text)
                return
            
            if response.status_code != 200:
                print(f"❌ ERROR: {response.text}")
                return
            
            property_data = response.json()
            
            print("\n✅ SUCCESS - Got Property Data!")
            print("\n" + "="*80)
            print("PROPERTY DATA RESPONSE")
            print("="*80)
            
            # Print raw response
            print(f"\nRaw response type: {type(property_data)}")
            print(f"Raw response length: {len(property_data) if isinstance(property_data, list) else 'N/A'}")
            print(f"\nFull response:\n{json.dumps(property_data, indent=2)}")
            
            # Parse the response
            if isinstance(property_data, list):
                if len(property_data) == 0:
                    print("\n❌ Empty response - no property data found")
                    return
                attributes = property_data[0]
            else:
                attributes = property_data
            
            # LOT SIZE DATA
            print("\n" + "="*80)
            print("🏠 LOT SIZE DATA (THE DATA WE NEED!)")
            print("="*80)
            
            acres = attributes.get('acres')
            
            if acres:
                acres_float = float(acres)
                sqft = int(acres_float * 43560)
                print(f"✅ Lot Size (acres): {acres_float:.4f} acres")
                print(f"✅ Lot Size (sqft):  {sqft:,} sqft")
                
                if sqft >= 10000:
                    print(f"   ✅ MEETS LOGOS MINIMUM (10,000 sqft)")
                else:
                    print(f"   ❌ Below LOGOS minimum (10,000 sqft)")
            else:
                print(f"❌ Lot Size: NOT AVAILABLE in response")
                print(f"\nAvailable fields: {list(attributes.keys())}")
            
            print("\n" + "="*80)
    
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_smarty_geocode())
