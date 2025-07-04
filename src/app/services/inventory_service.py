"""
Inventory service for T-Beauty stock management.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from datetime import datetime
from app.models.inventory import InventoryItem, StockMovement
from app.models.product import Product
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate, StockMovementCreate


class InventoryService:
    """Inventory service class for business logic."""
    
    @staticmethod
    def get_by_id(db: Session, item_id: int, owner_id: int = None) -> Optional[InventoryItem]:
        """Get inventory item by ID and owner."""
        query = (
            db.query(InventoryItem)
            .options(joinedload(InventoryItem.product))
            .filter(InventoryItem.id == item_id)
        )
        
        if owner_id is not None:
            query = query.filter(InventoryItem.owner_id == owner_id)
        
        return query.first()
    
    
    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        low_stock_only: bool = False,
        out_of_stock_only: bool = False
    ) -> List[InventoryItem]:
        """Get all inventory items with filtering and pagination."""
        query = (
            db.query(InventoryItem)
            .options(joinedload(InventoryItem.product))
            .filter(InventoryItem.owner_id == owner_id)
        )
        
        # Apply filters
        if is_active is not None:
            query = query.filter(InventoryItem.is_active == is_active)
        
        if category_id:
            query = query.join(InventoryItem.product).filter(Product.category_id == category_id)
        
        if brand_id:
            query = query.join(InventoryItem.product).filter(Product.brand_id == brand_id)
        
        if low_stock_only:
            query = query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock)
        
        if out_of_stock_only:
            query = query.filter(InventoryItem.current_stock <= 0)
        
        if search:
            search_filter = or_(
                InventoryItem.name.contains(search),
                InventoryItem.description.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        owner_id: int = None,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        low_stock_only: bool = False,
        out_of_stock_only: bool = False
    ) -> int:
        """Count inventory items with filtering."""
        query = db.query(InventoryItem)
        
        if owner_id:
            query = query.filter(InventoryItem.owner_id == owner_id)
        
        if is_active is not None:
            query = query.filter(InventoryItem.is_active == is_active)
        
        if category_id:
            query = query.join(InventoryItem.product).filter(Product.category_id == category_id)
        
        if brand_id:
            query = query.join(InventoryItem.product).filter(Product.brand_id == brand_id)
        
        if low_stock_only:
            query = query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock)
        
        if out_of_stock_only:
            query = query.filter(InventoryItem.current_stock <= 0)
        
        if search:
            search_filter = or_(
                InventoryItem.name.contains(search),
                InventoryItem.description.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.count()
    
    @staticmethod
    def create(db: Session, item_create: InventoryItemCreate, owner_id: int) -> InventoryItem:
        """Create a new inventory item linked to a product."""
        # Validate that the product exists and belongs to the owner
        product = db.query(Product).filter(
            and_(
                Product.id == item_create.product_id,
                Product.owner_id == owner_id
            )
        ).first()
        
        if not product:
            raise ValueError(f"Product with ID {item_create.product_id} not found or not owned by user")
        
        db_item = InventoryItem(
            **item_create.model_dump(),
            owner_id=owner_id
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Create initial stock movement record
        if db_item.current_stock > 0:
            InventoryService.create_stock_movement(
                db=db,
                movement=StockMovementCreate(
                    inventory_item_id=db_item.id,
                    movement_type="in",
                    quantity=db_item.current_stock,
                    reason="Initial stock",
                    unit_cost=db_item.cost_price
                ),
                user_id=None
            )
        
        # Get the item with proper relationships loaded
        return InventoryService.get_by_id(db, db_item.id, owner_id)
    
    @staticmethod
    def update(
        db: Session,
        item_id: int,
        item_update: InventoryItemUpdate
    ) -> Optional[InventoryItem]:
        """Update an inventory item."""
        db_item = InventoryService.get_by_id(db, item_id)
        if not db_item:
            return None
        
        update_data = item_update.model_dump(exclude_unset=True)
        
        # Handle stock changes separately
        if "current_stock" in update_data:
            new_stock = update_data.pop("current_stock")
            InventoryService.adjust_stock(
                db=db,
                item_id=item_id,
                new_quantity=new_stock,
                reason="Manual adjustment",
                user_id=None
            )
        
        # Update other fields
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def delete(db: Session, item_id: int, owner_id: int = None) -> bool:
        """Delete an inventory item and its related stock movements."""
        db_item = InventoryService.get_by_id(db, item_id, owner_id)
        if not db_item:
            return False
        
        # Check if item has any pending orders or is referenced elsewhere
        # This is a safety check to prevent deletion of items that are still in use
        from app.models.order import OrderItem
        pending_orders = db.query(OrderItem).filter(
            OrderItem.inventory_item_id == item_id
        ).first()
        
        if pending_orders:
            # Instead of hard delete, mark as inactive and discontinued
            db_item.is_active = False
            db_item.is_discontinued = True
            db.commit()
            return True
        
        # Delete related stock movements first (due to foreign key constraints)
        db.query(StockMovement).filter(
            StockMovement.inventory_item_id == item_id
        ).delete()
        
        # Delete the inventory item
        db.delete(db_item)
        db.commit()
        return True
    
    @staticmethod
    def adjust_stock(
        db: Session,
        item_id: int,
        new_quantity: int,
        reason: str = "Stock adjustment",
        user_id: Optional[int] = None
    ) -> Optional[InventoryItem]:
        """Adjust stock quantity and create movement record."""
        db_item = InventoryService.get_by_id(db, item_id)
        if not db_item:
            return None
        
        previous_stock = db_item.current_stock
        quantity_change = new_quantity - previous_stock
        
        # Update stock
        db_item.current_stock = new_quantity
        if new_quantity > previous_stock:
            db_item.last_restocked = datetime.utcnow()
        
        db.commit()
        db.refresh(db_item)
        
        # Create stock movement record
        movement_type = "in" if quantity_change > 0 else "out" if quantity_change < 0 else "adjustment"
        InventoryService.create_stock_movement(
            db=db,
            movement=StockMovementCreate(
                inventory_item_id=item_id,
                movement_type=movement_type,
                quantity=abs(quantity_change),
                reason=reason
            ),
            user_id=user_id
        )
        
        return db_item
    
    @staticmethod
    def create_stock_movement(
        db: Session,
        movement: StockMovementCreate,
        user_id: Optional[int] = None
    ) -> StockMovement:
        """Create a stock movement record."""
        db_item = InventoryService.get_by_id(db, movement.inventory_item_id)
        if not db_item:
            raise ValueError("Inventory item not found")
        
        # Calculate stock changes
        previous_stock = db_item.current_stock
        if movement.movement_type == "in":
            new_stock = previous_stock + movement.quantity
        elif movement.movement_type == "out":
            new_stock = previous_stock - movement.quantity
        else:  # adjustment
            new_stock = previous_stock
        
        db_movement = StockMovement(
            **movement.model_dump(),
            previous_stock=previous_stock,
            new_stock=new_stock,
            user_id=user_id
        )
        
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        return db_movement
    
    @staticmethod
    def get_low_stock_items(db: Session, owner_id: int = None) -> List[InventoryItem]:
        """Get items that are low in stock."""
        query = db.query(InventoryItem).filter(
            and_(
                InventoryItem.current_stock <= InventoryItem.minimum_stock,
                InventoryItem.is_active == True
            )
        )
        if owner_id:
            query = query.filter(InventoryItem.owner_id == owner_id)
        return query.all()
    
    @staticmethod
    def get_out_of_stock_items(db: Session, owner_id: int = None) -> List[InventoryItem]:
        """Get items that are out of stock."""
        query = db.query(InventoryItem).filter(
            and_(
                InventoryItem.current_stock <= 0,
                InventoryItem.is_active == True
            )
        )
        if owner_id:
            query = query.filter(InventoryItem.owner_id == owner_id)
        return query.all()
    
    @staticmethod
    def get_reorder_suggestions(db: Session, owner_id: int = None) -> List[InventoryItem]:
        """Get items that need to be reordered."""
        query = db.query(InventoryItem).filter(
            and_(
                InventoryItem.current_stock <= InventoryItem.reorder_point,
                InventoryItem.is_active == True
            )
        )
        if owner_id:
            query = query.filter(InventoryItem.owner_id == owner_id)
        return query.all()
    
    @staticmethod
    def get_categories(db: Session, owner_id: int = None) -> List[str]:
        """Get all unique categories from inventory items through products."""
        from app.models.category import Category
        query = (
            db.query(Category.name)
            .join(Product)
            .join(InventoryItem)
            .filter(InventoryItem.is_active == True)
        )
        if owner_id:
            query = query.filter(InventoryItem.owner_id == owner_id)
        
        result = query.distinct().all()
        return [category[0] for category in result if category[0]]
    
    @staticmethod
    def get_brands(db: Session, owner_id: int = None) -> List[str]:
        """Get all unique brands from inventory items through products."""
        from app.models.brand import Brand
        query = (
            db.query(Brand.name)
            .join(Product)
            .join(InventoryItem)
            .filter(InventoryItem.is_active == True)
        )
        if owner_id:
            query = query.filter(InventoryItem.owner_id == owner_id)
        
        result = query.distinct().all()
        return [brand[0] for brand in result if brand[0]]
    
    @staticmethod
    def get_top_selling_items(db: Session, owner_id: int, limit: int = 5) -> List[InventoryItem]:
        """Get top selling inventory items based on order history."""
        from app.models.order import OrderItem
        
        # Query to get items with highest order quantities
        top_items_query = (
            db.query(
                InventoryItem,
                func.sum(OrderItem.quantity).label('total_sold')
            )
            .join(OrderItem, InventoryItem.id == OrderItem.inventory_item_id)
            .filter(InventoryItem.owner_id == owner_id)
            .filter(InventoryItem.is_active == True)
            .group_by(InventoryItem.id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        
        # Extract just the inventory items
        return [item[0] for item in top_items_query.all()]
    
    @staticmethod
    def get_inventory_stats(db: Session, owner_id: int = None) -> dict:
        """Get inventory statistics."""
        base_query = db.query(InventoryItem)
        if owner_id:
            base_query = base_query.filter(InventoryItem.owner_id == owner_id)
        
        total_items = base_query.count()
        active_items = base_query.filter(InventoryItem.is_active == True).count()
        low_stock_items = base_query.filter(
            and_(
                InventoryItem.current_stock <= InventoryItem.minimum_stock,
                InventoryItem.is_active == True
            )
        ).count()
        out_of_stock_items = base_query.filter(
            and_(
                InventoryItem.current_stock <= 0,
                InventoryItem.is_active == True
            )
        ).count()
        
        # Calculate total stock value
        value_query = base_query.filter(InventoryItem.is_active == True)
        total_stock_value = value_query.with_entities(
            func.sum(InventoryItem.current_stock * InventoryItem.cost_price)
        ).scalar() or 0
        
        # Get top selling items if owner_id is provided
        top_selling_items = []
        if owner_id:
            top_selling_items = InventoryService.get_top_selling_items(db, owner_id, limit=5)
        
        return {
            "total_items": total_items,
            "active_items": active_items,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "total_stock_value": float(total_stock_value),
            "categories": InventoryService.get_categories(db, owner_id),
            "brands": InventoryService.get_brands(db, owner_id),
            "top_selling_items": top_selling_items
        }
    
    @staticmethod
    def get_all_customer_facing(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = True
    ) -> List[InventoryItem]:
        """Get inventory items for customer browsing."""
        query = (
            db.query(InventoryItem)
            .options(
                joinedload(InventoryItem.product).joinedload(Product.category),
                joinedload(InventoryItem.product).joinedload(Product.brand)
            )
            .filter(InventoryItem.is_active == True)
            .order_by(InventoryItem.created_at.desc())
        )
        
        # Apply filters
        if category_id:
            query = query.filter(InventoryItem.product.has(Product.category_id == category_id))
        
        if brand_id:
            query = query.filter(InventoryItem.product.has(Product.brand_id == brand_id))
        
        if search:
            query = query.filter(
                InventoryItem.name.contains(search) |
                InventoryItem.description.contains(search) |
                InventoryItem.product.has(Product.name.contains(search)) |
                InventoryItem.product.has(Product.description.contains(search))
            )
        
        if min_price is not None:
            query = query.filter(InventoryItem.selling_price >= min_price)
        
        if max_price is not None:
            query = query.filter(InventoryItem.selling_price <= max_price)
        
        if in_stock_only:
            query = query.filter(InventoryItem.quantity_available > 0)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_featured(db: Session, limit: int = 10) -> List[InventoryItem]:
        """Get featured products for customer browsing."""
        return (
            db.query(InventoryItem)
            .options(
                joinedload(InventoryItem.product).joinedload(Product.category),
                joinedload(InventoryItem.product).joinedload(Product.brand)
            )
            .filter(
                and_(
                    InventoryItem.is_active == True,
                    InventoryItem.quantity_available > 0
                )
            )
            .order_by(InventoryItem.created_at.desc())
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def search_customer_facing(
        db: Session,
        search_query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryItem]:
        """Search inventory items for customers."""
        return (
            db.query(InventoryItem)
            .options(
                joinedload(InventoryItem.product).joinedload(Product.category),
                joinedload(InventoryItem.product).joinedload(Product.brand)
            )
            .filter(
                and_(
                    InventoryItem.is_active == True,
                    InventoryItem.quantity_available > 0,
                    (
                        InventoryItem.name.contains(search_query) |
                        InventoryItem.description.contains(search_query) |
                        InventoryItem.product.has(Product.name.contains(search_query)) |
                        InventoryItem.product.has(Product.description.contains(search_query))
                    )
                )
            )
            .order_by(InventoryItem.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )