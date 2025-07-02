"""
Shopping cart schemas for T-Beauty customer experience.
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .product import ProductSummary


class CartItemBase(BaseModel):
    """Base cart item schema."""
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    notes: Optional[str] = None


class CartItemCreate(CartItemBase):
    """Cart item creation schema."""
    pass


class CartItemUpdate(BaseModel):
    """Cart item update schema."""
    quantity: Optional[int] = Field(None, gt=0, description="Quantity must be greater than 0")
    notes: Optional[str] = None


class CartItemResponse(CartItemBase):
    """Cart item response schema."""
    id: int
    customer_id: int
    unit_price: float
    total_price: float
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    product: Optional[ProductSummary] = None
    
    model_config = {"from_attributes": True}


class CartSummary(BaseModel):
    """Shopping cart summary."""
    items_count: int
    total_amount: float
    available_items_count: int
    unavailable_items_count: int
    items: List[CartItemResponse]


class CartResponse(BaseModel):
    """Complete cart response."""
    customer_id: int
    summary: CartSummary
    
    
class AddToCartRequest(BaseModel):
    """Add item to cart request."""
    product_id: int
    quantity: int = Field(1, gt=0, description="Quantity must be greater than 0")
    notes: Optional[str] = None


class CartToOrderRequest(BaseModel):
    """Convert cart to order request."""
    # Shipping information
    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: str = "Nigeria"
    delivery_method: str = "standard"
    
    # Order details
    order_source: str = "web"
    customer_notes: Optional[str] = None
    special_instructions: Optional[str] = None
    
    # Optional: only convert specific items (if not provided, convert all available items)
    item_ids: Optional[List[int]] = None


class CheckoutResponse(BaseModel):
    """Checkout response schema."""
    order: Any  # Will be OrderResponse but avoid circular import
    converted_items_count: int
    message: str