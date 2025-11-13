"""
Smarty API Provider
Provides property data for ALL property types including commercial/religious properties
CRITICAL: Requires match=enhanced to get smarty_key for property lookups
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)


class SmartyProvider:
    """
    Smarty API Provider for property data enrichment
    
    Two-step process:
    1. US Street Address API (with match=enhanced) -> Get SmartyKey
    2. US Enrichment API (property/principal) -> Get property data
    
    Key Features:
    - ✅ Works for ALL property types (residential, commercial, religious)
    - ✅ Lot size data (acres, sqft)
    - ✅ Building characteristics  
    - ✅ Parcel/lot numbers (APN)
    - ✅ Financial history (mortgages when available)
    - ✅ Property valuations
    - ✅ Available build space calculation
    """
    
    def __init__(
        self,
        auth_id: str,
        auth_token: str,
        timeout: int = 30
    ):
        """
        Initialize Smarty API provider
        
        Args:
            auth_id: Smarty Auth ID
            auth_token: Smarty Auth Token
            timeout: Request timeout in seconds
        """
        self.auth_id = auth_id
        self.auth_token = auth_token
        self.timeout = timeout
        
        # API Endpoints
        self.street_address_url = "https://us-street.api.smarty.com/street-address"
        self.enrichment_base_url = "https://us-enrichment.api.smarty.com/lookup"
    
    async def get_property_data(
        self,
        street: str,
        city: str,
        state: str,
        zipcode: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive property data including lot size and financials
        
        Args:
            street: Street address (e.g., "709 Manchester Ave")
            city: City name (e.g., "Los Angeles")
            state: State code (e.g., "CA")
            zipcode: ZIP code (e.g., "90044")
            
        Returns:
            Dict with property data or error information
        """
        try:
            # Step 1: Get SmartyKey from Street Address API
            smarty_key_result = await self._get_smarty_key(street, city, state, zipcode)
            
            if not smarty_key_result['success']:
                return smarty_key_result
            
            smarty_key = smarty_key_result['smarty_key']
            address_data = smarty_key_result['address_data']
            
            # Step 2: Get Property Data using SmartyKey
            property_result = await self._get_property_details(smarty_key)
            
            if not property_result['success']:
                return property_result
            
            # Combine and structure the data
            return self._structure_property_data(
                address_data=address_data,
                property_data=property_result['property_data'],
                smarty_key=smarty_key
            )
            
        except Exception as e:
            logger.error(f"Error getting Smarty property data: {e}")
            return {
                'success': False,
                'error': f"Smarty API error: {str(e)}",
                'provider': 'Smarty'
            }
    
    async def _get_smarty_key(
        self,
        street: str,
        city: str,
        state: str,
        zipcode: str
    ) -> Dict[str, Any]:
        """
        Step 1: Get SmartyKey from US Street Address API
        CRITICAL: Must use match=enhanced to get smarty_key in response
        """
        params = {
            "auth-id": self.auth_id,
            "auth-token": self.auth_token,
            "street": street,
            "city": city,
            "state": state,
            "zipcode": zipcode,
            "match": "enhanced"  # REQUIRED to get smarty_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.street_address_url, params=params)
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Street Address API error: {response.status_code}",
                        'details': response.text[:500]
                    }
                
                data = response.json()
                
                if not data or len(data) == 0:
                    return {
                        'success': False,
                        'error': "Address not found",
                        'details': "No results returned from Street Address API"
                    }
                
                # Get smarty_key from root level (not metadata!)
                smarty_key = data[0].get('smarty_key')
                
                if not smarty_key:
                    return {
                        'success': False,
                        'error': "No SmartyKey returned",
                        'details': "Address validated but no SmartyKey in response"
                    }
                
                logger.info(f"✅ Got SmartyKey: {smarty_key}")
                
                return {
                    'success': True,
                    'smarty_key': smarty_key,
                    'address_data': data[0]
                }
                
        except Exception as e:
            logger.error(f"Error getting SmartyKey: {e}")
            return {
                'success': False,
                'error': f"Street Address API exception: {str(e)}"
            }
    
    async def _get_property_details(self, smarty_key: str) -> Dict[str, Any]:
        """
        Step 2: Get property data from US Enrichment API using SmartyKey
        """
        # URL encode the smarty_key
        encoded_key = quote(str(smarty_key))
        url = f"{self.enrichment_base_url}/{encoded_key}/property/principal"
        
        params = {
            "auth-id": self.auth_id,
            "auth-token": self.auth_token
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 402:
                    return {
                        'success': False,
                        'error': "Payment required - Smarty subscription inactive",
                        'details': response.text[:500]
                    }
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f"Enrichment API error: {response.status_code}",
                        'details': response.text[:500]
                    }
                
                data = response.json()
                
                # Response is a list with one item containing attributes
                if isinstance(data, list) and len(data) > 0:
                    result = data[0]
                    attributes = result.get('attributes', {})
                else:
                    return {
                        'success': False,
                        'error': "No property data returned",
                        'details': "Empty response from Enrichment API"
                    }
                
                logger.info(f"✅ Got property data for SmartyKey: {smarty_key}")
                
                return {
                    'success': True,
                    'property_data': attributes
                }
                
        except Exception as e:
            logger.error(f"Error getting property details: {e}")
            return {
                'success': False,
                'error': f"Enrichment API exception: {str(e)}"
            }
    
    def _structure_property_data(
        self,
        address_data: Dict[str, Any],
        property_data: Dict[str, Any],
        smarty_key: str
    ) -> Dict[str, Any]:
        """
        Structure and calculate property data for LOGOS
        
        Key calculations:
        - Lot size (sqft and acres)
        - Building size (sqft)
        - Available Build Space = Lot Size - Building Size (THE MONEY NUMBER!)
        - Qualifies for LOGOS if Available Build Space >= 10,000 sqft
        """
        # Extract lot size data
        acres = float(property_data.get('acres', 0) or 0)
        lot_sqft = int(float(property_data.get('lot_sqft', 0) or 0))
        
        # If lot_sqft not provided, calculate from acres
        if lot_sqft == 0 and acres > 0:
            lot_sqft = int(acres * 43560)
        
        # Extract building size
        building_sqft = int(float(property_data.get('building_sqft', 0) or 0))
        
        # 🎯 CALCULATE AVAILABLE BUILD SPACE (THE KEY METRIC!)
        available_build_space = lot_sqft - building_sqft if lot_sqft > 0 else 0
        
        # Check if qualifies for LOGOS (>= 10,000 sqft available)
        qualifies_for_logos = available_build_space >= 10000
        
        # Extract lot/parcel numbers
        lot_number = property_data.get('lot_1', '')  # Can contain multiple lots (e.g., "182,183")
        parcel_number = property_data.get('parcel_raw_number', '') or property_data.get('parcel_number', '')
        
        # Extract valuation data
        assessed_value = int(float(property_data.get('assessed_value', 0) or 0))
        assessed_land_value = int(float(property_data.get('assessed_land_value', 0) or 0))
        assessed_improvement_value = int(float(property_data.get('assessed_improvement_value', 0) or 0))
        
        # Calculate estimated market value range (3-5x assessed value for CA)
        estimated_market_value_min = assessed_value * 3 if assessed_value > 0 else 0
        estimated_market_value_max = assessed_value * 5 if assessed_value > 0 else 0
        
        # Extract financial history (mortgages)
        financial_history = property_data.get('financial_history', [])
        has_mortgages = len(financial_history) > 0 if financial_history else False
        
        # Total mortgage amount
        total_mortgage_amount = sum(
            int(float(m.get('mortgage_amount', 0) or 0))
            for m in financial_history
        ) if financial_history else 0
        
        # Extract address components
        components = address_data.get('components', {})
        metadata = address_data.get('metadata', {})
        
        # Structure the response
        structured_data = {
            'success': True,
            'provider': 'Smarty',
            'smarty_key': smarty_key,
            
            # Address Information
            'address': {
                'street': address_data.get('delivery_line_1', ''),
                'city': components.get('city_name', ''),
                'state': components.get('state_abbreviation', ''),
                'zipcode': components.get('zipcode', ''),
                'zip_plus4': components.get('plus4_code', ''),
                'county': metadata.get('county_name', ''),
                'latitude': metadata.get('latitude'),
                'longitude': metadata.get('longitude')
            },
            
            # 🎯 CRITICAL METRICS FOR LOGOS
            'lot': {
                'size_acres': acres,
                'size_sqft': lot_sqft,
                'lot_numbers': lot_number,  # Can be multiple lots (e.g., "182,183")
                'parcel_number': parcel_number,  # APN
            },
            
            'building': {
                'size_sqft': building_sqft,
                'year_built': property_data.get('year_built'),
                'stories': property_data.get('stories'),
                'construction_type': property_data.get('construction_type'),
                '1st_floor_sqft': int(float(property_data.get('1st_floor_sqft', 0) or 0)),
                '2nd_floor_sqft': int(float(property_data.get('2nd_floor_sqft', 0) or 0)),
            },
            
            # 💰 THE MONEY NUMBER - Available Build Space
            'available_build_space': {
                'sqft': available_build_space,
                'acres': round(available_build_space / 43560, 4) if available_build_space > 0 else 0,
                'qualifies_for_logos': qualifies_for_logos,
                'minimum_required': 10000,
                'calculation': f"{lot_sqft:,} sqft (lot) - {building_sqft:,} sqft (building) = {available_build_space:,} sqft"
            },
            
            # Property Valuation
            'valuation': {
                'assessed_total': assessed_value,
                'assessed_land': assessed_land_value,
                'assessed_improvement': assessed_improvement_value,
                'assessed_year': property_data.get('assessor_taxroll_update'),
                'estimated_market_min': estimated_market_value_min,
                'estimated_market_max': estimated_market_value_max,
                'note': "Assessed value is for tax purposes. Estimated market value is 3-5x assessed value (typical for CA Prop 13)."
            },
            
            # Property Classification
            'property_type': {
                'land_use': property_data.get('land_use_standard', ''),
                'land_use_code': property_data.get('land_use_code', ''),
                'zoning': property_data.get('zoning', ''),
                'rdi': metadata.get('rdi', ''),  # Residential/Commercial indicator
            },
            
            # Financial History (Mortgages)
            'financial': {
                'has_mortgages': has_mortgages,
                'total_mortgage_amount': total_mortgage_amount,
                'mortgage_count': len(financial_history) if financial_history else 0,
                'mortgages': self._parse_financial_history(financial_history) if financial_history else []
            },
            
            # Owner Information
            'owner': {
                'name': property_data.get('deed_owner_full_name', ''),
                'last_sale_date': property_data.get('deed_sale_date', ''),
                'last_sale_price': int(float(property_data.get('sale_price', 0) or 0)),
            },
            
            # Raw data for reference
            'raw_property_data': property_data,
            'raw_address_data': address_data
        }
        
        logger.info(
            f"Property structured: {lot_sqft:,} sqft lot, {building_sqft:,} sqft building, "
            f"{available_build_space:,} sqft available - "
            f"{'✅ QUALIFIES' if qualifies_for_logos else '❌ Does not qualify'} for LOGOS"
        )
        
        return structured_data
    
    def _parse_financial_history(self, financial_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse and structure financial history (mortgages)"""
        mortgages = []
        
        for mortgage in financial_history:
            mortgages.append({
                'amount': int(float(mortgage.get('mortgage_amount', 0) or 0)),
                'type': mortgage.get('mortgage_type', ''),
                'lender_name': mortgage.get('lender_name', ''),
                'lender_city': mortgage.get('lender_city', ''),
                'lender_state': mortgage.get('lender_state', ''),
                'recording_date': mortgage.get('mortgage_recording_date', ''),
                'due_date': mortgage.get('mortgage_due_date', ''),
                'term': mortgage.get('mortgage_term', ''),
                'term_type': mortgage.get('mortgage_term_type', ''),
                'document_type': mortgage.get('document_type_description', '')
            })
        
        return mortgages
    
    async def close(self):
        """Close any open connections (for compatibility)"""
        pass
