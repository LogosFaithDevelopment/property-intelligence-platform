#!/usr/bin/env python3
"""
Test Enrichment Speed & Data Quality
Verifies that enrichment is fast and returns all data
"""

import asyncio
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, get_db
from app.models.property import Property
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy.orm import Session


async def test_enrichment():
    """Test enrichment speed and data completeness"""
    
    print("\n" + "="*80)
    print("🧪 ENRICHMENT SPEED & DATA QUALITY TEST")
    print("="*80)
    
    # Get database session
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Find a property to test with
    property_obj = db.query(Property).order_by(Property.id.desc()).first()
    
    if not property_obj:
        print("❌ No properties found in database")
        return
    
    print(f"\n📍 Testing with Property: {property_obj.name}")
    print(f"   Location: {property_obj.city}, {property_obj.state} {property_obj.zip_code}")
    print(f"   Property ID: {property_obj.id}")
    
    # Check current data status
    print(f"\n📊 Current Data Status:")
    data_sources = property_obj.data_sources or {}
    print(f"   Census: {'✅' if data_sources.get('census_demographics') else '❌'}")
    print(f"   FEMA: {'✅' if data_sources.get('fema_flood') else '❌'}")
    print(f"   HUD Income Limits: {'✅' if data_sources.get('hud_data', {}).get('income_limits') else '❌'}")
    print(f"   HUD FMR: {'✅' if data_sources.get('hud_data', {}).get('fair_market_rent') else '❌'}")
    print(f"   HUD Crosswalk: {'✅' if data_sources.get('hud_usps_crosswalk') else '❌'}")
    
    # Test enrichment speed
    print(f"\n⏱️  Starting Enrichment (with parallel API calls)...")
    start_time = time.time()
    
    try:
        service = PropertyEnrichmentService(db)
        await service.enrich_property(property_obj.id)
        
        elapsed = time.time() - start_time
        
        # Refresh property data
        db.refresh(property_obj)
        data_sources = property_obj.data_sources or {}
        
        print(f"\n✅ Enrichment Complete!")
        print(f"   ⚡ Time: {elapsed:.1f} seconds")
        
        # Check what data we got
        print(f"\n📊 Enrichment Results:")
        
        # Census
        census_data = data_sources.get('census_demographics', {})
        if census_data and census_data.get('status') == 'success':
            census_result = census_data.get('data', {})
            print(f"   ✅ Census Demographics:")
            print(f"      - Poverty Rate: {census_result.get('poverty_rate', 'N/A')}")
            print(f"      - Renter %: {census_result.get('renter_percentage', 'N/A')}")
            print(f"      - Median Income: ${census_result.get('median_income', 'N/A'):,}" if census_result.get('median_income') else "      - Median Income: N/A")
        else:
            error = census_data.get('error', 'No data')
            print(f"   ❌ Census Demographics: {error}")
        
        # FEMA
        fema_data = data_sources.get('fema_flood', {})
        if fema_data and fema_data.get('status') == 'success':
            fema_result = fema_data.get('data', {})
            print(f"   ✅ FEMA Flood Risk:")
            print(f"      - Flood Zone: {fema_result.get('flood_zone', 'N/A')}")
            print(f"      - Risk Level: {fema_result.get('risk_level', 'N/A')}")
        else:
            error = fema_data.get('error', 'No data')
            print(f"   ⚠️  FEMA Flood Risk: {error}")
        
        # HUD Income Limits
        hud_data = data_sources.get('hud_data', {})
        income_limits = hud_data.get('income_limits', {})
        if income_limits and income_limits.get('status') == 'success':
            il_data = income_limits.get('data', {})
            print(f"   ✅ HUD Income Limits:")
            print(f"      - Year: {il_data.get('year', 'N/A')}")
            print(f"      - Area: {il_data.get('area_name', 'N/A')}")
            print(f"      - Median: ${il_data.get('median', 'N/A'):,}" if il_data.get('median') else "      - Median: N/A")
            ami_data = il_data.get('income', {})
            if ami_data:
                print(f"      - 80% AMI (2-person): ${ami_data.get('l80_2', 'N/A'):,}" if ami_data.get('l80_2') else "      - 80% AMI (2-person): N/A")
        else:
            error = income_limits.get('error', 'No data')
            print(f"   ❌ HUD Income Limits: {error}")
        
        # HUD Fair Market Rent
        fmr = hud_data.get('fair_market_rent', {})
        if fmr and fmr.get('status') == 'success':
            fmr_data = fmr.get('data', {})
            print(f"   ✅ HUD Fair Market Rent:")
            print(f"      - Year: {fmr_data.get('year', 'N/A')}")
            print(f"      - 2BR FMR: ${fmr_data.get('rent_by_bedroom', {}).get('2_bedroom', 'N/A'):,}" if fmr_data.get('rent_by_bedroom', {}).get('2_bedroom') else "      - 2BR FMR: N/A")
        else:
            error = fmr.get('error', 'No data')
            print(f"   ❌ HUD Fair Market Rent: {error}")
        
        # HUD USPS Crosswalk
        crosswalk = data_sources.get('hud_usps_crosswalk', {})
        if crosswalk and crosswalk.get('status') == 'success':
            print(f"   ✅ HUD USPS Crosswalk")
        else:
            error = crosswalk.get('error', 'No data')
            print(f"   ⚠️  HUD USPS Crosswalk: {error}")
        
        # Speed assessment
        print(f"\n🚀 Performance:")
        if elapsed < 15:
            print(f"   ✅ EXCELLENT - {elapsed:.1f}s (target: <15s)")
        elif elapsed < 30:
            print(f"   ✅ GOOD - {elapsed:.1f}s (target: <30s)")
        elif elapsed < 60:
            print(f"   ⚠️  SLOW - {elapsed:.1f}s (should be <30s)")
        else:
            print(f"   ❌ TOO SLOW - {elapsed:.1f}s (sequential calls detected?)")
        
        print("\n" + "="*80)
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Enrichment Failed after {elapsed:.1f}s")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enrichment())
