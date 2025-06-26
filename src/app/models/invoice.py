"""
Invoice and payment tracking models for T-Beauty.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    POS = "pos"
    MOBILE_MONEY = "mobile_money"
    INSTAGRAM_PAYMENT = "instagram_payment"
    CRYPTO = "crypto"
    OTHER = "other"


class Invoice(Base):
    """Invoice model for billing customers."""
    
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Related entities
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))  # Optional: invoice might not be tied to order
    
    # Invoice details
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    
    # Amounts
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)
    
    # Payment terms
    payment_terms = Column(String(100), default="Due on receipt")
    due_date = Column(DateTime(timezone=True))
    
    # Invoice content
    description = Column(Text)
    notes = Column(Text)
    terms_and_conditions = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    
    # User tracking
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    order = relationship("Order", back_populates="invoices")
    invoice_items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    created_by = relationship("User")
    
    @property
    def is_paid(self):
        """Check if invoice is fully paid."""
        return self.amount_paid >= self.total_amount
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding amount."""
        return max(0, self.total_amount - self.amount_paid)
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.due_date and not self.is_paid:
            return func.now() > self.due_date
        return False


class InvoiceItem(Base):
    """Individual line items in an invoice."""
    
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Item details
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    total_price = Column(Float, nullable=False)
    
    # Optional product reference
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")
    inventory_item = relationship("InventoryItem")
    
    @property
    def line_total(self):
        """Calculate line total after discount."""
        return (self.unit_price * self.quantity) - self.discount_amount


class Payment(Base):
    """Payment tracking model."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_reference = Column(String(100), unique=True, index=True, nullable=False)
    
    # Related entities
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))  # Optional
    
    # Payment details
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Payment method specific details
    bank_name = Column(String(100))
    account_number = Column(String(50))
    transaction_reference = Column(String(255))
    pos_terminal_id = Column(String(50))
    mobile_money_number = Column(String(20))
    
    # Status and verification
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    verification_notes = Column(Text)
    
    # Notes
    notes = Column(Text)
    receipt_url = Column(String(500))  # Link to payment receipt/proof
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User tracking
    recorded_by_user_id = Column(Integer, ForeignKey("users.id"))
    verified_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer")
    order = relationship("Order")
    recorded_by = relationship("User", foreign_keys=[recorded_by_user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])