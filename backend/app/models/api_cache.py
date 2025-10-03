"""
API Cache Model
Cache responses from external APIs to reduce costs and improve performance
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Float, Boolean, Index
from sqlalchemy.sql import func
import hashlib
import json

from app.models.base import BaseModel


class APICache(BaseModel):
    """Cache for external API responses"""
    
    __tablename__ = "api_cache"
    
    # Cache Key Information
    api_provider = Column(String(50), nullable=False, index=True)  # "attom", "census", "hud", etc.
    endpoint = Column(String(255), nullable=False)  # API endpoint called
    params_hash = Column(String(64), nullable=False, index=True)  # Hash of request parameters
    
    # Request Information
    request_params = Column(Text, nullable=True)  # JSON string of original parameters
    request_url = Column(Text, nullable=True)  # Full URL called
    
    # Response Information
    response_data = Column(Text, nullable=False)  # JSON response data
    response_status = Column(Integer, nullable=False)  # HTTP status code
    response_size_bytes = Column(Integer, nullable=True)
    
    # Cache Metadata
    expires_at = Column(DateTime(timezone=True), nullable=False)
    hit_count = Column(Integer, default=0, nullable=False)  # How many times used
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # API Cost Tracking
    api_cost_estimate = Column(Float, nullable=True)  # Estimated cost of this API call
    
    # Data Quality
    is_valid = Column(Boolean, default=True, nullable=False)
    validation_errors = Column(Text, nullable=True)  # JSON array of any validation issues
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_api_cache_lookup', 'api_provider', 'endpoint', 'params_hash'),
        Index('ix_api_cache_expires', 'expires_at'),
        Index('ix_api_cache_provider_expires', 'api_provider', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<APICache(id={self.id}, provider='{self.api_provider}', hits={self.hit_count})>"
    
    @classmethod
    def generate_cache_key(cls, api_provider: str, endpoint: str, params: dict) -> str:
        """Generate consistent cache key hash"""
        # Sort parameters for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        combined = f"{api_provider}:{endpoint}:{sorted_params}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return self.expires_at < func.now()
    
    @property
    def response_data_json(self) -> dict:
        """Get response data as parsed JSON"""
        try:
            return json.loads(self.response_data)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def increment_hit_count(self):
        """Increment hit count and update last accessed"""
        self.hit_count += 1
        self.last_accessed = func.now()
    
    @property
    def cache_efficiency(self) -> float:
        """Calculate cache efficiency (cost savings)"""
        if self.hit_count <= 1:
            return 0.0
        
        # Estimate savings: (hits - 1) * estimated_cost
        savings = (self.hit_count - 1) * (self.api_cost_estimate or 0)
        return round(savings, 4)
