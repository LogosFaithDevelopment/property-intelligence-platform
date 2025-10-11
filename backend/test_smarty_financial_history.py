"""
Test Smarty API financial history with multiple properties
Some properties may not have mortgages (owned free and clear)
"""

import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import quote

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import httpx
from app.config import get_settings


async def test_property(client, settings, street, city, state, zipcode):
    """Test a single property for financial history"""
    
    print("\n" + "="*80)
    print(f"Testing: {street}, {city}, {state} {zipcode}")
    print("="*80)
    
    # Step 1: Get SmartyKey
    street_url = "https://us-street.api.smarty.com/street-address"
    params = {
        "auth-id": settings.smarty_auth_id,
        "auth-token": settings.smarty_auth_token,
        "street": street,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "match": "enhanced"
    }
    
    response = await client.get(street_url, params=params)
    
    if response.status_code != 200:
        print(f"❌ Street Address API failed: {response.status_code}")
        return
    
    data = response.json()
    if not data or len(data) == 0:
        print(f"❌ No address found")
        return
    
    smarty_key = data[0].get('smarty_key')
    if not smarty_key:
        print(f"❌ No SmartyKey returned")
        return
    
    print(f"✅ Got SmartyKey: {smarty_key}")
    
    # Step 2: Get Property Data
    property_url = f"https://us-enrichment.api.smarty.com/lookup/{quote(smarty_key)}/property/principal"
    prop_params = {
        "auth-id": settings.smarty_auth_id,
        "auth-token": settings.smarty_auth_token
    }
    
    prop_response = await client.get(property_url, params=prop_params)
    
    if prop_response.status_code != 200:
        print(f"❌ Property API failed: {prop_response.status_code}")
        print(f"   Response: {prop_response.text}")
        return
    
    prop_data = prop_response.json()
    
    if isinstance(prop_data, list) and len(prop_data) > 0:
        result = prop_data[0]
        attributes = result.get('attributes', {})
    else:
        print(f"❌ Unexpected response format")
        return
    
    # Check for financial history
    financial_history = attributes.get('financial_history', [])
    
    print(f"\n📊 Property Summary:")
    print(f"   Lot Size: {attributes.get('acres', 'N/A')} acres")
    print(f"   Building: {attributes.get('building_sqft', 'N/A')} sqft")
    print(f"   Year Built: {attributes.get('year_built', 'N/A')}")
    print(f"   Assessed Value: ${int(float(attributes.get('assessed_value', 0))):,}")
    
    print(f"\n💰 Financial History:")
    
    if financial_history and len(financial_history) > 0:
        print(f"   ✅ Found {len(financial_history)} mortgage(s)!")
        
        for idx, mortgage in enumerate(financial_history, 1):
            print(f"\n   Mortgage #{idx}:")
            print(f"      Amount: ${int(float(mortgage.get('mortgage_amount', 0))):,}")
            print(f"      Type: {mortgage.get('mortgage_type', 'N/A')}")
            print(f"      Lender: {mortgage.get('lender_name', 'N/A')}")
            print(f"      Recording Date: {mortgage.get('mortgage_recording_date', 'N/A')}")
            print(f"      Due Date: {mortgage.get('mortgage_due_date', 'N/A')}")
    else:
        print(f"   ⚪ No mortgages found (likely owned free and clear)")


async def test_multiple_properties():
    """Test multiple properties to find ones with financial history"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY API - FINANCIAL HISTORY TEST")
    print("="*80)
    print("\nTesting multiple properties to find financial history data...")
    
    # Test addresses - mix of commercial and residential
    test_addresses = [
        # Church (likely no mortgage)
        ("709 Manchester Ave", "Los Angeles", "CA", "90044"),
        
        # Some commercial properties in LA (more likely to have mortgages)
        ("1234 Wilshire Blvd", "Los Angeles", "CA", "90017"),
        ("100 Universal City Plaza", "Universal City", "CA", "91608"),
        ("1801 Century Park E", "Los Angeles", "CA", "90067"),
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for address in test_addresses:
            try:
                await test_property(client, settings, *address)
            except Exception as e:
                print(f"\n❌ Exception for {address[0]}: {str(e)}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\n💡 Key Findings:")
    print("   - Financial history is returned when available")
    print("   - Some properties have no mortgages (owned free and clear)")
    print("   - Churches often don't have traditional mortgages")
    print("   - Commercial properties more likely to have financing")


if __name__ == "__main__":
    asyncio.run(test_multiple_properties())
