"""
Test to see ALL available fields from Smarty API
Check for market value, sale price, and other valuation data
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


async def test_full_data():
    """Get all available fields from Smarty"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY API - FULL DATA FIELDS TEST")
    print("="*80)
    
    # Test address
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\nAddress: {street}, {city}, {state} {zipcode}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
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
        data = response.json()
        smarty_key = data[0].get('smarty_key')
        
        print(f"✅ Got SmartyKey: {smarty_key}")
        
        # Step 2: Get Property Data
        property_url = f"https://us-enrichment.api.smarty.com/lookup/{quote(smarty_key)}/property/principal"
        prop_params = {
            "auth-id": settings.smarty_auth_id,
            "auth-token": settings.smarty_auth_token
        }
        
        prop_response = await client.get(property_url, params=prop_params)
        prop_data = prop_response.json()
        
        if isinstance(prop_data, list) and len(prop_data) > 0:
            result = prop_data[0]
            attributes = result.get('attributes', {})
        else:
            print("❌ No data")
            return
        
        # Print ALL fields to see what's available
        print("\n" + "="*80)
        print("ALL AVAILABLE FIELDS:")
        print("="*80)
        
        # Look for valuation-related fields
        valuation_keywords = ['value', 'price', 'sale', 'market', 'appraisal']
        
        print("\n🔍 VALUATION-RELATED FIELDS:")
        print("-"*80)
        for key, value in sorted(attributes.items()):
            if any(keyword in key.lower() for keyword in valuation_keywords):
                print(f"  {key}: {value}")
        
        # Print all fields (truncated)
        print("\n📋 ALL FIELDS (first 50):")
        print("-"*80)
        for idx, (key, value) in enumerate(sorted(attributes.items())):
            if idx >= 50:
                print(f"\n  ... and {len(attributes) - 50} more fields")
                break
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:50] + "..."
            print(f"  {key}: {value_str}")
        
        # Specifically check for these valuation fields
        print("\n" + "="*80)
        print("💰 VALUATION SUMMARY:")
        print("="*80)
        
        # Assessed values
        print(f"\n📊 Assessed Values (Tax Purposes):")
        print(f"  Total Assessed: ${int(float(attributes.get('assessed_value', 0))):,}")
        print(f"  Land Value: ${int(float(attributes.get('assessed_land_value', 0))):,}")
        print(f"  Improvement Value: ${int(float(attributes.get('assessed_improvement_value', 0))):,}")
        print(f"  Assessment Year: {attributes.get('assessor_taxroll_update', 'N/A')}")
        
        # Market/Sale values
        print(f"\n💵 Market/Sale Values:")
        print(f"  Market Total Value: ${int(float(attributes.get('market_total_value', 0) or 0)):,}")
        print(f"  Market Land Value: ${int(float(attributes.get('market_land_value', 0) or 0)):,}")
        print(f"  Market Improvement Value: ${int(float(attributes.get('market_improvement_value', 0) or 0)):,}")
        
        # Last sale
        print(f"\n🏷️  Last Sale:")
        print(f"  Sale Price: ${int(float(attributes.get('sale_price', 0) or 0)):,}")
        print(f"  Sale Date: {attributes.get('sale_date', 'N/A')}")
        print(f"  Sale Recording Date: {attributes.get('sale_recording_date', 'N/A')}")
        
        # Price per sqft (if we have sale price)
        sale_price = float(attributes.get('sale_price', 0) or 0)
        building_sqft = float(attributes.get('building_sqft', 0) or 0)
        if sale_price > 0 and building_sqft > 0:
            price_per_sqft = sale_price / building_sqft
            print(f"  Price per SqFt: ${price_per_sqft:,.2f}")
        
        print("\n" + "="*80)
        print("📌 KEY INSIGHT:")
        print("="*80)
        print("\nCalifornia's Prop 13 keeps assessed values LOW for tax purposes.")
        print("Market value is typically 3-5x higher than assessed value.")
        print("Check 'sale_price' and 'sale_date' for actual market transactions.")


if __name__ == "__main__":
    asyncio.run(test_full_data())
