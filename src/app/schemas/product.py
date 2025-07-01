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
    
    # Image fields
    primary_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ProductCreate(ProductBase):
    """Product creation schema."""
    additional_image_urls: Optional[List[str]] = None  # List of additional image URLs


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
    
    # Image fields
    primary_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    additional_image_urls: Optional[List[str]] = None


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
    
    # Computed image fields
    all_image_urls: List[str] = []
    display_image_url: Optional[str] = None
    
    model_config = {"from_attributes": True}


class ProductImageUpdate(BaseModel):
    """Product image update schema."""
    primary_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    additional_image_urls: Optional[List[str]] = None


class ProductFormData(BaseModel):
    """Product form data schema for file uploads."""
    name: str
    description: Optional[str] = None
    base_price: float
    sku: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = False
    is_discontinued: Optional[bool] = False


class ProductUpdateFormData(BaseModel):
    """Product update form data schema for file uploads."""
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


class ProductSummary(BaseModel):
    """Product summary for lists and references."""
    id: int
    name: str
    sku: str
    base_price: float
    display_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    is_in_stock: bool
    total_stock: int = 0
    
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Product list response schema."""
    products: List[ProductResponse]
    total: int
    page: int
    size: int