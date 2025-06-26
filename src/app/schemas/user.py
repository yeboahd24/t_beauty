"""
User schemas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}