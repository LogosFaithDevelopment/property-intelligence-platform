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
        
        # Step 2-5: Fetch data from multiple APIs in parallel for speed
        logger.info("Fetching data from Census, FEMA, HUD, and ATTOM APIs in parallel")
        import asyncio

        # Run independent API calls concurrently
        demographics_task = asyncio.create_task(self._fetch_demographics(property_obj))
        flood_task = asyncio.create_task(self._fetch_flood_risk(property_obj))
        hud_task = asyncio.create_task(self._fetch_hud_data(property_obj))
        
        # Add property data fetch (Smarty PRIMARY, then ATTOM or LA County as fallback)
        property_data_task = None
        
        # Try Smarty first if available (works for ALL property types including commercial/religious)
        if settings.smarty_auth_id and settings.smarty_auth_token:
            logger.info("Using Smarty API for property data (supports all property types)")
            smarty_task = asyncio.create_task(self._fetch_smarty_data(property_obj))
            property_data_task = smarty_task
            tasks = [demographics_task, flood_task, hud_task, smarty_task]
        elif use_premium_apis and settings.attom_api_key:
            # Use ATTOM for premium access (residential only)
            logger.info("Using ATTOM API for property data (residential properties)")
            attom_task = asyncio.create_task(self._fetch_attom_data(property_obj))
            property_data_task = attom_task
            tasks = [demographics_task, flood_task, hud_task, attom_task]
        elif property_obj.state == "CA" or property_obj.state == "California":
            # Use LA County Assessor for California properties (free, no lot size)
            logger.info("Using LA County Assessor for property data (CA only, limited data)")
            la_county_task = asyncio.create_task(self._fetch_la_county_data(property_obj))
            property_data_task = la_county_task
            tasks = [demographics_task, flood_task, hud_task, la_county_task]
        else:
            tasks = [demographics_task, flood_task, hud_task]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results (even if some failed)
        enrichment_results["results"]["demographics"] = results[0] if not isinstance(results[0], Exception) else {"status": "error", "error": str(results[0])}
        enrichment_results["results"]["flood_risk"] = results[1] if not isinstance(results[1], Exception) else {"status": "error", "error": str(results[1])}
        enrichment_results["results"]["hud_data"] = results[2] if not isinstance(results[2], Exception) else {"status": "error", "error": str(results[2])}
        
        # Handle property data (Smarty, ATTOM, or LA County)
        if property_data_task and len(results) > 3:
            property_data_result = results[3] if not isinstance(results[3], Exception) else {"status": "error", "error": str(results[3])}
            
            # Determine which source was used
            if settings.smarty_auth_id and settings.smarty_auth_token:
                enrichment_results["results"]["smarty_data"] = property_data_result
                
                # If Smarty failed, try fallback for CA properties
                if (property_obj.state == "CA" or property_obj.state == "California") and \
                   (property_data_result.get("status") == "error" or not property_data_result.get("success")):
                    logger.info("Smarty data unavailable, trying LA County Assessor fallback")
                    la_county_result = await self._fetch_la_county_data(property_obj)
                    enrichment_results["results"]["la_county_data"] = la_county_result
                    
            elif use_premium_apis and settings.attom_api_key:
                enrichment_results["results"]["attom_data"] = property_data_result
                
                # If ATTOM failed or has no data, try LA County as fallback for CA properties
                if (property_obj.state == "CA" or property_obj.state == "California") and \
                   (property_data_result.get("status") == "error" or 
                    not property_data_result.get("data", {}).get("property_detail", {}).get("success")):
                    logger.info("ATTOM data unavailable, trying LA County Assessor fallback")
                    la_county_result = await self._fetch_la_county_data(property_obj)
                    enrichment_results["results"]["la_county_data"] = la_county_result
            else:
                enrichment_results["results"]["la_county_data"] = property_data_result
        
        # Step 5: Fetch nearby points of interest (if using premium APIs)
        if use_premium_apis and settings.google_maps_api_key:
            logger.info("Fetching nearby points of interest from Google Places")
            poi_result = await self._fetch_nearby_pois(property_obj)
            enrichment_results["results"]["nearby_pois"] = poi_result
        else:
            logger.info("Skipping nearby POIs (premium API not enabled)")
            enrichment_results["results"]["nearby_pois"] = {"status": "skipped", "reason": "premium_apis_not_enabled"}
        
        # Step 6: Update property with enriched data
        await self._update_property_with_enriched_data(property_obj, enrichment_results)
        
        enrichment_results["status"] = "success"
        enrichment_results["completed_at"] = datetime.utcnow().isoformat()
        
        return enrichment_results
    
    async def _geocode_address(
        self, 
        property_obj: Property,
        use_premium: bool = False
    ) -> Dict[str, Any]:
        """Geocode property address to get coordinates"""
        
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
        """
        Fetch demographic data from Census API
        
        Uses American Community Survey (ACS) 5-Year Data for detailed demographics.
        No API key required!
        """
        
        try:
            # First, get census tract from coordinates using Census Geocoder
            logger.info(f"Looking up census tract for coordinates: {property_obj.latitude}, {property_obj.longitude}")
            tract_info = await self._get_census_tract_from_coordinates(
                property_obj.latitude, 
                property_obj.longitude
            )
            
            if not tract_info.get("success"):
                logger.warning(f"Could not determine census tract: {tract_info.get('error')}")
                return {
                    "status": "partial_success",
                    "source": "us_census",
                    "data": {
                        "error": "Could not determine census tract",
                        "note": "Census data requires valid census tract"
                    }
                }
            
            state_fips = tract_info["state"]
            county_fips = tract_info["county"]
            tract_code = tract_info["tract"]
            
            logger.info(f"Found census tract: state={state_fips}, county={county_fips}, tract={tract_code}")
            
            # Fetch ACS 5-Year data for the tract
            # Using 2022 data (latest available as of 2025)
            demographics_data = await self._fetch_acs_data(state_fips, county_fips, tract_code)
            
            if demographics_data.get("success"):
                return {
                    "status": "success",
                    "source": "us_census_acs",
                    "data": {
                        "census_tract": f"{state_fips}{county_fips}{tract_code}",
                        "year": "2022",
                        **demographics_data["data"]
                    }
                }
            else:
                return {
                    "status": "error",
                    "source": "us_census_acs",
                    "error": demographics_data.get("error", "Failed to fetch demographics")
                }
                
        except Exception as e:
            logger.error(f"Census API error: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def _get_census_tract_from_coordinates(
        self, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get census tract from lat/lng using Census Geocoder API
        
        Free, no API key required
        """
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                "x": longitude,
                "y": latitude,
                "benchmark": "Public_AR_Current",  # Current address ranges
                "vintage": "Current_Current",  # Current geographic boundaries
                "format": "json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result") and data["result"].get("geographies"):
                        tracts = data["result"]["geographies"].get("Census Tracts", [])
                        if tracts:
                            tract = tracts[0]
                            return {
                                "success": True,
                                "state": tract["STATE"],
                                "county": tract["COUNTY"],
                                "tract": tract["TRACT"],
                                "basename": tract.get("BASENAME", "")
                            }
                    
                    return {
                        "success": False,
                        "error": "No census tract found for coordinates"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Census Geocoder returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Census geocoder error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_acs_data(
        self, 
        state_fips: str, 
        county_fips: str, 
        tract_code: str
    ) -> Dict[str, Any]:
        """
        Fetch American Community Survey (ACS) 5-Year data
        
        Variables fetched:
        - B01003_001E: Total population
        - B19013_001E: Median household income
        - B17001_002E: Population below poverty level
        - B25001_001E: Total housing units
        - B25003_002E: Owner-occupied housing units
        - B25003_003E: Renter-occupied housing units
        - B01002_001E: Median age
        
        Free, no API key required!
        """
        try:
            url = "https://api.census.gov/data/2022/acs/acs5"
            
            # Variables to fetch
            variables = [
                "B01003_001E",  # Total population
                "B19013_001E",  # Median household income
                "B17001_002E",  # Below poverty level
                "B25001_001E",  # Total housing units
                "B25003_002E",  # Owner-occupied units
                "B25003_003E",  # Renter-occupied units
                "B01002_001E",  # Median age
            ]
            
            params = {
                "get": ",".join(variables),
                "for": f"tract:{tract_code}",
                "in": f"state:{state_fips} county:{county_fips}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Census API returns [headers, values]
                    if len(data) >= 2:
                        headers = data[0]
                        values = data[1]
                        
                        # Create dict from headers and values
                        result = dict(zip(headers, values))
                        
                        # Parse and structure the data
                        total_pop = int(result.get("B01003_001E", 0) or 0)
                        median_income = int(result.get("B19013_001E", -666666666) or -666666666)
                        poverty_pop = int(result.get("B17001_002E", 0) or 0)
                        total_housing = int(result.get("B25001_001E", 0) or 0)
                        owner_occupied = int(result.get("B25003_002E", 0) or 0)
                        renter_occupied = int(result.get("B25003_003E", 0) or 0)
                        median_age = float(result.get("B01002_001E", 0) or 0)
                        
                        # Calculate derived metrics
                        poverty_rate = round((poverty_pop / total_pop * 100), 2) if total_pop > 0 else 0
                        occupancy_rate = round(((owner_occupied + renter_occupied) / total_housing * 100), 2) if total_housing > 0 else 0
                        
                        # Handle median income -666666666 (Census code for "not available")
                        median_income_display = None if median_income == -666666666 else median_income
                        
                        return {
                            "success": True,
                            "data": {
                                "population": total_pop,
                                "median_income": median_income_display,
                                "poverty_rate": poverty_rate,
                                "median_age": median_age,
                                "housing": {
                                    "total_units": total_housing,
                                    "owner_occupied": owner_occupied,
                                    "renter_occupied": renter_occupied,
                                    "occupancy_rate": occupancy_rate
                                },
                                "note": "Data from ACS 5-Year 2022"
                            }
                        }
                    
                    return {
                        "success": False,
                        "error": "No data returned from Census API"
                    }
                else:
                    logger.error(f"Census ACS API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"Census API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Census ACS data error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_flood_risk(self, property_obj: Property) -> Dict[str, Any]:
        """
        Fetch flood risk data from FEMA using OpenFEMA v2 API
        
        Uses a two-step approach:
        1. Check for historical flood disasters in the county
        2. Query NFIP (National Flood Insurance Program) data for the area
        
        Free, no API key required!
        """
        
        try:
            # Extract state and county information
            # Use property's state field (2-letter abbreviation like "CA") directly
            # FEMA API expects state abbreviation, not FIPS code
            state_code = property_obj.state  # e.g., "CA", "TX", "FL"
            county_fips = None
            
            if property_obj.data_sources:
                try:
                    data_sources = json.loads(property_obj.data_sources) if isinstance(property_obj.data_sources, str) else property_obj.data_sources
                    hud_data = data_sources.get("hud_data", {})
                    crosswalk = hud_data.get("usps_crosswalk", {})
                    
                    if crosswalk.get("status") == "success" and crosswalk.get("data", {}).get("results"):
                        # Get first census tract result
                        first_result = crosswalk["data"]["results"][0]
                        geoid = first_result.get("geoid", "")
                        
                        if len(geoid) >= 5:
                            # GEOID format: SSCCCTTTTTT (State 2 digits + County 3 digits + Tract 6 digits)
                            # Extract county FIPS (3 digits after state code)
                            county_fips = geoid[2:5]
                except Exception as e:
                    logger.warning(f"Could not extract county from HUD data: {e}")
            
            logger.info(f"Using state code '{state_code}' for FEMA disaster query")
            
            # Step 1: Check for recent flood disasters in the state/county using OpenFEMA v2
            disaster_history = await self._fetch_flood_disaster_history(state_code, county_fips)
            
            # Step 2: For now, estimate flood risk based on disaster history
            # In production, you would integrate with FEMA's Flood Map Service Center API
            flood_zone = self._estimate_flood_zone_from_history(disaster_history)
            risk_level = self._determine_flood_risk_level(flood_zone)
            description = self._get_flood_zone_description(flood_zone)
            
            return {
                "status": "success",
                "source": "openfema_v2",
                "data": {
                    "flood_zone": flood_zone,
                    "zone_subtype": None,
                    "in_sfha": flood_zone in ["A", "AE", "AH", "AO", "V", "VE"],
                    "risk_level": risk_level,
                    "description": description,
                    "base_flood_elevation": None,
                    "disaster_history": disaster_history,
                    "note": "Flood risk estimated from FEMA disaster history. For precise flood zone, consult FEMA Flood Map Service Center."
                }
            }
                    
        except Exception as e:
            logger.error(f"FEMA API error: {str(e)}", exc_info=True)
            return {
                "status": "error", 
                "source": "openfema_v2",
                "error": str(e)
            }
    
    async def _fetch_flood_disaster_history(self, state_code: Optional[str], county_fips: Optional[str]) -> Dict[str, Any]:
        """
        Fetch comprehensive natural disaster history from OpenFEMA v2 API
        
        Includes: Flood, Fire (wildfire), Tornado, Hurricane, Earthquake
        NOW WITH FULL DISASTER DETAILS for geographic filtering
        """
        try:
            # OpenFEMA v2 Disaster Declarations endpoint
            url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
            
            # Build filter for ALL natural disaster types
            filters = []
            
            if state_code:
                filters.append(f"state eq '{state_code}'")
            
            # Comprehensive disaster types
            disaster_types = [
                "Flood",
                "Severe Storm(s)",
                "Hurricane",
                "Coastal Storm",
                "Fire",           # Wildfire
                "Tornado",
                "Earthquake",
                "Typhoon"         # Pacific equivalent of hurricane
            ]
            incident_filter = " or ".join([f"incidentType eq '{t}'" for t in disaster_types])
            filters.append(f"({incident_filter})")
            
            # Get disasters from last 20 years for reliable risk assessment
            filters.append("declarationDate ge '2004-01-01'")
            
            filter_string = " and ".join(filters)
            
            params = {
                "$filter": filter_string,
                # Include designatedArea for county-level filtering
                "$select": "disasterNumber,declarationDate,incidentType,declarationTitle,designatedArea,fipsCountyCode,ihProgramDeclared,iaProgramDeclared",
                "$orderby": "declarationDate desc",
                "$top": 100  # Increased to capture more history
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    disasters = data.get("DisasterDeclarationsSummaries", [])
                    
                    # Categorize disasters by type (store FULL disaster objects for filtering)
                    flood_disasters = [d for d in disasters if "Flood" in d.get("incidentType", "") or "Storm" in d.get("incidentType", "")]
                    fire_disasters = [d for d in disasters if "Fire" in d.get("incidentType", "")]
                    tornado_disasters = [d for d in disasters if "Tornado" in d.get("incidentType", "")]
                    hurricane_disasters = [d for d in disasters if "Hurricane" in d.get("incidentType", "") or "Typhoon" in d.get("incidentType", "")]
                    earthquake_disasters = [d for d in disasters if "Earthquake" in d.get("incidentType", "")]
                    
                    return {
                        "total_disasters": len(disasters),
                        "flood": {
                            "count": len(flood_disasters),
                            "events": flood_disasters,  # Store ALL events for geographic filtering
                            "recent_events": flood_disasters[:3],
                            "has_history": len(flood_disasters) > 0
                        },
                        "fire": {
                            "count": len(fire_disasters),
                            "events": fire_disasters,
                            "recent_events": fire_disasters[:3],
                            "has_history": len(fire_disasters) > 0
                        },
                        "tornado": {
                            "count": len(tornado_disasters),
                            "events": tornado_disasters,
                            "recent_events": tornado_disasters[:3],
                            "has_history": len(tornado_disasters) > 0
                        },
                        "hurricane": {
                            "count": len(hurricane_disasters),
                            "events": hurricane_disasters,
                            "recent_events": hurricane_disasters[:3],
                            "has_history": len(hurricane_disasters) > 0
                        },
                        "earthquake": {
                            "count": len(earthquake_disasters),
                            "events": earthquake_disasters,
                            "recent_events": earthquake_disasters[:3],
                            "has_history": len(earthquake_disasters) > 0
                        },
                        "data_period": "2004-present",
                        "state_code": state_code,
                        "note": "Full event data included for geographic filtering"
                    }
                else:
                    logger.warning(f"OpenFEMA API returned {response.status_code}")
                    return self._empty_disaster_history()
                    
        except Exception as e:
            logger.error(f"Error fetching natural disaster history: {e}")
            return self._empty_disaster_history()
    
    def _empty_disaster_history(self) -> Dict[str, Any]:
        """Return empty disaster history structure"""
        return {
            "total_disasters": 0,
            "flood": {"count": 0, "recent_events": [], "has_history": False},
            "fire": {"count": 0, "recent_events": [], "has_history": False},
            "tornado": {"count": 0, "recent_events": [], "has_history": False},
            "hurricane": {"count": 0, "recent_events": [], "has_history": False},
            "earthquake": {"count": 0, "recent_events": [], "has_history": False}
        }
    
    def _estimate_flood_zone_from_history(self, disaster_history: Dict[str, Any]) -> str:
        """
        Estimate flood zone based on disaster history
        This is a simplified approach - production should use FEMA Flood Map Service
        """
        flood_data = disaster_history.get("flood", {})
        flood_count = flood_data.get("count", 0)
        
        if flood_count >= 5:
            return "A"  # High risk - multiple flood events
        elif flood_count >= 2:
            return "X500"  # Moderate risk - some flood history
        else:
            return "X"  # Minimal risk - no significant flood history
    
    def _determine_flood_risk_level(self, flood_zone: str) -> str:
        """
        Determine flood risk level from FEMA flood zone
        
        Zone Categories:
        - High Risk: A, AE, AH, AO, AR, A99, V, VE
        - Moderate Risk: B, X (shaded)
        - Minimal Risk: C, X (unshaded)
        """
        
        high_risk_zones = ["A", "AE", "AH", "AO", "AR", "A99", "V", "VE", "V1-30", "VE1-30"]
        moderate_risk_zones = ["B", "X500"]
        
        if flood_zone in high_risk_zones or flood_zone.startswith("A") or flood_zone.startswith("V"):
            return "high"
        elif flood_zone in moderate_risk_zones:
            return "moderate"
        else:
            return "minimal"
    
    def _get_flood_zone_description(self, flood_zone: str) -> str:
        """Get human-readable description of flood zone"""
        
        descriptions = {
            "X": "Area of minimal flood hazard (0.2% annual chance)",
            "A": "High risk - 1% annual chance flood zone (no BFE determined)",
            "AE": "High risk - 1% annual chance with Base Flood Elevation",
            "AH": "High risk - shallow flooding area (1-3 feet deep)",
            "AO": "High risk - sheet flow flooding area",
            "AR": "High risk - area with temporarily increased flood risk",
            "A99": "High risk - area protected by Federal flood control system under construction",
            "V": "High risk - coastal area with velocity hazard (wave action)",
            "VE": "High risk - coastal with velocity hazard and Base Flood Elevation",
            "B": "Moderate risk - area between 0.2% and 1% annual chance",
            "X500": "Moderate risk - 0.2% annual chance flood zone"
        }
        
        return descriptions.get(flood_zone, f"Flood Zone {flood_zone}")
    
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
            logger.info(f"Fetching fair market rents for county {county_fips or property_obj.county}")
            fmr_data = await self._fetch_hud_fair_market_rent(
                zip_code=property_obj.zip_code,
                county_fips=county_fips,
                state_code=state_code
            )
            results["fair_market_rent"] = fmr_data
            
            return {
                "status": "success",
                "source": "hud_api",
                "data": results
            }
            
        except Exception as e:
            logger.error(f"HUD API error: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e), "data": {}}
    
    async def _get_hud_entityid_from_state(
        self, 
        state_code: Optional[str], 
        county_fips: Optional[str]
    ) -> Optional[str]:
        """
        Get 10-digit HUD entityid by querying listCounties endpoint
        Returns entityid in format: 4845399999 (state+county+99999)
        """
        if not state_code or not county_fips:
            return None
        
        try:
            # Get state abbreviation from state FIPS code
            state_fips_to_abbr = {
                "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
                "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
                "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
                "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
                "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
                "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
                "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
                "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
                "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
                "56": "WY", "72": "PR"
            }
            
            state_abbr = state_fips_to_abbr.get(state_code)
            if not state_abbr:
                return None
            
            # Query HUD listCounties API
            url = f"https://www.huduser.gov/hudapi/public/fmr/listCounties/{state_abbr}"
            headers = {"Authorization": f"Bearer {settings.hud_api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    counties = data.get("data", [])
                    
                    # Find county matching our FIPS code
                    target_fips = f"{state_code}{county_fips}"
                    for county in counties:
                        fips_code = county.get("fips_code", "")
                        if fips_code.startswith(target_fips):
                            return fips_code
                            
        except Exception as e:
            logger.warning(f"Could not fetch HUD entityid: {e}")
        
        return None

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
        
        Critical for Logos: Validates affordability and tenant eligibility
        """
        
        try:
            # First, get the correct 10-digit FIPS entityid from HUD
            # Format: State(2) + County(3) + 99999 = 10 digits
            entityid = None
            
            if county_fips and len(county_fips) == 5:
                # Convert 5-digit FIPS (e.g., "48453") to 10-digit entityid
                # Format: 48453 + 99999 = 4845399999
                entityid = f"{county_fips}99999"
            
            if not entityid:
                # Fallback: Try to get entityid from listCounties
                entityid = await self._get_hud_entityid_from_state(state_code, county_fips)
            
            if not entityid:
                return {
                    "success": False,
                    "error": "Could not determine HUD entityid for county"
                }
            
            # HUD Income Limits API: /il/data/{entityid}
            url = f"https://www.huduser.gov/hudapi/public/il/data/{entityid}"
            headers = {
                "Authorization": f"Bearer {settings.hud_api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse the HUD IL API response structure
                    if data.get("data"):
                        il_data = data["data"]
                        
                        # Extract income limits (30%, 50%, 60%, 80%)
                        extremely_low = il_data.get("extremely_low", {})
                        very_low = il_data.get("very_low", {})
                        low = il_data.get("low", {})
                        
                        return {
                            "success": True,
                            "year": il_data.get("year"),
                            "area_name": il_data.get("area_name", il_data.get("county_name", "Unknown")),
                            "median_income": il_data.get("median_income"),
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
                            "error": "No income limit data found in response"
                        }
                else:
                    logger.error(f"HUD Income Limits API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"HUD Income Limits error: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _fetch_hud_fair_market_rent(
        self, 
        zip_code: str,
        county_fips: Optional[str] = None,
        state_code: Optional[str] = None
    ) -> Dict[str, Any]:
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
            # First, get the correct 10-digit FIPS entityid
            # Format: State(2) + County(3) + 99999 = 10 digits
            entityid = None
            
            if county_fips and len(county_fips) == 5:
                # Convert 5-digit FIPS to 10-digit entityid
                entityid = f"{county_fips}99999"
            
            if not entityid:
                # Fallback: Try to get entityid from listCounties
                entityid = await self._get_hud_entityid_from_state(state_code, county_fips)
            
            if not entityid:
                return {
                    "success": False,
                    "error": "Could not determine HUD entityid for county"
                }
            
            # HUD FMR API: /fmr/data/{entityid}
            url = f"https://www.huduser.gov/hudapi/public/fmr/data/{entityid}"
            headers = {
                "Authorization": f"Bearer {settings.hud_api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("data"):
                        fmr_info = data["data"]
                        
                        # Handle different response structures (single area vs small area FMRs)
                        if isinstance(fmr_info.get("basicdata"), dict):
                            # Standard FMR structure
                            fmr_data = fmr_info["basicdata"]
                            return {
                                "success": True,
                                "year": fmr_data.get("year"),
                                "area_name": fmr_info.get("area_name", fmr_info.get("county_name")),
                                "county_name": fmr_info.get("county_name"),
                                "rent_by_bedroom": {
                                    "studio": fmr_data.get("Efficiency"),
                                    "1_bedroom": fmr_data.get("One-Bedroom"),
                                    "2_bedroom": fmr_data.get("Two-Bedroom"),
                                    "3_bedroom": fmr_data.get("Three-Bedroom"),
                                    "4_bedroom": fmr_data.get("Four-Bedroom")
                                },
                                "logos_notes": {
                                    "section_8_basis": "FMR determines Section 8 voucher payment standards",
                                    "rent_ceiling": "Maximum rent Logos can charge voucher holders"
                                }
                            }
                        elif isinstance(fmr_info.get("basicdata"), list):
                            # Small Area FMR structure - get MSA-level data
                            basicdata_list = fmr_info["basicdata"]
                            msa_data = next((item for item in basicdata_list if item.get("zip_code") == "MSA level"), basicdata_list[0] if basicdata_list else {})
                            
                            return {
                                "success": True,
                                "year": fmr_info.get("year"),
                                "area_name": fmr_info.get("area_name", fmr_info.get("metro_name")),
                                "smallarea_status": True,
                                "rent_by_bedroom": {
                                    "studio": msa_data.get("Efficiency"),
                                    "1_bedroom": msa_data.get("One-Bedroom"),
                                    "2_bedroom": msa_data.get("Two-Bedroom"),
                                    "3_bedroom": msa_data.get("Three-Bedroom"),
                                    "4_bedroom": msa_data.get("Four-Bedroom")
                                },
                                "logos_notes": {
                                    "section_8_basis": "FMR determines Section 8 voucher payment standards",
                                    "rent_ceiling": "Maximum rent Logos can charge voucher holders"
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "error": "Unexpected FMR data structure"
                            }
                    else:
                        return {
                            "success": False,
                            "error": "No FMR data found in response"
                        }
                else:
                    logger.error(f"HUD FMR API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"HUD FMR error: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _fetch_attom_data(self, property_obj: Property) -> Dict[str, Any]:
        """
        Fetch property data from ATTOM API
        
        Provides:
        - Property details (lot size, building characteristics, zoning)
        - Automated Valuation Model (AVM) - estimated property value
        - Sales comparables - recent nearby sales
        """
        
        if not settings.attom_api_key:
            logger.warning("ATTOM API key not configured, skipping ATTOM data fetch")
            return {
                "status": "skipped",
                "reason": "ATTOM API key not configured",
                "data": {}
            }
        
        try:
            from app.api_providers.attom_provider import ATTOMProvider
            
            attom_provider = ATTOMProvider(api_key=settings.attom_api_key)
            
            results = {}
            
            # Step 1: Get property details
            logger.info(f"Fetching ATTOM property details for {property_obj.full_address}")
            property_detail = await attom_provider.get_property_detail(
                address=f"{property_obj.street_address}",
                address2=f"{property_obj.city} {property_obj.state}"
            )
            results["property_detail"] = property_detail
            
            # Step 2: Get AVM (Automated Valuation Model)
            logger.info(f"Fetching ATTOM valuation for {property_obj.full_address}")
            avm_result = await attom_provider.get_avm(
                address=f"{property_obj.street_address}",
                address2=f"{property_obj.city} {property_obj.state}"
            )
            results["avm"] = avm_result
            
            # Step 3: Get sales comparables
            logger.info(f"Fetching ATTOM sales comparables for {property_obj.full_address}")
            comps_result = await attom_provider.get_sales_comparables(
                address=f"{property_obj.street_address}",
                address2=f"{property_obj.city} {property_obj.state}",
                radius=0.5  # Half mile radius
            )
            results["sales_comparables"] = comps_result
            
            # Extract key data for easy access
            attom_summary = {
                "property_detail": {
                    "success": property_detail.get("success", False),
                    "lot_sqft": property_detail.get("data", {}).get("lot", {}).get("sqft", 0) if property_detail.get("success") else 0,
                    "building_sqft": property_detail.get("data", {}).get("building", {}).get("sqft", 0) if property_detail.get("success") else 0,
                    "bedrooms": property_detail.get("data", {}).get("building", {}).get("bedrooms", 0) if property_detail.get("success") else 0,
                    "bathrooms": property_detail.get("data", {}).get("building", {}).get("bathrooms", 0) if property_detail.get("success") else 0,
                    "year_built": property_detail.get("data", {}).get("building", {}).get("year_built") if property_detail.get("success") else None,
                    "zoning": property_detail.get("data", {}).get("zoning", "") if property_detail.get("success") else "",
                    "land_use": property_detail.get("data", {}).get("land_use", "") if property_detail.get("success") else ""
                },
                "valuation": {
                    "success": avm_result.get("success", False),
                    "estimated_value": avm_result.get("data", {}).get("amount", 0) if avm_result.get("success") else 0,
                    "value_range": {
                        "low": avm_result.get("data", {}).get("low", 0) if avm_result.get("success") else 0,
                        "high": avm_result.get("data", {}).get("high", 0) if avm_result.get("success") else 0
                    },
                    "confidence_score": avm_result.get("data", {}).get("confidence_score") if avm_result.get("success") else None
                },
                "market_comps": {
                    "success": comps_result.get("success", False),
                    "comp_count": comps_result.get("data", {}).get("count", 0) if comps_result.get("success") else 0,
                    "median_sale_price": comps_result.get("data", {}).get("median_price", 0) if comps_result.get("success") else 0,
                    "median_price_per_sqft": comps_result.get("data", {}).get("median_price_per_sqft", 0) if comps_result.get("success") else 0
                }
            }
            
            return {
                "status": "success",
                "source": "attom_data",
                "data": attom_summary,
                "raw_results": results
            }
            
        except Exception as e:
            logger.error(f"ATTOM API error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "data": {}
            }
    
    async def _fetch_la_county_data(self, property_obj: Property) -> Dict[str, Any]:
        """
        Fetch property data from LA County Assessor API
        
        Provides free alternative to ATTOM for Los Angeles County properties:
        - Lot size (square footage and acreage)
        - Assessed values (land, improvement, total)
        - Year built
        - Property use type
        - Building characteristics
        
        Coverage: Los Angeles County only
        Cost: FREE (public data)
        """
        
        try:
            from app.api_clients.la_county_assessor import \
                LACountyAssessorClient
            
            logger.info(f"Fetching LA County Assessor data for {property_obj.full_address}")
            
            # Initialize client
            la_client = LACountyAssessorClient()
            
            try:
                # Fetch property data by address
                result = await la_client.get_property_by_address(
                    street_address=property_obj.street_address,
                    city=property_obj.city,
                    zip_code=property_obj.zip_code
                )
                
                if not result.get("success"):
                    logger.warning(f"LA County Assessor API returned no data: {result.get('error')}")
                    return {
                        "status": "no_data",
                        "reason": result.get("error", "Property not found"),
                        "data": {}
                    }
                
                # Extract key fields for property model
                la_county_summary = {
                    "identification": {
                        "ain": result.get("ain"),
                        "assessor_id": result.get("assessor_id"),
                        "roll_year": result.get("roll_year")
                    },
                    "property_characteristics": {
                        "lot_sqft": result.get("lot_size_sqft"),
                        "lot_acres": result.get("lot_size_acres"),
                        "year_built": result.get("year_built"),
                        "effective_year_built": result.get("effective_year_built"),
                        "building_sqft": result.get("building_sqft"),
                        "bedrooms": result.get("bedrooms"),
                        "bathrooms": result.get("bathrooms"),
                        "units": result.get("units"),
                        "number_of_buildings": result.get("number_of_buildings")
                    },
                    "valuation": {
                        "total_assessed_value": result.get("assessed_value"),
                        "land_value": result.get("land_value"),
                        "improvement_value": result.get("improvement_value"),
                        "fixture_value": result.get("fixture_value")
                    },
                    "property_use": {
                        "use_type": result.get("use_type"),
                        "use_code": result.get("use_code"),
                        "classification": result.get("classification"),
                        "general_use": result.get("general_use")
                    },
                    "location": {
                        "address": result.get("address"),
                        "latitude": result.get("latitude"),
                        "longitude": result.get("longitude")
                    },
                    "dates": {
                        "last_recording_date": result.get("last_recording_date"),
                        "query_date": result.get("query_date")
                    }
                }
                
                logger.info(f"Successfully retrieved LA County data. Lot size: {result.get('lot_size_sqft')} sqft")
                
                return {
                    "status": "success",
                    "source": "la_county_assessor",
                    "data": la_county_summary,
                    "raw_result": result
                }
                
            finally:
                # Clean up client
                await la_client.close()
            
        except Exception as e:
            logger.error(f"LA County Assessor API error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "data": {}
            }
    
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
    
    def _combine_multi_address_data(
        self,
        all_addresses_data: list,
        demolish_all_structures: bool = False
    ) -> Dict[str, Any]:
        """
        Combine property data from multiple addresses
        
        Args:
            all_addresses_data: List of Smarty API results for each address
            demolish_all_structures: Whether user plans to demolish existing buildings
            
        Returns:
            Combined property data with total lot sizes and calculated available space
        """
        if not all_addresses_data:
            return None
        
        logger.info(f"Combining data from {len(all_addresses_data)} address(es)")
        
        # Initialize combined values
        total_lot_sqft = 0
        total_lot_acres = 0
        total_building_sqft = 0
        all_lot_numbers = []
        all_parcel_numbers = []
        individual_parcels = []  # NEW: Store individual parcel data
        
        # Aggregate data from all addresses
        for idx, addr_data in enumerate(all_addresses_data):
            if not addr_data.get('success'):
                continue
            
            lot_data = addr_data.get('lot', {})
            building_data = addr_data.get('building', {})
            
            # Sum lot sizes
            lot_sqft = lot_data.get('size_sqft', 0)
            lot_acres = lot_data.get('size_acres', 0)
            total_lot_sqft += lot_sqft
            total_lot_acres += lot_acres
            
            # Sum building sizes (only if NOT demolishing)
            building_sqft = building_data.get('size_sqft', 0)
            if not demolish_all_structures:
                total_building_sqft += building_sqft
            
            # Collect lot/parcel numbers
            lot_numbers = lot_data.get('lot_numbers', '')
            if lot_numbers:
                all_lot_numbers.append(lot_numbers)
            
            parcel_number = lot_data.get('parcel_number', '')
            if parcel_number:
                all_parcel_numbers.append(parcel_number)
            
            # NEW: Store individual parcel data for frontend display
            individual_parcels.append({
                'parcel_index': idx,
                'lot': {
                    'size_sqft': lot_sqft,
                    'size_acres': lot_acres,
                    'lot_numbers': lot_numbers,
                    'parcel_number': parcel_number
                },
                'building': {
                    'size_sqft': building_sqft,
                    'year_built': building_data.get('year_built'),
                    'stories': building_data.get('stories')
                }
            })
            
            logger.info(
                f"Address #{idx + 1}: Lot={lot_sqft:,} sqft, Building={building_sqft:,} sqft, "
                f"Lots={lot_numbers}, Parcel={parcel_number}"
            )
        
        # Calculate available build space
        available_build_space_sqft = total_lot_sqft - total_building_sqft
        available_build_space_acres = available_build_space_sqft / 43560 if available_build_space_sqft > 0 else 0
        qualifies_for_logos = available_build_space_sqft >= 10000
        
        # Use primary address data as base, but update with combined values
        primary_data = all_addresses_data[0]
        
        logger.info(
            f"✅ COMBINED TOTALS: Lot={total_lot_sqft:,} sqft ({total_lot_acres:.2f} acres), "
            f"Building={total_building_sqft:,} sqft, Available={available_build_space_sqft:,} sqft - "
            f"{'QUALIFIES' if qualifies_for_logos else 'Does not qualify'} for LOGOS"
        )
        
        # Return combined data structure
        return {
            'success': True,
            'lot': {
                'size_sqft': total_lot_sqft,
                'size_acres': total_lot_acres,
                'lot_numbers': ', '.join(all_lot_numbers),
                'parcel_number': ', '.join(all_parcel_numbers)
            },
            'building': primary_data.get('building', {}),  # Use primary building characteristics
            'available_build_space': {
                'sqft': available_build_space_sqft,
                'acres': round(available_build_space_acres, 4),
                'qualifies_for_logos': qualifies_for_logos,
                'minimum_required': 10000,
                'calculation': f"{total_lot_sqft:,} sqft (total lot) - {total_building_sqft:,} sqft (buildings) = {available_build_space_sqft:,} sqft",
                'demolish_all_structures': demolish_all_structures,
                'address_count': len(all_addresses_data)
            },
            'valuation': primary_data.get('valuation', {}),
            'financial': primary_data.get('financial', {}),
            'owner': primary_data.get('owner', {}),
            'property_type': primary_data.get('property_type', {}),
            'combined_lot_size_sqft': total_lot_sqft,
            'combined_building_size_sqft': total_building_sqft,
            'individual_parcels': individual_parcels  # NEW: Include individual parcel data
        }
    
    async def _update_property_with_enriched_data(
        self,
        property_obj: Property,
        enrichment_results: Dict[str, Any]
    ):
        """Update property record with enriched data"""
        
        # Store enrichment results in data_sources field
        property_obj.data_sources = json.dumps(enrichment_results["results"])
        property_obj.last_data_update = datetime.utcnow()
        
        # Extract and store specific fields from various sources
        
        # Flood risk data
        flood_data = enrichment_results["results"].get("flood_risk", {}).get("data", {})
        if flood_data.get("flood_zone"):
            property_obj.flood_zone = flood_data["flood_zone"]
        
        # ATTOM data - update property details if available
        attom_data = enrichment_results["results"].get("attom_data", {}).get("data", {})
        if attom_data and attom_data.get("property_detail", {}).get("success"):
            detail = attom_data["property_detail"]
            
            # Update property fields with ATTOM data (if not already set)
            if detail.get("lot_sqft") and not property_obj.lot_size_sqft:
                property_obj.lot_size_sqft = detail["lot_sqft"]
            
            if detail.get("building_sqft") and not property_obj.building_sqft:
                property_obj.building_sqft = detail["building_sqft"]
            
            if detail.get("year_built") and not property_obj.year_built:
                property_obj.year_built = detail["year_built"]
            
            if detail.get("zoning"):
                property_obj.zoning = detail["zoning"]
        
        # Store ATTOM valuation as market value estimate
        if attom_data and attom_data.get("valuation", {}).get("success"):
            valuation = attom_data["valuation"]
            if valuation.get("estimated_value") and valuation["estimated_value"] > 0:
                property_obj.market_value_estimate = valuation["estimated_value"]
        
        # LA County Assessor data - update property details if available (CA properties)
        la_county_data = enrichment_results["results"].get("la_county_data", {}).get("data", {})
        if la_county_data and enrichment_results["results"].get("la_county_data", {}).get("status") == "success":
            characteristics = la_county_data.get("property_characteristics", {})
            valuation = la_county_data.get("valuation", {})
            
            # Update property fields with LA County data (if not already set)
            if characteristics.get("lot_sqft") and not property_obj.lot_size_sqft:
                property_obj.lot_size_sqft = characteristics["lot_sqft"]
                # Calculate lot_size_acres from sqft (1 acre = 43,560 sqft)
                property_obj.lot_size_acres = round(characteristics["lot_sqft"] / 43560, 2)
                logger.info(f"Updated lot_size from LA County: {characteristics['lot_sqft']:,} sqft ({property_obj.lot_size_acres} acres)")
            
            if characteristics.get("building_sqft") and not property_obj.building_sqft:
                property_obj.building_sqft = characteristics["building_sqft"]
            
            if characteristics.get("year_built") and not property_obj.year_built:
                property_obj.year_built = characteristics["year_built"]
            
            # Store LA County assessed value (if ATTOM not available)
            if valuation.get("total_assessed_value") and not property_obj.assessed_value:
                property_obj.assessed_value = valuation["total_assessed_value"]
                logger.info(f"Updated assessed_value from LA County: ${valuation['total_assessed_value']:,}")
        
        # Smarty data - PRIORITY SOURCE for lot size (works for all property types)
        smarty_data = enrichment_results["results"].get("smarty_data", {}).get("data", {})
        if smarty_data:
            lot_info = smarty_data.get("lot", {})
            building_info = smarty_data.get("building", {})
            multi_address_info = smarty_data.get("multi_address", {})
            address_info = smarty_data.get("address", {})
            valuation_info = smarty_data.get("valuation", {})
            
            # Update lot size (always update from Smarty - most accurate)
            if lot_info.get("size_sqft"):
                property_obj.lot_size_sqft = lot_info["size_sqft"]
                property_obj.lot_size_acres = lot_info.get("size_acres", lot_info["size_sqft"] / 43560)
                logger.info(f"Updated lot_size from Smarty: {lot_info['size_sqft']:,} sqft ({property_obj.lot_size_acres:.2f} acres)")
            
            # Update building size and year_built
            if building_info.get("size_sqft"):
                property_obj.building_sqft = building_info["size_sqft"]
                logger.info(f"Updated building_sqft from Smarty: {building_info['size_sqft']:,} sqft")
            
            if building_info.get("year_built") and not property_obj.year_built:
                # Convert to int (Smarty returns string)
                property_obj.year_built = int(building_info["year_built"])
                logger.info(f"Updated year_built from Smarty: {building_info['year_built']}")
            
            # Update county from Smarty address data
            if address_info.get("county") and not property_obj.county:
                property_obj.county = address_info["county"]
                logger.info(f"Updated county from Smarty: {address_info['county']}")
            
            # Update assessed value from Smarty valuation
            if valuation_info.get("assessed_total") and not property_obj.assessed_value:
                property_obj.assessed_value = valuation_info["assessed_total"]
                logger.info(f"Updated assessed_value from Smarty: ${valuation_info['assessed_total']:,}")
            
            # Update combined lot/building sizes (for multi-address properties)
            if multi_address_info.get("combined_lot_size_sqft"):
                property_obj.combined_lot_size_sqft = multi_address_info["combined_lot_size_sqft"]
                logger.info(f"Stored combined_lot_size_sqft: {multi_address_info['combined_lot_size_sqft']:,} sqft")
            
            if multi_address_info.get("combined_building_size_sqft"):
                property_obj.combined_building_size_sqft = multi_address_info["combined_building_size_sqft"]
                logger.info(f"Stored combined_building_size_sqft: {multi_address_info['combined_building_size_sqft']:,} sqft")
        
        await self.db.commit()
        logger.info(f"Updated property {property_obj.id} with enriched data")
    
    async def _fetch_smarty_data(self, property_obj: Property) -> Dict[str, Any]:
        """
        Fetch property data from Smarty API
        
        PRIMARY PROPERTY DATA SOURCE - Works for ALL property types:
        - ✅ Residential properties
        - ✅ Commercial properties
        - ✅ Religious properties (churches, temples, etc.)
        - ✅ Industrial properties
        
        Provides comprehensive data:
        - Lot size (acres, sqft) - CRITICAL for LOGOS 10k sqft minimum
        - Building characteristics (size, year built, construction)
        - Available build space calculation (lot - building = available)
        - Parcel/lot numbers (APN)
        - Property valuations (assessed + estimated market value)
        - Financial history (mortgages when available)
        - Owner information
        
        This is the BEST source for lot size data on commercial/religious properties.
        
        NEW: Supports multi-address properties - fetches data for primary + additional addresses
        and combines lot sizes for accurate unit calculations.
        """
        
        if not settings.smarty_auth_id or not settings.smarty_auth_token:
            logger.warning("Smarty API credentials not configured, skipping Smarty data fetch")
            return {
                "status": "skipped",
                "reason": "Smarty API credentials not configured",
                "success": False,
                "data": {}
            }
        
        try:
            from app.api_providers.smarty_provider import SmartyProvider

            # Initialize Smarty provider
            smarty_provider = SmartyProvider(
                auth_id=settings.smarty_auth_id,
                auth_token=settings.smarty_auth_token
            )
            
            # Fetch PRIMARY address
            logger.info(f"Fetching Smarty property data for PRIMARY address: {property_obj.full_address}")
            
            result = await smarty_provider.get_property_data(
                street=property_obj.street_address,
                city=property_obj.city,
                state=property_obj.state,
                zipcode=property_obj.zip_code
            )
            
            if not result.get('success'):
                logger.warning(f"Smarty API returned no data for primary address: {result.get('error')}")
                await smarty_provider.close()
                return {
                    "status": "error",
                    "error": result.get('error', 'Unknown error'),
                    "success": False,
                    "data": {}
                }
            
            # Store primary address data
            all_addresses_data = [result]
            
            # Fetch ADDITIONAL addresses if they exist
            additional_addresses = property_obj.additional_addresses or []
            if additional_addresses and isinstance(additional_addresses, list):
                logger.info(f"Found {len(additional_addresses)} additional address(es) to fetch")
                
                for idx, addr in enumerate(additional_addresses):
                    try:
                        logger.info(f"Fetching Smarty data for additional address #{idx + 1}: {addr.get('address')}")
                        
                        additional_result = await smarty_provider.get_property_data(
                            street=addr.get('address', ''),
                            city=addr.get('city', ''),
                            state=addr.get('state', ''),
                            zipcode=addr.get('zip_code', '')
                        )
                        
                        if additional_result.get('success'):
                            all_addresses_data.append(additional_result)
                            logger.info(f"✅ Successfully fetched data for additional address #{idx + 1}")
                        else:
                            logger.warning(f"Failed to fetch data for additional address #{idx + 1}: {additional_result.get('error')}")
                    except Exception as e:
                        logger.error(f"Error fetching additional address #{idx + 1}: {str(e)}")
            
            # Close provider
            await smarty_provider.close()
            
            # Combine data from all addresses
            combined_data = self._combine_multi_address_data(all_addresses_data, property_obj.demolish_all_structures)
            
            # NEW: Enrich additional_addresses with individual parcel data
            if additional_addresses and len(all_addresses_data) > 1:
                logger.info(f"Enriching {len(additional_addresses)} additional address(es) with parcel data")
                for idx, addr in enumerate(additional_addresses):
                    # Skip primary (index 0), start from index 1
                    addr_data_index = idx + 1
                    if addr_data_index < len(all_addresses_data):
                        addr_smarty_data = all_addresses_data[addr_data_index]
                        if addr_smarty_data.get('success'):
                            # Add enriched_data to the address
                            addr['enriched_data'] = {
                                'lot': addr_smarty_data.get('lot', {}),
                                'building': addr_smarty_data.get('building', {}),
                                'owner': addr_smarty_data.get('owner', {}),
                                'valuation': addr_smarty_data.get('valuation', {})
                            }
                            logger.info(f"✅ Enriched address #{idx + 1} with Smarty data: {addr.get('address')}")
                
                # Mark additional_addresses as modified so SQLAlchemy saves it
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(property_obj, 'additional_addresses')
                logger.info("✅ Marked additional_addresses as modified for database update")
            
            if not combined_data:
                logger.warning("Failed to combine multi-address data")
                return {
                    "status": "error",
                    "error": "Failed to combine multi-address data",
                    "success": False,
                    "data": {}
                }
            
            # Extract key data for easy access and database storage (using COMBINED data)
            lot_data = combined_data.get('lot', {})
            building_data = combined_data.get('building', {})
            available_build_space = combined_data.get('available_build_space', {})
            valuation_data = combined_data.get('valuation', {})
            financial_data = combined_data.get('financial', {})
            owner_data = combined_data.get('owner', {})
            
            smarty_summary = {
                # Lot information (THE CRITICAL DATA!)
                "lot": {
                    "size_sqft": lot_data.get('size_sqft', 0),
                    "size_acres": lot_data.get('size_acres', 0),
                    "lot_numbers": lot_data.get('lot_numbers', ''),
                    "parcel_number": lot_data.get('parcel_number', '')
                },
                
                # Building information
                "building": {
                    "size_sqft": building_data.get('size_sqft', 0),
                    "year_built": building_data.get('year_built'),
                    "stories": building_data.get('stories'),
                    "construction_type": building_data.get('construction_type', ''),
                    "floor_1_sqft": building_data.get('1st_floor_sqft', 0),
                    "floor_2_sqft": building_data.get('2nd_floor_sqft', 0)
                },
                
                # 🎯 AVAILABLE BUILD SPACE - THE MONEY NUMBER!
                "available_build_space": {
                    "sqft": available_build_space.get('sqft', 0),
                    "acres": available_build_space.get('acres', 0),
                    "qualifies_for_logos": available_build_space.get('qualifies_for_logos', False),
                    "minimum_required": available_build_space.get('minimum_required', 10000),
                    "calculation": available_build_space.get('calculation', '')
                },
                
                # Property valuation
                "valuation": {
                    "assessed_total": valuation_data.get('assessed_total', 0),
                    "assessed_land": valuation_data.get('assessed_land', 0),
                    "assessed_improvement": valuation_data.get('assessed_improvement', 0),
                    "estimated_market_min": valuation_data.get('estimated_market_min', 0),
                    "estimated_market_max": valuation_data.get('estimated_market_max', 0),
                    "assessed_year": valuation_data.get('assessed_year', '')
                },
                
                # Financial history (mortgages)
                "financial": {
                    "has_mortgages": financial_data.get('has_mortgages', False),
                    "total_mortgage_amount": financial_data.get('total_mortgage_amount', 0),
                    "mortgage_count": financial_data.get('mortgage_count', 0),
                    "mortgages": financial_data.get('mortgages', [])
                },
                
                # Owner information
                "owner": {
                    "name": owner_data.get('name', ''),
                    "last_sale_date": owner_data.get('last_sale_date', ''),
                    "last_sale_price": owner_data.get('last_sale_price', 0)
                },
                
                # Property type
                "property_type": combined_data.get('property_type', {}),
                
                # Multi-address information
                "multi_address": {
                    "address_count": len(all_addresses_data),
                    "demolish_all_structures": property_obj.demolish_all_structures,
                    "combined_lot_size_sqft": combined_data.get('combined_lot_size_sqft', 0),
                    "combined_building_size_sqft": combined_data.get('combined_building_size_sqft', 0),
                    "individual_parcels": combined_data.get('individual_parcels', [])  # NEW: Individual parcel data
                }
            }
            
            logger.info(
                f"✅ Smarty data retrieved ({len(all_addresses_data)} address(es)): "
                f"{lot_data.get('size_sqft', 0):,} sqft lot, "
                f"{building_data.get('size_sqft', 0):,} sqft building, "
                f"{available_build_space.get('sqft', 0):,} sqft available - "
                f"{'QUALIFIES' if available_build_space.get('qualifies_for_logos') else 'Does not qualify'} for LOGOS"
            )
            
            return {
                "status": "success",
                "source": "smarty",
                "success": True,
                "data": smarty_summary,
                "raw_result": combined_data,
                "address_count": len(all_addresses_data)
            }
            
        except Exception as e:
            logger.error(f"Error fetching Smarty data: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "success": False,
                "data": {}
            }
