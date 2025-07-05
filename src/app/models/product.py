"""
Product model.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.db.base import Base


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
    
    # Product images
    primary_image_url = Column(String(500))  # Main product image
    image_urls = Column(Text)  # JSON array of additional image URLs
    thumbnail_url = Column(String(500))  # Optimized thumbnail image
    
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
    
    @property
    def all_image_urls(self):
        """Get all image URLs as a list."""
        import json
        images = []
        
        # Add primary image if exists
        if self.primary_image_url:
            images.append(self.primary_image_url)
        
        # Add additional images if exists
        if self.image_urls:
            try:
                additional_images = json.loads(self.image_urls)
                if isinstance(additional_images, list):
                    images.extend(additional_images)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return images
    
    @property
    def display_image_url(self):
        """Get the best image URL for display (primary, thumbnail, or first available)."""
        if self.primary_image_url:
            return self.primary_image_url
        elif self.thumbnail_url:
            return self.thumbnail_url
        elif self.all_image_urls:
            return self.all_image_urls[0]
        return None
    
    def set_image_urls(self, image_urls_list):
        """Set additional image URLs from a list."""
        import json
        if image_urls_list and isinstance(image_urls_list, list):
            self.image_urls = json.dumps(image_urls_list)
        else:
            self.image_urls = None