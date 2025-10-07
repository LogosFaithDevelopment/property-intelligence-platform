"""
LA County Assessor API Client

Provides comprehensive property data for Los Angeles County properties including:
- Lot size (square footage and acreage)
- Property valuations (land, improvements, total assessed value)
- Year built and effective year built
- Property use type and classification
- Building characteristics (bedrooms, bathrooms, units)
- Recording dates (last sale/transfer)
- Tax exemptions and assessed values
- Geographic coordinates

Data Source: LA County Assessor's Office via ArcGIS REST API
Coverage: 2021-present
Free alternative to ATTOM for California properties
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class LACountyAssessorClient:
    """Client for LA County Assessor parcel data API"""
    
    BASE_URL = "https://services.arcgis.com/RmCCgQtiZLDCtblq/arcgis/rest/services/Parcel_Data_2021_Table/FeatureServer/0"
    
    def __init__(self, timeout: int = 30):
        """
        Initialize LA County Assessor API client
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()
    
    async def get_property_by_address(
        self,
        street_address: str,
        city: str = None,
        zip_code: str = None
    ) -> Dict[str, Any]:
        """
        Get property data by address
        
        Args:
            street_address: Street address (e.g., "123 Main St")
            city: City name (optional, helps narrow results)
            zip_code: ZIP code (optional, helps narrow results)
            
        Returns:
            Property data dictionary or error information
        """
        try:
            # Parse street address into components
            # Format: "19700 Rinaldi St" -> house_no=19700, street="RINALDI ST"
            address_upper = street_address.upper().strip()
            parts = address_upper.split(None, 1)  # Split on first whitespace
            
            if len(parts) < 2:
                return {
                    'success': False,
                    'error': 'Invalid address format. Expected format: "123 Main St"',
                    'search_address': street_address
                }
            
            house_no = parts[0]
            street_name = parts[1]
            
            # Build query using individual fields (more accurate than PropertyLocation LIKE)
            where_clauses = []
            
            # House number (as integer)
            try:
                house_num = int(house_no)
                where_clauses.append(f"SitusHouseNo={house_num}")
            except ValueError:
                # If house number isn't numeric, fall back to PropertyLocation search
                where_clauses.append(f"PropertyLocation LIKE '%{address_upper}%'")
            
            # Street name (use LIKE for flexibility with St/Street, Ave/Avenue, etc.)
            if len(where_clauses) == 1:  # Only if house number was valid
                where_clauses.append(f"SitusStreet LIKE '{street_name}%'")
            
            # Add ZIP filter if provided (most accurate)
            if zip_code:
                zip5 = zip_code[:5]  # Use 5-digit ZIP
                where_clauses.append(f"SitusZIP5='{zip5}'")
            
            where_clause = " AND ".join(where_clauses)
            
            # Query parameters
            params = {
                'where': where_clause,
                'outFields': '*',  # Get all fields
                'returnGeometry': 'false',
                'f': 'json',
                'resultRecordCount': 1  # Limit to 1 result (most recent)
            }
            
            logger.info(f"Querying LA County Assessor API for address: {street_address}")
            logger.debug(f"Query where clause: {where_clause}")
            
            response = await self.session.get(
                f"{self.BASE_URL}/query",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for features
            features = data.get('features', [])
            if not features:
                logger.warning(f"No property found for address: {street_address}")
                return {
                    'success': False,
                    'error': 'Property not found in LA County Assessor database',
                    'search_address': street_address,
                    'search_city': city,
                    'search_zip': zip_code
                }
            
            # Extract property attributes
            property_data = features[0].get('attributes', {})
            
            # Parse and structure the data
            parsed_result = self._parse_property_data(property_data)
            
            # Extract key fields to top level for easy access
            key_fields = self.extract_key_fields(parsed_result)
            
            # Combine everything
            result = {
                'success': True,
                'data_source': 'LA County Assessor',
                'query_date': datetime.now().isoformat(),
                **key_fields,  # Flatten key fields to top level
                'detailed': parsed_result  # Keep structured data for reference
            }
            
            logger.info(f"Successfully retrieved LA County property data for {street_address}")
            logger.info(f"Lot size: {key_fields.get('lot_size_sqft')} sqft ({key_fields.get('lot_size_acres')} acres)")
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error querying LA County Assessor API: {e}")
            return {
                'success': False,
                'error': f'API request failed: {str(e)}',
                'search_address': street_address
            }
        except Exception as e:
            logger.error(f"Error querying LA County Assessor API: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'search_address': street_address
            }
    
    async def get_property_by_ain(self, ain: str) -> Dict[str, Any]:
        """
        Get property data by Assessor's Identification Number (AIN)
        
        Args:
            ain: Assessor's Identification Number (10 digits, e.g., "1234567890")
            
        Returns:
            Property data dictionary or error information
        """
        try:
            params = {
                'where': f"AIN = '{ain}'",
                'outFields': '*',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            logger.info(f"Querying LA County Assessor API for AIN: {ain}")
            
            response = await self.session.get(
                f"{self.BASE_URL}/query",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            if not features:
                logger.warning(f"No property found for AIN: {ain}")
                return {
                    'success': False,
                    'error': 'Property not found',
                    'ain': ain
                }
            
            property_data = features[0].get('attributes', {})
            parsed_result = self._parse_property_data(property_data)
            
            # Extract key fields to top level
            key_fields = self.extract_key_fields(parsed_result)
            
            result = {
                'success': True,
                'data_source': 'LA County Assessor',
                'query_date': datetime.now().isoformat(),
                **key_fields,
                'detailed': parsed_result
            }
            
            logger.info(f"Successfully retrieved property data for AIN: {ain}")
            return result
            
        except Exception as e:
            logger.error(f"Error querying LA County Assessor API: {e}")
            return {
                'success': False,
                'error': str(e),
                'ain': ain
            }
    
    async def get_property_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        distance_meters: int = 50
    ) -> Dict[str, Any]:
        """
        Get property data by geographic coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            distance_meters: Search radius in meters (default: 50m)
            
        Returns:
            Property data dictionary or error information
        """
        try:
            # Search within a small radius of the coordinates
            # Note: This is approximate - may need adjustment based on testing
            lat_tolerance = distance_meters / 111000  # Rough conversion: 1 degree ≈ 111km
            lon_tolerance = distance_meters / (111000 * abs(longitude))
            
            where_clause = (
                f"Center_lat >= {latitude - lat_tolerance} AND "
                f"Center_lat <= {latitude + lat_tolerance} AND "
                f"Center_lon >= {longitude - lon_tolerance} AND "
                f"Center_lon <= {longitude + lon_tolerance}"
            )
            
            params = {
                'where': where_clause,
                'outFields': '*',
                'returnGeometry': 'false',
                'f': 'json',
                'resultRecordCount': 1
            }
            
            logger.info(f"Querying LA County Assessor API for coordinates: {latitude}, {longitude}")
            
            response = await self.session.get(
                f"{self.BASE_URL}/query",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            if not features:
                logger.warning(f"No property found near coordinates: {latitude}, {longitude}")
                return {
                    'success': False,
                    'error': 'No property found at these coordinates',
                    'latitude': latitude,
                    'longitude': longitude
                }
            
            property_data = features[0].get('attributes', {})
            parsed_result = self._parse_property_data(property_data)
            
            # Extract key fields to top level
            key_fields = self.extract_key_fields(parsed_result)
            
            result = {
                'success': True,
                'data_source': 'LA County Assessor',
                'query_date': datetime.now().isoformat(),
                **key_fields,
                'detailed': parsed_result
            }
            
            logger.info(f"Successfully retrieved property data for coordinates: {latitude}, {longitude}")
            return result
            
        except Exception as e:
            logger.error(f"Error querying LA County Assessor API: {e}")
            return {
                'success': False,
                'error': str(e),
                'latitude': latitude,
                'longitude': longitude
            }
    
    def _parse_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and structure raw property data from LA County Assessor API
        
        Args:
            raw_data: Raw attributes from API response
            
        Returns:
            Structured property data dictionary with complete field mapping
        """
        # Location information
        location = {
            'property_location': raw_data.get('PropertyLocation'),
            'situs_address': {
                'house_number': raw_data.get('SitusHouseNo'),
                'fraction': raw_data.get('SitusFraction'),
                'direction': raw_data.get('SitusDirection'),
                'street': raw_data.get('SitusStreet'),
                'unit': raw_data.get('SitusUnit'),
                'city': raw_data.get('SitusCity'),
                'zip5': raw_data.get('SitusZIP5'),
                'zip_full': raw_data.get('SitusZIP')
            },
            'coordinates': {
                'latitude': raw_data.get('Center_lat'),  # Correct field name
                'longitude': raw_data.get('Center_lon')  # Correct field name
            }
        }
        
        # Parcel identification
        identification = {
            'ain': raw_data.get('AIN'),
            'assessor_id': raw_data.get('AssessorID'),
            'map_reference': raw_data.get('MapReference'),
            'roll_year': raw_data.get('RollYear'),
            'roll_id': raw_data.get('Roll_Roll_ID'),
            'tax_rate_area': raw_data.get('TaxRateArea'),
            'tax_rate_area_city': raw_data.get('TaxRateArea_CITY'),
            'row_id': raw_data.get('RowID_'),
            'object_id': raw_data.get('OBJECTID')
        }
        
        # Property characteristics
        sqft_main = raw_data.get('SQFTmain')
        characteristics = {
            # Lot dimensions
            'lot_size_sqft': sqft_main,
            'lot_size_acres': round(sqft_main / 43560, 2) if sqft_main else None,
            
            # Building info
            'year_built': raw_data.get('YearBuilt1'),
            'year_built_2': raw_data.get('YearBuilt2'),  # Additional building
            'year_built_3': raw_data.get('YearBuilt3'),
            'year_built_4': raw_data.get('YearBuilt4'),
            'year_built_5': raw_data.get('YearBuilt5'),
            'effective_year_built': raw_data.get('EffectiveYearBuilt1'),
            
            # Units & rooms
            'bedrooms': raw_data.get('Bedrooms1'),
            'bedrooms_2': raw_data.get('Bedrooms2'),
            'bedrooms_3': raw_data.get('Bedrooms3'),
            'bedrooms_4': raw_data.get('Bedrooms4'),
            'bedrooms_5': raw_data.get('Bedrooms5'),
            'bathrooms': raw_data.get('Bathrooms1'),
            'bathrooms_2': raw_data.get('Bathrooms2'),
            'bathrooms_3': raw_data.get('Bathrooms3'),
            'bathrooms_4': raw_data.get('Bathrooms4'),
            'bathrooms_5': raw_data.get('Bathrooms5'),
            'units': raw_data.get('Units1'),
            'units_2': raw_data.get('Units2'),
            'units_3': raw_data.get('Units3'),
            'units_4': raw_data.get('Units4'),
            'units_5': raw_data.get('Units5'),
            
            # Building counts
            'num_buildings': raw_data.get('totBuildingDataLines'),
            
            # Square footage
            'sqft_building_1': raw_data.get('SQFTmain1'),
            'sqft_building_2': raw_data.get('SQFTmain2'),
            'sqft_building_3': raw_data.get('SQFTmain3'),
            'sqft_building_4': raw_data.get('SQFTmain4'),
            'sqft_building_5': raw_data.get('SQFTmain5'),
            
            # Specific use codes per building
            'specific_use_1': raw_data.get('SpecificUseType1'),
            'specific_use_2': raw_data.get('SpecificUseType2'),
            'specific_use_3': raw_data.get('SpecificUseType3'),
            'specific_use_4': raw_data.get('SpecificUseType4'),
            'specific_use_5': raw_data.get('SpecificUseType5')
        }
        
        # Property use/zoning
        use_info = {
            'use_type': raw_data.get('UseType'),
            'use_code': raw_data.get('UseCode'),
            'use_code_descriptions': {
                'char1': raw_data.get('UseCode_Desc_Char1'),
                'char2': raw_data.get('UseCode_Desc_Char2'),
                'char3': raw_data.get('UseCode_Desc_Char3'),
                'char4': raw_data.get('UseCode_Desc_Char4')
            },
            'classification': raw_data.get('ParcelClassification'),
            'general_use_type': raw_data.get('GeneralUseType')
        }
        
        # Valuation data (Roll prefix = current tax roll)
        valuation = {
            # Land
            'land_value': raw_data.get('Roll_LandValue'),
            'land_base_year': raw_data.get('Roll_LandBaseYear'),
            
            # Improvements
            'improvement_value': raw_data.get('Roll_ImpValue'),
            'improvement_base_year': raw_data.get('Roll_ImpBaseYear'),
            
            # Combined land + improvements
            'total_land_improvement': raw_data.get('Roll_totLandImp'),
            
            # Other values
            'fixture_value': raw_data.get('Roll_FixtureValue'),
            'fixture_base_year': raw_data.get('Roll_FixtureBaseYear'),
            'personal_property_value': raw_data.get('Roll_PersPropValue'),
            'personal_property_base_year': raw_data.get('Roll_PPBaseYear'),
            
            # Total assessed value
            'total_value': raw_data.get('Roll_TotalValue'),
            'net_taxable_value': raw_data.get('netTaxableValue')
        }
        
        # Exemptions
        exemptions = {
            'homeowners_exemption': raw_data.get('Roll_HomeOwnersExemp'),
            'real_estate_exemption': raw_data.get('Roll_RealEstateExemp'),
            'fixture_exemption': raw_data.get('Roll_FixtureExemp'),
            'personal_property_exemption': raw_data.get('Roll_PersPropExemp'),
            'total_exemption': raw_data.get('Roll_TotalExemption'),
            'is_taxable': raw_data.get('isTaxableParcel')
        }
        
        # Recording information (sales/transfers)
        recording_date = raw_data.get('RecordingDate')
        if recording_date:
            try:
                # Convert epoch timestamp to datetime (milliseconds)
                recording_datetime = datetime.fromtimestamp(recording_date / 1000)
                recording_date_str = recording_datetime.strftime('%Y-%m-%d')
            except (ValueError, TypeError, OverflowError):
                recording_date_str = None
        else:
            recording_date_str = None
        
        # Administrative
        administrative = {
            'admin_region': raw_data.get('AdminRegion'),
            'cluster': raw_data.get('Cluster'),
            'recording_date': recording_date_str,
            'parcel_legal_description': raw_data.get('ParcelBoundaryDescription')
        }
        
        return {
            'location': location,
            'identification': identification,
            'characteristics': characteristics,
            'use_info': use_info,
            'valuation': valuation,
            'exemptions': exemptions,
            'administrative': administrative,
            'raw_data': raw_data  # Keep raw data for reference
        }
    
    def extract_key_fields(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key fields for Property model integration
        
        Args:
            parsed_data: Parsed property data from _parse_property_data()
            
        Returns:
            Dictionary with fields mapped to Property model
        """
        characteristics = parsed_data.get('characteristics', {})
        valuation = parsed_data.get('valuation', {})
        location = parsed_data.get('location', {})
        use_info = parsed_data.get('use_info', {})
        
        return {
            # Property dimensions
            'lot_size_sqft': characteristics.get('lot_size_sqft'),
            'lot_size_acres': characteristics.get('lot_size_acres'),
            
            # Property details
            'year_built': characteristics.get('year_built'),
            'bedrooms': characteristics.get('bedrooms'),
            'bathrooms': characteristics.get('bathrooms'),
            'units': characteristics.get('units'),
            
            # Valuation
            'assessed_value': valuation.get('total_value'),
            'land_value': valuation.get('land_value'),
            'improvement_value': valuation.get('improvement_value'),
            
            # Location (if needed to update/verify)
            'latitude': location.get('coordinates', {}).get('latitude'),
            'longitude': location.get('coordinates', {}).get('longitude'),
            
            # Use/Classification
            'use_type': use_info.get('use_type'),
            'use_code': use_info.get('use_code'),
            'classification': use_info.get('classification'),
            
            # Data source tracking
            'data_source': 'LA County Assessor',
            'data_date': parsed_data.get('query_date')
        }


# Convenience function for quick testing
async def test_la_county_api():
    """Test function for LA County Assessor API"""
    client = LACountyAssessorClient()
    
    try:
        # Test with a sample address (replace with real test address)
        result = await client.get_property_by_address(
            street_address="1234 Main St",
            city="Los Angeles",
            zip_code="90001"
        )
        
        print("LA County Assessor API Test Result:")
        print(f"Success: {result.get('success')}")
        
        if result.get('success'):
            key_fields = client.extract_key_fields(result)
            print("\nKey Fields:")
            for key, value in key_fields.items():
                print(f"  {key}: {value}")
        else:
            print(f"Error: {result.get('error')}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_la_county_api())
