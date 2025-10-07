#!/usr/bin/env python3
"""
Re-enrich Property Script
Diagnoses and re-enriches a property with all API data
"""

import asyncio
import json
import sys
from datetime import datetime

from app.database import AsyncSessionLocal
from app.models.property import Property
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def main():
    print("\n" + "="*80)
    print("🔄 PROPERTY RE-ENRICHMENT DIAGNOSTIC & FIX")
    print("="*80)
    
    async with AsyncSessionLocal() as db:
        # Get the most recent property
        result = await db.execute(
            select(Property).order_by(Property.id.desc()).limit(1)
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print("❌ No properties found in database")
            return
        
        print(f"\n📍 Property Found:")
        print(f"   ID: {property_obj.id}")
        print(f"   Name: {property_obj.name}")
        print(f"   Address: {property_obj.street_address}, {property_obj.city}, {property_obj.state} {property_obj.zip_code}")
        print(f"   Coordinates: {property_obj.latitude}, {property_obj.longitude}")
        
        # Check current enrichment status
        print(f"\n📊 Current Enrichment Status:")
        if property_obj.data_sources:
            try:
                data_sources = json.loads(property_obj.data_sources) if isinstance(property_obj.data_sources, str) else property_obj.data_sources
                
                # Check each data source
                demographics = data_sources.get("demographics", {})
                flood_risk = data_sources.get("flood_risk", {})
                hud_data = data_sources.get("hud_data", {})
                
                print(f"   Census Demographics: {'✅ ' + demographics.get('status', 'unknown') if demographics else '❌ missing'}")
                if demographics and demographics.get("data"):
                    census_data = demographics.get("data", {})
                    print(f"      Population: {census_data.get('population', 'N/A')}")
                    print(f"      Median Income: ${census_data.get('median_income', 'N/A'):,}" if census_data.get('median_income') else "      Median Income: N/A")
                    print(f"      Poverty Rate: {census_data.get('poverty_rate', 'N/A')}%")
                
                print(f"   FEMA Flood Risk: {'✅ ' + flood_risk.get('status', 'unknown') if flood_risk else '❌ missing'}")
                if flood_risk and flood_risk.get("data"):
                    flood_data = flood_risk.get("data", {})
                    print(f"      Flood Zone: {flood_data.get('flood_zone', 'N/A')}")
                    print(f"      Risk Level: {flood_data.get('risk_level', 'N/A')}")
                
                print(f"   HUD Data: {'✅ ' + hud_data.get('status', 'unknown') if hud_data else '❌ missing'}")
                if hud_data and hud_data.get("data"):
                    hud_results = hud_data.get("data", {})
                    income_limits = hud_results.get("income_limits", {})
                    fmr = hud_results.get("fair_market_rent", {})
                    
                    print(f"      Income Limits: {'✅' if income_limits.get('success') else '❌'}")
                    if income_limits.get("data"):
                        il_data = income_limits["data"]
                        print(f"         80% AMI (2-person): ${il_data.get('80_percent_ami', {}).get('2_person', 'N/A'):,}" if isinstance(il_data.get('80_percent_ami'), dict) else "         80% AMI: N/A")
                    
                    print(f"      Fair Market Rent: {'✅' if fmr.get('success') else '❌'}")
                    if fmr.get("data"):
                        fmr_data = fmr["data"]
                        print(f"         2BR Rent: ${fmr_data.get('rent_by_bedroom', {}).get('2_bedroom', 'N/A'):,}" if isinstance(fmr_data.get('rent_by_bedroom'), dict) else "         2BR Rent: N/A")
                
            except Exception as e:
                print(f"   ⚠️  Error parsing data_sources: {e}")
                print(f"   Raw data_sources length: {len(str(property_obj.data_sources))} characters")
        else:
            print("   ❌ No enrichment data found")
        
        # Ask user if they want to re-enrich
        print(f"\n" + "="*80)
        print("🔄 Re-Enrichment Options:")
        print("   1. Re-enrich with force_refresh (fetches fresh data from all APIs)")
        print("   2. Show raw data_sources JSON")
        print("   3. Exit")
        print("="*80)
        
        try:
            choice = input("\nEnter choice (1-3): ").strip()
        except EOFError:
            # Non-interactive mode, auto-select option 1
            choice = "1"
            print("1 (auto-selected in non-interactive mode)")
        
        if choice == "1":
            print(f"\n🚀 Starting re-enrichment with force_refresh=True...")
            print(f"   This will fetch fresh data from:")
            print(f"   ✓ Census API (demographics)")
            print(f"   ✓ FEMA API (flood risk)")
            print(f"   ✓ HUD API (income limits, fair market rent)")
            print(f"\n   Processing... (this may take 30-60 seconds)")
            
            service = PropertyEnrichmentService(db)
            
            try:
                start_time = datetime.now()
                results = await service.enrich_property(
                    property_id=property_obj.id,
                    use_premium_apis=False,
                    force_refresh=True
                )
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print(f"\n✅ Re-enrichment completed in {duration:.1f} seconds!")
                print(f"\n📊 Enrichment Results:")
                print(f"   Status: {results.get('status', 'unknown')}")
                
                # Show results for each API
                api_results = results.get("results", {})
                
                print(f"\n   📍 Geocoding: {api_results.get('geocoding', {}).get('status', 'unknown')}")
                
                demographics = api_results.get("demographics", {})
                print(f"   👥 Census Demographics: {demographics.get('status', 'unknown')}")
                if demographics.get("data"):
                    census_data = demographics["data"]
                    print(f"      Population: {census_data.get('population', 'N/A')}")
                    print(f"      Median Income: ${census_data.get('median_income', 'N/A'):,}" if census_data.get('median_income') else "      Median Income: N/A")
                    print(f"      Poverty Rate: {census_data.get('poverty_rate', 'N/A')}%")
                
                flood = api_results.get("flood_risk", {})
                print(f"   🌊 FEMA Flood Risk: {flood.get('status', 'unknown')}")
                if flood.get("data"):
                    flood_data = flood["data"]
                    print(f"      Flood Zone: {flood_data.get('flood_zone', 'N/A')}")
                    print(f"      Risk Level: {flood_data.get('risk_level', 'N/A')}")
                
                hud = api_results.get("hud_data", {})
                print(f"   🏠 HUD Data: {hud.get('status', 'unknown')}")
                if hud.get("data"):
                    hud_results = hud["data"]
                    
                    income_limits = hud_results.get("income_limits", {})
                    if income_limits.get("success") and income_limits.get("data"):
                        il_data = income_limits["data"]
                        print(f"      ✅ Income Limits:")
                        print(f"         80% AMI (2-person): ${il_data.get('80_percent_ami', {}).get('2_person', 'N/A'):,}" if isinstance(il_data.get('80_percent_ami'), dict) else "         Data format issue")
                    else:
                        print(f"      ❌ Income Limits: {income_limits.get('error', 'Failed')}")
                    
                    fmr = hud_results.get("fair_market_rent", {})
                    if fmr.get("success") and fmr.get("data"):
                        fmr_data = fmr["data"]
                        print(f"      ✅ Fair Market Rent:")
                        print(f"         2BR: ${fmr_data.get('rent_by_bedroom', {}).get('2_bedroom', 'N/A'):,}" if isinstance(fmr_data.get('rent_by_bedroom'), dict) else "         Data format issue")
                    else:
                        print(f"      ❌ Fair Market Rent: {fmr.get('error', 'Failed')}")
                
                print(f"\n" + "="*80)
                print("✅ RE-ENRICHMENT COMPLETE!")
                print("="*80)
                print(f"\nNext step: Run assessment test to see updated scores:")
                print(f"   docker-compose exec backend python test_phase4_integration.py")
                
            except Exception as e:
                print(f"\n❌ Error during re-enrichment: {e}")
                import traceback
                traceback.print_exc()
        
        elif choice == "2":
            print(f"\n📄 Raw data_sources JSON:")
            if property_obj.data_sources:
                data_sources = json.loads(property_obj.data_sources) if isinstance(property_obj.data_sources, str) else property_obj.data_sources
                print(json.dumps(data_sources, indent=2))
            else:
                print("   (empty)")
        
        else:
            print("\nExiting without changes.")


if __name__ == "__main__":
    asyncio.run(main())
