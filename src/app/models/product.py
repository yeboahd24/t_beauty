"""
Product model.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Product(Base):
    """Product model - Catalog definition of what can be sold."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text)
    base_price = Column(Float, nullable=False)  # Suggested retail price
    sku = Column(String(50), unique=True, index=True, nullable=False)  # Stock Keeping Unit
    
    # Product specifications
    weight = Column(Float)  # For shipping calculations
    dimensions = Column(String(100))  # L x W x H
    
    # Product categorization
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Product status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_discontinued = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    
    @property
    def total_stock(self):
        """Get total stock across all inventory locations."""
        return sum(item.current_stock for item in self.inventory_items if item.is_active)
    
    @property
    def available_stock(self):
        """Get available stock (excluding reserved/allocated)."""
        # For now, same as total_stock, but could include reservations later
        return self.total_stock
    
    @property
    def is_in_stock(self):
        """Check if product has any available stock."""
        return self.available_stock > 0