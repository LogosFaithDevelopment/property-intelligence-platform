"""
Quick test to fetch Smarty data for 706 W 85th St
"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import httpx
from app.config import get_settings


async def fetch_property_data():
    """Fetch property data for 706 W 85th St"""
    
    settings = get_settings()
    
    print("="*80)
    print("FETCHING: 706 W 85th St, Los Angeles, CA 90044")
    print("="*80)
    
    # Address to test
    street = "706 W 85th St"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # STEP 1: Get SmartyKey
        print("\n[1] Getting SmartyKey...")
        street_url = f"https://us-street.api.smarty.com/street-address"
        street_params = {
            "auth-id": settings.smarty_auth_id,
            "auth-token": settings.smarty_auth_token,
            "street": street,
            "city": city,
            "state": state,
            "zipcode": zipcode,
            "license": "us-property-data-principal-api-cloud"
        }
        
        response = await client.get(street_url, params=street_params)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            print("❌ Address not found!")
            return
        
        smarty_key = data[0].get('smarty_key')
        print(f"✅ SmartyKey: {smarty_key}")
        print(f"   Formatted: {data[0].get('delivery_line_1')}")
        
        # STEP 2: Get Property Data
        print("\n[2] Getting Property Data...")
        property_url = f"https://us-property.api.smarty.com/lookup/{smarty_key}"
        property_params = {
            "auth-id": settings.smarty_auth_id,
            "auth-token": settings.smarty_auth_token,
            "license": "us-property-data-principal-api-cloud"
        }
        
        response = await client.get(property_url, params=property_params)
        response.raise_for_status()
        property_data = response.json()
        
        # Extract key data
        print("\n" + "="*80)
        print("PROPERTY DATA")
        print("="*80)
        
        # Parcel/Lot Numbers
        lot_1 = property_data.get('lot_1', 'N/A')
        parcel_number = property_data.get('parcel_number', 'N/A')
        print(f"\n📋 PARCEL INFO:")
        print(f"   Lot Numbers: {lot_1}")
        print(f"   APN: {parcel_number}")
        
        # Lot Size
        acres = property_data.get('acres', 0)
        acres_float = float(acres) if acres else 0
        lot_sqft = int(acres_float * 43560) if acres_float > 0 else 0
        
        print(f"\n📐 LOT SIZE:")
        print(f"   Acres: {acres}")
        print(f"   Sqft: {lot_sqft:,}")
        
        # Building Size
        building_sqft = property_data.get('building_sqft', 0)
        building_sqft = int(float(building_sqft)) if building_sqft else 0
        
        print(f"\n🏠 BUILDING SIZE:")
        print(f"   Building: {building_sqft:,} sqft")
        
        # Available Build Space
        available_sqft = lot_sqft - building_sqft
        
        print(f"\n💰 AVAILABLE BUILD SPACE:")
        print(f"   Lot Size:      {lot_sqft:,} sqft")
        print(f"   Building:      {building_sqft:,} sqft")
        print(f"   ───────────────────────────")
        print(f"   Available:     {available_sqft:,} sqft")
        
        if available_sqft >= 10000:
            print(f"   ✅ QUALIFIES for LOGOS (>= 10,000 sqft)")
        else:
            print(f"   ❌ DOES NOT QUALIFY (< 10,000 sqft)")
        
        # Property Value
        assessed_total = property_data.get('assessed_value', 0)
        print(f"\n💵 PROPERTY VALUE:")
        print(f"   Assessed Value: ${assessed_total:,}")
        
        # Year Built
        year_built = property_data.get('year_built', 'N/A')
        print(f"\n🏗️  PROPERTY INFO:")
        print(f"   Year Built: {year_built}")
        
        print("\n" + "="*80)
        print("✅ FETCH COMPLETE")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(fetch_property_data())
