"""
Shopping cart models for T-Beauty customer experience.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CartItem(Base):
    """Shopping cart item model."""
    
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Related entities
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)  # Price at time of adding to cart
    notes = Column(Text)  # Customer notes/preferences
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="cart_items")
    product = relationship("Product")
    
    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.quantity * self.unit_price
    
    @property
    def is_available(self):
        """Check if the product is still available and has stock."""
        return (
            self.product and 
            self.product.is_active and 
            self.product.is_in_stock and
            self.product.available_stock >= self.quantity
        )