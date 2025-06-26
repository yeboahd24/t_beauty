"""
Product service for business logic.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Product service class."""
    
    @staticmethod
    def get_by_id(db: Session, product_id: int, owner_id: int) -> Optional[Product]:
        """Get product by ID and owner."""
        return db.query(Product).filter(
            and_(Product.id == product_id, Product.owner_id == owner_id)
        ).first()
    
    @staticmethod
    def get_all(
        db: Session, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get all products for owner with pagination and search."""
        query = db.query(Product).filter(Product.owner_id == owner_id)
        
        if search:
            query = query.filter(
                Product.name.contains(search) | 
                Product.description.contains(search)
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count(db: Session, owner_id: int, search: Optional[str] = None) -> int:
        """Count products for owner with optional search."""
        query = db.query(Product).filter(Product.owner_id == owner_id)
        
        if search:
            query = query.filter(
                Product.name.contains(search) | 
                Product.description.contains(search)
            )
        
        return query.count()
    
    @staticmethod
    def create(db: Session, product_create: ProductCreate, owner_id: int) -> Product:
        """Create a new product."""
        db_product = Product(
            **product_create.model_dump(),
            owner_id=owner_id
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def update(
        db: Session, 
        product_id: int, 
        product_update: ProductUpdate, 
        owner_id: int
    ) -> Optional[Product]:
        """Update a product."""
        db_product = ProductService.get_by_id(db, product_id, owner_id)
        if not db_product:
            return None
        
        update_data = product_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def delete(db: Session, product_id: int, owner_id: int) -> bool:
        """Delete a product."""
        db_product = ProductService.get_by_id(db, product_id, owner_id)
        if not db_product:
            return False
        
        db.delete(db_product)
        db.commit()
        return True
    
    @staticmethod
    def get_stats(db: Session, owner_id: int) -> dict:
        """Get product statistics for owner."""
        products = ProductService.get_all(db, owner_id, skip=0, limit=1000)
        
        total_products = len(products)
        total_value = sum(product.price * product.quantity for product in products)
        total_quantity = sum(product.quantity for product in products)
        active_products = sum(1 for product in products if product.is_active)
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "total_inventory_value": total_value,
            "total_quantity": total_quantity
        }