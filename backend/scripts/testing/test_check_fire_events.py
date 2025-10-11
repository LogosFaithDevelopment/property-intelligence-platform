"""
Check what fire event data is actually stored in the property
"""

import asyncio
import json

from app.database import AsyncSessionLocal
from app.models.property import Property
from sqlalchemy import select


async def check_fire_events():
    """Check what fire data is stored"""
    
    async with AsyncSessionLocal() as db:
        try:
            # Get property #14
            result = await db.execute(select(Property).where(Property.id == 14))
            property_obj = result.scalar_one_or_none()
            
            if not property_obj:
                print("❌ Property #14 not found")
                return
            
            print("=" * 80)
            print("CHECKING FIRE EVENT DATA - Property #14")
            print("=" * 80)
            print(f"\nProperty: {property_obj.full_address}")
            print(f"County: {property_obj.county}")
            print(f"Coordinates: {property_obj.latitude}, {property_obj.longitude}")
            
            if not property_obj.data_sources:
                print("\n❌ No data_sources found")
                return
            
            # Parse data_sources
            data_sources = json.loads(property_obj.data_sources)
            
            # Navigate to fire data
            flood_risk = data_sources.get("flood_risk", {})
            print(f"\n📊 flood_risk keys: {list(flood_risk.keys())}")
            
            fema_data = flood_risk.get("data", {})
            print(f"📊 fema data keys: {list(fema_data.keys())}")
            
            disaster_history = fema_data.get("disaster_history", {})
            print(f"📊 disaster_history keys: {list(disaster_history.keys())}")
            
            fire_data = disaster_history.get("fire", {})
            print(f"\n🔥 Fire data structure:")
            print(f"   - Keys: {list(fire_data.keys())}")
            print(f"   - Count: {fire_data.get('count', 0)}")
            print(f"   - Has 'events' key: {'events' in fire_data}")
            
            if 'events' in fire_data:
                events = fire_data.get('events', [])
                print(f"   - Events length: {len(events)}")
                if events:
                    print(f"\n📋 First event sample:")
                    first_event = events[0]
                    print(f"   - Keys: {list(first_event.keys())}")
                    print(f"   - Incident type: {first_event.get('incidentType')}")
                    print(f"   - Declaration title: {first_event.get('declarationTitle')}")
                    print(f"   - Designated area: {first_event.get('designatedArea')}")
                    print(f"   - FIPS county code: {first_event.get('fipsCountyCode')}")
            else:
                print(f"   ❌ NO 'events' key found!")
                print(f"   Available keys: {list(fire_data.keys())}")
            
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_fire_events())
