#!/usr/bin/env python3
"""
Test PDF Report Generation
Creates a mock assessment and generates a PDF report
"""

import asyncio
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, '/app')

from app.database import SyncSessionLocal
from app.models.assessment import Assessment, AssessmentStatus
from app.models.church import Church
from app.models.property import Property, PropertyType
from app.services.report_generator import ReportGenerator
from sqlalchemy import select


def create_test_data(db):
    """Create test church, property, and assessment"""
    
    # Create test church
    church = Church(
        name="Test Church for PDF",
        denomination="Baptist",
        street_address="123 Test St",
        city="Test City",
        state="CA",
        zip_code="12345",
        primary_email="test@testchurch.org",
        user_id="test_user_123"
    )
    db.add(church)
    db.flush()
    
    # Create test property
    property_obj = Property(
        street_address="456 Property Ave",
        city="Test City",
        state="CA",
        zip_code="12345",
        property_type=PropertyType.VACANT_LAND,
        lot_size_sqft=10000,
        zoning_description="R-3",
        latitude=34.0522,
        longitude=-118.2437,
        church_id=church.id
    )
    db.add(property_obj)
    db.flush()
    
    # Create test assessment with mock data
    assessment = Assessment(
        church_id=church.id,
        property_id=property_obj.id,
        user_id="test_user_123",
        status=AssessmentStatus.COMPLETED,
        
        # AI Assessment scores
        overall_score=85.5,
        location_score=90.0,
        financial_viability_score=82.0,
        zoning_compliance_score=88.0,
        community_impact_score=85.0,
        risk_assessment_score=80.0,
        
        # Assessment analysis
        location_analysis="Excellent location with high walkability and access to public transit. Strong demographics.",
        financial_analysis="Strong financial viability. Estimated ROI of 8-10% with reasonable development costs.",
        zoning_analysis="Property is zoned for multi-family residential. Permits should be straightforward.",
        community_impact_analysis="Project will provide 24 affordable housing units, addressing local housing shortage.",
        risk_analysis="Low to moderate risk. Main concerns are construction timeline and market volatility.",
        recommendation_summary="Strong Buy - This property represents an excellent investment opportunity.",
        
        # Enrichment data (mock)
        enrichment_data={
            "demographics": {
                "population": 50000,
                "median_income": 75000,
                "median_age": 35
            },
            "market": {
                "median_rent": 2500,
                "vacancy_rate": 3.5,
                "rent_growth": 5.2
            },
            "opportunity_zone": True,
            "flood_zone": False,
            "hud_data": {
                "fair_market_rent_2br": 2400
            }
        },
        
        # Financial projections
        estimated_development_cost=2500000,
        estimated_annual_revenue=350000,
        estimated_roi=8.5,
        
        # Church preferences
        congregation_approval="high",
        leadership_support="strong",
        timeline_readiness="6-12 months",
        preferred_unit_count=24,
        affordability_target=60  # 60% AMI
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    print(f"✅ Created test assessment ID: {assessment.id}")
    print(f"   Church: {church.name}")
    print(f"   Property: {property_obj.address}")
    print(f"   Overall Score: {assessment.overall_score}")
    
    return assessment.id


async def test_pdf_generation():
    """Test generating a PDF report"""
    
    print("\n🚀 Testing PDF Report Generation\n")
    
    # Create sync database session
    db = SyncSessionLocal()
    
    try:
        # Check if we have any completed assessments
        stmt = select(Assessment).where(
            Assessment.status.in_([AssessmentStatus.COMPLETED, AssessmentStatus.REVIEWED, AssessmentStatus.APPROVED])
        ).order_by(Assessment.id.desc()).limit(1)
        result = db.execute(stmt)
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            print("📝 No completed assessments found. Creating test data...")
            assessment_id = create_test_data(db)
        else:
            assessment_id = assessment.id
            print(f"✅ Found existing assessment ID: {assessment_id}")
        
        # Generate PDF
        print(f"\n📄 Generating PDF for assessment {assessment_id}...")
        generator = ReportGenerator(db)
        pdf_bytes = await generator.generate_assessment_report(assessment_id, include_detailed_analysis=True)
        
        # Save PDF to file
        output_path = f"/tmp/test_report_{assessment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF generated successfully!")
        print(f"   Size: {len(pdf_bytes):,} bytes")
        print(f"   Saved to: {output_path}")
        print(f"\n📥 Download the PDF from the container:")
        print(f"   docker cp property-intelligence-platform-backend-1:{output_path} ~/Desktop/test_report.pdf")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_pdf_generation())
