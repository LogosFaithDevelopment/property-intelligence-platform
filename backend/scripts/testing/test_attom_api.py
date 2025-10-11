"""
Test ATTOM API integration with real property
"""

import asyncio
import os

from app.api_providers.attom_provider import ATTOMProvider
from dotenv import load_dotenv

load_dotenv()

async def test_attom_api():
    """Test ATTOM API endpoints"""
    
    api_key = os.getenv("ATTOM_API_KEY")
    if not api_key:
        print("❌ ATTOM_API_KEY not found in .env")
        return
    
    print(f"✅ ATTOM API Key loaded: {api_key[:20]}...")
    print()
    
    # Initialize provider
    provider = ATTOMProvider(api_key=api_key)
    
    # Test property addresses - using ATTOM's examples from official docs
    test_addresses = [
        ("4529 Winona ct", "Denver CO"),  # Example from docs
        ("1 Infinite Loop", "Cupertino CA"),  # Apple HQ
        ("1600 Pennsylvania Ave", "Washington DC")  # White House
    ]
    
    # Use the first test address
    address1, address2 = test_addresses[0]
    test_address = f"{address1}, {address2}"
    
    print(f"🏠 Testing with address: {test_address}")
    print("=" * 60)
    print()
    
    # Test 1: Property Detail
    print("📋 TEST 1: Property Detail")
    print("-" * 60)
    detail_result = await provider.get_property_detail(address1, address2)
    
    if detail_result["success"]:
        data = detail_result["data"]
        print(f"✅ Property Detail Retrieved")
        print(f"   Address: {data.get('address', {}).get('street', 'N/A')}")
        print(f"   Lot Size: {data.get('lot', {}).get('sqft', 0):,} sqft ({data.get('lot', {}).get('acres', 0):.2f} acres)")
        print(f"   Building Size: {data.get('building', {}).get('sqft', 0):,} sqft")
        print(f"   Year Built: {data.get('building', {}).get('year_built', 'N/A')}")
        print(f"   Bedrooms: {data.get('building', {}).get('bedrooms', 0)}")
        print(f"   Bathrooms: {data.get('building', {}).get('bathrooms', 0)}")
        print(f"   Zoning: {data.get('zoning', 'N/A')}")
        print(f"   Land Use: {data.get('land_use', 'N/A')}")
        print(f"   Assessed Value: ${data.get('assessment', {}).get('assessed_value', 0):,}")
        print(f"   Market Value: ${data.get('assessment', {}).get('market_value', 0):,}")
    else:
        print(f"❌ Property Detail Failed: {detail_result.get('error', 'Unknown error')}")
        print(f"   Status Code: {detail_result.get('status_code', 'N/A')}")
        if detail_result.get('data'):
            print(f"   Response Data: {detail_result.get('data')}")
    
    print()
    
    # Test 2: AVM (Automated Valuation)
    print("💰 TEST 2: Automated Valuation Model (AVM)")
    print("-" * 60)
    avm_result = await provider.get_avm(address1, address2)
    
    if avm_result["success"]:
        data = avm_result["data"]
        print(f"✅ AVM Retrieved")
        print(f"   Estimated Value: ${data.get('amount', 0):,}")
        print(f"   Value Range: ${data.get('low', 0):,} - ${data.get('high', 0):,}")
        print(f"   Confidence Score: {data.get('confidence_score', 'N/A')}")
        print(f"   Valuation Date: {data.get('date', 'N/A')}")
    else:
        print(f"❌ AVM Failed: {avm_result.get('error', 'Unknown error')}")
        print(f"   Status Code: {avm_result.get('status_code', 'N/A')}")
        if avm_result.get('data'):
            print(f"   Response Data: {avm_result.get('data')}")
    
    print()
    
    # Test 3: Sales Comparables
    print("📊 TEST 3: Sales Comparables")
    print("-" * 60)
    comps_result = await provider.get_sales_comparables(address1, radius=0.5, address2=address2)
    
    if comps_result["success"]:
        data = comps_result["data"]
        print(f"✅ Sales Comps Retrieved")
        print(f"   Comparable Properties: {data.get('count', 0)}")
        print(f"   Median Sale Price: ${data.get('median_price', 0):,}")
        print(f"   Median $/sqft: ${data.get('median_price_per_sqft', 0):.2f}")
        
        if data.get('comparables'):
            print(f"\n   Recent Sales:")
            for i, comp in enumerate(data['comparables'][:5], 1):
                print(f"   {i}. ${comp.get('sale_price', 0):,} - {comp.get('address', 'N/A')[:40]}")
                print(f"      {comp.get('bedrooms', 0)} bed, {comp.get('bathrooms', 0)} bath, {comp.get('sqft', 0):,} sqft")
                print(f"      ${comp.get('price_per_sqft', 0):.2f}/sqft - {comp.get('distance_miles', 0):.2f} mi away")
                print()
    else:
        print(f"❌ Sales Comps Failed: {comps_result.get('error', 'Unknown error')}")
    
    print()
    
    # Test 4: Area Snapshot
    print("🌆 TEST 4: Area Snapshot (ZIP 90012)")
    print("-" * 60)
    area_result = await provider.get_area_snapshot("90012")
    
    if area_result["success"]:
        data = area_result["data"]
        print(f"✅ Area Snapshot Retrieved")
        print(f"   Median Home Value: ${data.get('median_home_value', 0):,}")
        print(f"   Median List Price: ${data.get('median_list_price', 0):,}")
        print(f"   Median Sale Price: ${data.get('median_sale_price', 0):,}")
        print(f"   Avg Days on Market: {data.get('average_days_on_market', 0)} days")
        print(f"   Recent Sales Count: {data.get('sales_count', 0)}")
        print(f"   1-Year Price Trend: {data.get('price_trend_1yr', 0):.1f}%")
        print(f"   Foreclosure Rate: {data.get('foreclosure_rate', 0):.2f}%")
    else:
        print(f"❌ Area Snapshot Failed: {area_result.get('error', 'Unknown error')}")
    
    print()
    
    # Test 5: Area Hierarchy Lookup (Area API)
    print("🗺️ TEST 5: Area Hierarchy Lookup")
    print("-" * 60)
    # Using coordinates from Denver test property
    test_lat = 39.7837
    test_lon = -105.0521
    print(f"Testing with coordinates: {test_lat}, {test_lon}")
    print()
    
    try:
        # Get all areas this point falls within
        hierarchy_result = await provider.get_area_hierarchy(test_lat, test_lon, "All")
        
        if hierarchy_result and hierarchy_result.get("areas"):
            print(f"✅ Area Hierarchy Retrieved")
            print(f"   Found {hierarchy_result.get('count', 0)} areas")
            print()
            
            # Group by type
            area_types = {}
            for area in hierarchy_result.get("areas", []):
                area_type = area.get("type", "Unknown")
                if area_type not in area_types:
                    area_types[area_type] = []
                area_types[area_type].append(area)
            
            # Display by type
            type_names = {
                "ZI": "Zip Code",
                "N1": "Macro Neighborhood",
                "N2": "Neighborhood",
                "N3": "Sub-Neighborhood",
                "N4": "Residential Subdivision",
                "DB": "School District",
                "SB": "School Attendance Area",
                "ST": "State",
                "CO": "County",
                "PL": "Place/City",
                "CB": "CBSA/Metro Area"
            }
            
            for area_type, areas in sorted(area_types.items()):
                type_label = type_names.get(area_type, area_type)
                print(f"   {type_label}:")
                for area in areas:
                    print(f"      • {area.get('name')} (ID: {area.get('id')})")
        else:
            print(f"❌ Area Hierarchy Failed: No areas found")
    except Exception as e:
        print(f"❌ Area Hierarchy Failed: {str(e)}")
    
    print()
    
    # Test 6: Get Area Boundary
    print("📍 TEST 6: Area Boundary Detail")
    print("-" * 60)
    try:
        # Get boundary for Denver's zip code (80212 from test address)
        boundary_result = await provider.get_area_boundary(area_id="ZI80212", format="geojson")
        
        if boundary_result:
            status = boundary_result.get("status", {})
            print(f"✅ Area Boundary Retrieved")
            print(f"   Status Code: {status.get('code')} - {status.get('short_description', 'Unknown')}")
            
            result = boundary_result.get("result", {})
            if result:
                package = result.get("package", {})
                item = package.get("item", {})
                if isinstance(item, list) and len(item) > 0:
                    item = item[0]
                if item:
                    print(f"   Area ID: {item.get('id', 'N/A')}")
                    print(f"   Area Name: {item.get('name', 'N/A')}")
                    print(f"   Area Type: {item.get('type', 'N/A')}")
                    print(f"   Center: ({item.get('geo_center_latitude')}, {item.get('geo_center_longitude')})")
                    
                    geometry = item.get("geometry", {})
                    if geometry:
                        print(f"   Geometry Type: {geometry.get('type', 'N/A')}")
                        coordinates = geometry.get("coordinates", [])
                        if coordinates:
                            print(f"   Boundary Points: {len(coordinates)} coordinate sets")
                else:
                    print(f"   ⚠️  No item data in response")
            else:
                print(f"   ⚠️  No result data in response")
        else:
            print(f"❌ Area Boundary Failed: No data returned")
    except Exception as e:
        print(f"❌ Area Boundary Failed: {str(e)}")
    
    print()
    
    # Test 7: Get States
    print("🗽 TEST 7: Get All States")
    print("-" * 60)
    try:
        states_result = await provider.get_all_states()
        
        if states_result:
            status = states_result.get("status", {})
            print(f"✅ States Retrieved")
            print(f"   Status: {status.get('short_description', 'Unknown')}")
            
            result = states_result.get("result", {})
            if result:
                package = result.get("package", {})
                items = package.get("item", [])
                if not isinstance(items, list):
                    items = [items] if items else []
                
                print(f"   Total States: {len(items)}")
                print(f"   Sample States:")
                for state in items[:5]:  # Show first 5
                    print(f"      • {state.get('name')} (ID: {state.get('id')})")
        else:
            print(f"❌ States Failed: No data returned")
    except Exception as e:
        print(f"❌ States Failed: {str(e)}")
    
    print()
    print("=" * 60)
    print("🎉 ATTOM API Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_attom_api())
