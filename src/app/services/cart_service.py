"""
Shopping cart service for T-Beauty customer experience.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from src.app.models.cart import CartItem
from src.app.models.customer import Customer
from src.app.models.product import Product
from src.app.schemas.cart import CartItemCreate, CartItemUpdate, AddToCartRequest, CartToOrderRequest
from src.app.schemas.order import CustomerOrderCreate, CustomerOrderItemCreate


class CartService:
    """Shopping cart service class for business logic."""
    
    @staticmethod
    def add_to_cart(
        db: Session, 
        customer_id: int, 
        add_request: AddToCartRequest
    ) -> CartItem:
        """Add an item to the customer's cart."""
        # Check if product exists and is available
        product = db.query(Product).filter(
            and_(
                Product.id == add_request.product_id,
                Product.is_active == True,
                Product.is_discontinued == False
            )
        ).first()
        
        if not product:
            raise ValueError("Product not found or not available")
        
        if not product.is_in_stock:
            raise ValueError("Product is currently out of stock")
            
        if product.available_stock < add_request.quantity:
            raise ValueError(f"Only {product.available_stock} items available in stock")
        
        # Check if item already exists in cart
        existing_cart_item = db.query(CartItem).filter(
            and_(
                CartItem.customer_id == customer_id,
                CartItem.product_id == add_request.product_id
            )
        ).first()
        
        if existing_cart_item:
            # Update existing cart item
            new_quantity = existing_cart_item.quantity + add_request.quantity
            if product.available_stock < new_quantity:
                raise ValueError(f"Cannot add {add_request.quantity} more items. Only {product.available_stock - existing_cart_item.quantity} more available")
            
            existing_cart_item.quantity = new_quantity
            existing_cart_item.notes = add_request.notes or existing_cart_item.notes
            db.commit()
            db.refresh(existing_cart_item)
            return existing_cart_item
        else:
            # Create new cart item
            cart_item = CartItem(
                customer_id=customer_id,
                product_id=add_request.product_id,
                quantity=add_request.quantity,
                unit_price=product.base_price,  # Use product base price
                notes=add_request.notes
            )
            
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def get_cart_items(db: Session, customer_id: int) -> List[CartItem]:
        """Get all items in customer's cart."""
        return (
            db.query(CartItem)
            .options(joinedload(CartItem.product))
            .filter(CartItem.customer_id == customer_id)
            .order_by(CartItem.created_at.desc())
            .all()
        )
    
    @staticmethod
    def get_cart_item(db: Session, customer_id: int, cart_item_id: int) -> Optional[CartItem]:
        """Get a specific cart item for a customer."""
        return (
            db.query(CartItem)
            .options(joinedload(CartItem.product))
            .filter(
                and_(
                    CartItem.id == cart_item_id,
                    CartItem.customer_id == customer_id
                )
            )
            .first()
        )
    
    @staticmethod
    def update_cart_item(
        db: Session, 
        customer_id: int, 
        cart_item_id: int, 
        update_data: CartItemUpdate
    ) -> Optional[CartItem]:
        """Update a cart item."""
        cart_item = CartService.get_cart_item(db, customer_id, cart_item_id)
        if not cart_item:
            return None
        
        # If updating quantity, check availability
        if update_data.quantity is not None:
            if cart_item.product.available_stock < update_data.quantity:
                raise ValueError(f"Only {cart_item.product.available_stock} items available in stock")
            cart_item.quantity = update_data.quantity
        
        if update_data.notes is not None:
            cart_item.notes = update_data.notes
        
        db.commit()
        db.refresh(cart_item)
        return cart_item
    
    @staticmethod
    def remove_from_cart(db: Session, customer_id: int, cart_item_id: int) -> bool:
        """Remove an item from the cart."""
        cart_item = CartService.get_cart_item(db, customer_id, cart_item_id)
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        return True
    
    @staticmethod
    def clear_cart(db: Session, customer_id: int) -> bool:
        """Clear all items from customer's cart."""
        deleted_count = db.query(CartItem).filter(
            CartItem.customer_id == customer_id
        ).delete()
        db.commit()
        return deleted_count > 0
    
    @staticmethod
    def get_cart_summary(db: Session, customer_id: int) -> dict:
        """Get cart summary with totals and availability."""
        cart_items = CartService.get_cart_items(db, customer_id)
        
        total_amount = 0.0
        available_items = 0
        unavailable_items = 0
        
        for item in cart_items:
            if item.is_available:
                available_items += 1
                total_amount += item.total_price
            else:
                unavailable_items += 1
        
        return {
            "items_count": len(cart_items),
            "total_amount": total_amount,
            "available_items_count": available_items,
            "unavailable_items_count": unavailable_items,
            "items": cart_items
        }
    
    @staticmethod
    def convert_cart_to_order(
        db: Session, 
        customer_id: int, 
        cart_to_order: CartToOrderRequest,
        owner_id: int = 1  # Default business owner
    ) -> dict:
        """Convert cart items to an order."""
        from src.app.services.order_service import OrderService
        
        cart_items = CartService.get_cart_items(db, customer_id)
        
        if not cart_items:
            raise ValueError("Cart is empty")
        
        # Filter items if specific item_ids provided
        if cart_to_order.item_ids:
            cart_items = [item for item in cart_items if item.id in cart_to_order.item_ids]
            if not cart_items:
                raise ValueError("No valid cart items found for the specified IDs")
        
        # Check availability of all items
        unavailable_items = [item for item in cart_items if not item.is_available]
        if unavailable_items:
            unavailable_names = [item.product.name for item in unavailable_items]
            raise ValueError(f"Some items are no longer available: {', '.join(unavailable_names)}")
        
        # Create order items from cart items
        order_items = []
        for cart_item in cart_items:
            order_items.append(CustomerOrderItemCreate(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                notes=cart_item.notes
            ))
        
        # Create order
        customer_order = CustomerOrderCreate(
            items=order_items,
            shipping_address_line1=cart_to_order.shipping_address_line1,
            shipping_address_line2=cart_to_order.shipping_address_line2,
            shipping_city=cart_to_order.shipping_city,
            shipping_state=cart_to_order.shipping_state,
            shipping_postal_code=cart_to_order.shipping_postal_code,
            shipping_country=cart_to_order.shipping_country,
            delivery_method=cart_to_order.delivery_method,
            order_source=cart_to_order.order_source,
            customer_notes=cart_to_order.customer_notes,
            special_instructions=cart_to_order.special_instructions
        )
        
        # Create the order
        order = OrderService.create_customer_order(
            db=db,
            customer_order=customer_order,
            customer_id=customer_id,
            owner_id=owner_id
        )
        
        # Remove converted items from cart
        for cart_item in cart_items:
            db.delete(cart_item)
        
        db.commit()
        
        # Convert order to Pydantic model for serialization
        from src.app.schemas.order import OrderResponse
        
        return {
            "order": OrderResponse.model_validate(order),
            "converted_items_count": len(cart_items),
            "message": f"Successfully created order {order.order_number} from {len(cart_items)} cart items"
        }