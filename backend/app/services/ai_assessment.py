"""
AI Assessment Service
Uses OpenAI to analyze property data and generate assessment scores
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.config import get_settings
from app.models.assessment import Assessment, AssessmentStatus
from app.models.church import Church
from app.models.property import Property
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
settings = get_settings()


class AIAssessmentService:
    """Service for AI-powered property assessment scoring"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def process_assessment(
        self,
        assessment_id: int,
        use_premium_model: bool = False
    ) -> Dict[str, Any]:
        """
        Process an assessment using AI to generate scores and analysis
        
        Args:
            assessment_id: Assessment database ID
            use_premium_model: Use GPT-4 instead of GPT-3.5
            
        Returns:
            Dictionary with assessment results
        """
        logger.info(f"Starting AI assessment processing for assessment_id={assessment_id}")
        
        # Get assessment with related data
        result = await self.db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        # Get related property and church
        property_result = await self.db.execute(
            select(Property).where(Property.id == assessment.property_id)
        )
        property_obj = property_result.scalar_one_or_none()
        
        church_result = await self.db.execute(
            select(Church).where(Church.id == assessment.church_id)
        )
        church = church_result.scalar_one_or_none()
        
        if not property_obj or not church:
            raise ValueError("Property or church not found")
        
        # Mark assessment as processing
        assessment.status = AssessmentStatus.PROCESSING
        assessment.processing_started_at = datetime.utcnow()
        await self.db.commit()
        
        try:
            # Step 1: Analyze location quality
            logger.info("Analyzing location quality...")
            location_score, location_analysis = await self._analyze_location(property_obj, assessment)
            
            # Step 2: Analyze market demand
            logger.info("Analyzing market demand...")
            market_score, market_analysis = await self._analyze_market(property_obj, church, assessment)
            
            # Step 3: Analyze financial viability
            logger.info("Analyzing financial viability...")
            financial_score, financial_analysis = await self._analyze_financials(property_obj, church, assessment)
            
            # Step 4: Analyze partnership fit
            logger.info("Analyzing partnership fit...")
            partnership_score, partnership_analysis = await self._analyze_partnership(property_obj, church, assessment)
            
            # Step 5: Analyze risk factors
            logger.info("Analyzing risk factors...")
            risk_score, risk_analysis = await self._analyze_risks(property_obj, church, assessment)
            
            # Step 6: Calculate overall score
            overall_score = self._calculate_overall_score(
                location_score,
                market_score,
                financial_score,
                partnership_score,
                risk_score
            )
            
            # Update assessment with results
            assessment.overall_score = overall_score
            assessment.location_score = location_score
            assessment.market_score = market_score
            assessment.financial_score = financial_score
            assessment.partnership_score = partnership_score
            assessment.risk_score = risk_score
            
            # Store detailed analysis
            assessment.market_analysis = market_analysis
            assessment.financial_projections = financial_analysis
            assessment.risk_factors = risk_analysis
            
            # Mark as completed
            assessment.status = AssessmentStatus.COMPLETED
            assessment.processing_completed_at = datetime.utcnow()
            
            if assessment.processing_started_at:
                duration = assessment.processing_completed_at - assessment.processing_started_at
                assessment.processing_duration_seconds = int(duration.total_seconds())
            
            await self.db.commit()
            
            logger.info(f"Assessment {assessment_id} completed with score: {overall_score}")
            
            return {
                "assessment_id": assessment_id,
                "status": "completed",
                "overall_score": overall_score,
                "scores": {
                    "location": location_score,
                    "market": market_score,
                    "financial": financial_score,
                    "partnership": partnership_score,
                    "risk": risk_score
                },
                "grade": assessment.score_grade,
                "processing_time_seconds": assessment.processing_duration_seconds
            }
            
        except Exception as e:
            logger.error(f"Assessment processing failed: {str(e)}", exc_info=True)
            assessment.status = AssessmentStatus.DRAFT
            await self.db.commit()
            raise
    
    async def _analyze_location(
        self,
        property_obj: Property,
        assessment: Assessment
    ) -> tuple[float, Dict[str, Any]]:
        """Analyze location quality using AI"""
        
        # Prepare property data
        property_data = {
            "address": property_obj.full_address,
            "coordinates": property_obj.coordinates,
            "lot_size_acres": property_obj.lot_size_acres,
            "data_sources": property_obj.data_sources
        }
        
        # Parse POI data if available
        poi_data = None
        if property_obj.data_sources:
            try:
                sources = json.loads(property_obj.data_sources)
                poi_data = sources.get("points_of_interest", {}).get("data", {})
            except:
                pass
        
        # Build prompt for OpenAI
        prompt = f"""Analyze this property location for affordable housing development potential.

Property: {property_obj.name or 'Unnamed Property'}
Address: {property_obj.full_address}
Lot Size: {property_obj.lot_size_acres} acres
Zoning: {property_obj.zoning_classification}

Nearby Amenities:
{json.dumps(poi_data, indent=2) if poi_data else "No nearby amenity data available"}

Assess the location on a 0-100 scale considering:
1. Access to public transportation
2. Proximity to schools and essential services
3. Neighborhood quality and safety
4. Job access and economic opportunity
5. Walkability and livability

Provide a score and brief analysis (2-3 sentences)."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert in affordable housing development site analysis. Provide objective, data-driven assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract score - look for "Score: XX" or "XX/100" pattern
            import re
            score_match = re.search(r'(?:Location Score|Score):\s*(\d{1,3})(?:/100)?', ai_response, re.IGNORECASE)
            if not score_match:
                score_match = re.search(r'(\d{1,3})/100', ai_response)
            if not score_match:
                # Last resort: look for standalone number, skip section numbers
                score_match = re.search(r'(?<!\d)(\d{2,3})(?!\.)(?:/100)?', ai_response)
            
            score = float(score_match.group(1)) if score_match else 70.0
            score = min(100, max(0, score))  # Clamp to 0-100
            
            analysis = {
                "score": score,
                "analysis": ai_response,
                "factors": {
                    "nearby_schools": poi_data.get("school", {}).get("count", 0) if poi_data else 0,
                    "nearby_transit": poi_data.get("transit_station", {}).get("count", 0) if poi_data else 0,
                    "nearby_grocery": poi_data.get("grocery_or_supermarket", {}).get("count", 0) if poi_data else 0
                },
                "ai_model": settings.openai_model
            }
            
            return score, analysis
            
        except Exception as e:
            logger.error(f"Location analysis failed: {str(e)}")
            # Return default moderate score if AI fails
            return 65.0, {
                "score": 65.0,
                "analysis": "AI analysis unavailable, using default moderate score",
                "error": str(e)
            }
    
    async def _analyze_market(
        self,
        property_obj: Property,
        church: Church,
        assessment: Assessment
    ) -> tuple[float, Dict[str, Any]]:
        """
        Analyze market demand using AI + enriched data
        
        For Logos Faith Development:
        - Validates Section 8 rent viability (critical!)
        - Checks AMI alignment with target tenant pool
        - Uses Census demographics for market validation
        - Assesses overall market demand
        """
        
        # Extract ALL enrichment data
        enrichment_data = self._extract_enrichment_data(property_obj)
        
        # Build enhanced prompt with enriched data
        data_context = ""
        
        # Add HUD FMR data
        fmr_data = enrichment_data.get("fair_market_rent", {})
        if fmr_data.get("success"):
            fmr = fmr_data.get("rent_by_bedroom", {})
            data_context += f"\nFair Market Rent (Section 8):\n"
            data_context += f"- 1BR: ${fmr.get('1_bedroom', 'N/A')}\n"
            data_context += f"- 2BR: ${fmr.get('2_bedroom', 'N/A')}\n"
            data_context += f"- 3BR: ${fmr.get('3_bedroom', 'N/A')}\n"
        
        # Add HUD Income Limits
        income_data = enrichment_data.get("income_limits", {})
        if income_data.get("success"):
            ami_80 = income_data.get("limits_by_household_size", {}).get("2_person", {}).get("80_percent_ami")
            if ami_80:
                data_context += f"\n80% AMI (2-person household): ${ami_80:,}/year\n"
        
        # Add Census demographics
        census_data = enrichment_data.get("census", {})
        if census_data.get("success"):
            data_context += f"\nLocal Demographics:\n"
            data_context += f"- Population: {census_data.get('population', 'N/A'):,}\n"
            data_context += f"- Median Income: ${census_data.get('median_income', 'N/A'):,}\n"
            data_context += f"- Poverty Rate: {census_data.get('poverty_rate', 'N/A')}%\n"
            housing = census_data.get('housing', {})
            if housing:
                data_context += f"- Renter Occupied: {housing.get('renter_occupied', 'N/A')} units\n"
                data_context += f"- Occupancy Rate: {housing.get('occupancy_rate', 'N/A')}%\n"
        
        prompt = f"""Analyze market demand for affordable housing at this location.

Location: {property_obj.city}, {property_obj.state}
Property Size: {property_obj.lot_size_acres} acres
Potential Units: {assessment.preferred_unit_count or 'Not specified'}
Target Affordability: {assessment.affordability_target or 'Mixed income'}
{data_context}

Consider:
1. Local housing shortage severity
2. Demographic trends and population growth
3. Employment and economic indicators
4. Existing affordable housing supply
5. Development pipeline and competition
6. Section 8 voucher availability and payment standards

Provide a market demand score (0-100) and brief analysis."""

        # Start with base score
        score = 70.0
        
        try:
            # Get AI analysis using GPT-4o for comprehensive market analysis
            # (gpt-4o-mini with 300 tokens was truncating the response)
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for detailed analysis
                messages=[
                    {"role": "system", "content": "You are a housing market analyst specializing in affordable housing demand assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000  # Increased from 300 to allow complete analysis
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract score - look for "Market Demand Score: XX/100" or "Score: XX"
            import re
            score_match = re.search(r'(?:Market Demand Score|Score):\s*(\d{1,3})(?:/100)?', ai_response, re.IGNORECASE)
            if not score_match:
                # Fallback: look for pattern like "85/100" at end of response
                score_match = re.search(r'(\d{1,3})/100', ai_response)
            if not score_match:
                # Last resort: look for standalone number, but skip section numbers (1., 2., etc)
                score_match = re.search(r'(?<!\d)(\d{2,3})(?!\.)(?:/100)?', ai_response)
            
            score = float(score_match.group(1)) if score_match else 70.0
            score = min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Market analysis AI failed: {str(e)}")
            ai_response = "AI analysis unavailable"
        
        # ============================================
        # LOGOS-SPECIFIC MARKET SCORING ADJUSTMENTS
        # ============================================
        
        # Adjust score based on HUD Fair Market Rent data
        fmr_adjustment = self._analyze_section8_viability(enrichment_data)
        score += fmr_adjustment["score_adjustment"]
        
        # Adjust score based on AMI alignment
        ami_adjustment = self._analyze_ami_alignment(enrichment_data, assessment)
        score += ami_adjustment["score_adjustment"]
        
        # Adjust score based on Census demographics
        census_adjustment = self._analyze_demographics(enrichment_data)
        score += census_adjustment["score_adjustment"]
        
        # Clamp final score
        score = min(100, max(0, score))
        
        return score, {
            "score": score,
            "analysis": ai_response,
            "city": property_obj.city,
            "state": property_obj.state,
            "ai_model": settings.openai_model,
            
            # Logos-specific market data
            "section8_viability": fmr_adjustment,
            "ami_alignment": ami_adjustment,
            "demographics": census_adjustment,
            "enrichment_data_available": any([
                enrichment_data.get("fair_market_rent", {}).get("success"),
                enrichment_data.get("income_limits", {}).get("success"),
                enrichment_data.get("census", {}).get("success")
            ]),
            "fair_market_rent": enrichment_data.get("fair_market_rent", {}).get("rent_by_bedroom"),
            "income_limits": enrichment_data.get("income_limits", {}).get("limits_by_household_size"),
            "census_data": {
                "population": census_data.get("population"),
                "median_income": census_data.get("median_income"),
                "poverty_rate": census_data.get("poverty_rate")
            } if census_data.get("success") else None
        }
    
    def _extract_enrichment_data(self, property_obj: Property) -> Dict[str, Any]:
        """
        Extract ALL enrichment data from property's data_sources JSON field
        
        Returns structured data from:
        - Census demographics
        - FEMA flood risk
        - HUD income limits
        - HUD fair market rent
        - Points of interest
        - Crosswalk data
        """
        
        if not property_obj.data_sources:
            return {}
        
        try:
            data_sources = json.loads(property_obj.data_sources)
            
            # Extract all enrichment data sources
            # Support both old and new key names for backward compatibility
            enrichment_data = {
                "census": data_sources.get("census_demographics") or data_sources.get("demographics", {}),
                "fema": data_sources.get("fema_flood") or data_sources.get("flood_risk", {}),
                "poi": data_sources.get("points_of_interest", {}),
                "crosswalk": data_sources.get("hud_usps_crosswalk", {}),
            }
            
            # Extract HUD data (income limits + FMR)
            hud_result = data_sources.get("hud_data", {})
            
            # Check if HUD data is in the new flat structure or old nested structure
            if hud_result.get("status") == "success":
                hud_data = hud_result.get("data", {})
                # New structure: data contains income_limits and fair_market_rent directly
                enrichment_data["income_limits"] = hud_data.get("income_limits", {})
                enrichment_data["fair_market_rent"] = hud_data.get("fair_market_rent", {})
            elif "income_limits" in hud_result or "fair_market_rent" in hud_result:
                # Old structure: income_limits and fair_market_rent are direct keys
                enrichment_data["income_limits"] = hud_result.get("income_limits", {})
                enrichment_data["fair_market_rent"] = hud_result.get("fair_market_rent", {})
            else:
                enrichment_data["income_limits"] = {}
                enrichment_data["fair_market_rent"] = {}
            
            return enrichment_data
            
        except Exception as e:
            logger.error(f"Error extracting enrichment data: {str(e)}")
            return {}
    
    def _analyze_section8_viability(self, enrichment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Section 8 voucher viability based on Fair Market Rent
        
        Critical for Logos: Their model depends on Section 8 vouchers.
        FMR determines maximum rent, which must support project economics.
        
        Scoring Logic:
        - High FMR (>$2000 for 2BR): +10 points (excellent)
        - Moderate FMR ($1500-$2000): +5 points (good)
        - Low FMR (<$1500): -10 points (challenging)
        - No data: 0 points (neutral, requires research)
        """
        
        fmr_data = enrichment_data.get("fair_market_rent", {})
        
        if not fmr_data or not fmr_data.get("success"):
            return {
                "score_adjustment": 0,
                "status": "no_data",
                "message": "FMR data not available - requires research",
                "recommendation": "Obtain local Section 8 payment standards before proceeding"
            }
        
        rent_by_br = fmr_data.get("rent_by_bedroom", {})
        br2_rent = rent_by_br.get("2_bedroom")
        
        if not br2_rent:
            return {
                "score_adjustment": 0,
                "status": "incomplete_data",
                "message": "2BR FMR not available"
            }
        
        # Analyze 2BR FMR (most common unit type for Logos)
        if br2_rent >= 2000:
            adjustment = 10
            status = "excellent"
            message = f"High FMR (${br2_rent}) supports strong project economics"
        elif br2_rent >= 1500:
            adjustment = 5
            status = "good"
            message = f"Moderate FMR (${br2_rent}) - project likely viable"
        elif br2_rent >= 1200:
            adjustment = 0
            status = "marginal"
            message = f"Lower FMR (${br2_rent}) - tight margins, careful underwriting needed"
        else:
            adjustment = -10
            status = "challenging"
            message = f"Low FMR (${br2_rent}) - may not support project economics"
        
        estimated_supportable_cost = br2_rent * 12 * 15
        
        return {
            "score_adjustment": adjustment,
            "status": status,
            "message": message,
            "fmr_2br": br2_rent,
            "annual_rent_2br": br2_rent * 12,
            "estimated_supportable_cost_per_unit": estimated_supportable_cost,
            "logos_target_cost": 325000,
            "meets_logos_threshold": estimated_supportable_cost >= 250000,
            "all_fmr": rent_by_br
        }
    
    def _analyze_ami_alignment(
        self,
        enrichment_data: Dict[str, Any],
        assessment: Assessment
    ) -> Dict[str, Any]:
        """
        Analyze AMI (Area Median Income) alignment
        
        For Logos: Target tenants are 60-80% AMI households.
        """
        
        income_limits = enrichment_data.get("income_limits", {})
        
        if not income_limits or not income_limits.get("success"):
            return {
                "score_adjustment": 0,
                "status": "no_data",
                "message": "AMI data not available"
            }
        
        limits_by_size = income_limits.get("limits_by_household_size", {})
        ami_80_2person = limits_by_size.get("2_person", {}).get("80_percent_ami")
        ami_60_2person = limits_by_size.get("2_person", {}).get("60_percent_ami")
        
        if not ami_80_2person:
            return {
                "score_adjustment": 0,
                "status": "incomplete_data",
                "message": "AMI limits not available"
            }
        
        if 50000 <= ami_80_2person <= 80000:
            adjustment = 5
            status = "ideal"
            message = f"80% AMI (${ami_80_2person:,}) is in Logos' target range"
        elif 40000 <= ami_80_2person < 50000:
            adjustment = 2
            status = "acceptable_low"
            message = f"80% AMI (${ami_80_2person:,}) is lower but workable"
        elif 80000 < ami_80_2person <= 100000:
            adjustment = 2
            status = "acceptable_high"
            message = f"80% AMI (${ami_80_2person:,}) is higher - strong tenant pool"
        else:
            adjustment = -5
            status = "challenging"
            message = f"80% AMI (${ami_80_2person:,}) may present tenant qualification challenges"
        
        return {
            "score_adjustment": adjustment,
            "status": status,
            "message": message,
            "ami_80_percent_2person": ami_80_2person,
            "ami_60_percent_2person": ami_60_2person,
            "max_affordable_rent_80ami": int(ami_80_2person * 0.3 / 12) if ami_80_2person else None,
            "logos_target_range": "60-80% AMI",
            "all_limits": limits_by_size
        }
    
    def _analyze_demographics(self, enrichment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Census demographics to validate affordable housing need
        """
        
        census_data = enrichment_data.get("census", {})
        
        if not census_data or not census_data.get("success"):
            return {
                "score_adjustment": 0,
                "status": "no_data",
                "message": "Census demographics not available"
            }
        
        adjustment = 0
        indicators = []
        
        poverty_rate = census_data.get("poverty_rate")
        if poverty_rate:
            if poverty_rate > 30:
                adjustment += 10
                indicators.append(f"High poverty rate ({poverty_rate}%) indicates strong affordable housing need")
            elif poverty_rate > 20:
                adjustment += 5
                indicators.append(f"Elevated poverty rate ({poverty_rate}%) suggests moderate need")
        
        housing = census_data.get("housing", {})
        if housing:
            renter_occupied = housing.get("renter_occupied", 0)
            total_occupied = housing.get("owner_occupied", 0) + renter_occupied
            if total_occupied > 0:
                renter_pct = (renter_occupied / total_occupied) * 100
                if renter_pct > 60:
                    adjustment += 5
                    indicators.append(f"High renter percentage ({renter_pct:.1f}%) validates rental market")
        
        return {
            "score_adjustment": adjustment,
            "status": "analyzed",
            "message": f"Demographics support affordable housing development (+{adjustment} points)",
            "indicators": indicators
        }
    
    async def _analyze_financials(
        self,
        property_obj: Property,
        church: Church,
        assessment: Assessment
    ) -> tuple[float, Dict[str, Any]]:
        """Analyze financial viability with Logos-specific requirements + enriched data"""
        
        # Get enrichment data for FMR and flood risk
        enrichment_data = self._extract_enrichment_data(property_obj)
        
        # PRIORITY: Use client-specified available build space if provided, otherwise use total lot size
        # This allows churches to specify a portion of their property for development
        if assessment.available_build_sqft and assessment.available_build_sqft > 0:
            lot_size_sqft = assessment.available_build_sqft
            using_available_space = True
            logger.info(f"Using client-specified available build space: {lot_size_sqft:,} sq ft")
        else:
            lot_size_sqft = property_obj.lot_size_sqft or 0
            using_available_space = False
            logger.info(f"Using total lot size from property data: {lot_size_sqft:,} sq ft")
        
        if lot_size_sqft < 10000:
            logger.warning(f"Property {property_obj.id} disqualified: {lot_size_sqft} sq ft < 10,000 sq ft minimum")
            return 0.0, {
                "score": 0.0,
                "disqualified": True,
                "disqualification_reason": "Below Logos minimum lot size requirement",
                "lot_size_sqft": lot_size_sqft,
                "minimum_required_sqft": 10000,
                "using_available_space": using_available_space,
                "note": "Property does not meet Logos Faith Development's 10,000 sq ft minimum threshold"
            }
        
        # Calculate unit capacity using the determined lot size (available space or total)
        unit_capacity_info = self._calculate_unit_capacity(property_obj, lot_size_sqft_override=lot_size_sqft)
        feasible_units = unit_capacity_info["feasible_units"]
        within_target_range = 40 <= feasible_units <= 140
        
        cost_per_unit_info = self._estimate_cost_per_unit(property_obj, feasible_units)
        cost_per_unit = cost_per_unit_info["cost_per_unit"]
        
        # Pass property location data for geographic disaster filtering
        flood_analysis = self._analyze_flood_risk(
            enrichment_data,
            property_lat=property_obj.latitude,
            property_lon=property_obj.longitude,
            property_county=property_obj.county,
            property_state=property_obj.state
        )
        flood_cost_per_unit = flood_analysis.get("mitigation_cost_per_unit", 0)
        total_flood_costs = flood_cost_per_unit * feasible_units
        
        adjusted_cost_per_unit = cost_per_unit + flood_cost_per_unit
        
        score = 75.0
        
        # BONUS: Larger available space = better score (proportional to size above minimum)
        # Score increases for every 10,000 sqft above the minimum, up to +15 points
        if lot_size_sqft >= 10000:
            excess_sqft = lot_size_sqft - 10000
            # Award 1 point per 5,000 sqft above minimum (max +15 points at 85,000 sqft)
            size_bonus = min(15, (excess_sqft / 5000) * 1)
            if size_bonus > 0:
                score += size_bonus
                logger.info(f"✓ Property {property_obj.id}: Size bonus +{size_bonus:.1f} points for {lot_size_sqft:,} sqft")
        
        if within_target_range:
            score += 15
            logger.info(f"✓ Property {property_obj.id}: {feasible_units} units within Logos target (40-140)")
        elif feasible_units < 40:
            penalty = min(20, (40 - feasible_units) * 2)
            score -= penalty
            logger.warning(f"✗ Property {property_obj.id}: Only {feasible_units} units (below 40 minimum)")
        else:
            penalty = min(15, (feasible_units - 140) * 0.5)
            score -= penalty
            logger.warning(f"⚠ Property {property_obj.id}: {feasible_units} units (above 140 target)")
        
        if adjusted_cost_per_unit <= 300000:
            score += 10
            logger.info(f"✓ Excellent cost per unit: ${adjusted_cost_per_unit:,.0f} (<$300K)")
        elif adjusted_cost_per_unit <= 325000:
            score += 5
            logger.info(f"✓ Good cost per unit: ${adjusted_cost_per_unit:,.0f} (<$325K)")
        elif adjusted_cost_per_unit <= 375000:
            score -= 10
            logger.warning(f"⚠ Above target cost per unit: ${adjusted_cost_per_unit:,.0f} (target: <$325K)")
        else:
            score -= 20
            logger.warning(f"✗ Significantly above target: ${adjusted_cost_per_unit:,.0f} (target: <$325K)")
        
        if property_obj.has_water and property_obj.has_sewer:
            score += 5
        else:
            score -= 10
        
        if church.annual_budget and church.annual_budget > 100000:
            score += 5
        
        revenue_projections = self._calculate_revenue_projections(
            enrichment_data, 
            feasible_units,
            adjusted_cost_per_unit
        )
        
        score = min(100, max(0, score))
        
        total_development_cost = cost_per_unit * feasible_units
        adjusted_total_cost = adjusted_cost_per_unit * feasible_units
        
        analysis = {
            "score": score,
            "disqualified": False,
            
            "lot_size_sqft": lot_size_sqft,
            "lot_size_acres": lot_size_sqft / 43560 if lot_size_sqft > 0 else None,
            "meets_minimum": True,
            "using_available_space": using_available_space,
            "available_build_sqft": assessment.available_build_sqft if using_available_space else None,
            "total_lot_size_sqft": property_obj.lot_size_sqft,
            "build_area_notes": assessment.build_area_notes if using_available_space else None,
            
            "unit_capacity": unit_capacity_info,
            "feasible_units": feasible_units,
            "within_target_range": within_target_range,
            "target_range": "40-140 units",
            
            "base_cost_per_unit": cost_per_unit,
            "flood_mitigation_cost_per_unit": flood_cost_per_unit,
            "adjusted_cost_per_unit": adjusted_cost_per_unit,
            "adjusted_cost_per_unit_formatted": f"${adjusted_cost_per_unit:,.0f}",
            "target_cost_per_unit": 325000,
            "under_target": adjusted_cost_per_unit <= 325000,
            "cost_breakdown": cost_per_unit_info["breakdown"],
            
            "base_development_cost": total_development_cost,
            "total_flood_mitigation_cost": total_flood_costs,
            "adjusted_development_cost": adjusted_total_cost,
            "adjusted_development_cost_formatted": f"${adjusted_total_cost:,.0f}",
            
            "revenue_projections": revenue_projections,
            
            "flood_risk_analysis": flood_analysis,
            
            "funding_sources": ["private_equity", "church_land_contribution", "construction_loan"],
            "notes": [
                "No LIHTC (private funding model)",
                "Church retains land ownership",
                "Zero land acquisition cost",
                f"Flood mitigation adds ${flood_cost_per_unit:,}/unit" if flood_cost_per_unit > 0 else "No flood mitigation required"
            ]
        }
        
        return score, analysis
    
    def _calculate_revenue_projections(
        self,
        enrichment_data: Dict[str, Any],
        unit_count: int,
        cost_per_unit: float
    ) -> Dict[str, Any]:
        """
        Calculate revenue projections using actual HUD Fair Market Rent data
        
        Returns detailed financial projections including:
        - Annual rent revenue by unit type
        - Operating expenses (40-45% of revenue)
        - Net Operating Income (NOI)
        - Return on Investment (ROI)
        - Cash-on-cash return
        """
        
        fmr_data = enrichment_data.get("fair_market_rent", {})
        
        if not fmr_data or not fmr_data.get("success"):
            return {
                "status": "no_data",
                "message": "FMR data not available - revenue projections are estimates",
                "estimated_revenue": "Contact local Housing Authority for Section 8 payment standards"
            }
        
        rent_by_bedroom = fmr_data.get("rent_by_bedroom", {})
        
        unit_mix = {
            "1_bedroom": {"count": int(unit_count * 0.20), "fmr": rent_by_bedroom.get("1_bedroom", 0)},
            "2_bedroom": {"count": int(unit_count * 0.60), "fmr": rent_by_bedroom.get("2_bedroom", 0)},
            "3_bedroom": {"count": int(unit_count * 0.20), "fmr": rent_by_bedroom.get("3_bedroom", 0)}
        }
        
        annual_revenue = 0
        revenue_by_type = {}
        
        for unit_type, data in unit_mix.items():
            if data["fmr"] > 0:
                monthly_revenue = data["count"] * data["fmr"]
                annual_revenue_type = monthly_revenue * 12
                annual_revenue += annual_revenue_type
                
                revenue_by_type[unit_type] = {
                    "unit_count": data["count"],
                    "monthly_rent": data["fmr"],
                    "monthly_revenue": monthly_revenue,
                    "annual_revenue": annual_revenue_type
                }
        
        operating_expense_ratio = 0.42
        operating_expenses = annual_revenue * operating_expense_ratio
        
        noi = annual_revenue - operating_expenses
        
        total_cost = cost_per_unit * unit_count
        
        roi_percent = (noi / total_cost * 100) if total_cost > 0 else 0
        cap_rate = (noi / total_cost * 100) if total_cost > 0 else 0
        
        equity_investment = total_cost * 0.30
        cash_on_cash = (noi / equity_investment * 100) if equity_investment > 0 else 0
        
        return {
            "status": "calculated",
            "data_source": f"HUD FMR {fmr_data.get('year', 'N/A')}",
            "unit_mix": unit_mix,
            "revenue_by_unit_type": revenue_by_type,
            "total_annual_revenue": annual_revenue,
            "total_annual_revenue_formatted": f"${annual_revenue:,.0f}",
            "operating_expenses": operating_expenses,
            "operating_expense_ratio": f"{operating_expense_ratio*100}%",
            "net_operating_income": noi,
            "noi_formatted": f"${noi:,.0f}",
            "total_development_cost": total_cost,
            "roi_percent": round(roi_percent, 2),
            "cap_rate": round(cap_rate, 2),
            "equity_investment_30pct": equity_investment,
            "cash_on_cash_return": round(cash_on_cash, 2),
            "assumptions": [
                "20% 1BR, 60% 2BR, 20% 3BR unit mix",
                "42% operating expense ratio (industry standard)",
                "100% occupancy (conservative for Section 8)",
                "30% equity / 70% debt financing"
            ],
            "notes": [
                "Actual FMR may vary by ZIP code within county",
                "Does not include debt service payments",
                "Does not include tax abatement benefits (98% CA Welfare exemption)"
            ]
        }
    
    def _calculate_unit_capacity(self, property_obj: Property, lot_size_sqft_override: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate feasible unit count based on lot size and density assumptions.
        
        Logos targets: 40-140 units per property
        
        Args:
            property_obj: Property object
            lot_size_sqft_override: Optional override for lot size (e.g., available build space)
        """
        # Use override if provided (client-specified available space), otherwise use property lot size
        lot_size_sqft = lot_size_sqft_override if lot_size_sqft_override is not None else (property_obj.lot_size_sqft or 0)
        lot_size_acres = lot_size_sqft / 43560 if lot_size_sqft > 0 else (property_obj.lot_size_acres or 0)
        
        units_per_acre = 45
        site_coverage_factor = 0.85
        
        developable_acres = lot_size_acres * site_coverage_factor
        feasible_units = int(developable_acres * units_per_acre)
        
        sqft_per_unit = 1800
        units_by_sqft = int((lot_size_sqft * site_coverage_factor) / sqft_per_unit)
        
        final_units = min(feasible_units, units_by_sqft)
        
        return {
            "feasible_units": final_units,
            "lot_size_acres": lot_size_acres,
            "lot_size_sqft": lot_size_sqft,
            "developable_acres": round(developable_acres, 2),
            "units_per_acre_assumed": units_per_acre,
            "site_coverage_factor": site_coverage_factor,
            "calculation_method": "conservative_estimate",
            "notes": [
                f"Assumes {units_per_acre} units/acre density",
                f"Accounts for {int((1-site_coverage_factor)*100)}% setbacks/easements",
                "Final estimate is conservative (lower of two methods)"
            ]
        }
    
    def _estimate_cost_per_unit(
        self,
        property_obj: Property,
        unit_count: int
    ) -> Dict[str, Any]:
        """
        Estimate cost per unit for Logos affordable housing model.
        
        Target: <$325K per unit
        """
        
        base_construction_cost_psf = 200
        avg_unit_size_sqft = 750
        
        building_construction = base_construction_cost_psf * avg_unit_size_sqft
        
        site_work = building_construction * 0.12
        
        parking = 25000 * 0.75
        
        utilities = 15000 if property_obj.has_water and property_obj.has_sewer else 40000
        
        hard_costs_subtotal = building_construction + site_work + parking + utilities
        soft_costs = hard_costs_subtotal * 0.22
        
        financing = hard_costs_subtotal * 0.06
        
        developer_fee = hard_costs_subtotal * 0.12
        
        total_cost_per_unit = (
            building_construction + 
            site_work + 
            parking + 
            utilities + 
            soft_costs + 
            financing + 
            developer_fee
        )
        
        if unit_count >= 100:
            total_cost_per_unit *= 0.92
        elif unit_count >= 60:
            total_cost_per_unit *= 0.95
        elif unit_count <= 30:
            total_cost_per_unit *= 1.08
        
        return {
            "cost_per_unit": int(total_cost_per_unit),
            "breakdown": {
                "building_construction": int(building_construction),
                "site_work": int(site_work),
                "parking": int(parking),
                "utilities_hookup": int(utilities),
                "soft_costs": int(soft_costs),
                "financing_costs": int(financing),
                "developer_fee": int(developer_fee)
            },
            "assumptions": {
                "construction_cost_psf": base_construction_cost_psf,
                "avg_unit_size_sqft": avg_unit_size_sqft,
                "parking_spaces_per_unit": 0.75,
                "unit_count": unit_count,
                "scale_factor_applied": unit_count >= 60
            },
            "notes": [
                "Costs are 2025 national averages",
                "Does not include land acquisition (church owns land)",
                "California Welfare Tax exemption not yet factored"
            ]
        }
    
    async def _analyze_partnership(
        self,
        property_obj: Property,
        church: Church,
        assessment: Assessment
    ) -> tuple[float, Dict[str, Any]]:
        """
        Analyze church-developer partnership fit
        
        LOGOS MODEL: Church provides land + support, Logos brings expertise
        Church development experience is NOT required (actually preferred they don't!)
        """
        
        score = 70.0
        
        # Church provides congregation support (critical!)
        if assessment.congregation_approval:
            score += 15
        
        # Leadership alignment (very important)
        if assessment.leadership_support in ["unanimous", "majority", "strong"]:
            score += 10
        elif assessment.leadership_support == "mixed":
            score += 5
        
        # Timeline readiness
        if assessment.timeline_readiness in ["ready_now", "6_months"]:
            score += 10
        elif assessment.timeline_readiness in ["1_year", "12_months"]:
            score += 5
        
        # Church owns land (HUGE benefit - zero acquisition cost)
        if property_obj.church_id:
            score += 5  # Bonus for church land ownership
        
        score = min(100, max(0, score))
        
        analysis = {
            "score": score,
            "readiness_factors": {
                "congregation_approval": assessment.congregation_approval,
                "leadership_support": assessment.leadership_support,
                "timeline_readiness": assessment.timeline_readiness,
                "land_ownership": "Church owns land (zero acquisition cost)"
            },
            "partnership_model": "Logos Development + Church Partnership",
            "church_role": "Land owner + Community support",
            "logos_role": "Development expertise + Financing + Construction + Management",
            "partnership_structure": assessment.revenue_sharing_preference or "to_be_determined"
        }
        
        return score, analysis
    
    async def _analyze_risks(
        self,
        property_obj: Property,
        church: Church,
        assessment: Assessment
    ) -> tuple[float, Dict[str, Any]]:
        """Analyze development risks (lower score = higher risk)"""
        
        enrichment_data = self._extract_enrichment_data(property_obj)
        
        score = 80.0
        risks = []
        mitigation_costs = {}
        
        if property_obj.zoning_classification == "unknown":
            score -= 15
            risks.append("Unknown zoning classification - requires research")
        elif property_obj.zoning_classification not in ["residential_medium_density", "residential_high_density", "mixed_use"]:
            score -= 10
            risks.append("May require zoning change or variance")
        
        # Pass property location data for geographic filtering
        flood_analysis = self._analyze_flood_risk(
            enrichment_data,
            property_lat=property_obj.latitude,
            property_lon=property_obj.longitude,
            property_county=property_obj.county,
            property_state=property_obj.state
        )
        score -= flood_analysis["score_penalty"]
        if flood_analysis["risks"]:
            risks.extend(flood_analysis["risks"])
        if flood_analysis["mitigation_cost"] > 0:
            mitigation_costs["flood_mitigation"] = flood_analysis["mitigation_cost"]
        
        if property_obj.lot_size_acres and property_obj.lot_size_acres < 1.0:
            score -= 10
            risks.append("Small lot size may limit development options")
        
        if property_obj.environmental_concerns:
            score -= 15
            risks.append("Environmental concerns noted")
        
        # NOTE: Church development experience is NOT a risk factor
        # Logos Development brings the expertise as the development partner
        # Church provides land + community support (their actual role)
        # if not church.previous_development_experience:
        #     score -= 5
        #     risks.append("Church lacks development experience")
        
        score = min(100, max(0, score))
        
        analysis = {
            "score": score,
            "risk_level": "low" if score >= 70 else "medium" if score >= 50 else "high",
            "identified_risks": risks,
            "mitigation_costs": mitigation_costs,
            "total_mitigation_cost": sum(mitigation_costs.values()),
            "flood_analysis": flood_analysis,
            "mitigation_strategies": []
        }
        
        return score, analysis
    
    def _analyze_flood_risk(
        self,
        enrichment_data: Dict[str, Any],
        property_lat: float = None,
        property_lon: float = None,
        property_county: str = None,
        property_state: str = None
    ) -> Dict[str, Any]:
        """
        Analyze FEMA flood risk data and calculate mitigation costs
        NOW INCLUDES COMPREHENSIVE NATURAL DISASTER ASSESSMENT WITH GEOGRAPHIC FILTERING
        
        Scoring Impact:
        - Zone X/C (minimal risk): 0 penalty
        - Zone A/AE/AH/AO (high risk): -20 points, +$50K/unit
        - Zone V/VE (coastal high risk): -30 points, +$75K/unit
        - No data: -5 points (uncertainty penalty)
        """
        
        # Call comprehensive natural disaster assessment WITH LOCATION DATA
        comprehensive = self._analyze_natural_disaster_risk(
            enrichment_data,
            property_lat=property_lat,
            property_lon=property_lon,
            property_county=property_county,
            property_state=property_state
        )
        flood_detail = comprehensive["disaster_risks"].get("flood", {})
        
        # Return legacy format for backward compatibility
        return {
            "score_penalty": comprehensive["total_score_penalty"],
            "risk_level": comprehensive["overall_risk_level"],
            "flood_zone": flood_detail.get("flood_zone", "Unknown"),
            "risks": comprehensive["combined_risks"],
            "mitigation_cost": 0,
            "mitigation_cost_per_unit": comprehensive["total_mitigation_cost_per_unit"],
            "recommendation": comprehensive["recommendation"],
            "disaster_breakdown": comprehensive["disaster_risks"]
        }
    
    def _analyze_natural_disaster_risk(
        self,
        enrichment_data: Dict[str, Any],
        property_lat: float = None,
        property_lon: float = None,
        property_county: str = None,
        property_state: str = None
    ) -> Dict[str, Any]:
        """
        Comprehensive natural disaster risk assessment WITH GEOGRAPHIC FILTERING
        
        Analyzes: Flood, Fire (wildfire), Tornado, Hurricane, Earthquake
        NOW filters disasters by distance to prevent false positives
        (e.g., downtown LA penalized for rural wildfires 300 miles away)
        
        Returns combined risk score, mitigation costs, and recommendations
        """
        
        fema_data = enrichment_data.get("fema", {})
        
        if not fema_data or not fema_data.get("status") == "success":
            return {
                "total_score_penalty": 5,
                "overall_risk_level": "unknown",
                "disaster_risks": {},
                "combined_risks": ["Natural disaster risk unknown - requires FEMA verification"],
                "total_mitigation_cost_per_unit": 0,
                "recommendation": "Conduct comprehensive natural disaster risk assessment"
            }
        
        # Extract data from FEMA enrichment structure
        fema_content = fema_data.get("data", {})
        disaster_history = fema_content.get("disaster_history", {})
        flood_zone = fema_content.get("flood_zone", "Unknown")
        
        # Analyze each disaster type WITH GEOGRAPHIC CONTEXT
        flood_risk = self._analyze_flood_risk_detail(flood_zone, disaster_history.get("flood", {}))
        fire_risk = self._analyze_fire_risk(
            disaster_history.get("fire", {}),
            property_lat=property_lat,
            property_lon=property_lon,
            property_county=property_county
        )
        tornado_risk = self._analyze_tornado_risk(disaster_history.get("tornado", {}))
        hurricane_risk = self._analyze_hurricane_risk(
            disaster_history.get("hurricane", {}),
            property_state=property_state,
            property_county=property_county
        )
        earthquake_risk = self._analyze_earthquake_risk(
            disaster_history.get("earthquake", {}),
            property_state=property_state
        )
        
        # Combine results
        total_penalty = (
            flood_risk["score_penalty"] +
            fire_risk["score_penalty"] +
            tornado_risk["score_penalty"] +
            hurricane_risk["score_penalty"] +
            earthquake_risk["score_penalty"]
        )
        
        total_mitigation_cost = (
            flood_risk["mitigation_cost_per_unit"] +
            fire_risk["mitigation_cost_per_unit"] +
            tornado_risk["mitigation_cost_per_unit"] +
            hurricane_risk["mitigation_cost_per_unit"] +
            earthquake_risk["mitigation_cost_per_unit"]
        )
        
        combined_risks = []
        for risk in [flood_risk, fire_risk, tornado_risk, hurricane_risk, earthquake_risk]:
            combined_risks.extend(risk.get("risks", []))
        
        # Determine overall risk level
        high_risk_count = sum(1 for r in [flood_risk, fire_risk, tornado_risk, hurricane_risk, earthquake_risk] 
                              if r["risk_level"] in ["high", "very_high"])
        
        if high_risk_count >= 2:
            overall_risk_level = "very_high"
        elif high_risk_count == 1:
            overall_risk_level = "high"
        elif total_penalty > 10:
            overall_risk_level = "moderate"
        else:
            overall_risk_level = "low"
        
        return {
            "total_score_penalty": min(40, total_penalty),  # Cap at 40 points
            "overall_risk_level": overall_risk_level,
            "disaster_risks": {
                "flood": flood_risk,
                "fire": fire_risk,
                "tornado": tornado_risk,
                "hurricane": hurricane_risk,
                "earthquake": earthquake_risk
            },
            "combined_risks": combined_risks,
            "total_mitigation_cost_per_unit": total_mitigation_cost,
            "recommendation": self._get_disaster_recommendation(overall_risk_level, high_risk_count)
        }
    
    def _analyze_flood_risk_detail(self, flood_zone: str, flood_history: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed flood risk analysis"""
        
        event_count = flood_history.get("count", 0)
        
        if flood_zone in ["X", "C", "B"] and event_count == 0:
            return {
                "type": "flood",
                "score_penalty": 0,
                "risk_level": "minimal",
                "flood_zone": flood_zone,
                "event_count": event_count,
                "risks": [],
                "mitigation_cost_per_unit": 0
            }
        
        elif any(flood_zone.startswith(prefix) for prefix in ["A", "AE", "AH", "AO"]):
            return {
                "type": "flood",
                "score_penalty": 5,  # Reduced from 10 - informational focus
                "risk_level": "moderate",
                "flood_zone": flood_zone,
                "event_count": event_count,
                "risks": [
                    f"ℹ️ FEMA Flood Zone {flood_zone} (1% annual flood chance)",
                    "Requires elevated construction (+$15K-$25K per unit)",
                    "Mandatory flood insurance required"
                ],
                "mitigation_cost_per_unit": 20000
            }
        
        elif flood_zone.startswith("V"):
            return {
                "type": "flood",
                "score_penalty": 15,  # Reduced from 30 - still significant but not crushing
                "risk_level": "high",  # Downgraded from very_high
                "flood_zone": flood_zone,
                "event_count": event_count,
                "risks": [
                    f"⚠️ Coastal High Hazard Zone {flood_zone}",
                    "Must be elevated on pilings/columns",
                    "High insurance costs expected"
                ],
                "mitigation_cost_per_unit": 75000
            }
        
        else:
            return {
                "type": "flood",
                "score_penalty": 5,
                "risk_level": "unknown",
                "flood_zone": flood_zone,
                "event_count": event_count,
                "risks": ["Flood risk requires verification"],
                "mitigation_cost_per_unit": 0
            }
    
    def _analyze_fire_risk(
        self,
        fire_history: Dict[str, Any],
        property_lat: float = None,
        property_lon: float = None,
        property_county: str = None
    ) -> Dict[str, Any]:
        """
        Wildfire risk analysis with GEOGRAPHIC FILTERING
        
        Prevents false positives like urban LA being penalized for rural fires
        """
        from app.services.disaster_distance_filter import \
            DisasterDistanceFilter
        
        event_count = fire_history.get("count", 0)
        all_events = fire_history.get("events", [])
        
        if event_count == 0:
            return {
                "type": "fire",
                "score_penalty": 0,
                "risk_level": "minimal",
                "event_count": 0,
                "event_count_nearby": 0,
                "risks": [],
                "mitigation_cost_per_unit": 0,
                "geographic_context": "No wildfire events in state"
            }
        
        # Apply geographic filtering if location data available
        if property_lat and property_lon and all_events:
            filtered = DisasterDistanceFilter.filter_disasters_by_distance(
                disasters=all_events,
                disaster_type='fire',
                property_lat=property_lat,
                property_lon=property_lon,
                property_county=property_county
            )
            
            # Use DIRECT RISK events only for scoring
            nearby_count = filtered['direct_count']
            regional_count = filtered['regional_count']
            direct_threshold = filtered['thresholds_miles']['direct']
            
            context = DisasterDistanceFilter.get_risk_context_message(
                disaster_type='fire',
                filtered_data=filtered,
                property_location=property_county or "this location"
            )
            
            # Score based on nearby events - REDUCED PENALTIES (informational focus)
            # County-level data means we can't pinpoint exact fire locations
            # So we keep penalties low and focus on providing information
            if nearby_count == 0:
                return {
                    "type": "fire",
                    "score_penalty": 0,
                    "risk_level": "minimal",
                    "event_count": event_count,
                    "event_count_nearby": nearby_count,
                    "event_count_regional": regional_count,
                    "risks": [],
                    "mitigation_cost_per_unit": 0,
                    "geographic_context": context,
                    "note": f"{event_count} statewide events, NONE in county"
                }
            elif nearby_count >= 5:
                # County has significant fire history - LIGHT penalty, show info
                return {
                    "type": "fire",
                    "score_penalty": 3,  # Reduced from 15
                    "risk_level": "informational",
                    "event_count": event_count,
                    "event_count_nearby": nearby_count,
                    "event_count_regional": regional_count,
                    "risks": [
                        f"ℹ️ {nearby_count} wildfire events in county since 2004",
                        f"📍 Note: County-level data (actual distance to fires unknown)",
                        "✓ Recommend fire-resistant materials as best practice",
                        "✓ Verify insurance requirements with local providers"
                    ],
                    "mitigation_cost_per_unit": 3000,  # Reduced from 8000
                    "geographic_context": context,
                    "note": "Informational only - county has fire history but exact property risk depends on specific location"
                }
            else:
                # Some county fire history - MINIMAL penalty
                return {
                    "type": "fire",
                    "score_penalty": 1,  # Reduced from 5
                    "risk_level": "low",
                    "event_count": event_count,
                    "event_count_nearby": nearby_count,
                    "event_count_regional": regional_count,
                    "risks": [
                        f"ℹ️ {nearby_count} wildfire events in county since 2004",
                        "✓ Standard fire safety practices recommended"
                    ],
                    "mitigation_cost_per_unit": 1000,  # Reduced from 3000
                    "geographic_context": context,
                    "note": "County has limited fire history"
                }
        
        # Fallback: use statewide counts (if no location data)
        # Apply same reduced penalties - informational focus
        if event_count >= 5:
            return {
                "type": "fire",
                "score_penalty": 3,  # Reduced from 15
                "risk_level": "informational",
                "event_count": event_count,
                "event_count_nearby": 0,
                "risks": [
                    f"ℹ️ {event_count} wildfire events in state since 2004",
                    "📍 Geographic filtering unavailable - verify local risk",
                    "✓ Recommend fire-resistant construction as best practice"
                ],
                "mitigation_cost_per_unit": 3000,  # Reduced from 8000
                "geographic_context": "Geographic filtering not available - statewide data shown for reference"
            }
        else:
            return {
                "type": "fire",
                "score_penalty": 1,  # Reduced from 5
                "risk_level": "low",
                "event_count": event_count,
                "event_count_nearby": 0,
                "risks": [
                    f"ℹ️ {event_count} wildfire event(s) in state since 2004",
                    "✓ Standard fire safety practices recommended"
                ],
                "mitigation_cost_per_unit": 1000,  # Reduced from 3000
                "geographic_context": "Geographic filtering not available - statewide data shown for reference"
            }
    
    def _analyze_tornado_risk(self, tornado_history: Dict[str, Any]) -> Dict[str, Any]:
        """Tornado risk analysis"""
        
        event_count = tornado_history.get("count", 0)
        
        if event_count == 0:
            return {
                "type": "tornado",
                "score_penalty": 0,
                "risk_level": "minimal",
                "event_count": 0,
                "risks": [],
                "mitigation_cost_per_unit": 0
            }
        elif event_count >= 5:
            return {
                "type": "tornado",
                "score_penalty": 12,
                "risk_level": "high",
                "event_count": event_count,
                "risks": [
                    f"{event_count} tornado declarations since 2004",
                    "Requires enhanced structural reinforcement",
                    "Safe rooms/storm shelters required",
                    "Higher construction standards"
                ],
                "mitigation_cost_per_unit": 10000  # Reinforced framing, safe rooms
            }
        else:
            return {
                "type": "tornado",
                "score_penalty": 5,
                "risk_level": "moderate",
                "event_count": event_count,
                "risks": [
                    f"{event_count} tornado declaration(s) since 2004",
                    "Consider enhanced wind resistance"
                ],
                "mitigation_cost_per_unit": 4000
            }
    
    def _analyze_hurricane_risk(
        self, 
        hurricane_history: Dict[str, Any],
        property_state: str = None,
        property_county: str = None
    ) -> Dict[str, Any]:
        """
        Hurricane risk analysis WITH GEOGRAPHIC FILTERING
        
        IMPORTANT: Hurricanes are COASTAL events (Gulf/Atlantic states)
        California, Nevada, Arizona, etc. should show ZERO hurricane risk
        even if state has historical tropical storm remnants
        """
        
        event_count = hurricane_history.get("count", 0)
        
        # GEOGRAPHIC FILTER: Hurricane-prone states (coastal Gulf/Atlantic)
        HURRICANE_STATES = [
            "FL", "LA", "TX", "MS", "AL", "GA", "SC", "NC", "VA", "MD", 
            "DE", "NJ", "NY", "CT", "RI", "MA", "NH", "ME", "HI"
        ]
        
        # If NOT in hurricane-prone state, return ZERO risk even if state has events
        if property_state and property_state not in HURRICANE_STATES:
            if event_count > 0:
                return {
                    "type": "hurricane",
                    "score_penalty": 0,
                    "risk_level": "not_applicable",
                    "event_count": event_count,
                    "risks": [],
                    "mitigation_cost_per_unit": 0,
                    "geographic_context": f"Hurricane risk: NOT APPLICABLE for {property_state}. {event_count} statewide tropical storm remnants listed for reference only. This is NOT a hurricane zone.",
                    "note": f"{event_count} statewide event(s) were tropical storm remnants, NOT hurricanes"
                }
            else:
                return {
                    "type": "hurricane",
                    "score_penalty": 0,
                    "risk_level": "not_applicable",
                    "event_count": 0,
                    "risks": [],
                    "mitigation_cost_per_unit": 0,
                    "geographic_context": f"Hurricane risk: NOT APPLICABLE for {property_state}"
                }
        
        # Only assess hurricane risk for coastal states
        if event_count == 0:
            return {
                "type": "hurricane",
                "score_penalty": 0,
                "risk_level": "minimal",
                "event_count": 0,
                "risks": [],
                "mitigation_cost_per_unit": 0
            }
        elif event_count >= 3:
            return {
                "type": "hurricane",
                "score_penalty": 15,
                "risk_level": "high",
                "event_count": event_count,
                "risks": [
                    f"{event_count} hurricane declarations since 2004",
                    "Requires hurricane-rated windows/doors",
                    "Enhanced roof tie-downs",
                    "Impact-resistant materials",
                    "Higher insurance costs"
                ],
                "mitigation_cost_per_unit": 12000  # Hurricane windows, reinforced roof
            }
        else:
            return {
                "type": "hurricane",
                "score_penalty": 6,
                "risk_level": "moderate",
                "event_count": event_count,
                "risks": [
                    f"{event_count} hurricane declaration(s) since 2004",
                    "Consider wind-resistant construction"
                ],
                "mitigation_cost_per_unit": 5000
            }
    
    def _analyze_earthquake_risk(
        self, 
        earthquake_history: Dict[str, Any],
        property_state: str = None
    ) -> Dict[str, Any]:
        """
        Earthquake risk analysis WITH GEOGRAPHIC CONTEXT
        
        NOTE: California, Alaska, and other seismic zones have inherent risk
        even if recent federal disaster declarations are low (most quakes don't
        trigger federal aid). Building codes already mandate seismic design.
        """
        
        event_count = earthquake_history.get("count", 0)
        
        # HIGH SEISMIC RISK STATES (always apply seismic standards)
        HIGH_SEISMIC_STATES = ["CA", "AK", "WA", "OR", "NV", "UT", "HI"]
        
        # For high seismic states, add context even if low event count
        if property_state in HIGH_SEISMIC_STATES:
            if event_count == 0:
                return {
                    "type": "earthquake",
                    "score_penalty": 5,  # Light penalty for inherent risk
                    "risk_level": "moderate",
                    "event_count": event_count,
                    "risks": [
                        f"ℹ️ {property_state} is in a high seismic risk zone",
                        "✓ Seismic building codes already mandated by state",
                        "✓ Standard California construction includes earthquake resistance",
                        "Note: Low federal disaster count doesn't mean low earthquake risk"
                    ],
                    "mitigation_cost_per_unit": 0,  # Already in building codes
                    "geographic_context": f"{property_state} seismic zone - codes mandate earthquake-resistant construction"
                }
            elif event_count >= 2:
                return {
                    "type": "earthquake",
                    "score_penalty": 18,
                    "risk_level": "high",
                    "event_count": event_count,
                    "risks": [
                        f"{event_count} earthquake declarations since 2004",
                        "Requires enhanced seismic design standards",
                        "Foundation reinforcement needed",
                        "Lateral bracing systems",
                        "Earthquake insurance required"
                    ],
                    "mitigation_cost_per_unit": 15000  # Enhanced seismic retrofitting
                }
            else:
                return {
                    "type": "earthquake",
                    "score_penalty": 8,
                    "risk_level": "moderate",
                    "event_count": event_count,
                    "risks": [
                        f"{event_count} earthquake declaration(s) since 2004",
                        f"✓ {property_state} building codes mandate seismic design",
                        "Standard seismic construction practices apply"
                    ],
                    "mitigation_cost_per_unit": 0  # Already in building codes
                }
        
        # For non-seismic states
        if event_count == 0:
            return {
                "type": "earthquake",
                "score_penalty": 0,
                "risk_level": "minimal",
                "event_count": 0,
                "risks": [],
                "mitigation_cost_per_unit": 0
            }
        elif event_count >= 2:
            return {
                "type": "earthquake",
                "score_penalty": 18,
                "risk_level": "high",
                "event_count": event_count,
                "risks": [
                    f"{event_count} earthquake declarations since 2004",
                    "Requires seismic design standards",
                    "Foundation reinforcement needed",
                    "Lateral bracing systems",
                    "Earthquake insurance required"
                ],
                "mitigation_cost_per_unit": 15000  # Seismic retrofitting
            }
        else:
            return {
                "type": "earthquake",
                "score_penalty": 8,
                "risk_level": "moderate",
                "event_count": event_count,
                "risks": [
                    f"{event_count} earthquake declaration(s) since 2004",
                    "Consider seismic design standards"
                ],
                "mitigation_cost_per_unit": 6000
            }
    
    def _get_disaster_recommendation(self, overall_risk_level: str, high_risk_count: int) -> str:
        """Get recommendation based on overall disaster risk"""
        
        if overall_risk_level == "very_high":
            return "CAUTION: Multiple high-risk natural hazards present. Conduct detailed feasibility study and cost-benefit analysis before proceeding."
        elif overall_risk_level == "high":
            return "High natural disaster risk. Ensure mitigation costs are included in pro forma and verify insurance availability."
        elif overall_risk_level == "moderate":
            return "Moderate risk level. Standard mitigation measures should be sufficient."
        else:
            return "Low natural disaster risk. Standard construction practices adequate."
    
    def _calculate_overall_score(
        self,
        location: float,
        market: float,
        financial: float,
        partnership: float,
        risk: float
    ) -> float:
        """Calculate weighted overall score"""
        
        weights = {
            "location": 0.25,
            "market": 0.25,
            "financial": 0.20,
            "partnership": 0.15,
            "risk": 0.15
        }
        
        overall = (
            location * weights["location"] +
            market * weights["market"] +
            financial * weights["financial"] +
            partnership * weights["partnership"] +
            risk * weights["risk"]
        )
        
        return round(overall, 1)
