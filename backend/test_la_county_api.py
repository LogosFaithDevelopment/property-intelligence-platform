"""
Test LA County Assessor API Client

This script tests the LA County Assessor API with real addresses to verify:
1. API connection and data retrieval
2. Data parsing and field mapping
3. Lot size extraction (key feature for property enrichment)
4. Integration readiness for property enrichment service
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.api_clients.la_county_assessor import LACountyAssessorClient


async def test_real_property():
    """Test with a real LA County property"""
    
    client = LACountyAssessorClient()
    
    try:
        print("=" * 80)
        print("LA COUNTY ASSESSOR API TEST")
        print("=" * 80)
        
        # Test address: Shepherd Church in Chatsworth, CA (real church property)
        test_address = "19700 Rinaldi St"
        test_city = "Chatsworth"
        test_zip = "91326"
        
        print(f"\n🔍 Testing with address: {test_address}, {test_city}, {test_zip}")
        print("-" * 80)
        
        result = await client.get_property_by_address(
            street_address=test_address,
            city=test_city,
            zip_code=test_zip
        )
        
        if not result.get('success'):
            print(f"❌ API call failed: {result.get('error')}")
            print("\nLet's try LA City Hall as fallback...")
            
            # Fallback: Try LA City Hall
            test_address = "200 N Spring St"
            test_city = "Los Angeles"
            test_zip = "90012"
            
            print(f"\n🔍 Testing fallback address: {test_address}, {test_city}, {test_zip}")
            print("-" * 80)
            
            result = await client.get_property_by_address(
                street_address=test_address,
                city=test_city,
                zip_code=test_zip
            )
        
        # Display results
        if result.get('success'):
            print("✅ Successfully retrieved property data!\n")
            
            # Location info
            location = result.get('location', {})
            print("📍 LOCATION:")
            print(f"  Property Address: {location.get('property_location')}")
            coords = location.get('coordinates', {})
            print(f"  Coordinates: {coords.get('latitude')}, {coords.get('longitude')}")
            
            # Identification
            identification = result.get('identification', {})
            print("\n🆔 IDENTIFICATION:")
            print(f"  AIN: {identification.get('ain')}")
            print(f"  Assessor ID: {identification.get('assessor_id')}")
            print(f"  Roll Year: {identification.get('roll_year')}")
            
            # Property characteristics (KEY DATA)
            characteristics = result.get('characteristics', {})
            print("\n📐 PROPERTY CHARACTERISTICS:")
            print(f"  Lot Size: {characteristics.get('lot_size_sqft'):,} sq ft")
            print(f"  Lot Size: {characteristics.get('lot_size_acres')} acres")
            print(f"  Year Built: {characteristics.get('year_built')}")
            print(f"  Bedrooms: {characteristics.get('bedrooms')}")
            print(f"  Bathrooms: {characteristics.get('bathrooms')}")
            print(f"  Units: {characteristics.get('units')}")
            print(f"  Number of Buildings: {characteristics.get('num_buildings')}")
            
            # Property use
            use_info = result.get('use_info', {})
            print("\n🏢 PROPERTY USE:")
            print(f"  Use Type: {use_info.get('use_type')}")
            print(f"  Use Code: {use_info.get('use_code')}")
            print(f"  Classification: {use_info.get('classification')}")
            print(f"  General Use: {use_info.get('general_use_type')}")
            
            # Valuation
            valuation = result.get('valuation', {})
            print("\n💰 VALUATION:")
            print(f"  Total Assessed Value: ${valuation.get('total_value'):,}" if valuation.get('total_value') else "  Total Assessed Value: N/A")
            print(f"  Land Value: ${valuation.get('land_value'):,}" if valuation.get('land_value') else "  Land Value: N/A")
            print(f"  Improvement Value: ${valuation.get('improvement_value'):,}" if valuation.get('improvement_value') else "  Improvement Value: N/A")
            
            # Recording date (last sale)
            administrative = result.get('administrative', {})
            recording_date = administrative.get('recording_date')
            if recording_date:
                print(f"\n📅 LAST RECORDING DATE: {recording_date}")
            
            # Extract key fields for Property model
            print("\n" + "=" * 80)
            print("KEY FIELDS FOR PROPERTY MODEL INTEGRATION")
            print("=" * 80)
            
            key_fields = client.extract_key_fields(result)
            for field, value in key_fields.items():
                if value is not None:
                    if isinstance(value, (int, float)) and field not in ['latitude', 'longitude', 'year_built']:
                        print(f"  {field}: {value:,}")
                    else:
                        print(f"  {field}: {value}")
            
            # Highlight lot size (critical for our use case)
            print("\n" + "=" * 80)
            print("✨ CRITICAL FIELD VALIDATION")
            print("=" * 80)
            lot_sqft = key_fields.get('lot_size_sqft')
            lot_acres = key_fields.get('lot_size_acres')
            
            if lot_sqft and lot_acres:
                print(f"✅ LOT SIZE DATA AVAILABLE:")
                print(f"   • Square Feet: {lot_sqft:,} sq ft")
                print(f"   • Acres: {lot_acres} acres")
                print(f"\n🎉 SUCCESS! This data can auto-populate lot_size in Property model")
            else:
                print("❌ LOT SIZE DATA NOT AVAILABLE")
                print("   This property may not have parcel dimensions in the database")
            
            # Save full response for inspection
            output_file = Path("/app/la_county_test_result.json")
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📄 Full API response saved to: {output_file}")
            
        else:
            print(f"❌ Failed to retrieve property data")
            print(f"   Error: {result.get('error')}")
            print("\n💡 This could mean:")
            print("   1. Address not found in LA County Assessor database")
            print("   2. API field names may have changed")
            print("   3. Property is exempt or not in the current roll year")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()
        print("\n" + "=" * 80)
        print("Test completed")
        print("=" * 80)


async def test_by_ain():
    """Test lookup by AIN (Assessor ID Number)"""
    
    client = LACountyAssessorClient()
    
    try:
        print("\n" + "=" * 80)
        print("TESTING AIN LOOKUP")
        print("=" * 80)
        
        # Sample AIN - replace with real one if you have it
        # This is a dummy example - you'd need a real AIN from LA County
        test_ain = "5149025028"  # Example format
        
        print(f"\n🔍 Testing with AIN: {test_ain}")
        print("-" * 80)
        
        result = await client.get_property_by_ain(test_ain)
        
        if result.get('success'):
            print("✅ Successfully retrieved property by AIN!")
            location = result.get('location', {})
            print(f"  Address: {location.get('property_location')}")
            
            characteristics = result.get('characteristics', {})
            print(f"  Lot Size: {characteristics.get('lot_size_acres')} acres")
        else:
            print(f"❌ AIN lookup failed: {result.get('error')}")
            print("   (This is expected if using a dummy AIN)")
    
    finally:
        await client.close()


if __name__ == "__main__":
    print("\n🚀 Starting LA County Assessor API Tests\n")
    
    # Run main address test
    asyncio.run(test_real_property())
    
    # Optionally test AIN lookup
    # asyncio.run(test_by_ain())
    
    print("\n✅ All tests completed!\n")
