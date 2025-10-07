"""
ATTOM Data API Provider
Provides property data, valuations, comparables, and risk assessments
"""

import logging
from typing import Any, Dict, Optional

import httpx
from app.api_providers.base import BaseAPIProvider

logger = logging.getLogger(__name__)


class ATTOMProvider(BaseAPIProvider):
    """ATTOM Data Solutions API Provider"""
    
    def get_base_url(self) -> str:
        return "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
    
    def get_area_base_url(self) -> str:
        """Base URL for Area API endpoints"""
        # v2.0.0 works for state/county lookups
        # v4.0.0 mentioned in docs but returns 404 for most endpoints
        return "https://api.gateway.attomdata.com/areaapi/v2.0.0"
    
    def get_provider_name(self) -> str:
        return "ATTOM Data"
    
    def get_required_env_vars(self) -> list:
        return ["ATTOM_API_KEY"]
    
    async def get_property_detail(
        self,
        address: str,
        address2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive property details
        
        Args:
            address: Street address (e.g., "4529 Winona ct" or full address)
            address2: Optional city/state (e.g., "Denver CO")
            
        Returns:
            Property details including lot size, building info, zoning, AVM
        """
        endpoint = f"{self.base_url}/property/detail"
        
        # Parse address - if it's a full address, split it
        if "," in address and not address2:
            parts = [p.strip() for p in address.split(",")]
            if len(parts) >= 2:
                params = {
                    "address1": parts[0],
                    "address2": " ".join(parts[1:])
                }
            else:
                params = {"address1": address}
        else:
            params = {"address1": address}
            if address2:
                params["address2"] = address2
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "data": self._parse_property_detail(data),
                        "raw": data
                    }
                elif response.status_code == 400:
                    return {
                        "success": False,
                        "error": "Bad Request - Invalid parameters",
                        "status_code": 400,
                        "details": response.text[:500]
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "error": "Unauthorized - Invalid API key",
                        "status_code": 401,
                        "details": response.text[:500]
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "error": "Property not found in ATTOM database",
                        "status_code": 404,
                        "details": response.text[:500]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ATTOM API returned status {response.status_code}",
                        "status_code": response.status_code,
                        "details": response.text[:500],
                        "url": str(response.url)
                    }
                    
        except Exception as e:
            logger.error(f"ATTOM property detail API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_property_expanded(
        self,
        address: str,
        address2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get expanded property profile with all available data
        
        Includes: property characteristics, assessment, building, lot, 
        utilities, area, owner, deed, mortgage, foreclosure, and more
        """
        endpoint = f"{self.base_url}/property/expandedprofile"
        
        # Parse address - if it's a full address, split it
        if "," in address and not address2:
            parts = [p.strip() for p in address.split(",")]
            if len(parts) >= 2:
                params = {
                    "address1": parts[0],
                    "address2": " ".join(parts[1:])
                }
            else:
                params = {"address1": address}
        else:
            params = {"address1": address}
            if address2:
                params["address2"] = address2
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "data": self._parse_expanded_profile(data),
                        "raw": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ATTOM API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"ATTOM expanded profile API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_avm(
        self,
        address: str,
        address2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Automated Valuation Model (AVM) - estimated property value
        
        Returns:
            Current market value estimate with confidence score
        """
        endpoint = f"{self.base_url}/attomavm/detail"
        
        # Parse address - if it's a full address, split it
        if "," in address and not address2:
            parts = [p.strip() for p in address.split(",")]
            if len(parts) >= 2:
                params = {
                    "address1": parts[0],
                    "address2": " ".join(parts[1:])
                }
            else:
                params = {"address1": address}
        else:
            params = {"address1": address}
            if address2:
                params["address2"] = address2
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "data": self._parse_avm(data),
                        "raw": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ATTOM API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"ATTOM AVM API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sales_comparables(
        self,
        address: str,
        radius: float = 0.5,
        min_beds: Optional[int] = None,
        max_beds: Optional[int] = None,
        address2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get recent sales of comparable properties
        
        Args:
            address: Property address
            radius: Search radius in miles (default 0.5)
            min_beds: Minimum bedrooms
            max_beds: Maximum bedrooms
            address2: Optional city/state
            
        Returns:
            List of comparable sales with prices, dates, property details
        """
        endpoint = f"{self.base_url}/sale/snapshot"
        
        # Parse address - if it's a full address, split it
        if "," in address and not address2:
            parts = [p.strip() for p in address.split(",")]
            if len(parts) >= 2:
                params = {
                    "address1": parts[0],
                    "address2": " ".join(parts[1:])
                }
            else:
                params = {"address1": address}
        else:
            params = {"address1": address}
            if address2:
                params["address2"] = address2
        
        params["radius"] = radius
        if min_beds:
            params["minbeds"] = min_beds
        if max_beds:
            params["maxbeds"] = max_beds
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "data": self._parse_sales_comps(data),
                        "raw": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ATTOM API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"ATTOM sales comparables API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_area_snapshot(
        self,
        zip_code: str
    ) -> Dict[str, Any]:
        """
        Get neighborhood/area statistics
        
        Returns:
            Market trends, median values, sales velocity, demographics
        """
        endpoint = f"{self.base_url}/salestrend/snapshot"
        
        params = {"postalcode": zip_code}
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "data": self._parse_area_snapshot(data),
                        "raw": data
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ATTOM API returned status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"ATTOM area snapshot API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_property_detail(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse property detail response"""
        try:
            property_data = data.get("property", [{}])[0]
            
            # Extract key fields
            address = property_data.get("address", {})
            lot = property_data.get("lot", {})
            building = property_data.get("building", {})
            assessment = property_data.get("assessment", {})
            
            return {
                "address": {
                    "street": address.get("oneLine", ""),
                    "city": address.get("locality", ""),
                    "state": address.get("countrySubd", ""),
                    "zip": address.get("postal1", "")
                },
                "lot": {
                    "sqft": lot.get("lotSize1", 0),
                    "acres": lot.get("lotSize2", 0),
                    "frontage": lot.get("frontFootage", 0),
                    "depth": lot.get("depth", 0)
                },
                "building": {
                    "sqft": building.get("size", {}).get("livingSize", 0),
                    "year_built": building.get("yearBuilt", None),
                    "bedrooms": building.get("rooms", {}).get("beds", 0),
                    "bathrooms": building.get("rooms", {}).get("baths", 0),
                    "stories": building.get("stories", 0),
                    "construction": building.get("construction", {}).get("constructionType", "")
                },
                "assessment": {
                    "assessed_value": assessment.get("assessed", {}).get("assdTtlValue", 0),
                    "market_value": assessment.get("market", {}).get("mktTtlValue", 0),
                    "tax_amount": assessment.get("tax", {}).get("taxAmt", 0),
                    "year": assessment.get("assessed", {}).get("assdYear", None)
                },
                "zoning": property_data.get("area", {}).get("zoning", ""),
                "land_use": property_data.get("summary", {}).get("proptype", "")
            }
            
        except Exception as e:
            logger.error(f"Error parsing ATTOM property detail: {e}")
            return {}
    
    def _parse_expanded_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse expanded profile response"""
        # Similar to property detail but with more fields
        return self._parse_property_detail(data)
    
    def _parse_avm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AVM response"""
        try:
            avm_data = data.get("avm", [{}])[0]
            
            return {
                "amount": avm_data.get("amount", {}).get("value", 0),
                "high": avm_data.get("amount", {}).get("high", 0),
                "low": avm_data.get("amount", {}).get("low", 0),
                "confidence_score": avm_data.get("score", None),
                "fsd": avm_data.get("fsd", None),  # Forecast Standard Deviation
                "date": avm_data.get("eventDate", None)
            }
            
        except Exception as e:
            logger.error(f"Error parsing ATTOM AVM: {e}")
            return {}
    
    def _parse_sales_comps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse sales comparables response"""
        try:
            comps = []
            properties = data.get("property", [])
            
            for prop in properties[:10]:  # Limit to 10 comps
                sale = prop.get("sale", {})
                address = prop.get("address", {})
                building = prop.get("building", {})
                
                comps.append({
                    "address": address.get("oneLine", ""),
                    "sale_price": sale.get("amount", {}).get("saleAmt", 0),
                    "sale_date": sale.get("saleTransDate", None),
                    "distance_miles": prop.get("distance", 0),
                    "bedrooms": building.get("rooms", {}).get("beds", 0),
                    "bathrooms": building.get("rooms", {}).get("baths", 0),
                    "sqft": building.get("size", {}).get("livingSize", 0),
                    "price_per_sqft": sale.get("amount", {}).get("saleAmt", 0) / 
                                     max(building.get("size", {}).get("livingSize", 1), 1)
                })
            
            return {
                "count": len(comps),
                "comparables": comps,
                "median_price": self._calculate_median([c["sale_price"] for c in comps]),
                "median_price_per_sqft": self._calculate_median([c["price_per_sqft"] for c in comps])
            }
            
        except Exception as e:
            logger.error(f"Error parsing ATTOM sales comps: {e}")
            return {"count": 0, "comparables": []}
    
    def _parse_area_snapshot(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse area snapshot response"""
        try:
            area = data.get("area", [{}])[0]
            
            return {
                "median_home_value": area.get("medianvalue", 0),
                "median_list_price": area.get("medianlistprice", 0),
                "median_sale_price": area.get("mediansaleprice", 0),
                "average_days_on_market": area.get("avgdom", 0),
                "inventory": area.get("inventory", 0),
                "sales_count": area.get("salescount", 0),
                "price_trend_1yr": area.get("pricetrend1yr", 0),
                "foreclosure_rate": area.get("foreclosurerate", 0)
            }
            
        except Exception as e:
            logger.error(f"Error parsing ATTOM area snapshot: {e}")
            return {}
    
    def _calculate_median(self, values: list) -> float:
        """Calculate median value"""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    # ============================================================
    # AREA API METHODS
    # ============================================================
    
    async def get_area_hierarchy(
        self,
        latitude: float,
        longitude: float,
        geo_type: str = "All"
    ) -> Dict[str, Any]:
        """
        Get all areas that a geographic point falls within
        
        Args:
            latitude: Latitude of the point
            longitude: Longitude of the point
            geo_type: Type of geography to return. Options:
                     All, PZ, SB, DB, ZI, N1, N2, N3, N4, ST, CO, PL, CB
                     - ZI: Zip Code Tabulation Area
                     - N1: Macro Neighborhood
                     - N2: Neighborhood
                     - N3: Sub-Neighborhood
                     - N4: Residential Subdivision
                     - DB: School District Boundary
                     - SB: School Attendance Area
                     - ST: State
                     - CO: County
                     - PL: Place (city/town)
                     - CB: CBSA (Core Based Statistical Area)
        
        Returns:
            Dictionary with area information
            
        Example:
            >>> await provider.get_area_hierarchy(41.66895, -71.5776, "ZI")
        """
        # Correct endpoint from docs: /lookup (not /hierarchy/lookup)
        endpoint = f"{self.get_area_base_url()}/lookup"
        
        # WKT format: POINT(longitude latitude) - note: longitude comes first in WKT!
        wkt_string = f"POINT({longitude} {latitude})"
        
        params = {
            "WKTString": wkt_string,
            "geoType": geo_type
        }
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_area_hierarchy(data)
                else:
                    logger.error(f"ATTOM area hierarchy returned status {response.status_code}: {response.text[:200]}")
                    return {}
        except Exception as e:
            logger.error(f"ATTOM area hierarchy lookup failed: {e}")
            raise
    
    async def get_area_boundary(
        self,
        geo_id_v4: Optional[str] = None,
        area_id: Optional[str] = None,
        format: str = "geojson"
    ) -> Dict[str, Any]:
        """
        Get the boundary geometry for a specific geographic area
        
        Args:
            geo_id_v4: Geocode identifier (e.g., "25c781485c834372b7e7b7ef0fc0c2fa")
            area_id: Known Geo ID (e.g., "ZI98648")
            format: Boundary format - "geojson" or "wkt"
        
        Returns:
            Dictionary with boundary information
            
        Example:
            >>> await provider.get_area_boundary(area_id="ZI80212", format="geojson")
        """
        # Correct endpoint from docs: /detail (not /boundary/detail)
        endpoint = f"{self.get_area_base_url()}/detail"
        
        params = {"format": format}
        
        if geo_id_v4:
            params["geoIdV4"] = geo_id_v4
        elif area_id:
            params["AreaId"] = area_id
        else:
            raise ValueError("Either geo_id_v4 or area_id must be provided")
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"ATTOM area boundary returned status {response.status_code}: {response.text[:200]}")
                    return {}
        except Exception as e:
            logger.error(f"ATTOM area boundary lookup failed: {e}")
            raise
    
    async def get_counties_in_state(self, state_id: str) -> Dict[str, Any]:
        """
        Get all counties within a state
        
        Args:
            state_id: State ID (e.g., "ST36" for New York)
        
        Returns:
            List of counties with their IDs and names
            
        Example:
            >>> await provider.get_counties_in_state("ST06")  # California
        """
        endpoint = f"{self.get_area_base_url()}/county/lookup"
        params = {"StateId": state_id}
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"ATTOM county lookup returned status {response.status_code}: {response.text[:200]}")
                    return {}
        except Exception as e:
            logger.error(f"ATTOM county lookup failed: {e}")
            raise
    
    async def get_all_states(self) -> Dict[str, Any]:
        """
        Get all US states and their IDs
        
        Returns:
            List of all states with their IDs
            
        Example:
            >>> await provider.get_all_states()
        """
        endpoint = f"{self.get_area_base_url()}/state/lookup"
        
        headers = {
            "Accept": "application/json",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(endpoint, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"ATTOM state lookup returned status {response.status_code}: {response.text[:200]}")
                    return {}
        except Exception as e:
            logger.error(f"ATTOM state lookup failed: {e}")
            raise
    
    def _parse_area_hierarchy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse area hierarchy response"""
        try:
            if not data or "status" not in data:
                return {}
            
            status = data.get("status", {})
            if status.get("code") != 0:
                logger.warning(f"ATTOM area hierarchy returned code {status.get('code')}: {status.get('short_description')}")
                return {}
            
            result = data.get("result", {})
            package = result.get("package", {})
            items = package.get("item", [])
            
            if not isinstance(items, list):
                items = [items] if items else []
            
            areas = []
            for item in items:
                area = {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": item.get("type"),
                    "geo_key": item.get("geo_key"),
                    "geo_center_latitude": item.get("geo_center_latitude"),
                    "geo_center_longitude": item.get("geo_center_longitude")
                }
                areas.append(area)
            
            return {
                "areas": areas,
                "count": len(areas)
            }
            
        except Exception as e:
            logger.error(f"Error parsing ATTOM area hierarchy: {e}")
            return {}
