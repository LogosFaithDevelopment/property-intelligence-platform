"""
Test PDF Report Generation for Oasis Church
Verifies the updated recommendation logic that prioritizes deal breakers
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SyncSessionLocal
from app.models.assessment import Assessment
from app.services.report_generator import ReportGenerator


async def generate_oasis_report():
    """Generate PDF report for Oasis Church (Assessment #44)"""
    print("\n" + "="*80)
    print("🏛️  TESTING OASIS CHURCH REPORT GENERATION")
    print("="*80 + "\n")
    
    db = SyncSessionLocal()
    
    try:
        # Check if assessment exists
        assessment = db.query(Assessment).filter(Assessment.id == 44).first()
        
        if not assessment:
            print("❌ Assessment #44 (Oasis Church) not found!")
            print("\nPlease run the full test script first:")
            print("   docker-compose exec backend python3 test_oasis_church_full.py")
            return
        
        print(f"✅ Found Assessment #44")
        print(f"   Property ID: {assessment.property_id}")
        print(f"   Overall Score: {assessment.overall_score:.1f}/100")
        print(f"   Financial Score: {assessment.financial_score:.1f}/100")
        
        # Check for deal breaker
        if assessment.financial_projections:
            fin_proj = assessment.financial_projections
            unit_capacity = fin_proj.get('unit_capacity', {})
            feasible_units = unit_capacity.get('feasible_units', 0)
            print(f"   Feasible Units: {feasible_units}")
            
            if feasible_units < 40:
                print(f"\n⚠️  DEAL BREAKER DETECTED: Only {feasible_units} units (requires 40+)")
                print("   Report should show 'NOT RECOMMENDED' despite 73.8 score")
            else:
                print(f"\n✅ NO DEAL BREAKER: {feasible_units} units feasible")
        
        print("\n" + "-"*80)
        print("📄 Generating PDF Report...")
        print("-"*80 + "\n")
        
        # Generate report
        generator = ReportGenerator(db)
        pdf_bytes = await generator.generate_assessment_report(
            assessment_id=44,
            include_detailed_analysis=True
        )
        
        # Save to container
        output_path = "/app/oasis_church_report_44_UPDATED.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF Generated Successfully!")
        print(f"   File Size: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
        print(f"   Saved to: {output_path}")
        
        print("\n" + "="*80)
        print("📋 WHAT TO VERIFY IN THE REPORT:")
        print("="*80)
        print("\n1. ✅ Page 3: 'Grading Analytics & Assessment'")
        print("   - Status box shows: '⚠️ CONDITIONALLY APPROVED' (73.8/100)")
        print("   - Grading breakdown table shows all 5 scores")
        print("\n2. 🎯 Page 3: 'RECOMMENDATION' section (RIGHT AFTER table)")
        print("   - Should show: '✗ NOT RECOMMENDED - CRITICAL DEAL BREAKER PRESENT'")
        print("   - Should state: 'Only 4 units feasible (requires 40+ units minimum)'")
        print("   - Should have RED background (#ffebee)")
        print("\n3. 📋 Page 3: 'KEY DATA DRIVING THIS ASSESSMENT'")
        print("   - Financial: Shows 4 units, cost per unit, revenue, NOI, ROI")
        print("   - Market: Shows FMR, AMI data")
        print("   - Location: Shows address, lot size, zoning")
        print("   - Risk: Shows flood zone A, disaster data")
        print("   - Partnership: Shows Oasis Church details")
        print("\n4. 🚨 Page 3: 'DETAILED ISSUES & ACTION ITEMS'")
        print("   - Deal Breakers section shows:")
        print("     '❌ LOT SIZE INSUFFICIENT FOR MINIMUM UNIT COUNT'")
        print("     - Current: 4 units feasible")
        print("     - Required: 1.05 acres (need 0.81 more acres)")
        print("     - Solutions: Acquire land, partner, or alternative site")
        
        print("\n" + "="*80)
        print("📥 TO COPY FILE TO YOUR DESKTOP:")
        print("="*80)
        print(f"\n   docker cp property-intelligence-platform-backend-1:{output_path} ~/Desktop/")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE - Review PDF to verify recommendation logic!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(generate_oasis_report())
