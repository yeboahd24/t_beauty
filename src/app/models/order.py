"""
Order management models for T-Beauty.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Order(Base):
    """Order model for managing customer orders."""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer information
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Order details
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Pricing
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Payment tracking
    amount_paid = Column(Float, default=0.0)
    payment_method = Column(String(50))  # "bank_transfer", "cash", "pos", "instagram_payment"
    payment_reference = Column(String(255))
    
    # Shipping information
    shipping_address_line1 = Column(String(255))
    shipping_address_line2 = Column(String(255))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_postal_code = Column(String(20))
    shipping_country = Column(String(100), default="Nigeria")
    
    # Delivery details
    delivery_method = Column(String(50), default="standard")  # "standard", "express", "pickup"
    tracking_number = Column(String(255))
    courier_service = Column(String(100))  # "dhl", "ups", "local_courier", etc.
    
    # Order source
    order_source = Column(String(50), default="instagram")  # "instagram", "website", "phone", "whatsapp"
    instagram_post_url = Column(String(500))  # Link to Instagram post if applicable
    
    # Notes and special instructions
    customer_notes = Column(Text)
    internal_notes = Column(Text)
    special_instructions = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    expected_delivery_date = Column(DateTime(timezone=True))
    
    # User tracking
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="order")
    created_by = relationship("User")
    
    @property
    def is_paid(self):
        """Check if order is fully paid."""
        return self.amount_paid >= self.total_amount
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding payment amount."""
        return max(0, self.total_amount - self.amount_paid)
    
    @property
    def can_be_shipped(self):
        """Check if order can be shipped."""
        return (self.status in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.PACKED] 
                and self.payment_status in [PaymentStatus.PAID, PaymentStatus.PARTIAL])


class OrderItem(Base):
    """Individual items within an order."""
    
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    
    # Product snapshot (in case product details change)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(50), nullable=False)
    product_description = Column(Text)
    
    # Special requests
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    inventory_item = relationship("InventoryItem", back_populates="order_items")
    
    @property
    def line_total(self):
        """Calculate line total after discount."""
        return (self.unit_price * self.quantity) - self.discount_amount