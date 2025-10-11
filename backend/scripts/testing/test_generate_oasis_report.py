"""
Test Script: Generate PDF Report for Oasis Church (Assessment #44)

This tests the complete PDF report generation system with the 
restructured "Grading Analytics & Assessment" page that shows
accurate recommendations (checks deal breakers FIRST).

Expected Result:
- Report shows Grade B (73.8/100)
- Recommendation: "NOT RECOMMENDED - CRITICAL DEAL BREAKER PRESENT"
- Deal Breaker: Only 4 units feasible (requires 40+ units)
"""

import asyncio
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.report_generator import ReportGenerator

# Create sync database session
engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_report():
    """Generate PDF report for Oasis Church Assessment #44"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("🔍 TESTING OASIS CHURCH PDF REPORT GENERATION")
        print("="*70)
        
        assessment_id = 44
        
        # Verify assessment exists
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            print(f"\n❌ Assessment #{assessment_id} not found!")
            return
        
        property_obj = db.query(Property).filter(Property.id == assessment.property_id).first()
        church = db.query(Church).filter(Church.id == property_obj.church_id).first()
        
        print(f"\n📋 Assessment Details:")
        print(f"   ID: {assessment.id}")
        print(f"   Property: {property_obj.name}")
        print(f"   Church: {church.name}")
        print(f"   Overall Score: {assessment.overall_score:.1f}/100")
        print(f"   Financial Score: {assessment.financial_score:.1f}/100")
        
        # Check for deal breakers
        if assessment.financial_projections:
            fin_proj = assessment.financial_projections
            unit_capacity = fin_proj.get('unit_capacity', {})
            feasible_units = unit_capacity.get('feasible_units', 0)
            print(f"   Feasible Units: {feasible_units} units")
            
            if feasible_units < 40:
                print(f"   ⚠️  DEAL BREAKER: Below 40-unit minimum!")
        
        print(f"\n📄 Generating PDF report...")
        
        # Generate report
        generator = ReportGenerator(db)
        pdf_bytes = asyncio.run(generator.generate_assessment_report(
            assessment_id=assessment_id,
            include_detailed_analysis=True
        ))
        
        # Save to container
        output_path = f"/app/oasis_church_report_{assessment_id}_test.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"\n✅ PDF Report Generated Successfully!")
        print(f"📥 PDF saved in container: {output_path}")
        print(f"📊 File size: {len(pdf_bytes):,} bytes")
        
        # Copy to Desktop
        desktop_path = os.path.expanduser(f"~/Desktop/oasis_church_report_{assessment_id}_test.pdf")
        
        print(f"\n📁 To copy to your Desktop, run:")
        print(f"   docker cp property-intelligence-platform-backend-1:{output_path} {desktop_path}")
        
        print(f"\n🔍 What to Check in the Report:")
        print(f"   1. Page 3: 'Grading Analytics & Assessment'")
        print(f"   2. Status box shows: Grade B (73.8/100)")
        print(f"   3. RECOMMENDATION section (right after grading table):")
        print(f"      - Should show: '✗ NOT RECOMMENDED - CRITICAL DEAL BREAKER PRESENT'")
        print(f"      - Should explain: Only 4 units feasible (requires 40+ units)")
        print(f"   4. No conflicting 'CONDITIONALLY APPROVED' recommendation")
        print(f"   5. DETAILED ISSUES section shows comprehensive lot size analysis")
        
        print(f"\n✅ TEST COMPLETE - Review PDF to verify recommendation logic!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    generate_report()
