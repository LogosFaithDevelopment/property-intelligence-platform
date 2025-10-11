"""
Test Smarty API with match=enhanced to get SmartyKey
According to Smarty support: "match=enhanced must be set in order to get smarty key"
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


async def test_enhanced_match():
    """Test Smarty with match=enhanced to get SmartyKey"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY API - ENHANCED MATCH TEST (Getting SmartyKey)")
    print("="*80)
    print("\n💡 KEY INSIGHT: match=enhanced must be set to get smarty_key")
    
    # Test address
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    print(f"Auth ID: {settings.smarty_auth_id}")
    
    street_url = "https://us-street.api.smarty.com/street-address"
    
    # THE CRITICAL PARAMETER: match=enhanced
    params = {
        "auth-id": settings.smarty_auth_id,
        "auth-token": settings.smarty_auth_token,
        "street": street,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "match": "enhanced"  # ⭐ THIS IS THE KEY!
    }
    
    print("\n" + "="*80)
    print("STEP 1: Getting SmartyKey with match=enhanced")
    print("="*80)
    print(f"URL: {street_url}")
    print(f"Params: {params}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(street_url, params=params)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ ERROR: {response.text}")
            return
        
        data = response.json()
        
        if not data or len(data) == 0:
            print("\n❌ No address found")
            return
        
        print(f"\n✅ Got response with {len(data)} result(s)")
        
        # Print the full response to see what we get
        print("\n" + "-"*80)
        print("FULL RESPONSE:")
        print("-"*80)
        print(json.dumps(data[0], indent=2))
        
        # Check for smarty_key - it's at the ROOT level, not in metadata!
        smarty_key = data[0].get('smarty_key')
        metadata = data[0].get('metadata', {})
        
        print("\n" + "="*80)
        if smarty_key:
            print("🎉🎉🎉 SUCCESS! FOUND SMARTY KEY! 🎉🎉🎉")
            print("="*80)
            print(f"\nSmartyKey: {smarty_key}")
            
            # Now try to get property data with this key
            print("\n" + "="*80)
            print("STEP 2: Getting Property Data with SmartyKey")
            print("="*80)
            
            from urllib.parse import quote
            encoded_key = quote(smarty_key)
            property_url = f"https://us-enrichment.api.smarty.com/lookup/{encoded_key}/property/principal"
            
            property_params = {
                "auth-id": settings.smarty_auth_id,
                "auth-token": settings.smarty_auth_token
                # Note: financial_history is included by default in property/principal
            }
            
            print(f"\nURL: {property_url}")
            
            prop_response = await client.get(property_url, params=property_params)
            
            print(f"Status Code: {prop_response.status_code}")
            
            if prop_response.status_code == 200:
                prop_data = prop_response.json()
                
                print(f"\n✅ Got property data!")
                print(f"Response type: {type(prop_data)}")
                
                # Parse the response structure: it's a list with one item that has 'attributes'
                if isinstance(prop_data, list) and len(prop_data) > 0:
                    result = prop_data[0]
                    attributes = result.get('attributes', {})
                elif isinstance(prop_data, dict):
                    attributes = prop_data.get('attributes', {})
                else:
                    print(f"\n⚠️ Unexpected response format")
                    print(json.dumps(prop_data, indent=2)[:500])
                    return
                
                # Check for lot size in attributes
                acres = attributes.get('acres')
                
                print("\n" + "="*80)
                print("🏠 LOT SIZE DATA")
                print("="*80)
                
                if acres:
                    acres_float = float(acres)
                    sqft = int(acres_float * 43560)
                    print(f"\n✅✅✅ SUCCESS! WE HAVE LOT SIZE DATA! ✅✅✅")
                    print(f"\nLot Size: {acres_float:.4f} acres ({sqft:,} sqft)")
                    
                    if sqft >= 10000:
                        print(f"✅ MEETS LOGOS MINIMUM (10,000 sqft)")
                    else:
                        print(f"⚠️ Below LOGOS minimum (10,000 sqft)")
                else:
                    print(f"\n❌ No 'acres' field in response")
                    print(f"\nAvailable fields: {list(attributes.keys())[:20]}")
                    print(f"\nFirst 500 chars of response:")
                    print(json.dumps(attributes, indent=2)[:500])
                
                # Check for financial history
                print("\n" + "="*80)
                print("💰 FINANCIAL HISTORY (MORTGAGES)")
                print("="*80)
                
                financial_history = attributes.get('financial_history', [])
                
                if financial_history and len(financial_history) > 0:
                    print(f"\n✅ Found {len(financial_history)} mortgage record(s)!")
                    
                    for idx, mortgage in enumerate(financial_history, 1):
                        print(f"\n{'─'*80}")
                        print(f"Mortgage #{idx}:")
                        print(f"{'─'*80}")
                        print(f"  Amount: ${int(float(mortgage.get('mortgage_amount', 0))):,}")
                        print(f"  Type: {mortgage.get('mortgage_type', 'N/A')}")
                        print(f"  Lender: {mortgage.get('lender_name', 'N/A')}")
                        print(f"  Recording Date: {mortgage.get('mortgage_recording_date', 'N/A')}")
                        print(f"  Due Date: {mortgage.get('mortgage_due_date', 'N/A')}")
                        print(f"  Term: {mortgage.get('mortgage_term', 'N/A')} {mortgage.get('mortgage_term_type', '')}")
                        
                        # Lender location
                        lender_city = mortgage.get('lender_city', '')
                        lender_state = mortgage.get('lender_state', '')
                        if lender_city and lender_state:
                            print(f"  Lender Location: {lender_city}, {lender_state}")
                else:
                    print(f"\n⚠️ No financial history found")
                    print(f"Note: This may mean no mortgages, or property is owned free and clear")
                
                # Print other useful property data
                print("\n" + "="*80)
                print("🏢 BUILDING INFORMATION")
                print("="*80)
                print(f"  Building Size: {attributes.get('building_sqft', 'N/A')} sqft")
                print(f"  1st Floor: {attributes.get('1st_floor_sqft', 'N/A')} sqft")
                print(f"  2nd Floor: {attributes.get('2nd_floor_sqft', 'N/A')} sqft")
                print(f"  Year Built: {attributes.get('year_built', 'N/A')}")
                
                print("\n" + "="*80)
                print("💵 ASSESSED VALUES")
                print("="*80)
                print(f"  Total Assessed Value: ${int(float(attributes.get('assessed_value', 0))):,}")
                print(f"  Land Value: ${int(float(attributes.get('assessed_land_value', 0))):,}")
                print(f"  Improvement Value: ${int(float(attributes.get('assessed_improvement_value', 0))):,}")
                print(f"  Last Update: {attributes.get('assessor_last_update', 'N/A')}")
            
            elif prop_response.status_code == 402:
                print(f"\n❌ 402 Payment Required")
                print(f"You may need to activate the Property Data subscription")
                print(f"Response: {prop_response.text}")
            
            else:
                print(f"\n❌ Error {prop_response.status_code}")
                print(f"Response: {prop_response.text}")
        
        else:
            print("❌ NO SMARTY KEY IN RESPONSE")
            print("="*80)
            print(f"\nMetadata fields present: {list(metadata.keys())}")
            print(f"\nThis is unexpected since match=enhanced was set.")
            print(f"Please check:")
            print(f"  1. Is your account configured for property data access?")
            print(f"  2. Contact Smarty support with this test result")


if __name__ == "__main__":
    asyncio.run(test_enhanced_match())
