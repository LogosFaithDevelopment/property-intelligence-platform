#!/usr/bin/env python3
"""
Generate PDF report with all the latest enhancements:
- Simplified Natural Disaster Risk section
- ATTOM professional property data
- Critical issues analysis
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SyncSessionLocal
from app.models.assessment import Assessment
from app.services.report_generator import ReportGenerator
from sqlalchemy.orm import Session


async def generate_report():
    """Generate PDF report for review"""
    db: Session = SyncSessionLocal()
    
    try:
        # Get the most recent assessment
        assessment = db.query(Assessment).order_by(Assessment.id.desc()).first()
        
        if not assessment:
            print("❌ No assessments found in database")
            return
        
        print(f"✓ Found assessment ID: {assessment.id}")
        print(f"  Property ID: {assessment.property_id}")
        print(f"  Overall Score: {assessment.overall_score:.1f}/100")
        
        # Generate report
        print("\n📄 Generating PDF report...")
        generator = ReportGenerator(db)
        pdf_bytes = await generator.generate_assessment_report(
            assessment_id=assessment.id,
            include_detailed_analysis=True
        )
        
        # Save to /tmp in container (accessible via docker cp)
        output_path = Path("/tmp") / f"property_assessment_{assessment.id}_enhanced.pdf"
        output_path.write_bytes(pdf_bytes)
        
        print(f"\n✅ SUCCESS!")
        print(f"📥 PDF saved in container: {output_path}")
        print(f"📊 File size: {len(pdf_bytes):,} bytes")
        print(f"\n📁 To copy to your Desktop, run:")
        print(f"   docker cp property-intelligence-platform-backend-1:{output_path} ~/Desktop/")
        print(f"\n💡 Open the file to review:")
        print(f"   - Simplified Natural Disaster Risk section")
        print(f"   - ATTOM professional property data")
        print(f"   - Critical issues analysis")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate_report())
