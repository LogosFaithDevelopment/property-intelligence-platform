"""
Apply local database schema to production
"""
import asyncio
# Read production DATABASE_URL from environment
import os

import asyncpg

DATABASE_URL = os.getenv('DATABASE_URL', '')

async def apply_schema():
    # Read the schema file
    with open('/app/../local_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Connect directly with asyncpg
    conn = await asyncpg.connect(DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
    
    try:
        # Execute the schema
        await conn.execute(schema_sql)
        print('Schema applied successfully!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(apply_schema())
