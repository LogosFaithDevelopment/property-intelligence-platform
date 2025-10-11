"""
Check what disaster data is actually stored for Shepherd Church Property #20
"""
import asyncio
import json
from app.database import AsyncSessionLocal
from app.models import Property
from sqlalchemy import select


async def main():
    print("=" * 80)
    print("SHEPHERD CHURCH PROPERTY #20 - DISASTER DATA CHECK")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # Get Property #20
        stmt = select(Property).where(Property.id == 20)
        result = await db.execute(stmt)
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            print("❌ Property #20 not found!")
            return
        
        print(f"\n✅ Property: {property_obj.name}")
        print(f"   Address: {property_obj.full_address}")
        print(f"   County: {property_obj.county}")
        print(f"   State: {property_obj.state}")
        print(f"   Flood Zone: {property_obj.flood_zone}")
        
        # Check data_sources
        if property_obj.data_sources:
            try:
                data_sources = json.loads(property_obj.data_sources)
                
                # Check FEMA data
                print("\n" + "=" * 80)
                print("FEMA FLOOD DATA:")
                print("=" * 80)
                fema_data = data_sources.get('fema_flood', {})
                if fema_data:
                    print(json.dumps(fema_data, indent=2))
                else:
                    print("No FEMA data found")
                
                # Check for disaster declarations
                print("\n" + "=" * 80)
                print("DISASTER DECLARATIONS DATA:")
                print("=" * 80)
                
                # Look for any disaster-related keys
                for key in data_sources.keys():
                    if 'disaster' in key.lower() or 'fema' in key.lower():
                        print(f"\n{key}:")
                        print(json.dumps(data_sources[key], indent=2))
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing data_sources JSON: {e}")
        else:
            print("\n❌ No data_sources found!")


if __name__ == "__main__":
    asyncio.run(main())
