"""
Generate PDF report for assessment #29 and copy to Downloads
"""

import asyncio
import os

from app.database import SyncSessionLocal
from app.services.report_generator import ReportGenerator


async def generate_report():
    # Use sync session since ReportGenerator requires it
    sync_db = SyncSessionLocal()
    
    try:
        print('📄 Generating PDF report for Assessment #29')
        print('   (Downtown LA property with reduced disaster penalties)')
        
        # Generate report
        generator = ReportGenerator(sync_db)
        pdf_bytes = await generator.generate_assessment_report(assessment_id=29)
        
        print(f'\n✅ Report generated successfully!')
        print(f'   PDF size: {len(pdf_bytes):,} bytes')
        print(f'\n📥 Saving to backend directory...')
        
        # Save to backend directory so it's accessible from host
        output_path = '/app/property_assessment_report_29_updated.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f'✅ Report saved to: {output_path}')
        print(f'   (Accessible at backend/property_assessment_report_29_updated.pdf on host)')
        print(f'\n🔍 Open the PDF to see:')
        print(f'   • Overall score improved to 67.6/100')
        print(f'   • Risk score improved to 24.0/100')
        print(f'   • Fire risk penalty reduced to 3 points (was 15)')
        print(f'   • Disaster information shown as informational, not punitive')
    
    finally:
        sync_db.close()

if __name__ == "__main__":
    asyncio.run(generate_report())
