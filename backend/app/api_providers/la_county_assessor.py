"""
LA County Assessor API Provider
Free public API for property data in Los Angeles County
Better than ATTOM for CA properties - includes churches and institutional properties
"""

import logging
from typing import Any, Dict, Optional

import httpx
from app.api_providers.base import APIResponse, BaseAPIProvider

logger = logging.getLogger(__name__)


class LACountyAssessorProvider(BaseAPIProvider):
    """
    LA County Assessor GeoService API Provider
    
    Free public API providing:
    - Lot size (SQFTmain)
    - Assessed land value (Roll_LandValue)
    - Assessed improvement value (Roll_ImpValue)  
    - Year built (YearBuilt)
    - Property use codes
    - Number of units, bedrooms, bathrooms
    - Coordinates (CENTER_LAT, CENTER_LON)
    - Recording date (last sale)
    - Parcel ID (AIN)
    
    Base URL: https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services
    """
    
    def get_base_url(self) -> str:
        return "https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services"
    
    def get_provider_name(self) -> str:
        return "la_county_assessor"
    
    def get_headers(self) -> Dict[str, str]:
        """No API key needed - public API"""
        return {
            "User-Agent": "Property-Intelligence-Platform/1.0",
            "Accept": "application/json"
        }
    
    def estimate_cost(self, endpoint: str, params: Dict[str, Any]) -> float:
        """Free public API"""
        return 0.0
    
    async def search_by_address(
        self,
        street_number: str,
        street_name: str,
        city: str = "Los Angeles",
        zip_code: Optional[str] = None
    ) -> APIResponse:
        """
        Search for property by address
        
        Args:
            street_number: Street number (e.g., "123")
            street_name: Street name (e.g., "Main St")
            city: City name (default: Los Angeles)
            zip_code: Optional ZIP code for more precise matching
            
        Returns:
            APIResponse with property data
        """
        # Build address query
        address_parts = [street_number, street_name]
        if city:
            address_parts.append(city)
        if zip_code:
            address_parts.append(zip_code)
        
        full_address = " ".join(address_parts)
        
        # Query parameters
        params = {
            "where": f"SitusAddress LIKE '%{street_number}%{street_name}%'",
            "outFields": (
                "AIN,SitusAddress,SitusCity,SitusZIP,"
                "SQFTmain,Roll_LandValue,Roll_ImpValue,Roll_LandBaseYear,Roll_ImpBaseYear,"
                "YearBuilt,Units,Bedrooms,Bathrooms,"
                "UseType,SpecificUseType,SpecificUseDetail1,SpecificUseDetail2,"
                "CENTER_LAT,CENTER_LON,RecordingDate"
            ),
            "returnGeometry": "false",
            "f": "json",
            "resultRecordCount": 10  # Get multiple matches to find best
        }
        
        logger.info(f"Searching LA County Assessor for address: {full_address}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/Parcel_Data_2021_Table/FeatureServer/0/query",
                    params=params,
                    headers=self.get_headers()
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Check for features (results)
                if not data.get("features"):
                    logger.warning(f"No properties found for address: {full_address}")
                    return APIResponse(
                        success=False,
                        data={},
                        status_code=200,
                        provider=self.provider_name,
                        endpoint="search_by_address",
                        error_message="No properties found"
                    )
                
                # Get the best match (first result)
                features = data["features"]
                best_match = features[0]["attributes"]
                
                # Transform to standardized format
                property_data = self._transform_property_data(best_match)
                
                logger.info(
                    f"Found property: AIN={best_match.get('AIN')}, "
                    f"Lot Size={property_data.get('lot_size_sqft')} sq ft"
                )
                
                return APIResponse(
                    success=True,
                    data=property_data,
                    status_code=200,
                    provider=self.provider_name,
                    endpoint="search_by_address",
                    cost_estimate=0.0
                )
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching LA County Assessor: {e}")
            return APIResponse(
                success=False,
                data={},
                status_code=getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500,
                provider=self.provider_name,
                endpoint="search_by_address",
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Error searching LA County Assessor: {e}")
            return APIResponse(
                success=False,
                data={},
                status_code=500,
                provider=self.provider_name,
                endpoint="search_by_address",
                error_message=str(e)
            )
    
    async def get_by_ain(self, ain: str) -> APIResponse:
        """
        Get property by Assessor Identification Number (AIN/Parcel ID)
        
        Args:
            ain: Assessor Identification Number (e.g., "5407-018-028")
            
        Returns:
            APIResponse with property data
        """
        params = {
            "where": f"AIN = '{ain}'",
            "outFields": (
                "AIN,SitusAddress,SitusCity,SitusZIP,"
                "SQFTmain,Roll_LandValue,Roll_ImpValue,Roll_LandBaseYear,Roll_ImpBaseYear,"
                "YearBuilt,Units,Bedrooms,Bathrooms,"
                "UseType,SpecificUseType,SpecificUseDetail1,SpecificUseDetail2,"
                "CENTER_LAT,CENTER_LON,RecordingDate"
            ),
            "returnGeometry": "false",
            "f": "json"
        }
        
        logger.info(f"Searching LA County Assessor for AIN: {ain}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/Parcel_Data_2021_Table/FeatureServer/0/query",
                    params=params,
                    headers=self.get_headers()
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Check for features
                if not data.get("features"):
                    logger.warning(f"No property found for AIN: {ain}")
                    return APIResponse(
                        success=False,
                        data={},
                        status_code=200,
                        provider=self.provider_name,
                        endpoint="get_by_ain",
                        error_message="Property not found"
                    )
                
                # Get property data
                property_attrs = data["features"][0]["attributes"]
                property_data = self._transform_property_data(property_attrs)
                
                logger.info(
                    f"Found property: AIN={ain}, "
                    f"Lot Size={property_data.get('lot_size_sqft')} sq ft"
                )
                
                return APIResponse(
                    success=True,
                    data=property_data,
                    status_code=200,
                    provider=self.provider_name,
                    endpoint="get_by_ain",
                    cost_estimate=0.0
                )
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting property by AIN: {e}")
            return APIResponse(
                success=False,
                data={},
                status_code=getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500,
                provider=self.provider_name,
                endpoint="get_by_ain",
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Error getting property by AIN: {e}")
            return APIResponse(
                success=False,
                data={},
                status_code=500,
                provider=self.provider_name,
                endpoint="get_by_ain",
                error_message=str(e)
            )
    
    def _transform_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform LA County Assessor data to standardized format
        
        Args:
            raw_data: Raw attributes from API response
            
        Returns:
            Standardized property data dictionary
        """
        # Calculate total assessed value
        land_value = raw_data.get("Roll_LandValue") or 0
        improvement_value = raw_data.get("Roll_ImpValue") or 0
        total_value = land_value + improvement_value
        
        # Calculate lot size in acres
        lot_size_sqft = raw_data.get("SQFTmain")
        lot_size_acres = None
        if lot_size_sqft and lot_size_sqft > 0:
            lot_size_acres = round(lot_size_sqft / 43560, 2)  # 1 acre = 43,560 sq ft
        
        # Build standardized response
        return {
            # Identifiers
            "parcel_id": raw_data.get("AIN"),
            "address": {
                "street": raw_data.get("SitusAddress"),
                "city": raw_data.get("SitusCity"),
                "zip": raw_data.get("SitusZIP")
            },
            
            # Lot information
            "lot_size_sqft": lot_size_sqft,
            "lot_size_acres": lot_size_acres,
            
            # Building information
            "year_built": raw_data.get("YearBuilt"),
            "units": raw_data.get("Units"),
            "bedrooms": raw_data.get("Bedrooms"),
            "bathrooms": raw_data.get("Bathrooms"),
            
            # Valuation (assessed values, not market values)
            "assessed_value": {
                "total": total_value,
                "land": land_value,
                "improvements": improvement_value,
                "land_base_year": raw_data.get("Roll_LandBaseYear"),
                "improvement_base_year": raw_data.get("Roll_ImpBaseYear")
            },
            
            # Property use/type
            "use_type": raw_data.get("UseType"),
            "specific_use_type": raw_data.get("SpecificUseType"),
            "use_details": {
                "detail1": raw_data.get("SpecificUseDetail1"),
                "detail2": raw_data.get("SpecificUseDetail2")
            },
            
            # Coordinates
            "coordinates": {
                "latitude": raw_data.get("CENTER_LAT"),
                "longitude": raw_data.get("CENTER_LON")
            },
            
            # Transaction info
            "recording_date": raw_data.get("RecordingDate"),
            
            # Metadata
            "data_source": "LA County Assessor",
            "data_year": "2021+",
            "is_institutional": self._is_institutional_property(raw_data)
        }
    
    def _is_institutional_property(self, raw_data: Dict[str, Any]) -> bool:
        """
        Determine if property is institutional (church, school, government)
        
        Args:
            raw_data: Raw attributes from API
            
        Returns:
            True if institutional property
        """
        use_type = (raw_data.get("UseType") or "").lower()
        specific_use = (raw_data.get("SpecificUseType") or "").lower()
        detail1 = (raw_data.get("SpecificUseDetail1") or "").lower()
        
        # Check for institutional keywords
        institutional_keywords = [
            "church", "religious", "worship", "temple", "mosque", "synagogue",
            "school", "education", "institutional", "government", "public",
            "nonprofit", "charity", "exempt"
        ]
        
        combined_text = f"{use_type} {specific_use} {detail1}"
        return any(keyword in combined_text for keyword in institutional_keywords)


# Factory function for easy instantiation
def get_la_county_assessor_provider() -> LACountyAssessorProvider:
    """Create and return LA County Assessor provider instance"""
    return LACountyAssessorProvider()
