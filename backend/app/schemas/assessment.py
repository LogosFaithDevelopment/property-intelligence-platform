"""
Assessment Pydantic Schemas
Request/response schemas for property assessments
"""

from datetime import datetime
from typing import Any, Dict, Optional

from app.models.assessment import AssessmentPriority, AssessmentStatus
from app.schemas.base import BaseSchema, TimestampMixin, UUIDMixin
from pydantic import Field, validator


class AssessmentBase(BaseSchema):
    """Base assessment schema with common fields"""
    
    # Church Readiness Information
    congregation_approval: Optional[bool] = Field(None, description="Has congregation voted?")
    leadership_support: Optional[str] = Field(None, max_length=50, description="unanimous, majority, mixed")
    timeline_readiness: Optional[str] = Field(None, max_length=50, description="ready_now, 6_months, 1_year")
    
    # Development Preferences
    preferred_unit_count: Optional[int] = Field(None, ge=1, le=1000, description="Desired number of units")
    preferred_unit_types: Optional[str] = Field(None, description="JSON: studio, 1br, 2br, 3br")
    affordability_target: Optional[str] = Field(None, max_length=50, description="30_ami, 60_ami, 80_ami")
    
    # Partnership Terms
    revenue_sharing_preference: Optional[str] = Field(None, max_length=50)
    development_involvement_level: Optional[str] = Field(None, max_length=50)
    special_requirements: Optional[str] = Field(None, description="Special needs or constraints")


class AssessmentCreate(AssessmentBase):
    """Schema for creating a new assessment"""
    
    church_id: int = Field(..., description="Church ID")
    property_id: int = Field(..., description="Property ID to assess")
    priority: Optional[AssessmentPriority] = Field(
        default=AssessmentPriority.MEDIUM,
        description="Assessment priority level"
    )


class AssessmentUpdate(BaseSchema):
    """Schema for updating assessment information"""
    
    status: Optional[AssessmentStatus] = None
    priority: Optional[AssessmentPriority] = None
    
    congregation_approval: Optional[bool] = None
    leadership_support: Optional[str] = Field(None, max_length=50)
    timeline_readiness: Optional[str] = Field(None, max_length=50)
    
    preferred_unit_count: Optional[int] = Field(None, ge=1, le=1000)
    preferred_unit_types: Optional[str] = None
    affordability_target: Optional[str] = Field(None, max_length=50)
    
    revenue_sharing_preference: Optional[str] = Field(None, max_length=50)
    development_involvement_level: Optional[str] = Field(None, max_length=50)
    special_requirements: Optional[str] = None
    
    reviewer_notes: Optional[str] = None


class AssessmentScores(BaseSchema):
    """Assessment scoring breakdown"""
    
    overall_score: Optional[float] = Field(None, ge=0, le=100, description="Overall assessment score")
    location_score: Optional[float] = Field(None, ge=0, le=100, description="Location quality score")
    market_score: Optional[float] = Field(None, ge=0, le=100, description="Market demand score")
    financial_score: Optional[float] = Field(None, ge=0, le=100, description="Financial viability score")
    partnership_score: Optional[float] = Field(None, ge=0, le=100, description="Partnership fit score")
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="Risk assessment score")


class LogosFinancialMetrics(BaseSchema):
    """Logos-specific financial metrics from enhanced scoring"""
    
    # Lot Size Validation
    lot_size_sqft: Optional[float] = Field(None, description="Lot size in square feet")
    lot_size_acres: Optional[float] = Field(None, description="Lot size in acres")
    meets_minimum: Optional[bool] = Field(None, description="Meets 10,000 sq ft minimum requirement")
    disqualified: Optional[bool] = Field(None, description="Property disqualified (below minimum)")
    disqualification_reason: Optional[str] = Field(None, description="Reason for disqualification")
    
    # Unit Capacity Analysis
    feasible_units: Optional[int] = Field(None, description="Calculated feasible unit count")
    within_target_range: Optional[bool] = Field(None, description="Within 40-140 unit target range")
    developable_acres: Optional[float] = Field(None, description="Developable acres (after setbacks)")
    units_per_acre_assumed: Optional[int] = Field(None, description="Density assumption (units/acre)")
    
    # Cost Per Unit Analysis
    cost_per_unit: Optional[float] = Field(None, description="Estimated cost per unit")
    cost_per_unit_formatted: Optional[str] = Field(None, description="Formatted cost per unit")
    target_cost_per_unit: Optional[int] = Field(None, description="Target cost per unit ($325K)")
    under_target: Optional[bool] = Field(None, description="Cost per unit under target")
    
    # Cost Breakdown
    building_construction_cost: Optional[float] = Field(None, description="Building construction cost")
    site_work_cost: Optional[float] = Field(None, description="Site work cost")
    parking_cost: Optional[float] = Field(None, description="Parking cost")
    utilities_hookup_cost: Optional[float] = Field(None, description="Utilities hookup cost")
    soft_costs: Optional[float] = Field(None, description="Soft costs (architecture, engineering, etc.)")
    financing_costs: Optional[float] = Field(None, description="Financing costs during construction")
    developer_fee: Optional[float] = Field(None, description="Developer fee")
    
    # Project Totals
    estimated_development_cost: Optional[float] = Field(None, description="Total estimated development cost")
    estimated_development_cost_formatted: Optional[str] = Field(None, description="Formatted total cost")


class AssessmentResponse(AssessmentBase, TimestampMixin, UUIDMixin):
    """Full assessment response with all data"""
    
    id: int
    church_id: int
    property_id: int
    status: AssessmentStatus
    priority: AssessmentPriority
    
    # Scores
    overall_score: Optional[float] = None
    location_score: Optional[float] = None
    market_score: Optional[float] = None
    financial_score: Optional[float] = None
    partnership_score: Optional[float] = None
    risk_score: Optional[float] = None
    
    # Analysis Results (JSON)
    market_analysis: Optional[Dict[str, Any]] = None
    financial_projections: Optional[Dict[str, Any]] = None
    risk_factors: Optional[Dict[str, Any]] = None
    comparable_projects: Optional[Dict[str, Any]] = None
    
    # Processing Metadata
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_duration_seconds: Optional[int] = None
    
    # Review Information
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    
    # Report Status
    report_generated: bool = False
    report_generated_at: Optional[datetime] = None
    
    # Computed Properties
    is_high_opportunity: bool = Field(False, description="Score >= 75")
    is_completed: bool = Field(False, description="Assessment is completed")
    score_grade: str = Field("N/A", description="Letter grade (A+, A, B, etc.)")
    
    class Config:
        from_attributes = True
    
    @property
    def logos_metrics(self) -> Optional[LogosFinancialMetrics]:
        """
        Extract Logos-specific metrics from financial_projections JSON
        Returns structured data for easier frontend consumption
        """
        if not self.financial_projections:
            return None
        
        fp = self.financial_projections
        
        # Extract cost breakdown if available
        cost_breakdown = fp.get("cost_breakdown", {})
        
        return LogosFinancialMetrics(
            # Lot Size Validation
            lot_size_sqft=fp.get("lot_size_sqft"),
            lot_size_acres=fp.get("lot_size_acres"),
            meets_minimum=fp.get("meets_minimum"),
            disqualified=fp.get("disqualified", False),
            disqualification_reason=fp.get("disqualification_reason"),
            
            # Unit Capacity
            feasible_units=fp.get("feasible_units"),
            within_target_range=fp.get("within_target_range"),
            developable_acres=fp.get("unit_capacity", {}).get("developable_acres"),
            units_per_acre_assumed=fp.get("unit_capacity", {}).get("units_per_acre_assumed"),
            
            # Cost Per Unit
            cost_per_unit=fp.get("cost_per_unit"),
            cost_per_unit_formatted=fp.get("cost_per_unit_formatted"),
            target_cost_per_unit=fp.get("target_cost_per_unit"),
            under_target=fp.get("under_target"),
            
            # Cost Breakdown
            building_construction_cost=cost_breakdown.get("building_construction"),
            site_work_cost=cost_breakdown.get("site_work"),
            parking_cost=cost_breakdown.get("parking"),
            utilities_hookup_cost=cost_breakdown.get("utilities_hookup"),
            soft_costs=cost_breakdown.get("soft_costs"),
            financing_costs=cost_breakdown.get("financing_costs"),
            developer_fee=cost_breakdown.get("developer_fee"),
            
            # Project Totals
            estimated_development_cost=fp.get("estimated_development_cost"),
            estimated_development_cost_formatted=fp.get("estimated_development_cost_formatted")
        )
    
    @property
    def logos_compliance_summary(self) -> Dict[str, Any]:
        """
        Quick summary of Logos Faith Development compliance
        Returns pass/fail status for key criteria
        """
        if not self.financial_projections:
            return {
                "status": "not_assessed",
                "message": "Assessment not yet processed"
            }
        
        fp = self.financial_projections
        
        # Check if disqualified
        if fp.get("disqualified", False):
            return {
                "status": "disqualified",
                "message": fp.get("disqualification_reason", "Property does not meet minimum requirements"),
                "meets_criteria": False
            }
        
        # Evaluate each criterion
        criteria = {
            "minimum_lot_size": {
                "passed": fp.get("meets_minimum", False),
                "requirement": "10,000 sq ft minimum",
                "actual": fp.get("lot_size_sqft"),
                "status": "✅ Pass" if fp.get("meets_minimum") else "❌ Fail"
            },
            "unit_capacity": {
                "passed": fp.get("within_target_range", False),
                "requirement": "40-140 units",
                "actual": fp.get("feasible_units"),
                "status": "✅ Pass" if fp.get("within_target_range") else "⚠️  Outside Range"
            },
            "cost_per_unit": {
                "passed": fp.get("under_target", False),
                "requirement": "< $325,000 per unit",
                "actual": fp.get("cost_per_unit_formatted"),
                "status": "✅ Pass" if fp.get("under_target") else "⚠️  Above Target"
            }
        }
        
        all_passed = all(c["passed"] for c in criteria.values())
        
        return {
            "status": "compliant" if all_passed else "partial_compliance",
            "meets_criteria": all_passed,
            "criteria": criteria,
            "summary": f"Passed {sum(c['passed'] for c in criteria.values())}/3 core requirements"
        }


class AssessmentProcessRequest(BaseSchema):
    """Request to trigger AI processing"""
    
    use_premium_apis: bool = Field(
        default=False,
        description="Use premium APIs (ATTOM, Google) instead of free alternatives"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh of cached API data"
    )


class AssessmentProcessResponse(BaseSchema):
    """Response from processing request"""
    
    success: bool
    message: str
    assessment_id: int
    status: AssessmentStatus
    estimated_completion_seconds: Optional[int] = Field(
        default=60,
        description="Estimated time to complete processing"
    )
