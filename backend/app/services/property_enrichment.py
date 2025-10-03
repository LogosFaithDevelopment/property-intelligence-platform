"""
Property Enrichment Service
Fetches additional property data from various APIs and enriches property records
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import httpx
from app.api_providers import APIProviderManager
from app.config import get_settings
from app.models.property import Property
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
settings = get_settings()


class PropertyEnrichmentService:
    """Service for enriching property data with external APIs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_manager = APIProviderManager()
    
    async def enrich_property(
        self,
        property_id: int,
        use_premium_apis: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich a property with data from external APIs
        
        Args:
            property_id: Property database ID
            use_premium_apis: Use premium APIs (Google, ATTOM) instead of free
            force_refresh: Force refresh even if data exists
            
        Returns:
            Dictionary with enrichment results
        """
        logger.info(f"Starting property enrichment for property_id={property_id}")
        
        # Get property from database
        result = await self.db.execute(
            select(Property).where(Property.id == property_id)
        )
        property_obj = result.scalar_one_or_none()
        
        if not property_obj:
            raise ValueError(f"Property {property_id} not found")
        
        enrichment_results = {
            "property_id": property_id,
            "started_at": datetime.utcnow().isoformat(),
            "use_premium_apis": use_premium_apis,
            "results": {}
        }
        
        # Step 1: Geocode address if needed
        if not property_obj.latitude or not property_obj.longitude or force_refresh:
            logger.info(f"Geocoding address: {property_obj.full_address}")
            geocode_result = await self._geocode_address(property_obj, use_premium_apis)
            enrichment_results["results"]["geocoding"] = geocode_result
        else:
            logger.info("Property already has coordinates, skipping geocoding")
            enrichment_results["results"]["geocoding"] = {"status": "skipped", "reason": "already_geocoded"}
        
        # Ensure we have coordinates for remaining API calls
        if not property_obj.latitude or not property_obj.longitude:
            logger.warning("Could not geocode property, skipping location-based enrichment")
            enrichment_results["status"] = "partial_success"
            enrichment_results["completed_at"] = datetime.utcnow().isoformat()
            return enrichment_results
        
        # Step 2: Fetch demographics from Census API
        logger.info("Fetching demographics from Census API")
        demographics_result = await self._fetch_demographics(property_obj)
        enrichment_results["results"]["demographics"] = demographics_result
        
        # Step 3: Fetch flood risk from FEMA
        logger.info("Fetching flood risk from FEMA")
        flood_result = await self._fetch_flood_risk(property_obj)
        enrichment_results["results"]["flood_risk"] = flood_result
        
        # Step 4: Fetch HUD data (income limits, fair market rents)
        logger.info("Fetching HUD data")
        hud_result = await self._fetch_hud_data(property_obj)
        enrichment_results["results"]["hud_data"] = hud_result
        
        # Step 5: Fetch nearby points of interest (if using premium APIs)
        if use_premium_apis and settings.google_maps_api_key:
            logger.info("Fetching nearby POIs from Google Places")
            poi_result = await self._fetch_nearby_pois(property_obj)
            enrichment_results["results"]["points_of_interest"] = poi_result
        
        # Step 6: Update property with enriched data
        await self._update_property_with_enriched_data(property_obj, enrichment_results)
        
        enrichment_results["status"] = "success"
        enrichment_results["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Property enrichment completed for property_id={property_id}")
        return enrichment_results
    
    async def _geocode_address(
        self,
        property_obj: Property,
        use_premium: bool
    ) -> Dict[str, Any]:
        """Geocode property address to get lat/long coordinates"""
        
        address = property_obj.full_address
        
        try:
            if use_premium and settings.google_maps_api_key:
                # Use Google Maps Geocoding API
                result = await self._geocode_with_google(address)
            else:
                # Use free OpenStreetMap Nominatim
                result = await self._geocode_with_nominatim(address)
            
            if result.get("success"):
                # Update property with coordinates
                property_obj.latitude = result["latitude"]
                property_obj.longitude = result["longitude"]
                
                # Extract additional address components if available
                if "county" in result:
                    property_obj.county = result["county"]
                
                await self.db.commit()
                
                return {
                    "status": "success",
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "source": result.get("source", "unknown")
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Geocoding failed")
                }
                
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _geocode_with_google(self, address: str) -> Dict[str, Any]:
        """Geocode using Google Maps API"""
        
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": settings.google_maps_api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            
            if data["status"] == "OK" and len(data["results"]) > 0:
                location = data["results"][0]["geometry"]["location"]
                
                # Extract county if available
                county = None
                for component in data["results"][0].get("address_components", []):
                    if "administrative_area_level_2" in component.get("types", []):
                        county = component["long_name"]
                        break
                
                return {
                    "success": True,
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "county": county,
                    "source": "google_maps"
                }
            else:
                return {
                    "success": False,
                    "error": f"Google Geocoding error: {data['status']}"
                }
    
    async def _geocode_with_nominatim(self, address: str) -> Dict[str, Any]:
        """Geocode using OpenStreetMap Nominatim (free)"""
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "PropertyIntelligencePlatform/1.0"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            data = response.json()
            
            if len(data) > 0:
                result = data[0]
                return {
                    "success": True,
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lon"]),
                    "source": "openstreetmap"
                }
            else:
                return {
                    "success": False,
                    "error": "Address not found"
                }
    
    async def _fetch_demographics(self, property_obj: Property) -> Dict[str, Any]:
        """Fetch demographic data from Census API"""
        
        try:
            # For now, return placeholder data
            # TODO: Implement actual Census API call based on lat/long
            return {
                "status": "success",
                "source": "us_census",
                "data": {
                    "population": None,
                    "median_income": None,
                    "poverty_rate": None,
                    "note": "Census API integration pending - requires Census block/tract lookup"
                }
            }
        except Exception as e:
            logger.error(f"Census API error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _fetch_flood_risk(self, property_obj: Property) -> Dict[str, Any]:
        """Fetch flood risk data from FEMA"""
        
        try:
            # For now, return placeholder
            # TODO: Implement FEMA National Flood Hazard Layer API call
            return {
                "status": "success",
                "source": "fema_nfhl",
                "data": {
                    "flood_zone": None,
                    "risk_level": "unknown",
                    "note": "FEMA API integration pending"
                }
            }
        except Exception as e:
            logger.error(f"FEMA API error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _fetch_hud_data(self, property_obj: Property) -> Dict[str, Any]:
        """
        Fetch HUD data (income limits, fair market rents, USPS crosswalk)
        
        For Logos Faith Development, this provides:
        - AMI (Area Median Income) thresholds for affordability targeting
        - Fair Market Rents (FMR) for Section 8 voucher viability
        - ZIP-to-County crosswalk for geographic data mapping
        """
        
        if not settings.hud_api_key:
            logger.warning("HUD API key not configured, skipping HUD data fetch")
            return {
                "status": "skipped",
                "reason": "HUD API key not configured",
                "data": {}
            }
        
        try:
            results = {
                "income_limits": None,
                "fair_market_rent": None,
                "usps_crosswalk": None
            }
            
            # Step 1: Get ZIP-to-County crosswalk data
            # This helps us determine the correct county for HUD queries
            logger.info(f"Fetching USPS crosswalk for ZIP {property_obj.zip_code}")
            crosswalk_data = await self._fetch_hud_usps_crosswalk(property_obj.zip_code)
            results["usps_crosswalk"] = crosswalk_data
            
            # Extract county FIPS from crosswalk (use the first result with highest res_ratio)
            county_fips = None
            state_code = None
            if crosswalk_data.get("success") and crosswalk_data.get("results"):
                # Sort by res_ratio (residential address ratio) descending
                sorted_results = sorted(
                    crosswalk_data["results"],
                    key=lambda x: x.get("res_ratio", 0),
                    reverse=True
                )
                if sorted_results:
                    # Extract state and county from tract GEOID (first 5 digits)
                    geoid = sorted_results[0].get("geoid", "")
                    if len(geoid) >= 5:
                        state_code = geoid[:2]
                        county_fips = geoid[:5]  # State FIPS + County FIPS
                        logger.info(f"Extracted county FIPS: {county_fips} from crosswalk")
            
            # Fallback: try to use property's county field if available
            if not county_fips and property_obj.county:
                logger.warning(f"Could not determine county FIPS from crosswalk, using property.county: {property_obj.county}")
            
            # Step 2: Fetch Income Limits (AMI thresholds)
            # Critical for Logos: determines tenant eligibility and affordability levels
            logger.info(f"Fetching income limits for county {county_fips or property_obj.county}")
            income_limits = await self._fetch_hud_income_limits(
                county_fips=county_fips,
                state_code=state_code,
                zip_code=property_obj.zip_code
            )
            results["income_limits"] = income_limits
            
            # Step 3: Fetch Fair Market Rents (FMR)
            # Critical for Logos: Section 8 voucher payment standards
            logger.info(f"Fetching fair market rents for county {county_fips}")
            fmr_data = await self._fetch_hud_fair_market_rent(property_obj.zip_code, county_fips)
            results["fair_market_rent"] = fmr_data
            
            return {
                "status": "success",
                "source": "hud_api",
                "data": results
            }
            
        except Exception as e:
            logger.error(f"HUD API error: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e), "data": {}}
    
    async def _fetch_hud_usps_crosswalk(self, zip_code: str) -> Dict[str, Any]:
        """
        Fetch ZIP-to-Tract crosswalk from HUD USPS API
        
        Type 1 = ZIP to Tract crosswalk
        This maps ZIP codes to Census tracts, which we can use to get county FIPS
        """
        
        try:
            url = "https://www.huduser.gov/hudapi/public/usps"
            params = {
                "type": 1,  # ZIP to Tract
                "query": zip_code
            }
            headers = {
                "Authorization": f"Bearer {settings.hud_api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("data") and data["data"].get("results"):
                        return {
                            "success": True,
                            "year": data["data"].get("year"),
                            "quarter": data["data"].get("quarter"),
                            "results": data["data"]["results"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No crosswalk data found for ZIP"
                        }
                else:
                    logger.error(f"HUD USPS API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"HUD USPS crosswalk error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_hud_income_limits(
        self,
        county_fips: Optional[str],
        state_code: Optional[str],
        zip_code: str
    ) -> Dict[str, Any]:
        """
        Fetch Income Limits from HUD API
        
        Returns AMI (Area Median Income) thresholds for various percentages:
        - 30% AMI (Extremely Low Income)
        - 60% AMI (Very Low Income)
        - 80% AMI (Low Income) - Logos' primary target
        - 110% AMI (Moderate Income)
        
        Critical for Logos: Validates affordability and tenant eligibility
        """
        
        try:
            # HUD Income Limits API endpoint
            # https://www.huduser.gov/portal/dataset/fmr-api.html
            # This API requires an entityid (FIPS code), not ZIP code
            # Format: {state_fips}{county_fips}99999 (e.g., 4802199999 for Travis County, TX)
            
            if not county_fips or len(county_fips) != 5:
                logger.warning(f"No valid county FIPS available for income limits lookup (got: {county_fips})")
                return {
                    "success": False,
                    "error": "County FIPS required for income limits - USPS crosswalk needed"
                }
            
            # Format entityid: county FIPS + 99999 suffix
            entityid = f"{county_fips}99999"
            url = f"https://www.huduser.gov/hudapi/public/il/data/{entityid}"
            
            headers = {
                "Authorization": f"Bearer {settings.hud_api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # API response structure has changed - data is directly accessible
                    # Response format: {"data": {"county_name": "...", "year": "2024", "median_income": 65900, "very_low": {...}, "extremely_low": {...}, "low": {...}}}
                    if data.get("data"):
                        response_data = data["data"]
                        
                        # Extract income limits (using the correct field names from API)
                        extremely_low = response_data.get("extremely_low", {})  # 30% AMI
                        very_low = response_data.get("very_low", {})  # 50% AMI
                        low = response_data.get("low", {})  # 80% AMI
                        
                        # Note: API doesn't provide 60% AMI directly, need to calculate or use 50%/80% range
                        return {
                            "success": True,
                            "year": response_data.get("year"),
                            "area_name": response_data.get("area_name"),
                            "county_name": response_data.get("county_name"),
                            "median_income": response_data.get("median_income"),
                            "limits_by_household_size": {
                                "1_person": {
                                    "30_percent_ami": extremely_low.get("il30_p1"),
                                    "50_percent_ami": very_low.get("il50_p1"),
                                    "80_percent_ami": low.get("il80_p1"),
                                },
                                "2_person": {
                                    "30_percent_ami": extremely_low.get("il30_p2"),
                                    "50_percent_ami": very_low.get("il50_p2"),
                                    "80_percent_ami": low.get("il80_p2"),
                                },
                                "3_person": {
                                    "30_percent_ami": extremely_low.get("il30_p3"),
                                    "50_percent_ami": very_low.get("il50_p3"),
                                    "80_percent_ami": low.get("il80_p3"),
                                },
                                "4_person": {
                                    "30_percent_ami": extremely_low.get("il30_p4"),
                                    "50_percent_ami": very_low.get("il50_p4"),
                                    "80_percent_ami": low.get("il80_p4"),
                                }
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No income limit data found"
                        }
                else:
                    logger.error(f"HUD Income Limits API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"HUD Income Limits error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_hud_fair_market_rent(self, zip_code: str, county_fips: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch Fair Market Rent (FMR) from HUD API
        
        Returns FMR for different unit types:
        - Studio (0 BR)
        - 1 Bedroom
        - 2 Bedroom  
        - 3 Bedroom
        - 4 Bedroom
        
        Critical for Logos: Section 8 Housing Choice Voucher payment standards
        are based on FMR. This determines maximum rent that can be charged
        to voucher holders, which is essential for Logos' Section 8-dependent model.
        """
        
        try:
            # HUD Fair Market Rent API endpoint
            # This API requires an entityid (FIPS code), not ZIP code
            # Format: {state_fips}{county_fips}99999 (e.g., 4802199999 for Travis County, TX)
            
            if not county_fips or len(county_fips) != 5:
                logger.warning(f"No valid county FIPS available for FMR lookup (got: {county_fips})")
                return {
                    "success": False,
                    "error": "County FIPS required for FMR - USPS crosswalk needed"
                }
            
            # Format entityid: county FIPS + 99999 suffix
            entityid = f"{county_fips}99999"
            url = f"https://www.huduser.gov/hudapi/public/fmr/data/{entityid}"
            
            headers = {
                "Authorization": f"Bearer {settings.hud_api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # API response format: {"data": {"county_name": "...", "basicdata": {"Efficiency": "758", "One-Bedroom": "769", ...}}}
                    if data.get("data") and data["data"].get("basicdata"):
                        response_data = data["data"]
                        fmr_data = response_data["basicdata"]
                        
                        return {
                            "success": True,
                            "year": fmr_data.get("year"),
                            "area_name": response_data.get("area_name"),
                            "county_name": response_data.get("county_name"),
                            "metro_name": response_data.get("metro_name"),
                            "rent_by_bedroom": {
                                "studio": int(float(fmr_data.get("Efficiency", 0))),  # Convert string to int
                                "1_bedroom": int(float(fmr_data.get("One-Bedroom", 0))),
                                "2_bedroom": int(float(fmr_data.get("Two-Bedroom", 0))),
                                "3_bedroom": int(float(fmr_data.get("Three-Bedroom", 0))),
                                "4_bedroom": int(float(fmr_data.get("Four-Bedroom", 0)))
                            },
                            # Calculate affordable rent limits (30% of income rule)
                            "logos_notes": {
                                "section_8_basis": "FMR determines Section 8 voucher payment standards",
                                "rent_ceiling": "Maximum rent Logos can charge voucher holders",
                                "model_dependency": "Critical for private funding model viability"
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No FMR data found for ZIP"
                        }
                else:
                    logger.error(f"HUD FMR API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"HUD FMR error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_nearby_pois(self, property_obj: Property) -> Dict[str, Any]:
        """Fetch nearby points of interest from Google Places"""
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            # Search for key POIs: schools, transit, grocery stores
            poi_types = ["school", "transit_station", "grocery_or_supermarket"]
            results = {}
            
            async with httpx.AsyncClient() as client:
                for poi_type in poi_types:
                    params = {
                        "location": f"{property_obj.latitude},{property_obj.longitude}",
                        "radius": 1609,  # 1 mile
                        "type": poi_type,
                        "key": settings.google_maps_api_key
                    }
                    
                    response = await client.get(url, params=params, timeout=10.0)
                    data = response.json()
                    
                    if data["status"] == "OK":
                        results[poi_type] = {
                            "count": len(data.get("results", [])),
                            "nearest": data["results"][0]["name"] if data.get("results") else None
                        }
            
            return {
                "status": "success",
                "source": "google_places",
                "data": results
            }
            
        except Exception as e:
            logger.error(f"Google Places API error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _update_property_with_enriched_data(
        self,
        property_obj: Property,
        enrichment_results: Dict[str, Any]
    ):
        """Update property record with enriched data"""
        
        # Store enrichment results in data_sources field
        property_obj.data_sources = json.dumps(enrichment_results["results"])
        property_obj.last_data_update = datetime.utcnow()
        
        # Extract and store specific fields
        flood_data = enrichment_results["results"].get("flood_risk", {}).get("data", {})
        if flood_data.get("flood_zone"):
            property_obj.flood_zone = flood_data["flood_zone"]
        
        await self.db.commit()
        logger.info(f"Updated property {property_obj.id} with enriched data")
