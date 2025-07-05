"""
Category service for business logic.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.app.models.category import Category
from src.app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Category service class."""
    
    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return db.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        """Get category by name."""
        return db.query(Category).filter(Category.name == name).first()
    
    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Category]:
        """Get category by slug."""
        return db.query(Category).filter(Category.slug == slug).first()
    
    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Category]:
        """Get all categories with pagination."""
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_count(db: Session, active_only: bool = True) -> int:
        """Get total count of categories."""
        query = db.query(func.count(Category.id))
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.scalar()
    
    @staticmethod
    def create(db: Session, category_create: CategoryCreate) -> Category:
        """Create a new category."""
        # Generate slug if not provided
        if not category_create.slug:
            category_create.slug = category_create.name.lower().replace(" ", "-")
        
        db_category = Category(**category_create.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def update(db: Session, category: Category, category_update: CategoryUpdate) -> Category:
        """Update an existing category."""
        update_data = category_update.model_dump(exclude_unset=True)
        
        # Update slug if name is changed
        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = update_data["name"].lower().replace(" ", "-")
        
        for field, value in update_data.items():
            setattr(category, field, value)
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def delete(db: Session, category: Category) -> bool:
        """Soft delete a category (set is_active to False)."""
        category.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def search(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Category]:
        """Search categories by name."""
        return (
            db.query(Category)
            .filter(Category.name.ilike(f"%{query}%"))
            .filter(Category.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )