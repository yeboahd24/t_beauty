"""
Product schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0


class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


class ProductUpdate(BaseModel):
    """Product update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Product list response schema."""
    products: List[ProductResponse]
    total: int
    page: int
    size: int