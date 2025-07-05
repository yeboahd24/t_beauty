"""
Order schemas for T-Beauty.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from src.app.models.order import OrderStatus, PaymentStatus
from .customer import CustomerSummary
from .inventory import InventoryItemSummary


class OrderItemBase(BaseModel):
    """Base order item schema."""
    product_id: int
    quantity: int
    unit_price: float
    discount_amount: float = 0.0
    notes: Optional[str] = None


class OrderItemCreate(BaseModel):
    """Order item creation schema."""
    product_id: int  # Customer orders a PRODUCT
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    unit_price: Optional[float] = None  # If not provided, use product base_price
    discount_amount: Optional[float] = 0.0
    notes: Optional[str] = None
    
    # Customer preferences for fulfillment
    requested_color: Optional[str] = None
    requested_shade: Optional[str] = None
    requested_size: Optional[str] = None


class OrderItemResponse(OrderItemBase):
    """Order item response schema."""
    id: int
    total_price: float
    product_name: str
    product_sku: str
    product_description: Optional[str] = None
    
    # Fulfillment tracking
    allocated_quantity: int = 0
    fulfilled_quantity: int = 0
    inventory_item_id: Optional[int] = None
    
    # Customer preferences
    requested_color: Optional[str] = None
    requested_shade: Optional[str] = None
    requested_size: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    allocated_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    
    # Related data
    inventory_item: Optional[InventoryItemSummary] = None
    
    # Computed properties
    is_fully_allocated: bool = False
    is_fully_fulfilled: bool = False
    pending_allocation: int = 0
    pending_fulfillment: int = 0
    
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
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Order must have at least one item")
    
    # Additional fields for order creation
    payment_method: Optional[str] = None
    shipping_cost: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    internal_notes: Optional[str] = None


class CustomerOrderItemCreate(BaseModel):
    """Customer order item creation schema."""
    product_id: int  # Customer orders PRODUCTS
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    unit_price: Optional[float] = None  # If not provided, use product base_price
    notes: Optional[str] = None
    
    # Customer preferences for fulfillment
    requested_color: Optional[str] = None
    requested_shade: Optional[str] = None
    requested_size: Optional[str] = None


class CustomerOrderCreate(BaseModel):
    """Customer order creation schema (no customer_id required)."""
    items: List[CustomerOrderItemCreate] = Field(..., min_length=1, description="Order must have at least one item")
    
    # Shipping information
    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: str = "Nigeria"
    delivery_method: str = "standard"
    
    # Order details
    order_source: str = "instagram"
    instagram_post_url: Optional[str] = None
    customer_notes: Optional[str] = None
    special_instructions: Optional[str] = None
    
    # Payment and pricing
    payment_method: Optional[str] = None
    shipping_cost: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0


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
    order_items: List[OrderItemResponse] = []
    customer: Optional[CustomerSummary] = None
    
    # Computed properties
    is_paid: bool = False
    outstanding_amount: float = 0.0
    can_be_shipped: bool = False
    
    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    """Order summary for lists."""
    id: int
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: float
    amount_paid: float
    outstanding_amount: float
    created_at: datetime
    customer: Optional[CustomerSummary] = None
    items_count: int = 0
    
    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    """Order status update schema."""
    status: OrderStatus
    tracking_number: Optional[str] = None
    courier_service: Optional[str] = None
    notes: Optional[str] = None


class PaymentUpdate(BaseModel):
    """Payment update schema."""
    amount_paid: float
    payment_method: str
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class OrderStats(BaseModel):
    """Order statistics schema."""
    period_days: int
    total_orders: int
    pending_orders: int
    confirmed_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    pending_revenue: float
    average_order_value: float


class OrderListResponse(BaseModel):
    """Order list response schema."""
    orders: List[OrderSummary]
    total: int
    page: int
    size: int


class LowStockImpactItem(BaseModel):
    """Low stock impact item schema."""
    name: str
    sku: Optional[str] = None
    current_stock: int
    minimum_stock: int
    ordered_quantity: int
    can_fulfill: bool


class LowStockImpact(BaseModel):
    """Low stock impact on orders schema."""
    order_id: int
    order_number: str
    customer_name: str
    total_amount: float
    low_stock_items: List[LowStockImpactItem]


class OrderConfirmation(BaseModel):
    """Order confirmation response."""
    order: OrderResponse
    stock_reductions: List[dict]
    message: str