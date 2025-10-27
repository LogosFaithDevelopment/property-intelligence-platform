"""Check what columns exist in the churches table"""
import asyncio

from app.database import engine
from sqlalchemy import text


async def check_columns():
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='churches' ORDER BY ordinal_position")
        )
        columns = [row[0] for row in result]
        print("\nColumns in 'churches' table:")
        for col in columns:
            print(f"  - {col}")
        print()


if __name__ == "__main__":
    asyncio.run(check_columns())
