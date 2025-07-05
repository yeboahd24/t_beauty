"""
Inventory model for T-Beauty stock management.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.db.base import Base


class InventoryItem(Base):
    """Inventory item model - Physical stock of products at specific locations."""
    
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Product link (REQUIRED - inventory must be linked to a product)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Location and ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String(255), default="main_warehouse")  # warehouse, store, etc.
    batch_number = Column(String(100))  # For tracking specific batches
    
    # Pricing
    cost_price = Column(Float, nullable=False)  # What we pay
    selling_price = Column(Float, nullable=False)  # What we charge
    
    # Stock management
    current_stock = Column(Integer, default=0, nullable=False)
    minimum_stock = Column(Integer, default=5)  # Low stock alert threshold
    maximum_stock = Column(Integer, default=100)  # Maximum stock level
    reorder_point = Column(Integer, default=10)  # When to reorder
    reorder_quantity = Column(Integer, default=20)  # How much to reorder
    
    # Variant details (specific to this inventory item)
    color = Column(String(50))
    shade = Column(String(50))
    size = Column(String(50))
    expiry_date = Column(DateTime(timezone=True))  # For products with expiration
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_discontinued = Column(Boolean, default=False)
    
    # Supplier information
    supplier_name = Column(String(255))
    supplier_contact = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_restocked = Column(DateTime(timezone=True))
    
    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    owner = relationship("User")
    order_items = relationship("OrderItem", back_populates="inventory_item")
    stock_movements = relationship("StockMovement", back_populates="inventory_item")
    
    @property
    def is_low_stock(self):
        """Check if item is below minimum stock level."""
        return self.current_stock <= self.minimum_stock
    
    @property
    def is_out_of_stock(self):
        """Check if item is out of stock."""
        return self.current_stock <= 0
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def stock_value(self):
        """Calculate total value of current stock."""
        return self.current_stock * self.cost_price
    
    @property
    def name(self):
        """Get product name."""
        return self.product.name if self.product else "Unknown Product"
    
    @property
    def description(self):
        """Get product description."""
        return self.product.description if self.product else None
    
    @property
    def brand(self):
        """Get brand through product relationship."""
        return self.product.brand if self.product else None
    
    @property
    def category(self):
        """Get category through product relationship."""
        return self.product.category if self.product else None
    
    @property
    def sku(self):
        """Get SKU through product relationship."""
        return self.product.sku if self.product else None
    
    @property
    def weight(self):
        """Get weight from product."""
        return self.product.weight if self.product else None
    
    @property
    def dimensions(self):
        """Get dimensions from product."""
        return self.product.dimensions if self.product else None


class StockMovement(Base):
    """Track all stock movements for inventory auditing."""
    
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    
    # Movement details
    movement_type = Column(String(50), nullable=False)  # "in", "out", "adjustment", "return"
    quantity = Column(Integer, nullable=False)  # Positive for in, negative for out
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    # Reference information
    reference_type = Column(String(50))  # "order", "restock", "adjustment", "return"
    reference_id = Column(Integer)  # ID of related order, restock, etc.
    
    # Details
    reason = Column(String(255))
    notes = Column(Text)
    unit_cost = Column(Float)  # Cost per unit for this movement
    
    # User tracking
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    movement_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="stock_movements")
    user = relationship("User")