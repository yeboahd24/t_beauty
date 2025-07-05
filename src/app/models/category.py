"""
Category model.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.db.base import Base


class Category(Base):
    """Category model for products and inventory."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    slug = Column(String(100), unique=True, index=True)  # URL-friendly name
    parent_id = Column(Integer, nullable=True)  # For hierarchical categories
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category")