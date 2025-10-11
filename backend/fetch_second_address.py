#!/usr/bin/env python3
"""
Fetch Smarty data for the second Manchester address
706 W 85th St, Los Angeles, CA 90044
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api_providers.smarty_provider import SmartyStreetProvider
from app.core.config import settings


async def main():
    print("=" * 80)
    print("FETCHING SMARTY DATA FOR SECOND MANCHESTER ADDRESS")
    print("=" * 80)
    print()
    
    address = "706 W 85th St, Los Angeles, CA 90044"
    print(f"Address: {address}")
    print()
    
    # Initialize provider
    provider = SmartyStreetProvider(
        auth_id=settings.smarty_auth_id,
        auth_token=settings.smarty_auth_token
    )
    
    print("Calling Smarty API...")
    result = await provider.get_property_data(
        street_address="706 W 85th St",
        city="Los Angeles",
        state="CA",
        zipcode="90044"
    )
    
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    if result.get('data'):
        data = result['data']
        
        # Lot information
        lot = data.get('lot', {})
        print(f"📍 LOT INFORMATION:")
        print(f"   Size: {lot.get('size_sqft', 'N/A'):,} sqft")
        print(f"   Acres: {lot.get('size_acres', 'N/A')}")
        print(f"   Lot Numbers: {lot.get('lot_numbers', 'N/A')}")
        print(f"   Parcel/APN: {lot.get('parcel_number', 'N/A')}")
        print()
        
        # Building information
        building = data.get('building', {})
        print(f"🏢 BUILDING INFORMATION:")
        print(f"   Size: {building.get('size_sqft', 'N/A')} sqft")
        print(f"   Year Built: {building.get('year_built', 'N/A')}")
        print(f"   Stories: {building.get('stories', 'N/A')}")
        print()
        
        # Available space
        available = data.get('available_build_space', {})
        print(f"🔨 AVAILABLE BUILD SPACE:")
        print(f"   Available: {available.get('sqft', 'N/A'):,} sqft")
        print(f"   Calculation: {available.get('calculation', 'N/A')}")
        print()
        
        # Compare to first address
        print("=" * 80)
        print("COMPARISON TO 709 W MANCHESTER AVE")
        print("=" * 80)
        print()
        print(f"709 W Manchester Ave:")
        print(f"  - Lot size: 13,708 sqft")
        print(f"  - Lot numbers: 182,183")
        print(f"  - Available: 11,220 sqft")
        print()
        print(f"706 W 85th St:")
        print(f"  - Lot size: {lot.get('size_sqft', 'N/A'):,} sqft")
        print(f"  - Lot numbers: {lot.get('lot_numbers', 'N/A')}")
        print(f"  - Available: {available.get('sqft', 'N/A'):,} sqft")
        print()
        
        # Calculate combined
        first_lot = 13708
        second_lot = lot.get('size_sqft', 0)
        if second_lot > 0:
            total = first_lot + second_lot
            print(f"🎯 COMBINED TOTALS:")
            print(f"   Total lot size: {total:,} sqft")
            print(f"   Average per parcel: {total/2:,.0f} sqft")
            print()
            
            # Unit calculations
            print(f"📊 UNIT CALCULATIONS (if developed together):")
            print()
            
            # 4 floors
            buildable_4 = (total * 0.65 * 4)
            units_4 = int(buildable_4 / 481)
            print(f"   4 floors @ 65% coverage:")
            print(f"     Buildable: {buildable_4:,.0f} sqft")
            print(f"     Units: {units_4} units")
            print()
            
            # 5 floors
            buildable_5 = (total * 0.65 * 5)
            units_5 = int(buildable_5 / 481)
            print(f"   5 floors @ 65% coverage:")
            print(f"     Buildable: {buildable_5:,.0f} sqft")
            print(f"     Units: {units_5} units")
            print()
            
            # 6 floors
            buildable_6 = (total * 0.65 * 6)
            units_6 = int(buildable_6 / 481)
            print(f"   6 floors @ 65% coverage:")
            print(f"     Buildable: {buildable_6:,.0f} sqft")
            print(f"     Units: {units_6} units")
            print()
            
            print(f"   🎯 LOGOS Target: 134 units")
            print()
    else:
        print("❌ No data returned from Smarty API")
        print()
        print("Error:", result.get('error', 'Unknown error'))

if __name__ == "__main__":
    asyncio.run(main())
