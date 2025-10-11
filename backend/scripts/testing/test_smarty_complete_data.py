"""
Complete Smarty API test for LOGOS requirements
Tests: Lot Numbers, Lot Size, Building Size, Available Build Space, Financial History

KEY REQUIREMENT: Available Build Space = Lot Size - Building Size
If Available Build Space >= 10,000 sqft = SWEET SPOT for LOGOS
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


async def test_complete_property_data():
    """Test complete property data extraction for LOGOS"""
    
    settings = get_settings()
    
    print("="*80)
    print("SMARTY API - COMPLETE PROPERTY DATA TEST")
    print("="*80)
    print("\n🎯 LOGOS Requirements Test:")
    print("   1. Lot Numbers (APN/Parcel)")
    print("   2. Lot Size (sqft)")
    print("   3. Building Size (sqft)")
    print("   4. Available Build Space (sqft) - THE MONEY NUMBER")
    print("   5. Financial History")
    
    # Test address - Manchester church with 2 lots
    street = "709 Manchester Ave"
    city = "Los Angeles"
    state = "CA"
    zipcode = "90044"
    
    print(f"\n📍 Test Address: {street}, {city}, {state} {zipcode}")
    print("   (Church property with 2 lot numbers)")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # STEP 1: Get SmartyKey
        print("\n" + "="*80)
        print("STEP 1: Getting SmartyKey from Street Address API")
        print("="*80)
        
        street_url = "https://us-street.api.smarty.com/street-address"
        street_params = {
            "auth-id": settings.smarty_auth_id,
            "auth-token": settings.smarty_auth_token,
            "street": street,
            "city": city,
            "state": state,
            "zipcode": zipcode,
            "match": "enhanced"  # REQUIRED to get smarty_key
        }
        
        response = await client.get(street_url, params=street_params)
        
        if response.status_code != 200:
            print(f"❌ ERROR: {response.text}")
            return
        
        street_data = response.json()
        if not street_data:
            print("❌ No address found")
            return
        
        smarty_key = street_data[0].get('smarty_key')
        if not smarty_key:
            print("❌ No SmartyKey returned")
            return
        
        print(f"✅ Got SmartyKey: {smarty_key}")
        print(f"   Address: {street_data[0].get('delivery_line_1')}")
        
        # STEP 2: Get Property Data
        print("\n" + "="*80)
        print("STEP 2: Getting Property Data from Enrichment API")
        print("="*80)
        
        property_url = f"https://us-enrichment.api.smarty.com/lookup/{quote(smarty_key)}/property/principal"
        prop_params = {
            "auth-id": settings.smarty_auth_id,
            "auth-token": settings.smarty_auth_token
        }
        
        prop_response = await client.get(property_url, params=prop_params)
        
        if prop_response.status_code != 200:
            print(f"❌ ERROR {prop_response.status_code}: {prop_response.text}")
            return
        
        prop_data = prop_response.json()
        
        if isinstance(prop_data, list) and len(prop_data) > 0:
            result = prop_data[0]
            attributes = result.get('attributes', {})
        else:
            print("❌ Unexpected response format")
            return
        
        print("✅ Got Property Data!")
        
        # EXTRACT ALL REQUIRED DATA
        print("\n" + "="*80)
        print("📋 COMPLETE PROPERTY DATA FOR LOGOS")
        print("="*80)
        
        # 1. LOT NUMBERS (APN/Parcel)
        print("\n" + "─"*80)
        print("1️⃣  LOT/PARCEL NUMBERS")
        print("─"*80)
        
        parcel_number = attributes.get('parcel_raw_number')
        apn_original = attributes.get('apn_original')
        lot_1 = attributes.get('lot_1')
        lot_2 = attributes.get('lot_2')
        lot_3 = attributes.get('lot_3')
        
        print(f"   Parcel Number (APN): {parcel_number or 'N/A'}")
        print(f"   APN Original: {apn_original or 'N/A'}")
        
        lots = []
        if lot_1:
            lots.append(lot_1)
            print(f"   Lot 1: {lot_1}")
        if lot_2:
            lots.append(lot_2)
            print(f"   Lot 2: {lot_2}")
        if lot_3:
            lots.append(lot_3)
            print(f"   Lot 3: {lot_3}")
        
        if not lots:
            print(f"   ⚠️  No lot numbers found")
        else:
            print(f"   ✅ Total Lots: {len(lots)}")
        
        # 2. LOT SIZE
        print("\n" + "─"*80)
        print("2️⃣  LOT SIZE")
        print("─"*80)
        
        acres = attributes.get('acres')
        lot_sqft_raw = attributes.get('lot_sqft')
        
        if acres:
            acres_float = float(acres)
            lot_sqft_calculated = int(acres_float * 43560)
            print(f"   Acres: {acres_float:.4f}")
            print(f"   Lot Size: {lot_sqft_calculated:,} sqft (calculated from acres)")
            lot_sqft = lot_sqft_calculated
        elif lot_sqft_raw:
            lot_sqft = int(float(lot_sqft_raw))
            print(f"   Lot Size: {lot_sqft:,} sqft (direct from API)")
            print(f"   Acres: {lot_sqft / 43560:.4f} (calculated)")
        else:
            print(f"   ❌ No lot size data available")
            lot_sqft = 0
        
        # 3. BUILDING SIZE
        print("\n" + "─"*80)
        print("3️⃣  BUILDING SIZE")
        print("─"*80)
        
        building_sqft_raw = attributes.get('building_sqft')
        floor_1_sqft = attributes.get('1st_floor_sqft')
        floor_2_sqft = attributes.get('2nd_floor_sqft')
        
        if building_sqft_raw:
            building_sqft = int(float(building_sqft_raw))
            print(f"   Total Building: {building_sqft:,} sqft")
        else:
            building_sqft = 0
            print(f"   ⚠️  No building size data")
        
        if floor_1_sqft:
            print(f"   1st Floor: {floor_1_sqft} sqft")
        if floor_2_sqft:
            print(f"   2nd Floor: {floor_2_sqft} sqft")
        
        # 4. AVAILABLE BUILD SPACE - THE MONEY NUMBER!
        print("\n" + "─"*80)
        print("4️⃣  💰 AVAILABLE BUILD SPACE - THE MONEY NUMBER!")
        print("─"*80)
        
        if lot_sqft > 0 and building_sqft > 0:
            available_build_space = lot_sqft - building_sqft
            print(f"   Lot Size:        {lot_sqft:,} sqft")
            print(f"   Building Size:   {building_sqft:,} sqft")
            print(f"   ─────────────────────────────")
            print(f"   Available Space: {available_build_space:,} sqft")
            
            if available_build_space >= 10000:
                print(f"\n   🎉🎉🎉 SWEET SPOT! >= 10,000 sqft available! 🎉🎉🎉")
                print(f"   ✅ QUALIFIES FOR LOGOS FINANCING")
            else:
                print(f"\n   ⚠️  Below 10,000 sqft threshold")
                print(f"   ❌ Does not meet LOGOS minimum")
        else:
            print(f"   ❌ Cannot calculate - missing lot or building size")
            available_build_space = None
        
        # 5. ASSESSED VALUES
        print("\n" + "─"*80)
        print("5️⃣  ASSESSED VALUES")
        print("─"*80)
        
        assessed_value = int(float(attributes.get('assessed_value', 0)))
        assessed_land = int(float(attributes.get('assessed_land_value', 0)))
        assessed_improvement = int(float(attributes.get('assessed_improvement_value', 0)))
        
        print(f"   Total Value:       ${assessed_value:,}")
        print(f"   Land Value:        ${assessed_land:,}")
        print(f"   Improvement Value: ${assessed_improvement:,}")
        print(f"   Last Update:       {attributes.get('assessor_last_update', 'N/A')}")
        
        # 6. FINANCIAL HISTORY
        print("\n" + "─"*80)
        print("6️⃣  💵 FINANCIAL HISTORY (MORTGAGES)")
        print("─"*80)
        
        financial_history = attributes.get('financial_history', [])
        
        if financial_history and len(financial_history) > 0:
            print(f"   ✅ Found {len(financial_history)} mortgage(s)!")
            
            for idx, mortgage in enumerate(financial_history, 1):
                print(f"\n   Mortgage #{idx}:")
                print(f"      Amount:         ${int(float(mortgage.get('mortgage_amount', 0))):,}")
                print(f"      Type:           {mortgage.get('mortgage_type', 'N/A')}")
                print(f"      Lender:         {mortgage.get('lender_name', 'N/A')}")
                print(f"      Recording Date: {mortgage.get('mortgage_recording_date', 'N/A')}")
                print(f"      Due Date:       {mortgage.get('mortgage_due_date', 'N/A')}")
                print(f"      Term:           {mortgage.get('mortgage_term', 'N/A')} {mortgage.get('mortgage_term_type', '')}")
        else:
            print(f"   ⚪ No mortgages found")
            print(f"   (Likely owned free and clear)")
        
        # 7. ADDITIONAL PROPERTY INFO
        print("\n" + "─"*80)
        print("7️⃣  ADDITIONAL PROPERTY INFO")
        print("─"*80)
        
        print(f"   Year Built:     {attributes.get('year_built', 'N/A')}")
        print(f"   Property Type:  {attributes.get('property_use_standardized', 'N/A')}")
        print(f"   Zoning:         {attributes.get('zoning', 'N/A')}")
        print(f"   County:         {attributes.get('county_name', 'N/A')}")
        
        # FINAL SUMMARY
        print("\n" + "="*80)
        print("✅ FINAL SUMMARY FOR LOGOS")
        print("="*80)
        
        print(f"\n📍 Address: {street_data[0].get('delivery_line_1')}, {city}, {state} {zipcode}")
        
        if lots:
            print(f"📋 Parcel/Lot Numbers: {', '.join(lots)}")
        else:
            print(f"📋 Parcel Number: {parcel_number or 'N/A'}")
        
        print(f"\n📐 Property Dimensions:")
        print(f"   • Lot Size: {lot_sqft:,} sqft ({acres_float:.4f} acres)" if acres else f"   • Lot Size: {lot_sqft:,} sqft")
        print(f"   • Building Size: {building_sqft:,} sqft")
        
        if available_build_space is not None:
            print(f"   • 💰 Available Build Space: {available_build_space:,} sqft")
            
            if available_build_space >= 10000:
                print(f"\n🎯 RESULT: ✅ QUALIFIES FOR LOGOS (>= 10,000 sqft available)")
            else:
                print(f"\n🎯 RESULT: ❌ Below threshold ({10000 - available_build_space:,} sqft short)")
        
        print(f"\n💵 Property Value: ${assessed_value:,}")
        
        if financial_history:
            total_debt = sum(int(float(m.get('mortgage_amount', 0))) for m in financial_history)
            print(f"💳 Total Mortgages: ${total_debt:,} ({len(financial_history)} mortgage(s))")
        else:
            print(f"💳 No Existing Mortgages (Free and Clear)")
        
        print("\n" + "="*80)
        print("🎉 ALL DATA RETRIEVED SUCCESSFULLY!")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_complete_property_data())
