"""
Test Smarty API for lot size data - CORRECT APPROACH
Testing: 709 Manchester Ave, Los Angeles, CA 90044 (Church Property)

IMPORTANT: Smarty requires a 2-step process:
1. US Street Address API -> Get SmartyKey
2. US Enrichment API (property/principal) -> Get lot size data

This is the CORRECT API endpoint documented by Smarty support
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import httpx
from app.config import get_settings


async def test_smarty_property_api():
    """Test Smarty Property API (correct 2-step process)"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY PROPERTY API TEST - CORRECT ENDPOINT")
    print("="*80)
    
    # Test address
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    print(f"Auth ID: {settings.smarty_auth_id}")
    print(f"Auth Token: {settings.smarty_auth_token}")
    
    # STEP 1: Get SmartyKey from US Street Address API
    print("\n" + "="*80)
    print("STEP 1: Getting SmartyKey from US Street Address API")
    print("="*80)
    
    street_url = "https://us-street.api.smarty.com/street-address"
    
    street_params = {
        "auth-id": settings.smarty_auth_id,
        "auth-token": settings.smarty_auth_token,
        "street": street,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "match": "enhanced"  # Try enhanced matching
    }
    
    print(f"\nURL: {street_url}")
    print(f"Params: {street_params}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(street_url, params=street_params)
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ ERROR: {response.text}")
                return
            
            street_data = response.json()
            
            if not street_data or len(street_data) == 0:
                print("\n❌ No address found")
                return
            
            # Extract SmartyKey from metadata (if available)
            smarty_key = street_data[0].get('metadata', {}).get('smarty_key')
            
            # If no SmartyKey in response, construct it manually from address components
            # Format: {primary_number}:{street_predirection}:{street_name}:{street_suffix}:{city_name}:{state_abbreviation}:{zipcode}
            if not smarty_key:
                print("\nℹ️  No SmartyKey in metadata, constructing manually...")
                components = street_data[0].get('components', {})
                
                # Build SmartyKey from components
                parts = []
                parts.append(components.get('primary_number', ''))
                
                if components.get('street_predirection'):
                    parts.append(components.get('street_predirection'))
                
                parts.append(components.get('street_name', ''))
                parts.append(components.get('street_suffix', ''))
                parts.append(components.get('city_name', ''))
                parts.append(components.get('state_abbreviation', ''))
                parts.append(components.get('zipcode', ''))
                
                # Join with dashes (this is how Smarty typically formats keys)
                smarty_key = '-'.join([str(p).upper() for p in parts if p])
                print(f"Constructed SmartyKey: {smarty_key}")
            
            print(f"\n✅ SUCCESS - Got SmartyKey: {smarty_key}")
            print(f"Validated Address: {street_data[0].get('delivery_line_1')}")
            
            # STEP 2: Get Property Data using SmartyKey
            print("\n" + "="*80)
            print("STEP 2: Getting Property Data from US Enrichment API")
            print("="*80)
            
            # URL-encode the SmartyKey for the API call
            encoded_smarty_key = quote(smarty_key)
            
            # THIS IS THE CORRECT ENDPOINT FOR PROPERTY DATA
            property_url = f"https://us-enrichment.api.smarty.com/lookup/{encoded_smarty_key}/property/principal"
            
            property_params = {
                "auth-id": settings.smarty_auth_id,
                "auth-token": settings.smarty_auth_token,
                "features": "financial"  # Include financial history
            }
            
            print(f"\nURL: {property_url}")
            print(f"Params: {property_params}")
            
            response = await client.get(property_url, params=property_params)
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 402:
                print("\n❌ ERROR 402: Payment Required")
                print("Your Smarty account needs an active subscription for Property Data")
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
            
            # Print raw response for debugging
            print(f"\nRaw response type: {type(property_data)}")
            print(f"Raw response: {json.dumps(property_data, indent=2)[:500]}...")
            
            # Parse the response - it's a list of results
            if isinstance(property_data, list):
                if len(property_data) == 0:
                    print("\n❌ Empty response - no property data found")
                    return
                # The response is a list of attributes
                attributes = property_data[0] if property_data else {}
            else:
                attributes = property_data.get('attributes', {})
            
            # LOT SIZE DATA
            print("\n" + "-"*80)
            print("🏠 LOT SIZE DATA (THE DATA WE NEED!)")
            print("-"*80)
            
            acres = attributes.get('acres')
            
            if acres:
                acres_float = float(acres)
                sqft = int(acres_float * 43560)  # Convert acres to sqft
                print(f"✅ Lot Size (acres): {acres_float:.4f} acres")
                print(f"✅ Lot Size (sqft):  {sqft:,} sqft")
                
                if sqft >= 10000:
                    print(f"   ✅ MEETS LOGOS MINIMUM (10,000 sqft)")
                else:
                    print(f"   ❌ Below LOGOS minimum (10,000 sqft)")
            else:
                print(f"❌ Lot Size: NOT AVAILABLE")
            
            # BUILDING DATA
            print("\n" + "-"*80)
            print("🏢 BUILDING DATA")
            print("-"*80)
            print(f"1st Floor: {attributes.get('1st_floor_sqft', 'N/A')} sqft")
            print(f"2nd Floor: {attributes.get('2nd_floor_sqft', 'N/A')} sqft")
            print(f"Attic Area: {attributes.get('attic_area', 'N/A')} sqft")
            print(f"Year Built: {attributes.get('year_built', 'N/A')}")
            
            # ASSESSMENT DATA
            print("\n" + "-"*80)
            print("💰 ASSESSMENT DATA")
            print("-"*80)
            print(f"Assessed Value: ${int(float(attributes.get('assessed_value', 0))):,}")
            print(f"Assessed Land Value: ${int(float(attributes.get('assessed_land_value', 0))):,}")
            print(f"Assessed Improvement Value: ${int(float(attributes.get('assessed_improvement_value', 0))):,}")
            print(f"Last Update: {attributes.get('assessor_last_update', 'N/A')}")
            
            # FINANCIAL HISTORY
            financial_history = attributes.get('financial_history', [])
            if financial_history:
                print("\n" + "-"*80)
                print("💵 FINANCIAL HISTORY (MORTGAGES)")
                print("-"*80)
                for idx, fin in enumerate(financial_history, 1):
                    print(f"\nMortgage #{idx}:")
                    print(f"  Amount: ${int(float(fin.get('mortgage_amount', 0))):,}")
                    print(f"  Type: {fin.get('mortgage_type', 'N/A')}")
                    print(f"  Lender: {fin.get('lender_name', 'N/A')}")
                    print(f"  Recording Date: {fin.get('mortgage_recording_date', 'N/A')}")
                    print(f"  Due Date: {fin.get('mortgage_due_date', 'N/A')}")
            
            # SUMMARY
            print("\n" + "="*80)
            print("📋 FINAL SUMMARY")
            print("="*80)
            
            if acres:
                print(f"✅ SMARTY HAS LOT SIZE DATA: {sqft:,} sqft ({acres_float:.4f} acres)")
                print(f"✅ Smarty Property API works for church properties!")
                print(f"\n💡 RECOMMENDATION: Use Smarty US Enrichment API for lot size data")
                print(f"   Endpoint: https://us-enrichment.api.smarty.com/lookup/{{{smarty_key}}}/property/principal")
            else:
                print(f"❌ Smarty does NOT have lot size data for this property")
                print(f"⚠️  May need to investigate other APIs")
            
            print("\n" + "="*80)
    
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_smarty_property_api())
