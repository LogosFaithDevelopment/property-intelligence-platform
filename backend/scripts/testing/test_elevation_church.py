"""
Test script for Elevation Church - Complete flow with PDF generation
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from app.database import AsyncSessionLocal
from app.models import Assessment, Church, Property
from app.services.ai_assessment import AIAssessmentService
from app.services.report_generator import ReportGenerator
from sqlalchemy import select


async def main():
    """Complete test flow for Elevation Church"""
    print("=" * 80)
    print("ELEVATION CHURCH - COMPLETE TEST FLOW")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Get Church and Property
            print("\n📍 Step 1: Loading Church and Property...")
            
            church_stmt = select(Church).where(Church.id == 19)
            church_result = await db.execute(church_stmt)
            church = church_result.scalar_one_or_none()
            
            if not church:
                print("❌ Church ID 19 not found!")
                return
            
            print(f"✅ Church: {church.name}")
            print(f"   Location: {church.city}, {church.state}")
            print(f"   Congregation: {church.congregation_size:,}")
            
            property_stmt = select(Property).where(Property.id == 16)
            property_result = await db.execute(property_stmt)
            property_obj = property_result.scalar_one_or_none()
            
            if not property_obj:
                print("❌ Property ID 16 not found!")
                return
            
            print(f"\n✅ Property: {property_obj.name}")
            print(f"   Address: {property_obj.full_address}")
            print(f"   Lot Size: {property_obj.lot_size_acres} acres")
            
            # 2. Create Assessment
            print("\n📍 Step 2: Creating Assessment...")
            
            assessment = Assessment(
                church_id=church.id,
                property_id=property_obj.id,
                congregation_approval=True,
                leadership_support="unanimous",
                timeline_readiness="ready_now",
                preferred_unit_count=60,
                affordability_target="60_ami",
                priority="high",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(assessment)
            await db.commit()
            await db.refresh(assessment)
            
            print(f"✅ Assessment Created: ID {assessment.id}")
            print(f"   Status: {assessment.status.value}")
            print(f"   Priority: {assessment.priority.value}")
            
            # 3. Process Assessment with AI
            print("\n📍 Step 3: Processing Assessment with AI...")
            print("   (This takes 15-20 seconds...)")
            
            ai_service = AIAssessmentService(db)
            result = await ai_service.process_assessment(assessment.id)
            
            if result["status"] == "completed":
                print(f"\n✅ AI Processing Complete!")
                print(f"   Overall Score: {result['overall_score']:.1f}/100")
                print(f"   Grade: {result.get('grade', 'N/A')}")
                print(f"   Duration: {result.get('processing_time_seconds', 'N/A')}s")
                
                print(f"\n📊 Score Breakdown:")
                scores = result.get('scores', {})
                print(f"   Financial: {scores.get('financial_score', 0):.1f}/100")
                print(f"   Location: {scores.get('location_score', 0):.1f}/100")
                print(f"   Market: {scores.get('market_score', 0):.1f}/100")
                print(f"   Partnership: {scores.get('partnership_score', 0):.1f}/100")
                print(f"   Risk: {scores.get('risk_score', 0):.1f}/100")
            else:
                print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                return
            
            # 4. Generate PDF Report
            print("\n📍 Step 4: Generating PDF Report...")
            print("   (This takes 10-15 seconds...)")
            
            # Reload assessment with all relationships
            assessment_stmt = select(Assessment).where(Assessment.id == assessment.id)
            assessment_result = await db.execute(assessment_stmt)
            assessment = assessment_result.scalar_one()
            
            # Generate report (using sync session)
            from app.database import SyncSessionLocal
            sync_db = SyncSessionLocal()
            try:
                generator = ReportGenerator(sync_db)
                pdf_bytes = await generator.generate_assessment_report(assessment.id)
            finally:
                sync_db.close()
            
            if pdf_bytes:
                # Save PDF to Desktop
                desktop_path = Path.home() / "Desktop" / f"elevation_church_report_{assessment.id}.pdf"
                with open(desktop_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                file_size = len(pdf_bytes)
                print(f"\n✅ PDF Report Generated!")
                print(f"   File: {desktop_path}")
                print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
                print(f"   ✅ Saved to Desktop")
            else:
                print(f"❌ PDF generation failed!")
                return
            
            # 5. Summary
            print("\n" + "=" * 80)
            print("✅ SUCCESS - COMPLETE TEST FLOW FINISHED")
            print("=" * 80)
            print(f"\n📋 Summary:")
            print(f"   Church: {church.name}")
            print(f"   Property: {property_obj.full_address}")
            print(f"   Assessment ID: {assessment.id}")
            print(f"   Score: {assessment.overall_score:.1f}/100 ({assessment.score_grade})")
            print(f"   Report: ~/Desktop/elevation_church_report_{assessment.id}.pdf")
            
            # Data Sources
            print(f"\n📡 Data Sources Used:")
            if property_obj.data_sources:
                import json
                sources = json.loads(property_obj.data_sources)
                for source_type, source_data in sources.items():
                    if isinstance(source_data, dict) and source_data.get('success'):
                        print(f"   ✅ {source_type}")
            
            print(f"\n🎉 Ready for review!\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
