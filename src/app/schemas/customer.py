"""
Customer schemas for T-Beauty.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    """Base customer schema."""
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    instagram_handle: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Nigeria"
    is_vip: bool = False
    notes: Optional[str] = None
    preferred_contact_method: str = "instagram"


class CustomerCreate(CustomerBase):
    """Customer creation schema."""
    pass


class CustomerUpdate(BaseModel):
    """Customer update schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    instagram_handle: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None
    is_vip: Optional[bool] = None
    notes: Optional[str] = None
    preferred_contact_method: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Customer response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_order_date: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class CustomerSummary(BaseModel):
    """Customer summary for lists."""
    id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    instagram_handle: Optional[str] = None
    is_vip: bool
    last_order_date: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    """Customer list response schema."""
    customers: List[CustomerSummary]
    total: int
    page: int
    size: int