"""
Quick test script to check ATTOM API lot size data
Testing: 709 Manchester Ave, Los Angeles, CA 90044
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.api_providers.attom_provider import ATTOMProvider
from app.config import get_settings


async def test_attom_lot_size():
    """Test ATTOM API for lot size data"""
    
    # Get settings to load API key
    settings = get_settings()
    
    # Initialize provider with API key
    provider = ATTOMProvider(api_key=settings.attom_api_key)
    
    # Test address
    address = "709 Manchester Ave"
    city_state = "Los Angeles, CA 90044"
    
    print("="*80)
    print("ATTOM API LOT SIZE TEST")
    print("="*80)
    print(f"\nAddress: {address}, {city_state}")
    print(f"API Key: {os.getenv('ATTOM_API_KEY', 'NOT SET')[:20]}...")
    print("\nFetching property details from ATTOM...\n")
    
    # Fetch property details
    result = await provider.get_property_detail(
        address=address,
        address2=city_state
    )
    
    if result.get("success"):
        data = result.get("data", {})
        lot_info = data.get("lot", {})
        
        print("✅ SUCCESS - Property found in ATTOM database")
        print("\n" + "-"*80)
        print("LOT SIZE DATA:")
        print("-"*80)
        print(f"Lot Size (sqft): {lot_info.get('sqft', 0):,}")
        print(f"Lot Size (acres): {lot_info.get('acres', 0):.4f}")
        print(f"Lot Frontage (ft): {lot_info.get('frontage', 0)}")
        print(f"Lot Depth (ft): {lot_info.get('depth', 0)}")
        
        print("\n" + "-"*80)
        print("BUILDING DATA:")
        print("-"*80)
        building_info = data.get("building", {})
        print(f"Building Size (sqft): {building_info.get('sqft', 0):,}")
        print(f"Year Built: {building_info.get('year_built', 'N/A')}")
        
        print("\n" + "-"*80)
        print("ADDRESS DATA:")
        print("-"*80)
        address_info = data.get("address", {})
        print(f"Street: {address_info.get('street', '')}")
        print(f"City: {address_info.get('city', '')}")
        print(f"State: {address_info.get('state', '')}")
        print(f"ZIP: {address_info.get('zip', '')}")
        
        print("\n" + "-"*80)
        print("ASSESSMENT DATA:")
        print("-"*80)
        assessment_info = data.get("assessment", {})
        print(f"Assessed Value: ${assessment_info.get('assessed_value', 0):,}")
        print(f"Market Value: ${assessment_info.get('market_value', 0):,}")
        print(f"Assessment Year: {assessment_info.get('year', 'N/A')}")
        
        print("\n" + "-"*80)
        print("ZONING & LAND USE:")
        print("-"*80)
        print(f"Zoning: {data.get('zoning', 'N/A')}")
        print(f"Land Use: {data.get('land_use', 'N/A')}")
        
        print("\n" + "="*80)
        print("CONCLUSION:")
        print("="*80)
        lot_sqft = lot_info.get('sqft', 0)
        if lot_sqft > 0:
            print(f"✅ ATTOM HAS LOT SIZE DATA: {lot_sqft:,} sqft")
            if lot_sqft >= 10000:
                print(f"✅ Meets LOGOS minimum (10,000 sqft)")
            else:
                print(f"❌ Below LOGOS minimum (10,000 sqft)")
        else:
            print("❌ No lot size data available from ATTOM")
        
    else:
        print("❌ FAILED - Could not retrieve property data")
        print(f"\nError: {result.get('error', 'Unknown error')}")
        print(f"Status Code: {result.get('status_code', 'N/A')}")
        print(f"Details: {result.get('details', 'N/A')}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_attom_lot_size())
