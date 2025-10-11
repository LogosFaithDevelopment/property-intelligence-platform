#!/usr/bin/env python3
"""
Simple enrichment diagnostic - runs inside Docker container
"""

import asyncio
import sys
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

import os

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:password@db:5432/property_intelligence'

from app.database import AsyncSessionLocal, engine
from app.models.property import Property
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def main():
    print("\n" + "="*80)
    print("🧪 ENRICHMENT DIAGNOSTIC")
    print("="*80)
    
    async with AsyncSessionLocal() as db:
        # Get latest property
        result = await db.execute(
            select(Property).order_by(Property.id.desc()).limit(1)
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print("❌ No properties found")
            return
        
        print(f"\n📍 Property: {property_obj.name}")
        print(f"   ID: {property_obj.id}")
        print(f"   Location: {property_obj.city}, {property_obj.state} {property_obj.zip_code}")
        
        # Check current data
        data_sources = property_obj.data_sources or {}
        print(f"\n📊 Current Data:")
        print(f"   Census: {'✅' if data_sources.get('census_demographics') else '❌'}")
        print(f"   FEMA: {'✅' if data_sources.get('fema_flood') else '❌'}")
        hud = data_sources.get('hud_data', {})
        print(f"   HUD IL: {'✅' if hud.get('income_limits') else '❌'}")
        print(f"   HUD FMR: {'✅' if hud.get('fair_market_rent') else '❌'}")
        
        # Run enrichment
        print(f"\n⏱️  Running Enrichment...")
        start = time.time()
        
        try:
            service = PropertyEnrichmentService(db)
            await service.enrich_property(property_obj.id)
            
            elapsed = time.time() - start
            print(f"\n✅ Complete in {elapsed:.1f}s")
            
            # Check results
            await db.refresh(property_obj)
            data_sources = property_obj.data_sources or {}
            
            print(f"\n📊 Results:")
            
            # Census
            census = data_sources.get('census_demographics', {})
            if census.get('status') == 'success':
                data = census.get('data', {})
                print(f"   ✅ Census: Poverty {data.get('poverty_rate')}%, Renter {data.get('renter_percentage')}%")
            else:
                print(f"   ❌ Census: {census.get('error', 'No data')}")
            
            # HUD
            hud = data_sources.get('hud_data', {})
            fmr = hud.get('fair_market_rent', {})
            if fmr.get('status') == 'success':
                data = fmr.get('data', {})
                rent = data.get('rent_by_bedroom', {}).get('2_bedroom')
                print(f"   ✅ HUD FMR: ${rent:,} (2BR)" if rent else "   ✅ HUD FMR: Success")
            else:
                print(f"   ❌ HUD FMR: {fmr.get('error', 'No data')}")
            
            il = hud.get('income_limits', {})
            if il.get('status') == 'success':
                data = il.get('data', {})
                ami = data.get('income', {}).get('l80_2')
                print(f"   ✅ HUD IL: ${ami:,} (80% AMI)" if ami else "   ✅ HUD IL: Success")
            else:
                print(f"   ❌ HUD IL: {il.get('error', 'No data')}")
            
            # FEMA
            fema = data_sources.get('fema_flood', {})
            if fema.get('status') == 'success':
                data = fema.get('data', {})
                print(f"   ✅ FEMA: Zone {data.get('flood_zone', 'Unknown')}")
            else:
                print(f"   ⚠️  FEMA: {fema.get('error', 'No data')}")
            
            print(f"\n🚀 Performance: {'✅ EXCELLENT' if elapsed < 15 else '⚠️ SLOW'} ({elapsed:.1f}s)")
            print("="*80 + "\n")
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"\n❌ Failed after {elapsed:.1f}s: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
