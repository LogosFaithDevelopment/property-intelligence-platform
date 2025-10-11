"""
Script to recalculate IRR for existing assessments
Run this to add IRR data to assessments created before IRR feature was added
"""
import asyncio
import json

from app.database import AsyncSessionLocal
from app.models.assessment import Assessment
from app.services.ai_assessment import AIAssessmentService
from sqlalchemy import select


async def recalculate_irr():
    """Recalculate IRR for all assessments that have financial projections but no IRR"""
    
    async with AsyncSessionLocal() as session:
        # Get all assessments with financial projections
        result = await session.execute(
            select(Assessment)
            .where(Assessment.financial_projections.isnot(None))
        )
        assessments = result.scalars().all()
        
        print(f"Found {len(assessments)} assessments with financial projections")
        
        updated_count = 0
        
        for assessment in assessments:
            # Check if IRR is already calculated
            if assessment.financial_projections:
                revenue_proj = assessment.financial_projections.get("revenue_projections", {})
                
                if revenue_proj.get("irr_percent") is not None:
                    print(f"Assessment {assessment.id}: IRR already calculated ({revenue_proj.get('irr_percent')}%)")
                    continue
                
                # Calculate IRR
                total_cost = revenue_proj.get("total_development_cost", 0)
                noi = revenue_proj.get("net_operating_income", 0)
                
                if total_cost > 0 and noi > 0:
                    # Create service instance
                    service = AIAssessmentService(session)
                    
                    # Calculate IRR
                    irr_analysis = service._calculate_project_irr(
                        total_dev_cost=total_cost,
                        annual_noi=noi
                    )
                    
                    # Update the assessment
                    revenue_proj["irr_analysis"] = irr_analysis
                    revenue_proj["irr_percent"] = irr_analysis.get("irr_percent")
                    revenue_proj["meets_irr_target"] = irr_analysis.get("meets_logos_target", False)
                    revenue_proj["yield_on_cost"] = revenue_proj.get("cap_rate", 0)
                    
                    # Also add to notes if not already there
                    if "IRR calculated" not in str(revenue_proj.get("notes", [])):
                        notes = revenue_proj.get("notes", [])
                        notes.append("IRR calculated over 10-year hold period with 24-month construction")
                        revenue_proj["notes"] = notes
                    
                    # Update the assessment
                    assessment.financial_projections["revenue_projections"] = revenue_proj
                    
                    # Mark as modified
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(assessment, "financial_projections")
                    
                    updated_count += 1
                    
                    irr_percent = irr_analysis.get("irr_percent")
                    if irr_percent:
                        print(f"✅ Assessment {assessment.id}: IRR calculated = {irr_percent:.2f}%")
                    else:
                        print(f"⚠️  Assessment {assessment.id}: IRR calculation returned None")
                else:
                    print(f"⚠️  Assessment {assessment.id}: Missing data (cost={total_cost}, noi={noi})")
        
        # Commit changes
        await session.commit()
        
        print(f"\n✅ Updated {updated_count} assessments with IRR data")

if __name__ == "__main__":
    asyncio.run(recalculate_irr())
