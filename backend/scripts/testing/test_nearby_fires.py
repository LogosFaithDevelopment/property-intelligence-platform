"""
Debug script to see which fires are being counted as "nearby" for downtown LA
"""

import asyncio
import json

from app.database import AsyncSessionLocal
from app.models.property import Property
from app.services.disaster_distance_filter import DisasterDistanceFilter
from sqlalchemy import select


async def check_nearby_fires():
    """Check which fires are within 15 miles of downtown LA"""
    
    async with AsyncSessionLocal() as db:
        try:
            # Get property #14 (downtown LA)
            result = await db.execute(select(Property).where(Property.id == 14))
            property_obj = result.scalar_one_or_none()
            
            if not property_obj:
                print("❌ Property #14 not found")
                return
            
            print("=" * 80)
            print("CHECKING NEARBY FIRES - Downtown LA Property")
            print("=" * 80)
            print(f"\nProperty: {property_obj.full_address}")
            print(f"County: {property_obj.county}")
            print(f"Coordinates: {property_obj.latitude}, {property_obj.longitude}")
            
            # Get fire data
            data_sources = json.loads(property_obj.data_sources)
            flood_risk = data_sources.get("flood_risk", {})
            fema_data = flood_risk.get("data", {})
            disaster_history = fema_data.get("disaster_history", {})
            fire_data = disaster_history.get("fire", {})
            all_events = fire_data.get('events', [])
            
            print(f"\n📊 Total California Fire Events: {len(all_events)}")
            
            # Apply geographic filtering
            filtered = DisasterDistanceFilter.filter_disasters_by_distance(
                disasters=all_events,
                disaster_type='fire',
                property_lat=property_obj.latitude,
                property_lon=property_obj.longitude,
                property_county=property_obj.county
            )
            
            print(f"\n🔥 NEARBY FIRES (within 15 miles):")
            print(f"   Count: {filtered['direct_count']}")
            
            if filtered['direct_risk']:
                for i, event in enumerate(filtered['direct_risk'], 1):
                    title = event.get('declarationTitle', 'Unknown')
                    area = event.get('designatedArea', 'Unknown')
                    date = event.get('declarationDate', 'Unknown')[:10]
                    distance = event.get('_distance_miles', 'N/A')
                    
                    print(f"\n   {i}. {title}")
                    print(f"      Area: {area}")
                    print(f"      Date: {date}")
                    print(f"      Distance: {distance} miles")
            
            print(f"\n🌐 REGIONAL FIRES (15-35 miles):")
            print(f"   Count: {filtered['regional_count']}")
            
            if filtered['regional_risk']:
                for i, event in enumerate(filtered['regional_risk'][:5], 1):
                    title = event.get('declarationTitle', 'Unknown')
                    area = event.get('designatedArea', 'Unknown')
                    distance = event.get('_distance_miles', 'N/A')
                    print(f"   {i}. {title} in {area} ({distance} miles)")
            
            print(f"\n📍 INFORMATIONAL FIRES (>35 miles):")
            print(f"   Count: {filtered['informational_count']}")
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_nearby_fires())
