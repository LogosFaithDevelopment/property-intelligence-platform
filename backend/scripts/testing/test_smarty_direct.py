"""
Test Smarty US Enrichment API DIRECTLY
Testing with a known SmartyKey to bypass the 402 error on Street Address API

According to Smarty docs, we can call the Enrichment API directly:
https://us-enrichment.api.smarty.com/lookup/{smarty_key}/property/principal
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


async def test_enrichment_api_directly():
    """Test US Enrichment API directly without Street Address API"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY US ENRICHMENT API - DIRECT TEST")
    print("="*80)
    
    # Test with example SmartyKey from docs
    smarty_keys_to_test = [
        ("111111", "Example from docs"),
        ("1000000", "Another example"),
    ]
    
    for smarty_key, description in smarty_keys_to_test:
        print(f"\n{'='*80}")
        print(f"Testing SmartyKey: {smarty_key} ({description})")
        print("="*80)
        
        # THIS IS THE CORRECT ENDPOINT
        url = f"https://us-enrichment.api.smarty.com/lookup/{smarty_key}/property/principal"
        
        params = {
            "auth-id": settings.smarty_auth_id,
            "auth-token": settings.smarty_auth_token,
            "features": "financial"  # Include financial history
        }
        
        print(f"\nURL: {url}")
        print(f"Auth ID: {settings.smarty_auth_id}")
        print(f"Auth Token: {settings.smarty_auth_token[:10]}...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                print(f"\nStatus Code: {response.status_code}")
                
                if response.status_code == 200:
                    property_data = response.json()
                    
                    print("\n✅ SUCCESS!")
                    print("\nResponse structure:")
                    print(json.dumps(property_data, indent=2)[:1000])  # First 1000 chars
                    
                    # Check for acres field
                    if isinstance(property_data, list) and len(property_data) > 0:
                        attributes = property_data[0].get('attributes', {})
                    else:
                        attributes = property_data.get('attributes', {})
                    
                    acres = attributes.get('acres')
                    if acres:
                        print(f"\n✅ LOT SIZE FOUND: {acres} acres")
                    else:
                        print(f"\n❌ No lot size data in response")
                    
                elif response.status_code == 402:
                    print("\n❌ ERROR 402: Payment Required")
                    print("Your account needs property data subscription activated")
                    print(f"\nError: {response.text}")
                    
                elif response.status_code == 404:
                    print("\n⚠️  404: No property data for this SmartyKey")
                    print("(This is expected for test SmartyKeys)")
                    
                else:
                    print(f"\n❌ ERROR: {response.text}")
        
        except Exception as e:
            print(f"\n❌ EXCEPTION: {str(e)}")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\nIf you got 402 errors:")
    print("  → Your 45-day free trial needs to be ACTIVATED")
    print("  → Contact Smarty support to enable property data access")
    print("\nIf you got 200 responses:")
    print("  → Your trial is active! Proceed to test with real addresses")


if __name__ == "__main__":
    asyncio.run(test_enrichment_api_directly())
