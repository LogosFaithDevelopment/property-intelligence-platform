"""
Test the Smarty Provider integration
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.api_providers.smarty_provider import SmartyProvider
from app.config import get_settings


async def test_smarty_provider():
    """Test Smarty Provider with the Manchester Ave church"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY PROVIDER TEST")
    print("="*80)
    
    # Initialize provider
    provider = SmartyProvider(
        auth_id=settings.smarty_auth_id,
        auth_token=settings.smarty_auth_token
    )
    
    # Test address (LOGOS church property)
    test_address = {
        'street': '709 Manchester Ave',
        'city': 'Los Angeles',
        'state': 'CA',
        'zipcode': '90044'
    }
    
    print(f"\n📍 Testing Address:")
    print(f"   {test_address['street']}")
    print(f"   {test_address['city']}, {test_address['state']} {test_address['zipcode']}")
    
    # Get property data
    print(f"\n🔄 Fetching property data from Smarty...")
    
    result = await provider.get_property_data(**test_address)
    
    if not result.get('success'):
        print(f"\n❌ ERROR:")
        print(f"   {result.get('error')}")
        print(f"   {result.get('details', '')}")
        return
    
    print(f"\n✅ SUCCESS! Got property data")
    
    # Display key metrics
    print("\n" + "="*80)
    print("🏠 PROPERTY SUMMARY")
    print("="*80)
    
    # Address
    address = result.get('address', {})
    print(f"\n📍 Address:")
    print(f"   {address.get('street')}")
    print(f"   {address.get('city')}, {address.get('state')} {address.get('zipcode')}")
    print(f"   County: {address.get('county')}")
    print(f"   Coordinates: {address.get('latitude')}, {address.get('longitude')}")
    
    # Lot Information
    lot = result.get('lot', {})
    print(f"\n📐 Lot Information:")
    print(f"   Size: {lot.get('size_acres'):.4f} acres ({lot.get('size_sqft'):,} sqft)")
    print(f"   Lot Numbers: {lot.get('lot_numbers', 'N/A')}")
    print(f"   Parcel/APN: {lot.get('parcel_number', 'N/A')}")
    
    # Building Information
    building = result.get('building', {})
    print(f"\n🏢 Building Information:")
    print(f"   Size: {building.get('size_sqft'):,} sqft")
    print(f"   Year Built: {building.get('year_built', 'N/A')}")
    print(f"   1st Floor: {building.get('1st_floor_sqft'):,} sqft")
    print(f"   2nd Floor: {building.get('2nd_floor_sqft'):,} sqft")
    print(f"   Construction: {building.get('construction_type', 'N/A')}")
    
    # 🎯 THE MONEY NUMBER - Available Build Space
    available = result.get('available_build_space', {})
    print(f"\n💰 AVAILABLE BUILD SPACE (THE KEY METRIC!):")
    print(f"   {available.get('sqft'):,} sqft ({available.get('acres'):.4f} acres)")
    print(f"   Calculation: {available.get('calculation')}")
    print(f"   Minimum Required: {available.get('minimum_required'):,} sqft")
    
    if available.get('qualifies_for_logos'):
        print(f"   ✅✅✅ QUALIFIES FOR LOGOS FINANCING! ✅✅✅")
    else:
        print(f"   ❌ Does not meet LOGOS minimum")
    
    # Valuation
    valuation = result.get('valuation', {})
    print(f"\n💵 Property Valuation:")
    print(f"   Assessed Value (Tax): ${valuation.get('assessed_total'):,}")
    print(f"   - Land: ${valuation.get('assessed_land'):,}")
    print(f"   - Improvements: ${valuation.get('assessed_improvement'):,}")
    print(f"   Assessment Year: {valuation.get('assessed_year', 'N/A')}")
    print(f"\n   Estimated Market Value Range:")
    print(f"   ${valuation.get('estimated_market_min'):,} - ${valuation.get('estimated_market_max'):,}")
    print(f"\n   Note: {valuation.get('note', '')}")
    
    # Property Type
    prop_type = result.get('property_type', {})
    print(f"\n🏛️  Property Classification:")
    print(f"   Land Use: {prop_type.get('land_use', 'N/A')}")
    print(f"   Type Indicator: {prop_type.get('rdi', 'N/A')}")
    
    # Financial History
    financial = result.get('financial', {})
    print(f"\n💰 Financial History:")
    if financial.get('has_mortgages'):
        print(f"   ✅ Has {financial.get('mortgage_count')} mortgage(s)")
        print(f"   Total Mortgage Amount: ${financial.get('total_mortgage_amount'):,}")
        
        print(f"\n   Mortgage Details:")
        for idx, mortgage in enumerate(financial.get('mortgages', []), 1):
            print(f"\n   Mortgage #{idx}:")
            print(f"      Amount: ${mortgage.get('amount'):,}")
            print(f"      Type: {mortgage.get('type', 'N/A')}")
            print(f"      Lender: {mortgage.get('lender_name', 'N/A')}")
            print(f"      Location: {mortgage.get('lender_city', '')}, {mortgage.get('lender_state', '')}")
            print(f"      Recording Date: {mortgage.get('recording_date', 'N/A')}")
            print(f"      Due Date: {mortgage.get('due_date', 'N/A')}")
    else:
        print(f"   ⚪ No mortgages found (property likely owned free and clear)")
    
    # Owner Information
    owner = result.get('owner', {})
    print(f"\n👤 Owner Information:")
    print(f"   Name: {owner.get('name', 'N/A')}")
    print(f"   Last Sale Date: {owner.get('last_sale_date', 'N/A')}")
    if owner.get('last_sale_price', 0) > 0:
        print(f"   Last Sale Price: ${owner.get('last_sale_price'):,}")
    
    print("\n" + "="*80)
    print("✅ SMARTY PROVIDER TEST COMPLETE")
    print("="*80)
    
    print("\n📋 Summary:")
    print(f"   • Property data retrieved successfully")
    print(f"   • Lot size: {lot.get('size_sqft'):,} sqft")
    print(f"   • Building size: {building.get('size_sqft'):,} sqft")
    print(f"   • Available build space: {available.get('sqft'):,} sqft")
    print(f"   • LOGOS qualification: {'✅ YES' if available.get('qualifies_for_logos') else '❌ NO'}")
    print(f"   • Mortgages: {'Yes' if financial.get('has_mortgages') else 'No'}")
    
    # Close provider
    await provider.close()


if __name__ == "__main__":
    asyncio.run(test_smarty_provider())
