"""
Order schemas for T-Beauty.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.order import OrderStatus, PaymentStatus


class OrderItemBase(BaseModel):
    """Base order item schema."""
    inventory_item_id: int
    quantity: int
    unit_price: float
    discount_amount: float = 0.0
    notes: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    """Order item creation schema."""
    pass


class OrderItemResponse(OrderItemBase):
    """Order item response schema."""
    id: int
    total_price: float
    product_name: str
    product_sku: str
    product_description: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class OrderBase(BaseModel):
    """Base order schema."""
    customer_id: int
    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: str = "Nigeria"
    delivery_method: str = "standard"
    order_source: str = "instagram"
    instagram_post_url: Optional[str] = None
    customer_notes: Optional[str] = None
    special_instructions: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema."""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Order update schema."""
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    tracking_number: Optional[str] = None
    courier_service: Optional[str] = None
    internal_notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None


class OrderResponse(OrderBase):
    """Order response schema."""
    id: int
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: float
    discount_amount: float
    tax_amount: float
    shipping_cost: float
    total_amount: float
    amount_paid: float
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    tracking_number: Optional[str] = None
    courier_service: Optional[str] = None
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    
    # Related data
    order_items: List[OrderItemResponse]
    
    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    """Order summary for lists."""
    id: int
    order_number: str
    customer_id: int
    customer_name: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: float
    amount_paid: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    """Order status update schema."""
    status: OrderStatus
    notes: Optional[str] = None


class PaymentUpdate(BaseModel):
    """Payment update schema."""
    amount_paid: float
    payment_method: str
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class OrderStats(BaseModel):
    """Order statistics schema."""
    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    average_order_value: float


class OrderListResponse(BaseModel):
    """Order list response schema."""
    orders: List[OrderSummary]
    total: int
    page: int
    size: int
    stats: OrderStats