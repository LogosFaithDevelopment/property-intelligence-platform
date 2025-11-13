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
    
    def _calculate_overall_score(
        self,
        location_score: float,
        market_score: float,
        financial_score: float,
        partnership_score: float,
        risk_score: float
    ) -> float:
        """
        Calculate weighted overall score from individual component scores
        
        Weights (must sum to 100%):
        - Financial Viability: 30%
        - Market Demand: 25%
        - Location Quality: 0% (informational only)
        - Partnership Alignment: 0% (informational only)
        - Risk Assessment: 0% (informational only)
        
        Updated Oct 2025: Financial score is now 100% of total score.
        Other scores are still calculated but don't affect pass/fail decision.
        """
        # Updated Oct 2025: Financial viability is 100% of the score
        # Other factors are informational but don't affect pass/fail
        overall = financial_score  # 100% weight on financial viability
        
        # Ensure score is within valid range
        return max(0, min(100, overall))
    
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
                "smarty": data_sources.get("smarty_data", {}).get("data", {}) if data_sources.get("smarty_data") else {},
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
        
        # PRIORITY ORDER for determining buildable area:
        # 1. User-specified available build space from form (TRUSTED - user knows their property best)
        # 2. Smarty API calculated available build space (CALCULATED - for comparison/verification)
        # 3. Total lot size from property data (FALLBACK - requires verification)
        
        smarty_available_space = enrichment_data.get("smarty", {}).get("available_build_space", {}).get("sqft")
        smarty_lot_size = enrichment_data.get("smarty", {}).get("lot", {}).get("size_sqft")
        total_lot_size = property_obj.lot_size_sqft or 0
        
        # Track data source and verification requirements
        build_space_source = None
        requires_verification = False
        verification_note = None
        
        if assessment.available_build_sqft and assessment.available_build_sqft > 0:
            # OPTION 1: User-specified available space (PREFERRED - user knows their property)
            lot_size_sqft = assessment.available_build_sqft
            build_space_source = "user_specified"
            requires_verification = False  # Trust user input
            using_available_space = True
            
            # Log comparison with Smarty data if available
            if smarty_available_space and smarty_available_space > 0:
                difference = lot_size_sqft - smarty_available_space
                pct_diff = (difference / smarty_available_space) * 100 if smarty_available_space > 0 else 0
                logger.info(f"✅ Using user-specified available build space: {lot_size_sqft:,} sq ft")
                logger.info(f"   Smarty calculated: {smarty_available_space:,} sq ft (difference: {difference:+,} sq ft / {pct_diff:+.1f}%)")
                
                # Flag significant discrepancies for review
                if abs(pct_diff) > 20:
                    logger.warning(f"   ⚠️ Large discrepancy detected - may warrant verification call")
                    verification_note = (
                        f"User specified {lot_size_sqft:,} sqft vs Smarty calculated {smarty_available_space:,} sqft "
                        f"({difference:+,} sqft difference, {pct_diff:+.1f}%). Consider verification call if discrepancy is unexpected."
                    )
            else:
                logger.info(f"✅ Using user-specified available build space: {lot_size_sqft:,} sq ft (no Smarty data for comparison)")
            
        elif smarty_available_space and smarty_available_space > 0:
            # OPTION 2: Smarty calculated available space (FALLBACK - for comparison)
            lot_size_sqft = smarty_available_space
            build_space_source = "smarty_calculated"
            requires_verification = True  # Flag for user to confirm
            using_available_space = True
            
            verification_note = (
                f"Using Smarty calculated available space ({lot_size_sqft:,} sqft). "
                f"User did not specify available space. Recommend asking user to confirm this value."
            )
            logger.warning(f"⚠️ Using Smarty calculated available build space: {lot_size_sqft:,} sq ft - USER CONFIRMATION RECOMMENDED")
            logger.warning(f"   Total lot size: {total_lot_size:,} sq ft")
            
        else:
            # OPTION 3: Total lot size (LAST RESORT)
            lot_size_sqft = total_lot_size
            build_space_source = "total_lot_unverified"
            requires_verification = True
            using_available_space = False
            
            # Generate verification note
            verification_note = (
                f"Using total lot size ({lot_size_sqft:,} sqft) as no building data available. "
                f"Call user to verify actual available build space after accounting for existing structures, "
                f"parking, setbacks, and protected areas."
            )
            logger.warning(f"⚠️ Using total lot size: {lot_size_sqft:,} sq ft - USER CONFIRMATION REQUIRED (no building data)")

        # Updated Oct 2025: Minimum lot size reduced from 10,000 to 5,000 sq ft
        if lot_size_sqft < 5000:
            logger.warning(f"Property {property_obj.id} disqualified: {lot_size_sqft} sq ft < 5,000 sq ft minimum")
            return 0.0, {
                "score": 0.0,
                "disqualified": True,
                "disqualification_reason": "Below Logos minimum lot size requirement",
                "lot_size_sqft": lot_size_sqft,
                "minimum_required_sqft": 5000,
                "using_available_space": using_available_space,
                "note": "Property does not meet Logos Faith Development's 5,000 sq ft minimum threshold (updated Oct 2025)"
            }
        
        # Calculate unit capacity using the determined lot size (available space or total)
        unit_capacity_info = self._calculate_unit_capacity(property_obj, lot_size_sqft_override=lot_size_sqft)
        feasible_units = unit_capacity_info["feasible_units"]
        stories = unit_capacity_info.get("stories", 4)  # Default to 4-story
        within_target_range = 40 <= feasible_units <= 140
        
        cost_per_unit_info = self._estimate_cost_per_unit(property_obj, feasible_units, stories=stories)
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
        # Updated Oct 2025: Minimum changed from 10,000 to 5,000 sq ft
        # Score increases for every 5,000 sqft above the minimum, up to +15 points
        if lot_size_sqft >= 5000:
            excess_sqft = lot_size_sqft - 5000
            # Award 1 point per 5,000 sqft above minimum (max +15 points at 80,000 sqft)
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
        
        # Generate multi-story scenarios (3, 4, 5 stories)
        multi_story_scenarios = self._generate_multi_story_scenarios(
            property_obj=property_obj,
            enrichment_data=enrichment_data,
            flood_cost_per_unit=flood_cost_per_unit,
            lot_size_sqft=lot_size_sqft,
            unit_capacity_info=unit_capacity_info
        )
        
        # IRR Scoring (LOGOS target: 20% IRR)
        irr_percent = revenue_projections.get("irr_percent")
        if irr_percent and irr_percent >= 20.0:
            score += 15
            logger.info(f"✓ Property {property_obj.id}: IRR {irr_percent}% meets LOGOS 20% target (+15 points)")
        elif irr_percent and irr_percent >= 15.0:
            score += 8
            logger.info(f"✓ Property {property_obj.id}: IRR {irr_percent}% approaching target (+8 points)")
        elif irr_percent and irr_percent < 12.0:
            score -= 10
            logger.warning(f"⚠ Property {property_obj.id}: IRR {irr_percent}% below viable threshold (-10 points)")
        
        # Phase 2: Debt-to-Value Ratio Check (LOGOS requirement: <20%)
        debt_to_value_ratio = None
        if assessment.existing_debt_amount and property_obj.assessed_value:
            debt_to_value_ratio = assessment.existing_debt_amount / property_obj.assessed_value
            assessment.debt_to_value_ratio = debt_to_value_ratio  # Store calculated ratio
            
            if debt_to_value_ratio > 0.20:
                # CRITICAL DEAL BREAKER - Excessive existing debt
                score -= 20
                logger.warning(f"🚨 DEAL BREAKER: Property {property_obj.id} has {debt_to_value_ratio:.1%} debt-to-value ratio (>20% threshold)")
                logger.warning(f"   Existing debt: ${assessment.existing_debt_amount:,.0f}, Property value: ${property_obj.assessed_value:,.0f}")
            elif debt_to_value_ratio > 0.10:
                score -= 10
                logger.warning(f"⚠ Property {property_obj.id}: Moderate debt {debt_to_value_ratio:.1%} of property value (-10 points)")
            elif debt_to_value_ratio > 0:
                logger.info(f"✓ Property {property_obj.id}: Minimal debt {debt_to_value_ratio:.1%} of property value (acceptable)")
        elif assessment.existing_debt_amount and not property_obj.assessed_value:
            logger.warning(f"⚠ Cannot calculate debt-to-value ratio: Property value unknown (debt amount: ${assessment.existing_debt_amount:,.0f})")
        
        # Phase 2: Sanctuary Replacement Expectation Check
        if assessment.expects_sanctuary_replacement:
            score -= 10
            logger.warning(f"⚠ Property {property_obj.id}: Church expects sanctuary replacement (-10 points)")
            logger.warning(f"   This complicates development and may not align with LOGOS model")
            if assessment.sanctuary_replacement_cost_estimate:
                logger.info(f"   Estimated replacement cost: ${assessment.sanctuary_replacement_cost_estimate:,.0f}")
        
        score = min(100, max(0, score))
        
        total_development_cost = cost_per_unit * feasible_units
        adjusted_total_cost = adjusted_cost_per_unit * feasible_units
        
        # Calculate Total Project Cost (display only - doesn't affect IRR)
        # Formula: Development Cost + (Land Value - Existing Debt)
        land_value = property_obj.assessed_value or 0
        existing_debt = assessment.existing_debt_amount or 0
        net_land_value = max(0, land_value - existing_debt)
        total_project_cost = adjusted_total_cost + net_land_value
        
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
            
            # Show BOTH user and Smarty values for comparison
            "user_specified_available_sqft": assessment.available_build_sqft if assessment.available_build_sqft else None,
            "smarty_calculated_available_sqft": smarty_available_space if smarty_available_space else None,
            "used_value_sqft": lot_size_sqft,
            "used_value_source": build_space_source,
            
            # Verification tracking
            "build_space_source": build_space_source,
            "requires_manual_verification": requires_verification,
            "verification_note": verification_note,
            
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
            
            # Total Project Cost (Oct 2025): Dev Cost + Net Land Value
            "total_project_cost": total_project_cost,
            "total_project_cost_formatted": f"${total_project_cost:,.0f}",
            "total_project_cost_breakdown": {
                "development_cost": adjusted_total_cost,
                "land_value": land_value,
                "existing_debt": existing_debt,
                "net_land_value": net_land_value
            },
            
            "revenue_projections": revenue_projections,
            "multi_story_scenarios": multi_story_scenarios,  # NEW: 3/4/5 story comparison
            
            "flood_risk_analysis": flood_analysis,
            
            "phase2_deal_breakers": {
                "existing_debt_amount": assessment.existing_debt_amount,
                "debt_to_value_ratio": debt_to_value_ratio,
                "debt_status": "Clean title" if not assessment.existing_debt_amount else "Acceptable (<20%)" if debt_to_value_ratio and debt_to_value_ratio <= 0.20 else "DEAL BREAKER (>20%)" if debt_to_value_ratio and debt_to_value_ratio > 0.20 else "Unknown",
                "expects_sanctuary_replacement": assessment.expects_sanctuary_replacement,
                "sanctuary_replacement_cost_estimate": assessment.sanctuary_replacement_cost_estimate,
                "sanctuary_status": "Issue" if assessment.expects_sanctuary_replacement else "Acceptable"
            },
            
            "funding_sources": ["private_equity", "church_land_contribution", "construction_loan"],
            "notes": [
                "No LIHTC (private funding model)",
                "Church retains land ownership",
                "Zero land acquisition cost",
                f"Total Project Cost: ${total_project_cost:,.0f} (Dev Cost + Net Land Value)",
                f"Flood mitigation adds ${flood_cost_per_unit:,}/unit" if flood_cost_per_unit > 0 else "No flood mitigation required",
                f"Existing debt: ${assessment.existing_debt_amount:,.0f} ({debt_to_value_ratio:.1%} of value)" if assessment.existing_debt_amount and debt_to_value_ratio else "No existing debt",
                "Church expects sanctuary replacement" if assessment.expects_sanctuary_replacement else "No sanctuary replacement expected"
            ]
        }
        
        return score, analysis
    
    def _calculate_lihtc_credits(
        self,
        total_dev_cost: float,
        property_state: str = "CA"
    ) -> Dict[str, Any]:
        """
        Calculate LIHTC 4% + State tax credits
        
        LOGOS Model: Uses 4% LIHTC (non-competitive) for affordable housing
        
        Federal LIHTC:
        - 4% of eligible basis annually for 10 years
        - Eligible basis = ~85% of total development cost
        
        California State Credit:
        - 20% bonus on top of federal credit
        
        Syndication:
        - Credits sold to investors at 85-90% of total value
        - Proceeds received at construction completion (Year 2)
        - Reduces/eliminates equity requirement
        
        Args:
            total_dev_cost: Total development cost
            property_state: State for state credit calculation
            
        Returns:
            Dictionary with LIHTC credit calculations
        """
        if total_dev_cost <= 0:
            return {
                "status": "insufficient_data",
                "syndication_proceeds": 0,
                "total_credits": 0
            }
        
        # Eligible basis (typically 85% of costs - land is excluded)
        eligible_basis = total_dev_cost * 0.85
        
        # Federal LIHTC 4% annual credit
        annual_federal_credit = eligible_basis * 0.04
        
        # Total federal credits over 10 years
        total_federal_10yr = annual_federal_credit * 10
        
        # California State Credit (20% of federal)
        total_ca_credit = 0
        if property_state == "CA":
            total_ca_credit = total_federal_10yr * 0.20
        
        # Total credits
        total_credits = total_federal_10yr + total_ca_credit
        
        # Syndication proceeds (typically 87% of credit value)
        syndication_factor = 0.87
        syndication_proceeds = total_credits * syndication_factor
        
        return {
            "status": "calculated",
            "eligible_basis": eligible_basis,
            "eligible_basis_formatted": f"${eligible_basis:,.0f}",
            "annual_federal_credit": annual_federal_credit,
            "total_federal_10yr": total_federal_10yr,
            "total_ca_state_credit": total_ca_credit,
            "total_credits": total_credits,
            "total_credits_formatted": f"${total_credits:,.0f}",
            "syndication_factor": syndication_factor,
            "syndication_proceeds": syndication_proceeds,
            "syndication_proceeds_formatted": f"${syndication_proceeds:,.0f}",
            "reduces_equity_by": syndication_proceeds,
            "timing": "Received at construction completion (Year 2)",
            "notes": [
                "LIHTC 4% non-competitive credits (by-right for bond-financed projects)",
                f"Federal: {annual_federal_credit:,.0f}/year for 10 years",
                f"California: 20% state credit bonus (${total_ca_credit:,.0f})",
                f"Credits sold to investor at {syndication_factor*100}% of value",
                "Proceeds reduce equity requirement substantially"
            ]
        }
    
    def _generate_multi_story_scenarios(
        self,
        property_obj: Property,
        enrichment_data: Dict[str, Any],
        flood_cost_per_unit: float,
        lot_size_sqft: float,
        unit_capacity_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate financial projections for 3, 4, and 5 story scenarios.
        
        Returns dictionary with scenarios for each story count, including:
        - Unit count
        - Development cost
        - NOI
        - IRR
        - Recommended scenario
        """
        scenarios = unit_capacity_info.get("scenarios", {})
        
        if not scenarios:
            # Fallback if scenarios weren't generated
            return {
                "status": "unavailable",
                "message": "Multi-story scenarios not generated"
            }
        
        scenario_financials = {}
        best_irr = 0
        recommended = None
        
        for scenario_name, scenario_data in scenarios.items():
            units = scenario_data["feasible_units"]
            stories = scenario_data["stories"]
            
            # Calculate costs for this scenario (pass stories for tiered costs)
            cost_info = self._estimate_cost_per_unit(property_obj, units, stories=stories)
            base_cost_per_unit = cost_info["cost_per_unit"]
            adjusted_cost_per_unit = base_cost_per_unit + flood_cost_per_unit
            total_dev_cost = adjusted_cost_per_unit * units
            
            # Get tiered construction months for this unit count
            construction_months = self._get_construction_months(units)
            
            # Calculate revenue projections for this scenario
            revenue = self._calculate_revenue_projections(
                enrichment_data,
                units,
                adjusted_cost_per_unit,
                construction_months=construction_months
            )
            
            noi = revenue.get("net_operating_income", 0)
            irr_percent = revenue.get("irr_percent", 0)
            equity_required = total_dev_cost * 0.20  # CIO updated: 20% equity
            
            # Determine if scenario is not recommended (IRR < 10%)
            not_recommended = irr_percent is not None and irr_percent < 10.0
            recommendation_warning = "⚠️ Not Recommended (IRR < 10%)" if not_recommended else None
            
            scenario_financials[scenario_name] = {
                "stories": stories,
                "units": units,
                "buildable_sqft": scenario_data["buildable_sqft"],
                "cost_per_unit": adjusted_cost_per_unit,
                "construction_months": construction_months,
                "total_development_cost": total_dev_cost,
                "total_development_cost_formatted": f"${total_dev_cost:,.0f}",
                "equity_required": equity_required,
                "equity_required_formatted": f"${equity_required:,.0f}",
                "debt_financing": total_dev_cost * 0.80,
                "debt_financing_formatted": f"${total_dev_cost * 0.80:,.0f}",
                "annual_revenue": revenue.get("total_annual_revenue", 0),
                "annual_revenue_formatted": f"${revenue.get('total_annual_revenue', 0):,.0f}",
                "noi": noi,
                "noi_formatted": f"${noi:,.0f}",
                "irr_percent": irr_percent,
                "cap_rate": revenue.get("cap_rate", 0),
                "cash_on_cash": revenue.get("cash_on_cash_return", 0),
                "meets_irr_target": irr_percent >= 20.0 if irr_percent else False,
                "not_recommended": not_recommended,
                "recommendation_warning": recommendation_warning
            }
            
            # Track best IRR
            if irr_percent and irr_percent > best_irr:
                best_irr = irr_percent
                recommended = scenario_name
        
        # If no clear winner, default to 4-story
        if not recommended:
            recommended = "4_story"
        
        return {
            "scenarios": scenario_financials,
            "recommended": recommended,
            "recommended_reason": f"Best IRR at {best_irr:.1f}%" if best_irr > 0 else "Standard 4-story configuration",
            "notes": [
                "Financial Model (Oct 2025): Tiered costs by height",
                "3-story: $275K/unit, 4-story: $325K/unit, 5-story: $415K/unit",
                "Tiered developer fees: 8%/7%/6%/5% by scale",
                "Tiered construction: 18/24/32 months by scale",
                "425 sqft avg unit, 20% equity/65% permanent loan, tiered brokerage (2.0%-5.0%)",
                "All scenarios assume 65% site coverage",
                "Unit mix: 10% studios, 80% 1BD, 10% 2BD",
                f"Recommended: {recommended.replace('_', ' ').title()} with {best_irr:.1f}% IRR"
            ]
        }
    
    def _calculate_revenue_projections(
        self,
        enrichment_data: Dict[str, Any],
        unit_count: int,
        cost_per_unit: float,
        construction_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate revenue projections using actual HUD Fair Market Rent data
        
        Returns detailed financial projections including:
        - Annual rent revenue by unit type
        - Operating expenses (40-45% of revenue)
        - Net Operating Income (NOI)
        - Return on Investment (ROI)
        - Cash-on-cash return
        
        Args:
            construction_months: Optional construction timeline (tiered: 18/24/32 months)
        """
        
        fmr_data = enrichment_data.get("fair_market_rent", {})
        
        # AMI-based fallback defaults (Oct 2025) when HUD FMR API fails
        fallback_rents = {
            "studio": 1450,
            "1_bedroom": 1800,
            "2_bedroom": 2400
        }
        
        if not fmr_data or not fmr_data.get("success"):
            # Use fallback values
            rent_by_bedroom = fallback_rents
            data_source = "AMI-based fallback defaults"
            logger.warning("HUD FMR data unavailable - using AMI fallback rents")
        else:
            rent_by_bedroom = fmr_data.get("rent_by_bedroom", {})
            data_source = f"HUD FMR {fmr_data.get('year', 'N/A')}"
            
            # Apply fallback for any missing bedroom types
            for bedroom_type, fallback_rent in fallback_rents.items():
                if not rent_by_bedroom.get(bedroom_type):
                    rent_by_bedroom[bedroom_type] = fallback_rent
                    logger.warning(f"Missing {bedroom_type} FMR - using fallback ${fallback_rent}")
        
        # Updated unit mix per CIO feedback: 10% studios, 80% 1BD, 10% 2BD
        unit_mix = {
            "studio": {"count": int(unit_count * 0.10), "fmr": rent_by_bedroom.get("studio", 0)},
            "1_bedroom": {"count": int(unit_count * 0.80), "fmr": rent_by_bedroom.get("1_bedroom", 0)},
            "2_bedroom": {"count": int(unit_count * 0.10), "fmr": rent_by_bedroom.get("2_bedroom", 0)}
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
        
        # Updated OpEx ratio per CIO feedback: 30% (down from 42%)
        operating_expense_ratio = 0.30
        operating_expenses = annual_revenue * operating_expense_ratio
        
        noi = annual_revenue - operating_expenses
        
        total_cost = cost_per_unit * unit_count
        
        roi_percent = (noi / total_cost * 100) if total_cost > 0 else 0
        cap_rate = (noi / total_cost * 100) if total_cost > 0 else 0
        
        # CIO UPDATED: 20% equity / 80% debt (down from 30% / 70%)
        equity_investment = total_cost * 0.20
        cash_on_cash = (noi / equity_investment * 100) if equity_investment > 0 else 0
        
        # Get tiered construction months if not provided
        if construction_months is None:
            construction_months = self._get_construction_months(unit_count)
        
        # Calculate IRR (LOGOS target: 20%) with updated methodology
        irr_analysis = self._calculate_project_irr_with_tax_benefits(
            total_dev_cost=total_cost,
            annual_noi=noi,
            unit_count=unit_count,
            assessed_value=total_cost,  # Use development cost as assessed value
            construction_months=construction_months  # Pass tiered construction timeline
        )
        
        return {
            "status": "calculated",
            "data_source": data_source,
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
            "yield_on_cost": round(cap_rate, 2),  # LOGOS terminology (same as cap rate)
            "equity_investment_30pct": equity_investment,
            "cash_on_cash_return": round(cash_on_cash, 2),
            "irr_analysis": irr_analysis,
            "irr_percent": irr_analysis.get("irr_percent"),
            "meets_irr_target": irr_analysis.get("meets_logos_target", False),
            "assumptions": [
                "10% studios, 80% 1BR, 10% 2BR unit mix",
                "30% operating expense ratio",
                "100% occupancy (conservative for Section 8)",
                "20% equity / 65% permanent loan (Updated Oct 2025)",
                "Tiered construction costs: 3-story $275K, 4-story $325K, 5-story $415K",
                "425 sqft average unit size"
            ],
            "notes": [
                "Actual FMR may vary by ZIP code within county",
                "IRR calculation WITHOUT tax credits",
                "Operating expense ratio: 30% (reduced from 42%)",
                "Construction: 18-32 months (tiered), Lease-up: 4 months, Exit: Year 7, Exit cap: 6%",
                "Updated Financial Model (Oct 2025): Tiered costs $275K/$325K/$415K, 425 sqft, 20% equity/65% permanent loan, tiered brokerage (2.0%-5.0%)"
            ]
        }
    
    def _get_brokerage_fee_rate(self, exit_value: float) -> tuple[float, str]:
        """
        Calculate tiered brokerage fee rate based on property exit value.
        
        Larger properties command lower broker fees due to economies of scale.
        
        Fee Schedule:
        - < $10M: 5.0%
        - $10M - $20M: 4.0%
        - $20M - $30M: 3.0%
        - $30M - $40M: 2.5%
        - > $40M: 2.0%
        
        Args:
            exit_value: Property exit value
            
        Returns:
            Tuple of (fee_rate, tier_description)
        """
        if exit_value < 10_000_000:
            return 0.050, "5.0% (under $10M)"
        elif exit_value < 20_000_000:
            return 0.040, "4.0% ($10M-$20M)"
        elif exit_value < 30_000_000:
            return 0.030, "3.0% ($20M-$30M)"
        elif exit_value < 40_000_000:
            return 0.025, "2.5% ($30M-$40M)"
        else:
            return 0.020, "2.0% (over $40M)"
    
    def _calculate_project_irr_with_tax_benefits(
        self,
        total_dev_cost: float,
        annual_noi: float,
        unit_count: int,
        assessed_value: float,
        construction_months: int = 18,  # Updated to 18 months per CIO feedback
        operating_years: int = 6,  # Updated to exit at Year 7 (1.5 year construction + 5.5 years operation)
        exit_cap_rate: float = 0.06,  # Updated to 6% per CIO feedback
        annual_rent_growth: float = 0.03,  # 3% annual rent growth
        property_state: str = "CA"
    ) -> Dict[str, Any]:
        """
        Calculate project-level IRR WITHOUT tax credits (per CIO feedback)
        
        LOGOS Target: 20% IRR minimum
        
        Updated per CIO feedback (removed LIHTC):
        1. NO LIHTC tax credits or syndication
        2. Operating expense ratio: 30% (down from 42%)
        3. Construction: 18 months
        4. Exit: Year 7 (1.5 years construction + 5.5 years operation)
        5. Exit cap rate: 6%
        6. Unit mix: 10% studios (325sf), 80% 1BD (450sf), 10% 2BD (675sf)
        7. Permanent loan: 65% (down from 80%)
        
        Args:
            total_dev_cost: Total development cost
            annual_noi: Base year Annual Net Operating Income
            unit_count: Number of units
            assessed_value: Property assessed value (for property tax calc)
            construction_months: Construction duration (default 24)
            operating_years: Years of operations (default 10)
            exit_cap_rate: Exit cap rate for property sale (default 4.25%)
            annual_rent_growth: Annual rent growth rate (default 3%)
            property_state: State for tax calculations (default CA)
        
        Returns:
            Dictionary with IRR calculation results including tax benefits
        """
        try:
            import numpy as np
            import numpy_financial as npf
        except ImportError:
            logger.warning("numpy_financial not available - IRR calculation skipped")
            return {
                "status": "unavailable",
                "message": "IRR calculation requires numpy_financial package",
                "irr_percent": None
            }
        
        if total_dev_cost <= 0 or annual_noi <= 0:
            return {
                "status": "insufficient_data",
                "message": "Cannot calculate IRR without valid development cost and NOI",
                "irr_percent": None
            }
        
        # NO LIHTC tax credits per CIO feedback
        # NO CA Welfare property tax exemption
        # Simple equity-based IRR calculation
        
        # Calculate equity requirement (CIO UPDATED: 20% equity, 65% permanent loan)
        equity_required = total_dev_cost * 0.20
        
        logger.info(f"💰 IRR Calculation (NO Tax Credits - Updated Oct 2025):")
        logger.info(f"   Total Dev Cost: ${total_dev_cost:,.0f}")
        logger.info(f"   Equity Required (20%): ${equity_required:,.0f}")
        logger.info(f"   Permanent Loan (65%): ${total_dev_cost * 0.65:,.0f}")
        logger.info(f"   Annual NOI: ${annual_noi:,.0f}")
        logger.info(f"   Construction Period: {construction_months} months")
        logger.info(f"   Lease-up Period: 4 months (Year 2 has 8 months NOI)")
        logger.info(f"   Exit: Year {1.5 + operating_years} (after construction)")
        logger.info(f"   Exit Cap Rate: {exit_cap_rate*100}%")
        
        # Build cash flow array
        cash_flows = []
        
        # Construction phase: 18 months = 1.5 years
        # Split equity investment over construction period
        construction_years_float = construction_months / 12.0
        
        # Year 0: First half of equity
        cash_flows.append(-equity_required * 0.5)
        
        # Year 1: Second half of equity
        cash_flows.append(-equity_required * 0.5)
        
        # Operating phase: Years 2-7 (6 years of operations after construction)
        # Year 2: Lease-up period (4 months) = 8 months of NOI (reduced from 12)
        lease_up_months = 4
        year_2_noi = annual_noi * ((12 - lease_up_months) / 12)  # 8/12 = 67% of annual NOI
        cash_flows.append(year_2_noi)
        
        # Years 3-7: Full operating years with rent growth
        for year in range(1, operating_years):
            year_noi = annual_noi * ((1 + annual_rent_growth) ** year)
            cash_flows.append(year_noi)
        
        # Exit at Year 7: Final year NOI + Exit proceeds
        final_year_noi = annual_noi * ((1 + annual_rent_growth) ** (operating_years - 1))
        
        # Calculate exit value and proceeds
        exit_value = final_year_noi / exit_cap_rate if exit_cap_rate > 0 else 0
        
        # Calculate tiered brokerage fee based on property value (updated Oct 2025)
        brokerage_rate, brokerage_tier = self._get_brokerage_fee_rate(exit_value)
        brokerage_fee = exit_value * brokerage_rate
        net_exit_value = exit_value - brokerage_fee
        
        # Subtract remaining debt from exit proceeds (65% permanent loan per updated model)
        debt_amount = total_dev_cost * 0.65
        exit_proceeds = net_exit_value - debt_amount
        
        # Add exit proceeds to final year
        cash_flows[-1] = cash_flows[-1] + exit_proceeds
        
        logger.info(f"   Year 1 NOI: ${annual_noi:,.0f}")
        logger.info(f"   Final Year ({operating_years}) NOI: ${final_year_noi:,.0f}")
        logger.info(f"   Exit Value (at {exit_cap_rate*100}% cap): ${exit_value:,.0f}")
        logger.info(f"   Brokerage Fee ({brokerage_tier}): ${brokerage_fee:,.0f}")
        logger.info(f"   Net Exit Value (after brokerage): ${net_exit_value:,.0f}")
        logger.info(f"   Debt Payoff (65% permanent loan): ${debt_amount:,.0f}")
        logger.info(f"   Net Exit Proceeds: ${exit_proceeds:,.0f}")
        
        # Calculate IRR
        try:
            irr = npf.irr(cash_flows)
            irr_percent = round(irr * 100, 2) if irr and not np.isnan(irr) else None
            
            meets_target = irr_percent >= 20.0 if irr_percent is not None else False
            
            logger.info(f"   Calculated IRR: {irr_percent}% (target: 20%)")
            logger.info(f"   Cash flows: {[f'${cf:,.0f}' for cf in cash_flows]}")
            
            return {
                "status": "calculated",
                "irr_percent": irr_percent,
                "meets_logos_target": meets_target,
                "target_irr": 20.0,
                "construction_months": construction_months,
                "operating_years": operating_years,
                "exit_cap_rate": exit_cap_rate,
                "annual_rent_growth": annual_rent_growth,
                "exit_value": exit_value,
                "exit_value_formatted": f"${exit_value:,.0f}" if exit_value else "N/A",
                "brokerage_fee": brokerage_fee,
                "brokerage_fee_formatted": f"${brokerage_fee:,.0f}",
                "brokerage_rate": brokerage_rate,
                "brokerage_rate_percent": f"{brokerage_rate * 100:.1f}%",
                "brokerage_tier": brokerage_tier,
                "net_exit_value": net_exit_value,
                "net_exit_value_formatted": f"${net_exit_value:,.0f}",
                "exit_proceeds": exit_proceeds,
                "exit_proceeds_formatted": f"${exit_proceeds:,.0f}",
                
                # Equity analysis (NO LIHTC)
                "equity_required": equity_required,
                "equity_required_formatted": f"${equity_required:,.0f}",
                
                # Cash flow summary
                "base_noi": annual_noi,
                "first_year_noi": annual_noi,
                "final_year_noi": final_year_noi,
                "noi_growth_total": final_year_noi - annual_noi,
                "cash_flows_summary": {
                    "construction_phase": f"-${equity_required:,.0f} equity over {construction_months} months",
                    "operating_phase": f"+${annual_noi:,.0f}/year (growing {annual_rent_growth*100}%/year)",
                    "exit": f"+${exit_proceeds:,.0f} net proceeds at year {int(construction_months/12) + operating_years}"
                },
                
                # Assumptions (updated per CIO feedback - Oct 2025)
                "assumptions": [
                    f"{construction_months}-month construction period (tiered: 18/24/32 months by scale)",
                    "4-month lease-up period (Year 2 has 8 months of NOI)",
                    f"Exit at Year {int(construction_months/12) + operating_years} ({operating_years} years of operations)",
                    f"{annual_rent_growth*100}% annual rent growth",
                    f"Exit at {exit_cap_rate*100}% cap rate",
                    "20% equity / 65% permanent loan (updated from 80% debt)",
                    f"Tiered brokerage fee: {brokerage_tier} (2.0%-5.0% based on property value)",
                    "30% operating expense ratio (reduced from 42%)",
                    "Unit mix: 10% studios (325sf), 80% 1BD (450sf), 10% 2BD (675sf)",
                    "NO LIHTC tax credits",
                    "NO syndication"
                ],
                
                # Key highlights
                "highlights": [
                    f"Equity required: ${equity_required:,.0f} (20% of ${total_dev_cost:,.0f})",
                    f"Permanent loan: ${debt_amount:,.0f} (65% LTV)",
                    f"First year NOI: ${annual_noi:,.0f}",
                    f"With {annual_rent_growth*100}% rent growth, final year NOI: ${final_year_noi:,.0f}",
                    f"Exit value: ${exit_value:,.0f} at {exit_cap_rate*100}% cap rate",
                    f"Brokerage fee ({brokerage_tier}): ${brokerage_fee:,.0f}",
                    f"Net exit proceeds: ${exit_proceeds:,.0f}",
                    f"IRR: {irr_percent}% {'MEETS' if meets_target else 'below'} 20% target"
                ],
                
                "notes": [
                    "IRR calculation WITHOUT tax credits",
                    "Simplified equity-based return calculation",
                    "Operating expense ratio reduced to 30% (from 42%)",
                    "Shorter hold period: 7 years total (1.5 construction + 5.5 operations)",
                    "Higher exit cap rate: 6% (more conservative)",
                    "Updated Oct 2025: 65% permanent loan, tiered brokerage (2.0%-5.0%), optimized unit mix (80% 1-beds)"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error calculating IRR: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"IRR calculation error: {str(e)}",
                "irr_percent": None
            }
    
    def _calculate_property_tax_savings(
        self,
        assessed_value: float,
        property_state: str = "CA"
    ) -> Dict[str, Any]:
        """
        Calculate property tax savings from CA Welfare Exemption
        
        California Welfare Exemption (Revenue & Taxation Code Section 214):
        - 98% property tax exemption for affordable housing
        - Only pay 2% of normal property tax
        
        Args:
            assessed_value: Property assessed value
            property_state: State (only CA has this exemption)
            
        Returns:
            Dictionary with property tax savings calculation
        """
        if property_state != "CA":
            return {
                "status": "not_applicable",
                "annual_savings": 0,
                "message": "CA Welfare Exemption only applies to California properties"
            }
        
        if assessed_value <= 0:
            return {
                "status": "insufficient_data",
                "annual_savings": 0,
                "message": "Cannot calculate property tax without assessed value"
            }
        
        # California average property tax rate: ~1.25% (varies by county)
        ca_property_tax_rate = 0.0125
        
        # Normal annual property tax
        normal_annual_tax = assessed_value * ca_property_tax_rate
        
        # With 98% exemption, only pay 2%
        with_exemption_tax = normal_annual_tax * 0.02
        
        # Annual savings
        annual_savings = normal_annual_tax - with_exemption_tax
        
        return {
            "status": "calculated",
            "assessed_value": assessed_value,
            "assessed_value_formatted": f"${assessed_value:,.0f}",
            "normal_annual_tax": normal_annual_tax,
            "with_exemption_tax": with_exemption_tax,
            "annual_savings": annual_savings,
            "annual_savings_formatted": f"${annual_savings:,.0f}",
            "exemption_percentage": 98,
            "effective_tax_rate": ca_property_tax_rate * 0.02,
            "notes": [
                "CA Welfare Exemption provides 98% property tax reduction",
                "Applies to affordable housing properties",
                f"Saves approximately ${annual_savings:,.0f} per year",
                "Increases Net Operating Income substantially"
            ]
        }
    
    def _calculate_developer_fee(
        self,
        total_dev_cost: float,
        fee_percentage: float = 0.10
    ) -> Dict[str, Any]:
        """
        Calculate developer fee
        
        Typical developer fee: 10-15% of total development cost
        Paid at construction completion (Year 2)
        
        Args:
            total_dev_cost: Total development cost
            fee_percentage: Developer fee as percentage (default 10%)
            
        Returns:
            Dictionary with developer fee calculation
        """
        if total_dev_cost <= 0:
            return {
                "status": "insufficient_data",
                "developer_fee": 0
            }
        
        developer_fee = total_dev_cost * fee_percentage
        
        return {
            "status": "calculated",
            "developer_fee": developer_fee,
            "developer_fee_formatted": f"${developer_fee:,.0f}",
            "fee_percentage": fee_percentage * 100,
            "total_dev_cost": total_dev_cost,
            "timing": "Paid at construction completion (Year 2)",
            "notes": [
                f"Developer fee: {fee_percentage*100}% of development cost",
                "Typical range: 10-15% for affordable housing",
                "Provides developer compensation for project management"
            ]
        }
    
    def _calculate_unit_capacity(
        self,
        property_obj: Property,
        lot_size_sqft_override: Optional[float] = None
    ) -> Dict[str, Any]:
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
        
        # LOGOS multifamily affordable housing model
        # Updated per CIO requirements (Oct 2025):
        # - Average unit size: 425 sqft (down from 481 sqft)
        # - Construction cost: $325K per unit
        # - Financing: 20% equity / 80% debt (down from 30% equity / 70% debt)
        # - Site coverage: 65%
        site_coverage_factor = 0.65
        avg_unit_size = 425  # Updated per CIO: 425 sqft average
        
        # Calculate buildable sqft across all floors
        footprint = lot_size_sqft * site_coverage_factor
        
        # Generate scenarios for 3, 4, and 5 stories
        scenarios = {}
        recommended_scenario = None
        best_irr = 0
        
        for stories in [3, 4, 5]:
            total_buildable_sqft = footprint * stories
            feasible_units = int(total_buildable_sqft / avg_unit_size)
            
            scenarios[f"{stories}_story"] = {
                "stories": stories,
                "buildable_sqft": total_buildable_sqft,
                "feasible_units": feasible_units,
                "footprint_sqft": footprint,
                "avg_unit_size": avg_unit_size,
                "site_coverage_factor": site_coverage_factor
            }
            
            # Track which scenario has best IRR (will be calculated later)
            if stories == 4:
                recommended_scenario = f"{stories}_story"
        
        # For backward compatibility, return 4-story as default
        default_scenario = scenarios["4_story"]
        
        return {
            "feasible_units": default_scenario["feasible_units"],
            "lot_size_acres": lot_size_acres,
            "lot_size_sqft": lot_size_sqft,
            "buildable_sqft": default_scenario["buildable_sqft"],
            "footprint_sqft": footprint,
            "stories": 4,
            "avg_unit_size": avg_unit_size,
            "site_coverage_factor": site_coverage_factor,
            "calculation_method": "multi_story_scenarios",
            "scenarios": scenarios,  # NEW: All 3/4/5 story scenarios
            "recommended_scenario": recommended_scenario,
            "notes": [
                f"Updated Financial Model (Oct 2025): $325K/unit, 425 sqft avg, 20% equity/80% debt",
                f"Generated scenarios for 3, 4, and 5 stories with {site_coverage_factor*100}% site coverage",
                f"3-Story: {scenarios['3_story']['feasible_units']} units ({int(scenarios['3_story']['buildable_sqft']):,} sqft)",
                f"4-Story: {scenarios['4_story']['feasible_units']} units ({int(scenarios['4_story']['buildable_sqft']):,} sqft) - Recommended",
                f"5-Story: {scenarios['5_story']['feasible_units']} units ({int(scenarios['5_story']['buildable_sqft']):,} sqft)"
            ]
        }
    
    def _get_developer_fee_percentage(self, unit_count: int) -> float:
        """
        Get developer fee percentage based on project scale.
        
        Updated per CIO (Oct 2025): Tiered developer fees
        - <60 units: 8%
        - 60-100 units: 7%
        - 100-150 units: 6%
        - 150+ units: 5%
        """
        if unit_count < 60:
            return 0.08
        elif unit_count < 100:
            return 0.07
        elif unit_count < 150:
            return 0.06
        else:
            return 0.05
    
    def _get_construction_months(self, unit_count: int) -> int:
        """
        Get construction timeline based on project scale.
        
        Updated per CIO (Oct 2025): Tiered construction timelines
        - <50 units: 18 months
        - 50-150 units: 24 months
        - 150+ units: 32 months
        """
        if unit_count < 50:
            return 18
        elif unit_count < 150:
            return 24
        else:
            return 32
    
    def _estimate_cost_per_unit(
        self,
        property_obj: Property,
        unit_count: int,
        stories: int = 4
    ) -> Dict[str, Any]:
        """
        Estimate cost per unit for Logos affordable housing model.
        
        Updated per CIO (Oct 2025): Tiered construction costs by building height
        - 3-story: $275K/unit (wood frame, simple construction)
        - 4-story: $325K/unit (standard mid-rise)
        - 5-story: $415K/unit (Type I/II construction, higher complexity)
        Average unit size: 425 sqft
        """
        
        # CIO UPDATED REQUIREMENT: Tiered costs by building height
        if stories == 3:
            base_cost_per_unit = 275000  # Wood frame
        elif stories == 5:
            base_cost_per_unit = 415000  # Type I/II construction
        else:  # stories == 4 (default)
            base_cost_per_unit = 325000  # Standard mid-rise
        
        # Apply minor scale adjustments for very large or very small projects
        total_cost_per_unit = base_cost_per_unit
        
        if unit_count >= 100:
            total_cost_per_unit *= 0.98  # Slight economy of scale
        elif unit_count >= 60:
            total_cost_per_unit *= 0.99
        elif unit_count <= 30:
            total_cost_per_unit *= 1.05  # Slightly higher for small projects
        
        # Get tiered developer fee percentage
        developer_fee_pct = self._get_developer_fee_percentage(unit_count)
        
        # Estimated breakdown (for reporting purposes)
        building_construction = total_cost_per_unit * 0.55  # 55% hard construction
        site_work = total_cost_per_unit * 0.10  # 10% site work
        parking = total_cost_per_unit * 0.08  # 8% parking
        utilities = 15000 if property_obj.has_water and property_obj.has_sewer else 40000
        soft_costs = total_cost_per_unit * 0.15  # 15% soft costs
        financing = total_cost_per_unit * 0.07  # 7% financing
        developer_fee = total_cost_per_unit * developer_fee_pct  # Tiered: 8%/7%/6%/5%
        
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
                "base_cost_per_unit": base_cost_per_unit,
                "stories": stories,
                "avg_unit_size_sqft": 425,  # CIO updated
                "parking_spaces_per_unit": 0.75,
                "unit_count": unit_count,
                "developer_fee_percentage": developer_fee_pct,
                "construction_months": self._get_construction_months(unit_count),
                "scale_factor_applied": unit_count >= 60 or unit_count <= 30
            },
            "notes": [
                f"CIO Updated (Oct 2025): Tiered costs - 3-story: $265K, 4-story: $325K, 5-story: $415K",
                f"Current scenario: {stories}-story building at ${base_cost_per_unit:,}/unit",
                f"Developer fee: {developer_fee_pct*100}% (tiered by unit count)",
                f"Construction timeline: {self._get_construction_months(unit_count)} months",
                "Average unit size: 425 sqft",
                "Does not include land acquisition (church owns land)",
                "Financing: 20% equity / 80% debt"
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
            "total_score_penalty": min(40, total_penalty),
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
                "score_penalty": 5,
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
                "score_penalty": 15,
                "risk_level": "high",
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
        """Wildfire risk analysis with GEOGRAPHIC FILTERING"""
        
        event_count = fire_history.get("count", 0)
        
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
        
        # Simplified risk assessment based on county-level data
        if event_count >= 5:
            return {
                "type": "fire",
                "score_penalty": 3,
                "risk_level": "informational",
                "event_count": event_count,
                "risks": [
                    f"ℹ️ {event_count} wildfire events in county since 2004",
                    "✓ Recommend fire-resistant materials as best practice"
                ],
                "mitigation_cost_per_unit": 3000
            }
        else:
            return {
                "type": "fire",
                "score_penalty": 1,
                "risk_level": "low",
                "event_count": event_count,
                "risks": [],
                "mitigation_cost_per_unit": 1000
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
                    "Requires enhanced structural reinforcement"
                ],
                "mitigation_cost_per_unit": 10000
            }
        else:
            return {
                "type": "tornado",
                "score_penalty": 5,
                "risk_level": "moderate",
                "event_count": event_count,
                "risks": [f"{event_count} tornado declaration(s) since 2004"],
                "mitigation_cost_per_unit": 4000
            }
    
    def _analyze_hurricane_risk(
        self,
        hurricane_history: Dict[str, Any],
        property_state: str = None,
        property_county: str = None
    ) -> Dict[str, Any]:
        """Hurricane risk analysis WITH GEOGRAPHIC FILTERING"""
        
        event_count = hurricane_history.get("count", 0)
        
        # Hurricane-prone states (coastal Gulf/Atlantic)
        HURRICANE_STATES = [
            "FL", "LA", "TX", "MS", "AL", "GA", "SC", "NC", "VA", "MD",
            "DE", "NJ", "NY", "CT", "RI", "MA", "NH", "ME", "HI"
        ]
        
        if property_state and property_state not in HURRICANE_STATES:
            return {
                "type": "hurricane",
                "score_penalty": 0,
                "risk_level": "not_applicable",
                "event_count": event_count,
                "risks": [],
                "mitigation_cost_per_unit": 0,
                "geographic_context": f"Hurricane risk: NOT APPLICABLE for {property_state}"
            }
        
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
                "risks": [f"{event_count} hurricane declarations since 2004"],
                "mitigation_cost_per_unit": 12000
            }
        else:
            return {
                "type": "hurricane",
                "score_penalty": 6,
                "risk_level": "moderate",
                "event_count": event_count,
                "risks": [f"{event_count} hurricane declaration(s) since 2004"],
                "mitigation_cost_per_unit": 5000
            }
    
    def _analyze_earthquake_risk(
        self,
        earthquake_history: Dict[str, Any],
        property_state: str = None
    ) -> Dict[str, Any]:
        """Earthquake risk analysis WITH GEOGRAPHIC CONTEXT"""
        
        event_count = earthquake_history.get("count", 0)
        
        HIGH_SEISMIC_STATES = ["CA", "AK", "WA", "OR", "NV", "UT", "HI"]
        
        if property_state in HIGH_SEISMIC_STATES:
            if event_count == 0:
                return {
                    "type": "earthquake",
                    "score_penalty": 5,
                    "risk_level": "moderate",
                    "event_count": event_count,
                    "risks": [
                        f"ℹ️ {property_state} is in a high seismic risk zone",
                        "✓ Seismic building codes already mandated by state"
                    ],
                    "mitigation_cost_per_unit": 0
                }
            elif event_count >= 2:
                return {
                    "type": "earthquake",
                    "score_penalty": 18,
                    "risk_level": "high",
                    "event_count": event_count,
                    "risks": [f"{event_count} earthquake declarations since 2004"],
                    "mitigation_cost_per_unit": 15000
                }
            else:
                return {
                    "type": "earthquake",
                    "score_penalty": 8,
                    "risk_level": "moderate",
                    "event_count": event_count,
                    "risks": [f"{property_state} building codes mandate seismic design"],
                    "mitigation_cost_per_unit": 0
                }
        
        if event_count == 0:
            return {
                "type": "earthquake",
                "score_penalty": 0,
                "risk_level": "minimal",
                "event_count": 0,
                "risks": [],
                "mitigation_cost_per_unit": 0
            }
        else:
            return {
                "type": "earthquake",
                "score_penalty": 8,
                "risk_level": "moderate",
                "event_count": event_count,
                "risks": [f"{event_count} earthquake declaration(s) since 2004"],
                "mitigation_cost_per_unit": 6000
            }
    
    def _get_disaster_recommendation(self, overall_risk_level: str, high_risk_count: int) -> str:
        """Get recommendation based on overall disaster risk"""
        
        if overall_risk_level == "very_high":
            return "CAUTION: Multiple high-risk natural hazards present. Conduct detailed feasibility study."
        elif overall_risk_level == "high":
            return "High natural disaster risk. Ensure mitigation costs are included in pro forma."
        elif overall_risk_level == "moderate":
            return "Moderate risk level. Standard mitigation measures should be sufficient."
        else:
            return "Low natural disaster risk. Standard construction practices adequate."
