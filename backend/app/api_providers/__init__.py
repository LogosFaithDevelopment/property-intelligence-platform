"""
API Providers package initialization
Unified access to all API providers with automatic fallback
"""

from typing import Dict, Any, Optional
import logging

from app.api_providers.free_providers import get_free_providers
from app.api_providers.professional_providers import get_professional_providers
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class APIProviderManager:
    """Manages API providers with automatic fallback from professional to free"""
    
    def __init__(self):
        self.free_providers = get_free_providers()
        self.professional_providers = get_professional_providers()
        
        logger.info(f"Initialized API providers:")
        logger.info(f"- Free providers: {list(self.free_providers.keys())}")
        logger.info(f"- Professional providers: {list(self.professional_providers.keys())}")
    
    def get_property_provider(self):
        """Get the best available property data provider"""
        return (
            self.professional_providers.get("property_data") or
            self.free_providers.get("housing_data")
        )
    
    def get_location_provider(self):
        """Get the best available location provider"""
        return (
            self.professional_providers.get("location") or
            self.free_providers.get("location")
        )
    
    def get_demographics_provider(self):
        """Get demographics provider (Census API)"""
        return self.free_providers.get("demographics")
    
    def get_risk_provider(self):
        """Get risk assessment provider (FEMA)"""
        return self.free_providers.get("flood_risk")
    
    def get_rental_provider(self):
        """Get rental market data provider"""
        return self.professional_providers.get("rental_data")
    
    @property
    def has_professional_apis(self) -> bool:
        """Check if professional APIs are available"""
        return len(self.professional_providers) > 0
    
    @property
    def provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "professional_active": self.has_professional_apis,
            "available_providers": {
                "property_data": bool(self.get_property_provider()),
                "location": bool(self.get_location_provider()),
                "demographics": bool(self.get_demographics_provider()),
                "risk_assessment": bool(self.get_risk_provider()),
                "rental_data": bool(self.get_rental_provider())
            },
            "api_keys_configured": {
                "attom": bool(settings.attom_api_key),
                "google_maps": bool(settings.google_maps_api_key),
                "rentberry": bool(settings.rentberry_api_key),
                "census": bool(settings.census_api_key)
            }
        }


# Global provider manager instance
provider_manager = APIProviderManager()


# Convenience functions for easy access
def get_property_provider():
    """Get the best available property data provider"""
    return provider_manager.get_property_provider()


def get_location_provider():
    """Get the best available location provider"""  
    return provider_manager.get_location_provider()


def get_demographics_provider():
    """Get demographics provider"""
    return provider_manager.get_demographics_provider()


def get_risk_provider():
    """Get risk assessment provider"""
    return provider_manager.get_risk_provider()


def get_rental_provider():
    """Get rental market data provider"""
    return provider_manager.get_rental_provider()


__all__ = [
    "APIProviderManager",
    "provider_manager",
    "get_property_provider",
    "get_location_provider", 
    "get_demographics_provider",
    "get_risk_provider",
    "get_rental_provider"
]
