#!/usr/bin/env python3
"""
Script to re-run Assessment #50 with updated IRR calculation logic
Updated per CIO feedback:
- NO LIHTC tax credits
- NO syndication
- OpEx: 30% (down from 42%)
- Unit mix: 20% studios (325sf), 55% 1BD (450sf), 25% 2BD (675sf)
- Construction: 18 months
- Lease-up: 4 months
- Exit: Year 7
- Exit cap: 6%
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_db
from app.services.ai_assessment import AIAssessmentService


async def rerun_assessment():
    """Re-run assessment #50 to get updated IRR without tax credits"""
    
    print("\n" + "="*70)
    print("🔄 RE-RUNNING ASSESSMENT #50 WITH NEW IRR CALCULATION")
    print("="*70 + "\n")
    
    assessment_id = 50
    
    print(f"📋 Assessment ID: {assessment_id}")
    print("🎯 Updated Parameters (CIO Feedback):")
    print("   ❌ NO LIHTC tax credits")
    print("   ❌ NO syndication")
    print("   ✅ OpEx ratio: 30% (down from 42%)")
    print("   ✅ Unit mix: 20% studios, 55% 1BD, 25% 2BD")
    print("   ✅ Construction: 18 months")
    print("   ✅ Lease-up: 4 months")
    print("   ✅ Exit: Year 7")
    print("   ✅ Exit cap: 6%")
    print("\n" + "-"*70 + "\n")
    
    # Get database session
    async for db in get_db():
        try:
            print("🔍 Initializing AI Assessment Service...")
            ai_service = AIAssessmentService(db)
            
            print(f"🚀 Processing assessment {assessment_id}...\n")
            
            # Run the assessment with the new IRR calculation
            results = await ai_service.process_assessment(
                assessment_id=assessment_id,
                use_premium_model=False  # Use GPT-3.5 for speed
            )
            
            print("\n" + "="*70)
            print("✅ ASSESSMENT PROCESSING COMPLETE!")
            print("="*70 + "\n")
            
            # Display key results
            if results and 'financial_projections' in results:
                fp = results['financial_projections']
                
                print("📊 KEY FINANCIAL METRICS:")
                print("-"*70)
                
                # IRR
                irr = fp.get('irr_percent', 'N/A')
                print(f"\n💰 IRR (WITHOUT Tax Credits): {irr}%")
                
                if isinstance(irr, (int, float)) and irr >= 20:
                    print("   ✅ MEETS 20% LOGOS TARGET!")
                else:
                    print("   ⚠️  Below 20% target")
                
                # Units
                units = results.get('unit_capacity', {}).get('feasible_units', 'N/A')
                print(f"\n🏢 Units: {units}")
                print(f"   Unit mix: 20% studios (325sf), 55% 1BD (450sf), 25% 2BD (675sf)")
                print(f"   Average unit size: 481 sqft")
                
                # NOI
                noi = fp.get('net_operating_income', 0)
                print(f"\n💵 Net Operating Income:")
                print(f"   Annual NOI: ${noi:,.0f}")
                print(f"   OpEx ratio: 30% (down from 42%)")
                
                # Equity
                equity = fp.get('equity_investment_30pct', 0)
                print(f"\n💼 Equity Analysis:")
                print(f"   Equity Required (30%): ${equity:,.0f}")
                print(f"   No LIHTC syndication")
                
                print("\n" + "="*70 + "\n")
                
                # Next steps
                print("🎯 NEXT STEPS:")
                print("-"*70)
                print("1. Open Assessment #50 in browser:")
                print("   http://localhost:3000/admin/submissions/50/assessment")
                print("\n2. Verify IRR displays correctly:")
                print(f"   Expected: {irr}%")
                print("\n3. Verify updated parameters:")
                print("   - NO LIHTC credits shown")
                print("   - OpEx: 30%")
                print("   - Units increased (smaller avg size)")
                print("   - Exit: Year 7 (not Year 11)")
                print("\n" + "="*70 + "\n")
            
            else:
                print("⚠️  Results returned but no financial projections found")
                print(f"Results keys: {results.keys() if results else 'None'}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("\nFull error details:")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    print("\n🏗️  Property Intelligence Platform - Assessment Re-run Tool\n")
    
    # Run the assessment
    results = asyncio.run(rerun_assessment())
    
    if results:
        print("✅ Successfully re-ran assessment!")
        sys.exit(0)
    else:
        print("❌ Failed to re-run assessment")
        sys.exit(1)
