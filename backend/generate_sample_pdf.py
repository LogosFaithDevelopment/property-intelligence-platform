"""
Generate a sample PDF report to demonstrate the enhanced formatting
"""
import asyncio
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, '/app')

from app.database import SyncSessionLocal
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property
from app.services.report_generator import ReportGenerator


async def main():
    """Generate a sample PDF report"""
    db = SyncSessionLocal()
    
    try:
        # Find an assessment with some data
        assessment = db.query(Assessment).filter(Assessment.id == 1).first()
        
        if not assessment:
            print("❌ Assessment #1 not found")
            return
        
        print(f"✓ Found Assessment #{assessment.id}")
        
        # Get property
        property_obj = db.query(Property).filter(Property.id == assessment.property_id).first()
        if not property_obj:
            print("❌ Property not found")
            return
        
        print(f"✓ Found Property #{property_obj.id}: {property_obj.name}")
        
        # Get church
        church = db.query(Church).filter(Church.id == property_obj.church_id).first()
        if not church:
            print("❌ Church not found")
            return
        
        print(f"✓ Found Church #{church.id}: {church.name}")
        
        # Generate PDF
        print("\n🔄 Generating PDF report...")
        report_gen = ReportGenerator(db=db)
        
        pdf_bytes = await report_gen.generate_assessment_report(
            assessment_id=assessment.id,
            include_detailed_analysis=True
        )
        
        # Write to file
        output_path = "/tmp/sample_property_assessment_report.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        pdf_path = output_path
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        print(f"\n✅ PDF generated successfully!")
        print(f"   Location: {pdf_path}")
        print(f"   Size: {file_size:,} bytes")
        
        print("\n📋 To copy to your Desktop, run:")
        print(f"   docker cp property-intelligence-platform-backend-1:{pdf_path} ~/Desktop/")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
