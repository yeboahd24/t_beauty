"""
Customer model for T-Beauty business management.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.db.base import Base


class Customer(Base):
    """Customer model for managing client information."""
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))  # For customer authentication
    phone = Column(String(20))
    instagram_handle = Column(String(100), index=True)
    
    # Address information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="Nigeria")
    
    # Customer status
    is_active = Column(Boolean, default=True)
    is_vip = Column(Boolean, default=False)
    
    # Notes and preferences
    notes = Column(Text)
    preferred_contact_method = Column(String(50), default="instagram")  # instagram, email, phone
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_order_date = Column(DateTime(timezone=True))
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")
    cart_items = relationship("CartItem", back_populates="customer", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Get customer's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Get display name with Instagram handle if available."""
        if self.instagram_handle:
            return f"{self.full_name} (@{self.instagram_handle})"
        return self.full_name