"""
Base API Provider
Abstract base classes for external API integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import asyncio
import logging
from dataclasses import dataclass

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class APIResponse:
    """Standardized API response wrapper"""
    
    success: bool
    data: Dict[Any, Any]
    status_code: int
    provider: str
    endpoint: str
    cached: bool = False
    cost_estimate: float = 0.0
    error_message: Optional[str] = None


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def acquire(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.utcnow()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < timedelta(minutes=1)]
        
        # Check if we can make a call
        if len(self.calls) >= self.calls_per_minute:
            # Wait until we can make a call
            oldest_call = min(self.calls)
            wait_time = 60 - (now - oldest_call).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this call
        self.calls.append(now)


class BaseAPIProvider(ABC):
    """Abstract base class for all API providers"""
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 60):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(rate_limit)
        self.base_url = self.get_base_url()
        self.provider_name = self.get_provider_name()
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Return the base URL for this API"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name for caching and logging"""
        pass
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        headers = {
            "User-Agent": "Property-Intelligence-Platform/1.0",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def estimate_cost(self, endpoint: str, params: Dict[str, Any]) -> float:
        """Estimate the cost of an API call"""
        # Override in subclasses with actual pricing
        return 0.0
    
    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> APIResponse:
        """Make an HTTP request to the API"""
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self.get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, params=params, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Parse response
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"raw_content": response.text}
                
                # Estimate cost
                cost = self.estimate_cost(endpoint, params or {})
                
                return APIResponse(
                    success=response.status_code < 400,
                    data=response_data,
                    status_code=response.status_code,
                    provider=self.provider_name,
                    endpoint=endpoint,
                    cost_estimate=cost,
                    error_message=None if response.status_code < 400 else response_data.get("error", "API Error")
                )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {self.provider_name} API: {endpoint}")
            return APIResponse(
                success=False,
                data={},
                status_code=408,
                provider=self.provider_name,
                endpoint=endpoint,
                error_message="Request timeout"
            )
        except Exception as e:
            logger.error(f"Error calling {self.provider_name} API: {e}", exc_info=True)
            return APIResponse(
                success=False,
                data={},
                status_code=500,
                provider=self.provider_name,
                endpoint=endpoint,
                error_message=str(e)
            )


class PropertyDataProvider(BaseAPIProvider):
    """Abstract base class for property data providers"""
    
    @abstractmethod
    async def get_property_details(self, address: str) -> APIResponse:
        """Get detailed property information"""
        pass
    
    @abstractmethod
    async def get_property_value(self, address: str) -> APIResponse:
        """Get property valuation"""
        pass
    
    @abstractmethod
    async def get_ownership_info(self, address: str) -> APIResponse:
        """Get property ownership information"""
        pass


class DemographicsProvider(BaseAPIProvider):
    """Abstract base class for demographics data providers"""
    
    @abstractmethod
    async def get_census_data(self, latitude: float, longitude: float) -> APIResponse:
        """Get census demographic data for location"""
        pass
    
    @abstractmethod
    async def get_income_data(self, latitude: float, longitude: float) -> APIResponse:
        """Get income statistics for area"""
        pass


class RiskAssessmentProvider(BaseAPIProvider):
    """Abstract base class for risk assessment providers"""
    
    @abstractmethod
    async def get_flood_risk(self, latitude: float, longitude: float) -> APIResponse:
        """Get flood risk assessment"""
        pass
    
    @abstractmethod
    async def get_environmental_risks(self, address: str) -> APIResponse:
        """Get environmental risk factors"""
        pass


class LocationProvider(BaseAPIProvider):
    """Abstract base class for location and mapping providers"""
    
    @abstractmethod
    async def geocode_address(self, address: str) -> APIResponse:
        """Convert address to coordinates"""
        pass
    
    @abstractmethod
    async def get_nearby_amenities(self, latitude: float, longitude: float, radius_miles: float = 1.0) -> APIResponse:
        """Get nearby amenities and services"""
        pass
    
    @abstractmethod
    async def get_walkability_score(self, address: str) -> APIResponse:
        """Get walkability and transit scores"""
        pass
