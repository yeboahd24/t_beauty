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
    base_price: float
    sku: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None


class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


class ProductUpdate(BaseModel):
    """Product update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    sku: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_discontinued: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema."""
    id: int
    is_active: bool
    is_featured: bool
    is_discontinued: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    brand: Optional[BrandSummary] = None
    category: Optional[CategorySummary] = None
    
    # Computed fields from inventory
    total_stock: int = 0
    available_stock: int = 0
    is_in_stock: bool = False
    
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Product list response schema."""
    products: List[ProductResponse]
    total: int
    page: int
    size: int