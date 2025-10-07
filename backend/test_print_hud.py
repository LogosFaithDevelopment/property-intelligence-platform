#!/usr/bin/env python3
"""
Print complete HUD data structure
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.models.property import Property
from sqlalchemy import select


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Property).where(Property.id == 9))
        prop = result.scalar_one_or_none()
        
        data = json.loads(prop.data_sources)
        hud = data.get('hud_data', {})
        
        print(json.dumps(hud, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
