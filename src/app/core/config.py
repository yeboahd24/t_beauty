"""
Application configuration settings.
"""
import os
from typing import Optional
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
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
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