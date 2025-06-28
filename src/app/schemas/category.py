"""
Category schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str
    description: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Category creation schema."""
    pass


class CategoryUpdate(BaseModel):
    """Category update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Category response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    """Category summary for dropdowns and lists."""
    id: int
    name: str
    slug: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Category list response schema."""
    categories: List[CategoryResponse]
    total: int
    page: int
    size: int