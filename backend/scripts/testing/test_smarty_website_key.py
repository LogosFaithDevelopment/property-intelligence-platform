"""
Test Smarty API with Website Key authentication
Based on Smarty's example showing 'key' parameter instead of 'auth-id' and 'auth-token'

Example from Smarty:
curl "https://us-street.api.smarty.com/street-address?key=21102174564513388&street=3331%20Erie%20Ave&city=Cincinnati&state=OH&zipcode=45208&candidates=10&match=enhanced&license=us-rooftop-geocoding-cloud"
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import httpx
from app.config import get_settings


async def test_with_website_key():
    """Test Smarty with website key authentication"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY API - WEBSITE KEY AUTHENTICATION TEST")
    print("="*80)
    
    # Test address
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    print(f"\nCurrent Auth ID: {settings.smarty_auth_id}")
    print(f"Current Auth Token: {settings.smarty_auth_token}")
    
    # Check if there's a website key in settings
    website_key = settings.smarty_website_key
    
    if website_key:
        print(f"\n✅ Found Website Key: {website_key}")
    else:
        print(f"\n⚠️  No SMARTY_WEBSITE_KEY in settings")
        print(f"\n📋 ACTION NEEDED:")
        print(f"   1. Log into your Smarty account dashboard")
        print(f"   2. Look for 'API Keys' or 'Website Keys' section")
        print(f"   3. Find a key that looks like: 21102174564513388")
        print(f"   4. Add it to your .env file as: SMARTY_WEBSITE_KEY=<your-key>")
        print(f"\n   This is different from auth-id and auth-token!")
        return
    
    print("\n" + "="*80)
    print("TEST 1: Using Website Key with license parameter")
    print("="*80)
    
    street_url = "https://us-street.api.smarty.com/street-address"
    
    # Try with different license options
    license_options = [
        "us-rooftop-geocoding-cloud",
        "us-property-data-principal",
        "us-enrichment-key",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for license_type in license_options:
            print(f"\n{'─'*80}")
            print(f"Trying license: {license_type}")
            print(f"{'─'*80}")
            
            params = {
                "key": website_key,
                "street": street,
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "candidates": 10,
                "match": "enhanced",
                "license": license_type
            }
            
            print(f"URL: {street_url}")
            print(f"Params: {params}")
            
            try:
                response = await client.get(street_url, params=params)
                
                print(f"\nStatus Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        print(f"\n✅ SUCCESS!")
                        
                        # Check for smarty_key in metadata
                        metadata = data[0].get('metadata', {})
                        smarty_key = metadata.get('smarty_key')
                        
                        if smarty_key:
                            print(f"\n🎉 FOUND SMARTY KEY: {smarty_key}")
                            print(f"\n{'='*80}")
                            print(f"THIS IS THE KEY WE NEED!")
                            print(f"{'='*80}")
                            return smarty_key
                        else:
                            print(f"\n⚠️  No smarty_key in metadata")
                            print(f"\nAvailable metadata fields:")
                            for key in metadata.keys():
                                print(f"  - {key}: {metadata[key]}")
                    else:
                        print(f"\n⚠️  Empty response")
                        
                elif response.status_code == 401:
                    print(f"\n❌ 401 Unauthorized - Website key may be invalid")
                    print(f"Response: {response.text}")
                    
                elif response.status_code == 402:
                    print(f"\n❌ 402 Payment Required - License not subscribed")
                    print(f"Response: {response.text}")
                    
                else:
                    print(f"\n❌ Error {response.status_code}")
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"\n❌ Exception: {str(e)}")
    
    print("\n" + "="*80)
    print("TEST 2: Using auth-id/auth-token with license parameter")
    print("="*80)
    
    # Create a new client for test 2
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try with your current auth method
        for license_type in license_options:
            print(f"\n{'─'*80}")
            print(f"Trying license: {license_type}")
            print(f"{'─'*80}")
            
            params = {
                "auth-id": settings.smarty_auth_id,
                "auth-token": settings.smarty_auth_token,
                "street": street,
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "candidates": 10,
                "match": "enhanced",
                "license": license_type
            }
            
            try:
                response = await client.get(street_url, params=params)
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        metadata = data[0].get('metadata', {})
                        smarty_key = metadata.get('smarty_key')
                        
                        if smarty_key:
                            print(f"\n🎉 FOUND SMARTY KEY: {smarty_key}")
                            print(f"\n{'='*80}")
                            print(f"THIS IS THE KEY WE NEED!")
                            print(f"{'='*80}")
                            return smarty_key
                        else:
                            print(f"⚠️  No smarty_key in metadata")
                    else:
                        print(f"⚠️  Empty response")
                        
                elif response.status_code == 402:
                    print(f"❌ 402 Payment Required - License '{license_type}' not subscribed")
                    
                else:
                    print(f"❌ Error {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n❌ No SmartyKey found with any method")
    print("\n📋 NEXT STEPS:")
    print("   1. Check your Smarty dashboard for a 'Website Key' or 'Embedded Key'")
    print("   2. Look for active licenses/subscriptions that include property data")
    print("   3. Contact Smarty support about enabling SmartyKey in API responses")


if __name__ == "__main__":
    asyncio.run(test_with_website_key())
