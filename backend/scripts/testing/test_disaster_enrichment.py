"""
Test comprehensive natural disaster enrichment
"""

import asyncio
import json

from app.database import AsyncSessionLocal
from app.models.property import Property
from app.services.property_enrichment import PropertyEnrichmentService
from sqlalchemy import select


async def main():
    async with AsyncSessionLocal() as db:
        # Get property #14
        result = await db.execute(select(Property).where(Property.id == 14))
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print("Property #14 not found!")
            return
        
        print(f"Property: {property_obj.full_address}")
        print("="*80)
        
        # Re-enrich with force_refresh to get new disaster data
        service = PropertyEnrichmentService(db)
        enrichment_result = await service.enrich_property(
            property_id=14,
            force_refresh=True
        )
        
        print("\n✅ Enrichment Complete!")
        print(f"Status: {enrichment_result.get('status', 'completed')}")
        
        # Check flood/disaster data
        flood_result = enrichment_result.get('results', {}).get('flood_risk', {})
        if flood_result.get('status') == 'success':
            flood_data = flood_result.get('data', {})
            disaster_history = flood_data.get('disaster_history', {})
            
            print("\n📊 Natural Disaster History (2004-present):")
            print(f"  State: {disaster_history.get('state_code', 'N/A')}")
            print(f"  Total Disasters: {disaster_history.get('total_disasters', 0)}")
            print()
            print(f"  🌊 Flood: {disaster_history.get('flood', {}).get('count', 0)} events")
            print(f"  🔥 Fire: {disaster_history.get('fire', {}).get('count', 0)} events")
            print(f"  🌪️  Tornado: {disaster_history.get('tornado', {}).get('count', 0)} events")
            print(f"  🌀 Hurricane: {disaster_history.get('hurricane', {}).get('count', 0)} events")
            print(f"  🏚️  Earthquake: {disaster_history.get('earthquake', {}).get('count', 0)} events")
            
            # Show recent events
            for disaster_type in ['flood', 'fire', 'tornado', 'hurricane', 'earthquake']:
                events = disaster_history.get(disaster_type, {}).get('recent_events', [])
                if events:
                    print(f"\n  Recent {disaster_type.upper()} events:")
                    for event in events[:2]:  # Show top 2
                        print(f"    - {event.get('declarationDate', 'N/A')}: {event.get('declarationTitle', 'N/A')}")
        else:
            print(f"\n⚠️  Flood risk status: {flood_result.get('status')}")
            print(f"Error: {flood_result.get('error', 'Unknown')}")
        
        # Show updated property data_sources
        await db.refresh(property_obj)
        if property_obj.data_sources:
            data_sources = json.loads(property_obj.data_sources) if isinstance(property_obj.data_sources, str) else property_obj.data_sources
            flood_risk_data = data_sources.get('flood_risk', {})
            if flood_risk_data:
                print("\n✅ Property data_sources updated with disaster data!")

if __name__ == "__main__":
    asyncio.run(main())
