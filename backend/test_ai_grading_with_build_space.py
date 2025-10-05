"""
Test AI Grading Logic with Available Build Space

This script tests the conditional AI grading logic:
1. When available_build_sqft is provided - uses that for scoring
2. When NOT provided - falls back to total lot size
3. Verifies size bonus is calculated correctly
4. Compares scores between different scenarios

Expected Behavior:
- Larger available space = higher score (up to +15 points bonus)
- Size bonus: +1 point per 5,000 sqft above 10,000 minimum (max +15 at 85,000 sqft)
- Financial analysis should reflect which space is being used
"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Church, Property, Assessment
from app.services.ai_assessment import AIAssessmentService
from app.services.property_enrichment import PropertyEnrichmentService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/property_intelligence"

async def test_ai_grading_scenarios():
    """Test three scenarios to validate conditional AI grading logic"""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        
        # === SCENARIO 1: Small Available Space (15,000 sqft) ===
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 1: Small Available Build Space (15,000 sqft)")
        logger.info("="*80)
        
        church1 = Church(
            name="Test Church Small Space",
            address="Test Address 1",
            city="Los Angeles",
            state="CA",
            zip_code="90001"
        )
        db.add(church1)
        await db.flush()
        
        property1 = Property(
            church_id=church1.id,
            address="Test Address 1",
            city="Los Angeles",
            state="CA",
            zip_code="90001",
            lot_size_sqft=100000,  # Total lot is 100K sqft (2.3 acres)
            lot_size_acres=2.30,
            latitude=34.0,
            longitude=-118.0,
            has_water=True,
            has_sewer=True
        )
        db.add(property1)
        await db.flush()
        
        assessment1 = Assessment(
            property_id=property1.id,
            assessment_type="initial",
            available_build_sqft=15000,  # Church only wants to use 15K sqft
            available_build_acres=0.34,
            build_area_notes="Small corner of parking lot"
        )
        db.add(assessment1)
        await db.flush()
        
        # Run AI assessment
        ai_service = AIAssessmentService(db)
        result1 = await ai_service.run_assessment(property1, church1, assessment1)
        
        logger.info(f"\n✅ SCENARIO 1 RESULTS:")
        logger.info(f"   Total Lot Size: {property1.lot_size_sqft:,} sqft ({property1.lot_size_acres} acres)")
        logger.info(f"   Available Build Space: {assessment1.available_build_sqft:,} sqft")
        logger.info(f"   AI Score: {result1['scores']['overall_score']}/100")
        logger.info(f"   Grade: {result1['grade']}")
        
        financial = result1['detailed_results']['financial']
        logger.info(f"   Using Available Space: {financial.get('using_available_space')}")
        logger.info(f"   Lot Size Used: {financial.get('lot_size_sqft'):,} sqft")
        logger.info(f"   Feasible Units: {financial.get('feasible_units')}")
        
        # === SCENARIO 2: Large Available Space (50,000 sqft) ===
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 2: Large Available Build Space (50,000 sqft)")
        logger.info("="*80)
        
        church2 = Church(
            name="Test Church Large Space",
            address="Test Address 2",
            city="Los Angeles",
            state="CA",
            zip_code="90002"
        )
        db.add(church2)
        await db.flush()
        
        property2 = Property(
            church_id=church2.id,
            address="Test Address 2",
            city="Los Angeles",
            state="CA",
            zip_code="90002",
            lot_size_sqft=200000,  # Total lot is 200K sqft (4.6 acres)
            lot_size_acres=4.59,
            latitude=34.0,
            longitude=-118.0,
            has_water=True,
            has_sewer=True
        )
        db.add(property2)
        await db.flush()
        
        assessment2 = Assessment(
            property_id=property2.id,
            assessment_type="initial",
            available_build_sqft=50000,  # Church willing to use 50K sqft
            available_build_acres=1.15,
            build_area_notes="Large section of property available for development"
        )
        db.add(assessment2)
        await db.flush()
        
        # Run AI assessment
        result2 = await ai_service.run_assessment(property2, church2, assessment2)
        
        logger.info(f"\n✅ SCENARIO 2 RESULTS:")
        logger.info(f"   Total Lot Size: {property2.lot_size_sqft:,} sqft ({property2.lot_size_acres} acres)")
        logger.info(f"   Available Build Space: {assessment2.available_build_sqft:,} sqft")
        logger.info(f"   AI Score: {result2['scores']['overall_score']}/100")
        logger.info(f"   Grade: {result2['grade']}")
        
        financial2 = result2['detailed_results']['financial']
        logger.info(f"   Using Available Space: {financial2.get('using_available_space')}")
        logger.info(f"   Lot Size Used: {financial2.get('lot_size_sqft'):,} sqft")
        logger.info(f"   Feasible Units: {financial2.get('feasible_units')}")
        
        # === SCENARIO 3: No Available Space Specified (uses total lot) ===
        logger.info("\n" + "="*80)
        logger.info("SCENARIO 3: No Available Build Space (uses total lot size)")
        logger.info("="*80)
        
        church3 = Church(
            name="Test Church No Space",
            address="Test Address 3",
            city="Los Angeles",
            state="CA",
            zip_code="90003"
        )
        db.add(church3)
        await db.flush()
        
        property3 = Property(
            church_id=church3.id,
            address="Test Address 3",
            city="Los Angeles",
            state="CA",
            zip_code="90003",
            lot_size_sqft=150000,  # Total lot is 150K sqft (3.4 acres)
            lot_size_acres=3.44,
            latitude=34.0,
            longitude=-118.0,
            has_water=True,
            has_sewer=True
        )
        db.add(property3)
        await db.flush()
        
        assessment3 = Assessment(
            property_id=property3.id,
            assessment_type="initial"
            # No available_build_sqft specified - should use total lot
        )
        db.add(assessment3)
        await db.flush()
        
        # Run AI assessment
        result3 = await ai_service.run_assessment(property3, church3, assessment3)
        
        logger.info(f"\n✅ SCENARIO 3 RESULTS:")
        logger.info(f"   Total Lot Size: {property3.lot_size_sqft:,} sqft ({property3.lot_size_acres} acres)")
        logger.info(f"   Available Build Space: Not specified")
        logger.info(f"   AI Score: {result3['scores']['overall_score']}/100")
        logger.info(f"   Grade: {result3['grade']}")
        
        financial3 = result3['detailed_results']['financial']
        logger.info(f"   Using Available Space: {financial3.get('using_available_space')}")
        logger.info(f"   Lot Size Used: {financial3.get('lot_size_sqft'):,} sqft")
        logger.info(f"   Feasible Units: {financial3.get('feasible_units')}")
        
        # === COMPARISON SUMMARY ===
        logger.info("\n" + "="*80)
        logger.info("COMPARISON SUMMARY")
        logger.info("="*80)
        
        logger.info(f"\nScenario 1 (15K sqft available):")
        logger.info(f"  - Score: {result1['scores']['overall_score']}/100")
        logger.info(f"  - Units: {financial['feasible_units']}")
        logger.info(f"  - Size Bonus: {(result1['scores']['overall_score'] - 75):.1f} points")
        
        logger.info(f"\nScenario 2 (50K sqft available):")
        logger.info(f"  - Score: {result2['scores']['overall_score']}/100")
        logger.info(f"  - Units: {financial2['feasible_units']}")
        logger.info(f"  - Size Bonus: {(result2['scores']['overall_score'] - 75):.1f} points")
        
        logger.info(f"\nScenario 3 (150K sqft total lot):")
        logger.info(f"  - Score: {result3['scores']['overall_score']}/100")
        logger.info(f"  - Units: {financial3['feasible_units']}")
        logger.info(f"  - Size Bonus: {(result3['scores']['overall_score'] - 75):.1f} points")
        
        # Validate expected behavior
        logger.info("\n" + "="*80)
        logger.info("VALIDATION CHECKS")
        logger.info("="*80)
        
        # Check 1: Scenario 2 should score higher than Scenario 1 (larger space)
        if result2['scores']['overall_score'] > result1['scores']['overall_score']:
            logger.info("✅ PASS: Larger available space (50K) scored higher than smaller space (15K)")
        else:
            logger.warning("❌ FAIL: Larger space should score higher!")
        
        # Check 2: Scenario 3 should score highest (uses full 150K sqft)
        if result3['scores']['overall_score'] > result2['scores']['overall_score']:
            logger.info("✅ PASS: Full lot size (150K) scored higher than partial space (50K)")
        else:
            logger.warning("⚠️  NOTE: Full lot didn't score highest - may be due to unit count penalties")
        
        # Check 3: Verify using_available_space flag is correct
        if financial['using_available_space'] == True and financial2['using_available_space'] == True and financial3['using_available_space'] == False:
            logger.info("✅ PASS: using_available_space flag is correctly set for all scenarios")
        else:
            logger.warning("❌ FAIL: using_available_space flag is incorrect!")
        
        # Check 4: Verify lot sizes used in calculations
        if financial['lot_size_sqft'] == 15000 and financial2['lot_size_sqft'] == 50000 and financial3['lot_size_sqft'] == 150000:
            logger.info("✅ PASS: Correct lot sizes used in financial calculations")
        else:
            logger.warning("❌ FAIL: Incorrect lot sizes in calculations!")
        
        # Clean up test data
        await db.rollback()
        
        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETE")
        logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(test_ai_grading_scenarios())
