"""
Application Configuration
Using Pydantic Settings for environment-based configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Property Intelligence Platform"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    secret_key: str = Field(..., alias="SECRET_KEY")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(..., alias="REDIS_URL")
    
    # Authentication (Clerk)
    clerk_secret_key: str = Field(..., alias="CLERK_SECRET_KEY")
    clerk_webhook_secret: Optional[str] = Field(None, alias="CLERK_WEBHOOK_SECRET")
    
    # AI/ML APIs
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")
    
    # Free Tier APIs
    census_api_key: Optional[str] = Field(None, alias="CENSUS_API_KEY")
    
    # Professional Tier APIs (activated later)
    attom_api_key: Optional[str] = Field(None, alias="ATTOM_API_KEY")
    google_maps_api_key: Optional[str] = Field(None, alias="GOOGLE_MAPS_API_KEY")
    rentberry_api_key: Optional[str] = Field(None, alias="RENTBERRY_API_KEY")
    
    # API Configuration
    api_rate_limit: int = Field(default=60, alias="API_RATE_LIMIT_PER_MINUTE")
    premium_rate_limit: int = Field(default=1000, alias="PREMIUM_API_RATE_LIMIT_PER_MINUTE")
    
    # File Upload
    max_file_size_mb: int = Field(default=10, alias="MAX_FILE_SIZE_MB")
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx", "jpg", "jpeg", "png"], 
        alias="ALLOWED_FILE_TYPES"
    )
    
    # Email (Optional)
    smtp_host: Optional[str] = Field(None, alias="SMTP_HOST")
    smtp_port: Optional[int] = Field(None, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(None, alias="SMTP_PASSWORD")
    
    # Monitoring (Optional)
    sentry_dsn: Optional[str] = Field(None, alias="SENTRY_DSN")
    posthog_api_key: Optional[str] = Field(None, alias="POSTHOG_API_KEY")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="ALLOWED_ORIGINS"
    )
    
    @validator("allowed_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_file_types(cls, v):
        """Parse allowed file types from string or list"""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def has_professional_apis(self) -> bool:
        """Check if professional tier APIs are configured"""
        return bool(self.attom_api_key and self.google_maps_api_key)
    
    @property
    def database_url_async(self) -> str:
        """Convert database URL to async format for SQLAlchemy 2.0"""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()


# Export commonly used settings
settings = get_settings()
