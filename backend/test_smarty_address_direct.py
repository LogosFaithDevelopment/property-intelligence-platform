"""
Test Smarty API - Direct property lookup by address components
Testing if we can query property data directly without SmartyKey
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


async def test_smarty_direct_address():
    """Test direct property lookup by address"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY PROPERTY API - DIRECT ADDRESS LOOKUP")
    print("="*80)
    
    # Test address
    street = "709 W Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    
    # Try different endpoint formats
    endpoints_to_try = [
        {
            "name": "Search by street address",
            "url": "https://us-enrichment.api.smarty.com/search/property/principal",
            "params": {
                "auth-id": settings.smarty_auth_id,
                "auth-token": settings.smarty_auth_token,
                "street": street,
                "city": city,
                "state": state,
                "zipcode": zipcode
            }
        },
        {
            "name": "Lookup by freeform address",
            "url": "https://us-enrichment.api.smarty.com/lookup",
            "params": {
                "auth-id": settings.smarty_auth_id,
                "auth-token": settings.smarty_auth_token,
                "freeform": f"{street}, {city}, {state} {zipcode}"
            }
        },
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for idx, endpoint in enumerate(endpoints_to_try, 1):
            print(f"\n{'='*80}")
            print(f"ATTEMPT #{idx}: {endpoint['name']}")
            print(f"{'='*80}")
            print(f"URL: {endpoint['url']}")
            print(f"Params: {endpoint['params']}")
            
            try:
                response = await client.get(endpoint['url'], params=endpoint['params'])
                
                print(f"\nStatus Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n✅ SUCCESS!")
                    print(f"Response type: {type(data)}")
                    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
                    
                    # Check if we got property data
                    if isinstance(data, list) and len(data) > 0:
                        print(f"\n🎉 GOT PROPERTY DATA!")
                        return data
                    elif data:
                        print(f"\n🎉 GOT SOME DATA!")
                        return data
                    else:
                        print(f"\n⚠️ Empty response")
                else:
                    print(f"❌ Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
    
    print(f"\n{'='*80}")
    print("❌ ALL ATTEMPTS FAILED")
    print(f"{'='*80}")
    print("\n💡 CONCLUSION: Smarty Property API requires a valid SmartyKey")
    print("   SmartyKey must be obtained from Street Address API with proper license")
    print("   You may need to contact Smarty support to enable SmartyKey in responses")


if __name__ == "__main__":
    asyncio.run(test_smarty_direct_address())
