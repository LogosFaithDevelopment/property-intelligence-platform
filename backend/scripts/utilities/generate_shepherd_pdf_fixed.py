"""
Generate PDF for Shepherd Church Assessment #38 with fixed financial data and pages
"""
import asyncio
from pathlib import Path

from app.database import SyncSessionLocal
from app.services.report_generator import ReportGenerator


def main():
    """Generate PDF for Assessment #38"""
    print("=" * 80)
    print("GENERATING PDF FOR ASSESSMENT #38 (SHEPHERD CHURCH)")
    print("=" * 80)
    
    assessment_id = 38
    
    # Generate PDF
    db = SyncSessionLocal()
    try:
        generator = ReportGenerator(db)
        pdf_bytes = asyncio.run(generator.generate_assessment_report(assessment_id))
        
        if pdf_bytes:
            # Save to /app directory
            pdf_path = Path("/app") / f"shepherd_church_report_fixed_{assessment_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            file_size = len(pdf_bytes)
            print(f"\n✅ PDF Generated Successfully!")
            print(f"   File: {pdf_path}")
            print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            print(f"\n📥 To copy to Desktop, run:")
            print(f"   docker cp property-intelligence-platform-backend-1:/app/shepherd_church_report_fixed_{assessment_id}.pdf ~/Desktop/")
            print(f"\n🎉 Ready for review!\n")
        else:
            print("❌ PDF generation failed!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
