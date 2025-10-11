#!/usr/bin/env python3
"""
Check what's actually stored in the database after enrichment
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.property import Property
from sqlalchemy import select


async def check_data():
    """Check enrichment data in database"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING STORED ENRICHMENT DATA")
    print("="*80)
    
    property_id = 9
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Property).where(Property.id == property_id)
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print(f"❌ Property not found")
            return
        
        print(f"\n📍 Property: {property_obj.name}")
        
        # Get raw data_sources
        data_sources = property_obj.data_sources
        
        print(f"\n📦 Raw Data Type: {type(data_sources)}")
        
        if isinstance(data_sources, str):
            print(f"   Length: {len(data_sources)} characters")
            data_sources = json.loads(data_sources)
        
        print(f"\n📊 Data Sources Keys:")
        for key in data_sources.keys():
            print(f"   - {key}")
        
        # Check each source
        print(f"\n📋 Detailed Status:")
        
        # Census/Demographics
        if 'demographics' in data_sources:
            demo = data_sources['demographics']
            print(f"\n   📈 Demographics:")
            print(f"      Status: {demo.get('status')}")
            if demo.get('status') == 'success':
                data = demo.get('data', {})
                print(f"      Population: {data.get('population')}")
                print(f"      Median Income: {data.get('median_income')}")
                print(f"      Poverty Rate: {data.get('poverty_rate')}")
        
        # Check if using old 'census_demographics' key
        if 'census_demographics' in data_sources:
            census = data_sources['census_demographics']
            print(f"\n   📈 Census Demographics:")
            print(f"      Status: {census.get('status')}")
            if census.get('status') == 'success':
                data = census.get('data', {})
                print(f"      Population: {data.get('population')}")
        
        # FEMA
        if 'flood_risk' in data_sources:
            fema = data_sources['flood_risk']
            print(f"\n   🌊 Flood Risk:")
            print(f"      Status: {fema.get('status')}")
            if fema.get('status') == 'success':
                data = fema.get('data', {})
                print(f"      Flood Zone: {data.get('flood_zone')}")
                print(f"      Risk Level: {data.get('risk_level')}")
        
        if 'fema_flood' in data_sources:
            fema = data_sources['fema_flood']
            print(f"\n   🌊 FEMA Flood:")
            print(f"      Status: {fema.get('status')}")
        
        # HUD
        if 'hud_data' in data_sources:
            hud = data_sources['hud_data']
            print(f"\n   🏘️  HUD Data:")
            print(f"      Keys: {list(hud.keys())}")
            
            if 'income_limits' in hud:
                il = hud['income_limits']
                print(f"      Income Limits Status: {il.get('status')}")
                if il.get('status') == 'success':
                    data = il.get('data', {})
                    print(f"         Year: {data.get('year')}")
                    income = data.get('income', {})
                    print(f"         80% AMI (2-person): ${income.get('l80_2')}")
            
            if 'fair_market_rent' in hud:
                fmr = hud['fair_market_rent']
                print(f"      FMR Status: {fmr.get('status')}")
                if fmr.get('status') == 'success':
                    data = fmr.get('data', {})
                    print(f"         Year: {data.get('year')}")
                    rent = data.get('rent_by_bedroom', {})
                    print(f"         2BR: ${rent.get('2_bedroom')}")
        
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(check_data())
