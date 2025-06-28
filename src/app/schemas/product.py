"""
Product schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .brand import BrandSummary
from .category import CategorySummary


class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0
    sku: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


class ProductUpdate(BaseModel):
    """Product update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    sku: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    brand: Optional[BrandSummary] = None
    category: Optional[CategorySummary] = None
    
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Product list response schema."""
    products: List[ProductResponse]
    total: int
    page: int
    size: int