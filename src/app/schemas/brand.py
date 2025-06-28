"""
Brand schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class BrandBase(BaseModel):
    """Base brand schema."""
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class BrandCreate(BrandBase):
    """Brand creation schema."""
    pass


class BrandUpdate(BaseModel):
    """Brand update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    """Brand response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class BrandSummary(BaseModel):
    """Brand summary for dropdowns and lists."""
    id: int
    name: str
    
    model_config = {"from_attributes": True}


class BrandListResponse(BaseModel):
    """Brand list response schema."""
    brands: List[BrandResponse]
    total: int
    page: int
    size: int