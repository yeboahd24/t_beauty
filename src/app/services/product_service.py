"""
Product service for business logic.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Product service class."""
    
    @staticmethod
    def get_by_id(db: Session, product_id: int, owner_id: int) -> Optional[Product]:
        """Get product by ID and owner with inventory information."""
        return (
            db.query(Product)
            .options(
                joinedload(Product.brand), 
                joinedload(Product.category),
                joinedload(Product.inventory_items)
            )
            .filter(and_(Product.id == product_id, Product.owner_id == owner_id))
            .first()
        )
    
    @staticmethod
    def get_by_sku(db: Session, sku: str, owner_id: int) -> Optional[Product]:
        """Get product by SKU and owner."""
        return (
            db.query(Product)
            .options(joinedload(Product.brand), joinedload(Product.category))
            .filter(and_(Product.sku == sku, Product.owner_id == owner_id))
            .first()
        )
    
    @staticmethod
    def get_all(
        db: Session, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        brand_id: Optional[int] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        in_stock_only: bool = False
    ) -> List[Product]:
        """Get all products for owner with pagination, search and filtering."""
        query = (
            db.query(Product)
            .options(
                joinedload(Product.brand), 
                joinedload(Product.category),
                joinedload(Product.inventory_items)
            )
            .filter(Product.owner_id == owner_id)
        )
        
        # Apply filters
        if search:
            query = query.filter(
                Product.name.contains(search) | 
                Product.description.contains(search) |
                Product.sku.contains(search)
            )
        
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        if in_stock_only:
            # Only products that have inventory with stock > 0
            from app.models.inventory import InventoryItem
            query = query.join(InventoryItem).filter(
                and_(
                    InventoryItem.current_stock > 0,
                    InventoryItem.is_active == True
                )
            ).distinct()
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count(db: Session, owner_id: int, search: Optional[str] = None) -> int:
        """Count products for owner with optional search."""
        query = db.query(Product).filter(Product.owner_id == owner_id)
        
        if search:
            query = query.filter(
                Product.name.contains(search) | 
                Product.description.contains(search) |
                Product.sku.contains(search)
            )
        
        return query.count()
    
    @staticmethod
    def create(db: Session, product_create: ProductCreate, owner_id: int) -> Product:
        """Create a new product (catalog entry)."""
        # Check if SKU already exists for this owner
        existing_product = ProductService.get_by_sku(db, product_create.sku, owner_id)
        if existing_product:
            raise ValueError(f"Product with SKU '{product_create.sku}' already exists")
        
        # Extract additional image URLs before creating product
        product_data = product_create.model_dump()
        additional_image_urls = product_data.pop('additional_image_urls', None)
        
        db_product = Product(
            **product_data,
            owner_id=owner_id
        )
        
        # Set additional image URLs if provided
        if additional_image_urls:
            db_product.set_image_urls(additional_image_urls)
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return ProductService.get_by_id(db, db_product.id, owner_id)
    
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
        
        # Handle additional image URLs separately
        additional_image_urls = update_data.pop('additional_image_urls', None)
        
        # Update regular fields
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        # Update additional image URLs if provided
        if additional_image_urls is not None:
            db_product.set_image_urls(additional_image_urls)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def update_images(
        db: Session, 
        product_id: int, 
        primary_image_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        additional_image_urls: Optional[List[str]] = None,
        owner_id: int = None
    ) -> Optional[Product]:
        """Update product images specifically."""
        db_product = ProductService.get_by_id(db, product_id, owner_id)
        if not db_product:
            return None
        
        # Update image fields
        if primary_image_url is not None:
            db_product.primary_image_url = primary_image_url
        
        if thumbnail_url is not None:
            db_product.thumbnail_url = thumbnail_url
        
        if additional_image_urls is not None:
            db_product.set_image_urls(additional_image_urls)
        
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
    def get_with_inventory(db: Session, product_id: int, owner_id: int) -> Optional[Product]:
        """Get product with its linked inventory items."""
        from app.models.inventory import InventoryItem
        
        product = ProductService.get_by_id(db, product_id, owner_id)
        if not product:
            return None
        
        # Get linked inventory items
        inventory_items = (
            db.query(InventoryItem)
            .filter(InventoryItem.product_id == product_id)
            .all()
        )
        
        # Add inventory items as a dynamic attribute
        product.inventory_items = inventory_items
        return product
    
    @staticmethod
    def get_stats(db: Session, owner_id: int) -> dict:
        """Get product statistics for owner."""
        products = ProductService.get_all(db, owner_id, skip=0, limit=1000)
        
        total_products = len(products)
        active_products = sum(1 for product in products if product.is_active)
        featured_products = sum(1 for product in products if product.is_featured)
        discontinued_products = sum(1 for product in products if product.is_discontinued)
        in_stock_products = sum(1 for product in products if product.is_in_stock)
        
        # Calculate total inventory value from linked inventory items
        total_inventory_value = 0.0
        total_stock_quantity = 0
        for product in products:
            for inventory_item in product.inventory_items:
                if inventory_item.is_active:
                    total_inventory_value += inventory_item.stock_value
                    total_stock_quantity += inventory_item.current_stock
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "featured_products": featured_products,
            "discontinued_products": discontinued_products,
            "in_stock_products": in_stock_products,
            "total_inventory_value": total_inventory_value,
            "total_stock_quantity": total_stock_quantity,
            "average_stock_per_product": total_stock_quantity / total_products if total_products > 0 else 0
        }
    
    @staticmethod
    def get_available_for_order(
        db: Session, 
        product_id: int, 
        owner_id: int,
        requested_color: Optional[str] = None,
        requested_shade: Optional[str] = None,
        requested_size: Optional[str] = None
    ) -> List['InventoryItem']:
        """Get available inventory items for a product that can fulfill an order."""
        from app.models.inventory import InventoryItem
        
        query = (
            db.query(InventoryItem)
            .filter(
                and_(
                    InventoryItem.product_id == product_id,
                    InventoryItem.owner_id == owner_id,
                    InventoryItem.is_active == True,
                    InventoryItem.current_stock > 0
                )
            )
        )
        
        # Apply variant filters if specified
        if requested_color:
            query = query.filter(InventoryItem.color == requested_color)
        
        if requested_shade:
            query = query.filter(InventoryItem.shade == requested_shade)
        
        if requested_size:
            query = query.filter(InventoryItem.size == requested_size)
        
        # Order by stock level (highest first) and selling price (lowest first for better margins)
        return query.order_by(
            InventoryItem.current_stock.desc(),
            InventoryItem.selling_price.asc()
        ).all()
    
    @staticmethod
    def check_availability(
        db: Session, 
        product_id: int, 
        quantity: int, 
        owner_id: int,
        requested_color: Optional[str] = None,
        requested_shade: Optional[str] = None,
        requested_size: Optional[str] = None
    ) -> dict:
        """Check if a product can fulfill the requested quantity with preferences."""
        available_inventory = ProductService.get_available_for_order(
            db, product_id, owner_id, requested_color, requested_shade, requested_size
        )
        
        total_available = sum(item.current_stock for item in available_inventory)
        can_fulfill = total_available >= quantity
        
        # Suggest allocation strategy
        allocation_plan = []
        remaining_quantity = quantity
        
        for inventory_item in available_inventory:
            if remaining_quantity <= 0:
                break
            
            allocate_qty = min(remaining_quantity, inventory_item.current_stock)
            allocation_plan.append({
                "inventory_item_id": inventory_item.id,
                "location": inventory_item.location,
                "available_stock": inventory_item.current_stock,
                "allocate_quantity": allocate_qty,
                "color": inventory_item.color,
                "shade": inventory_item.shade,
                "size": inventory_item.size,
                "selling_price": inventory_item.selling_price
            })
            remaining_quantity -= allocate_qty
        
        return {
            "can_fulfill": can_fulfill,
            "total_available": total_available,
            "requested_quantity": quantity,
            "shortage": max(0, quantity - total_available),
            "allocation_plan": allocation_plan,
            "alternative_variants": len(available_inventory) if not can_fulfill else 0
        }