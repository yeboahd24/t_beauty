"""
Application configuration settings.
"""
import os
from typing import Optional, List, Union, Any
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "T-Beauty Business Management System"
    PROJECT_DESCRIPTION: str = "Custom-built Business Management System for Instagram-based cosmetics retailer"
    VERSION: str = "1.0.0"
    
    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from various input formats."""
        if v is None:
            return ["*"]
        
        if isinstance(v, list):
            # Already a list, ensure all items are strings
            return [str(item) for item in v]
        
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return ["*"]
            
            # Handle JSON-like string format
            if v.strip().startswith("[") and v.strip().endswith("]"):
                import json
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                    else:
                        return [str(parsed)]
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as single origin
                    return [v.strip()]
            
            # Handle comma-separated string
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else ["*"]
        
        # Handle any other type
        return [str(v)]
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY must be set")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()