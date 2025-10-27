#!/usr/bin/env python3
"""
Test script to verify Assessment model works with production database
Run this after deployment to verify no column errors
"""
from app.database import SyncSessionLocal
from app.models.assessment import Assessment
from app.models.church import Church
from app.models.property import Property


def test_assessment_loading():
    """Test that Assessment model can load from database"""
    db = SyncSessionLocal()
    try:
        # Try to load assessment 4
        assessment = db.query(Assessment).filter(Assessment.id == 4).first()
        
        if not assessment:
            print("❌ Assessment 4 not found in database")
            return False
        
        print("✅ Assessment loaded successfully")
        print(f"   - ID: {assessment.id}")
        print(f"   - Overall Score: {assessment.overall_score}")
        print(f"   - Existing Debt: {assessment.existing_debt_amount}")
        print(f"   - Special Requirements: {assessment.special_requirements}")
        print(f"   - Property Improvement Needs: {assessment.property_improvement_needs}")
        print(f"   - Capital Financing Need: {assessment.capital_financing_need}")
        
        # Test loading related objects
        property_obj = db.query(Property).filter(Property.id == assessment.property_id).first()
        church = db.query(Church).filter(Church.id == assessment.church_id).first()
        
        print(f"\n✅ Property loaded: {property_obj.street_address if property_obj else 'Not found'}")
        print(f"✅ Church loaded: {church.name if church else 'Not found'}")
        
        # Test PDF generator can access the data
        if assessment and property_obj and church:
            print("\n✅ All objects loaded - ready for PDF generation")
            return True
        else:
            print("\n❌ Some objects missing")
            return False
            
    except Exception as e:
        print(f"\n❌ Error loading assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_assessment_loading()
    exit(0 if success else 1)
