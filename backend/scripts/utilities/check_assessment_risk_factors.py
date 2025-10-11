"""
Check disaster data in Assessment #38 risk_factors
"""
import asyncio
import json
from app.database import AsyncSessionLocal
from app.models import Assessment
from sqlalchemy import select


async def main():
    print("=" * 80)
    print("ASSESSMENT #38 - RISK FACTORS DISASTER DATA")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        stmt = select(Assessment).where(Assessment.id == 38)
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            print("❌ Assessment #38 not found!")
            return
        
        print(f"\n✅ Assessment ID: {assessment.id}")
        print(f"   Risk Score: {assessment.risk_score:.1f}/100")
        
        if assessment.risk_factors:
            print("\n" + "=" * 80)
            print("RISK FACTORS JSON:")
            print("=" * 80)
            print(json.dumps(assessment.risk_factors, indent=2))
        else:
            print("\n❌ No risk_factors found!")


if __name__ == "__main__":
    asyncio.run(main())
