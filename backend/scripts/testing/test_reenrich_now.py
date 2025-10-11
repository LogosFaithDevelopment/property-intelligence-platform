#!/usr/bin/env python3
"""
Re-enrich Test Property
Triggers enrichment for property ID 9 (the Phase 4 test property)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.property import Property
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def reenrich_property():
    """Re-enrich the test property"""
    
    print("\n" + "="*80)
    print("🔄 RE-ENRICHING TEST PROPERTY")
    print("="*80)
    
    property_id = 9  # The test property from Phase 4
    
    async with AsyncSessionLocal() as db:
        # Get property
        result = await db.execute(
            select(Property).where(Property.id == property_id)
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print(f"❌ Property ID {property_id} not found")
            return
        
        print(f"\n📍 Property: {property_obj.name}")
        print(f"   Location: {property_obj.city}, {property_obj.state} {property_obj.zip_code}")
        print(f"   Coordinates: {property_obj.latitude}, {property_obj.longitude}")
        
        # Check current data
        import json
        data_sources = property_obj.data_sources or {}
        if isinstance(data_sources, str):
            data_sources = json.loads(data_sources)
        
        print(f"\n📊 Current Data Status:")
        print(f"   Census: {'✅' if data_sources.get('census_demographics') else '❌'}")
        print(f"   FEMA: {'✅' if data_sources.get('fema_flood') else '❌'}")
        hud = data_sources.get('hud_data', {})
        print(f"   HUD Income Limits: {'✅' if hud.get('income_limits') else '❌'}")
        print(f"   HUD FMR: {'✅' if hud.get('fair_market_rent') else '❌'}")
        
        # Run enrichment
        print(f"\n⏱️  Starting Enrichment...")
        print(f"   This will fetch fresh data from all 7 APIs...")
        
        import time
        start = time.time()
        
        try:
            service = PropertyEnrichmentService(db)
            await service.enrich_property(property_id)
            
            elapsed = time.time() - start
            
            print(f"\n✅ Enrichment Complete in {elapsed:.1f} seconds!")
            
            # Refresh and check results
            await db.refresh(property_obj)
            data_sources = property_obj.data_sources or {}
            if isinstance(data_sources, str):
                data_sources = json.loads(data_sources)
            
            print(f"\n📊 Updated Data Status:")
            
            # Census
            census = data_sources.get('census_demographics', {})
            if census.get('status') == 'success':
                data = census.get('data', {})
                print(f"   ✅ Census Demographics:")
                print(f"      - Population: {data.get('population', 'N/A'):,}" if data.get('population') else "      - Population: N/A")
                print(f"      - Median Income: ${data.get('median_income', 'N/A'):,}" if data.get('median_income') else "      - Median Income: N/A")
                print(f"      - Poverty Rate: {data.get('poverty_rate', 'N/A')}%")
                housing = data.get('housing', {})
                renter_pct = round((housing.get('renter_occupied', 0) / (housing.get('renter_occupied', 0) + housing.get('owner_occupied', 1)) * 100), 2)
                print(f"      - Renter Percentage: {renter_pct}%")
            else:
                print(f"   ❌ Census: {census.get('error', 'No data')}")
            
            # FEMA
            fema = data_sources.get('fema_flood', {})
            if fema.get('status') == 'success':
                data = fema.get('data', {})
                print(f"   ✅ FEMA Flood Risk:")
                print(f"      - Flood Zone: {data.get('flood_zone', 'N/A')}")
                print(f"      - Risk Level: {data.get('risk_level', 'N/A')}")
                history = data.get('disaster_history', {})
                print(f"      - Flood Events: {history.get('flood_count', 0)}")
            else:
                print(f"   ❌ FEMA: {fema.get('error', 'No data')}")
            
            # HUD
            hud = data_sources.get('hud_data', {})
            
            il = hud.get('income_limits', {})
            if il.get('status') == 'success':
                data = il.get('data', {})
                ami = data.get('income', {}).get('l80_2')
                print(f"   ✅ HUD Income Limits: ${ami:,} (80% AMI)" if ami else "   ✅ HUD Income Limits: Success")
            else:
                print(f"   ❌ HUD Income Limits: {il.get('error', 'No data')}")
            
            fmr = hud.get('fair_market_rent', {})
            if fmr.get('status') == 'success':
                data = fmr.get('data', {})
                rent = data.get('rent_by_bedroom', {}).get('2_bedroom')
                print(f"   ✅ HUD Fair Market Rent: ${rent:,} (2BR)" if rent else "   ✅ HUD FMR: Success")
            else:
                print(f"   ❌ HUD FMR: {fmr.get('error', 'No data')}")
            
            print(f"\n🎉 Re-Enrichment Complete!")
            print(f"   Property is now ready for a fresh AI assessment")
            print("="*80 + "\n")
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"\n❌ Enrichment Failed after {elapsed:.1f}s")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(reenrich_property())
