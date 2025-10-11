#!/usr/bin/env python3
"""
Test ATTOM Integration in Property Enrichment Flow
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models.property import Property
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def test_attom_enrichment():
    """Test ATTOM API integration in enrichment flow"""
    
    print("🧪 Testing ATTOM Integration in Property Enrichment")
    print("=" * 70)
    print()
    
    async for db in get_db():
        try:
            # Get the first property from database
            result = await db.execute(select(Property).limit(1))
            property_obj = result.scalar_one_or_none()
            
            if not property_obj:
                print("❌ No properties found in database")
                print("Create a property first using:")
                print("   POST /api/v1/properties")
                return
            
            print(f"📍 Test Property:")
            print(f"   ID: {property_obj.id}")
            print(f"   Address: {property_obj.full_address}")
            print(f"   Coordinates: {property_obj.latitude}, {property_obj.longitude}")
            print()
            
            # Run enrichment with premium APIs enabled (includes ATTOM)
            print("🚀 Running enrichment with ATTOM API...")
            print()
            
            service = PropertyEnrichmentService(db)
            results = await service.enrich_property(
                property_id=property_obj.id,
                use_premium_apis=True,  # Enable ATTOM
                force_refresh=True
            )
            
            print("📊 Enrichment Results:")
            print("=" * 70)
            print()
            
            # Check ATTOM data
            attom_results = results.get("results", {}).get("attom_data", {})
            
            if attom_results.get("status") == "success":
                print("✅ ATTOM DATA - SUCCESS!")
                print("-" * 70)
                
                data = attom_results.get("data", {})
                
                # Property Details
                detail = data.get("property_detail", {})
                if detail.get("success"):
                    print()
                    print("🏠 Property Details:")
                    print(f"   Lot Size: {detail.get('lot_sqft', 0):,} sqft")
                    print(f"   Building Size: {detail.get('building_sqft', 0):,} sqft")
                    print(f"   Year Built: {detail.get('year_built', 'N/A')}")
                    print(f"   Bedrooms: {detail.get('bedrooms', 0)}")
                    print(f"   Bathrooms: {detail.get('bathrooms', 0)}")
                    print(f"   Zoning: {detail.get('zoning', 'N/A')}")
                    print(f"   Land Use: {detail.get('land_use', 'N/A')}")
                else:
                    print("   ⚠️ Property detail request failed")
                
                # Valuation
                valuation = data.get("valuation", {})
                if valuation.get("success"):
                    print()
                    print("💰 Automated Valuation Model (AVM):")
                    print(f"   Estimated Value: ${valuation.get('estimated_value', 0):,}")
                    value_range = valuation.get("value_range", {})
                    print(f"   Value Range: ${value_range.get('low', 0):,} - ${value_range.get('high', 0):,}")
                    conf = valuation.get("confidence_score")
                    if conf:
                        print(f"   Confidence Score: {conf}")
                else:
                    print("   ⚠️ Valuation request failed")
                
                # Market Comparables
                comps = data.get("market_comps", {})
                if comps.get("success"):
                    print()
                    print("📊 Market Comparables:")
                    print(f"   Comparable Sales Found: {comps.get('comp_count', 0)}")
                    print(f"   Median Sale Price: ${comps.get('median_sale_price', 0):,}")
                    print(f"   Median Price/sqft: ${comps.get('median_price_per_sqft', 0):.2f}")
                else:
                    print("   ⚠️ Comparables request failed")
                
            elif attom_results.get("status") == "skipped":
                print("⏭️  ATTOM DATA - SKIPPED")
                print(f"   Reason: {attom_results.get('reason', 'Unknown')}")
                print()
                print("💡 To enable ATTOM data:")
                print("   1. Make sure ATTOM_API_KEY is set in .env")
                print("   2. Use use_premium_apis=true in API call")
                
            elif attom_results.get("status") == "error":
                print("❌ ATTOM DATA - ERROR")
                print(f"   Error: {attom_results.get('error', 'Unknown error')}")
            
            print()
            print("=" * 70)
            
            # Show other enrichment data too
            print()
            print("📋 Other Enrichment Data:")
            print("-" * 70)
            
            # Demographics
            demographics = results.get("results", {}).get("demographics", {})
            if demographics.get("status") == "success":
                demo_data = demographics.get("data", {})
                print(f"✅ Census Demographics: Population {demo_data.get('population', 'N/A'):,}")
            else:
                print(f"⚠️  Census Demographics: {demographics.get('status', 'unknown')}")
            
            # Flood Risk
            flood = results.get("results", {}).get("flood_risk", {})
            if flood.get("status") == "success":
                flood_data = flood.get("data", {})
                print(f"✅ FEMA Flood Risk: Zone {flood_data.get('flood_zone', 'N/A')} ({flood_data.get('risk_level', 'unknown')} risk)")
            else:
                print(f"⚠️  FEMA Flood Risk: {flood.get('status', 'unknown')}")
            
            # HUD Data
            hud = results.get("results", {}).get("hud_data", {})
            if hud.get("status") == "success":
                print(f"✅ HUD Data: Retrieved successfully")
            else:
                print(f"⚠️  HUD Data: {hud.get('status', 'unknown')}")
            
            print()
            print("=" * 70)
            print("🎉 ATTOM Integration Test Complete!")
            print()
            print("✅ Benefits Added:")
            print("   • Professional property valuations")
            print("   • Market comparables for context")
            print("   • Detailed property characteristics")
            print("   • Enhanced property intelligence")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(test_attom_enrichment())
