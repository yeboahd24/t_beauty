"""
Brand service for business logic.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandService:
    """Brand service class."""
    
    @staticmethod
    def get_by_id(db: Session, brand_id: int) -> Optional[Brand]:
        """Get brand by ID."""
        return db.query(Brand).filter(Brand.id == brand_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Brand]:
        """Get brand by name."""
        return db.query(Brand).filter(Brand.name == name).first()
    
    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Brand]:
        """Get all brands with pagination."""
        query = db.query(Brand)
        if active_only:
            query = query.filter(Brand.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_count(db: Session, active_only: bool = True) -> int:
        """Get total count of brands."""
        query = db.query(func.count(Brand.id))
        if active_only:
            query = query.filter(Brand.is_active == True)
        return query.scalar()
    
    @staticmethod
    def create(db: Session, brand_create: BrandCreate) -> Brand:
        """Create a new brand."""
        db_brand = Brand(**brand_create.model_dump())
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        return db_brand
    
    @staticmethod
    def update(db: Session, brand: Brand, brand_update: BrandUpdate) -> Brand:
        """Update an existing brand."""
        update_data = brand_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)
        db.commit()
        db.refresh(brand)
        return brand
    
    @staticmethod
    def delete(db: Session, brand: Brand) -> bool:
        """Soft delete a brand (set is_active to False)."""
        brand.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def search(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Search brands by name."""
        return (
            db.query(Brand)
            .filter(Brand.name.ilike(f"%{query}%"))
            .filter(Brand.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )