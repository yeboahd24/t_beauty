"""
Order service for T-Beauty order management with automatic stock reduction.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import uuid

from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.customer import Customer
from app.models.inventory import InventoryItem
from app.schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, CustomerOrderCreate, CustomerOrderItemCreate
from app.services.inventory_service import InventoryService
from app.schemas.inventory import StockMovementCreate


class OrderService:
    """Order service class for business logic."""
    
    @staticmethod
    def generate_order_number() -> str:
        """Generate a unique order number."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TB-{timestamp}-{unique_id}"
    
    @staticmethod
    def get_by_id(db: Session, order_id: int, owner_id: int = None) -> Optional[Order]:
        """Get order by ID with all relationships loaded."""
        query = (
            db.query(Order)
            .options(
                joinedload(Order.customer),
                joinedload(Order.order_items).joinedload(OrderItem.inventory_item),
                joinedload(Order.created_by)
            )
            .filter(Order.id == order_id)
        )
        
        if owner_id is not None:
            query = query.filter(Order.created_by_user_id == owner_id)
        
        return query.first()
    
    @staticmethod
    def get_by_order_number(db: Session, order_number: str, owner_id: int = None) -> Optional[Order]:
        """Get order by order number."""
        query = (
            db.query(Order)
            .options(
                joinedload(Order.customer),
                joinedload(Order.order_items).joinedload(OrderItem.inventory_item)
            )
            .filter(Order.order_number == order_number)
        )
        
        if owner_id is not None:
            query = query.filter(Order.created_by_user_id == owner_id)
        
        return query.first()
    
    @staticmethod
    def get_by_customer(db: Session, customer_id: int) -> List[Order]:
        """Get all orders for a specific customer."""
        return (
            db.query(Order)
            .options(
                joinedload(Order.customer),
                joinedload(Order.order_items).joinedload(OrderItem.inventory_item)
            )
            .filter(Order.customer_id == customer_id)
            .order_by(desc(Order.created_at))
            .all()
        )
    
    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        customer_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Order]:
        """Get all orders with filtering and pagination."""
        query = (
            db.query(Order)
            .options(
                joinedload(Order.customer),
                joinedload(Order.order_items)
            )
            .filter(Order.created_by_user_id == owner_id)
            .order_by(desc(Order.created_at))
        )
        
        # Apply filters
        if status:
            query = query.filter(Order.status == status)
        
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if search:
            query = query.filter(
                Order.order_number.contains(search) |
                Order.customer.has(Customer.first_name.contains(search)) |
                Order.customer.has(Customer.last_name.contains(search)) |
                Order.customer.has(Customer.email.contains(search))
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        owner_id: int,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        customer_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> int:
        """Count orders with filtering."""
        query = db.query(Order).filter(Order.created_by_user_id == owner_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if search:
            query = query.filter(
                Order.order_number.contains(search) |
                Order.customer.has(Customer.first_name.contains(search)) |
                Order.customer.has(Customer.last_name.contains(search)) |
                Order.customer.has(Customer.email.contains(search))
            )
        
        return query.count()
    
    @staticmethod
    def create(db: Session, order_create: OrderCreate, owner_id: int) -> Order:
        """Create a new order with items."""
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == order_create.customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        # Generate order number
        order_number = OrderService.generate_order_number()
        
        # Create order
        db_order = Order(
            order_number=order_number,
            customer_id=order_create.customer_id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            payment_method=order_create.payment_method,
            order_source=order_create.order_source or "instagram",
            instagram_post_url=order_create.instagram_post_url,
            customer_notes=order_create.customer_notes,
            internal_notes=order_create.internal_notes,
            special_instructions=order_create.special_instructions,
            delivery_method=order_create.delivery_method or "standard",
            created_by_user_id=owner_id
        )
        
        # Add shipping address fields directly from order_create
        db_order.shipping_address_line1 = order_create.shipping_address_line1
        db_order.shipping_address_line2 = order_create.shipping_address_line2
        db_order.shipping_city = order_create.shipping_city
        db_order.shipping_state = order_create.shipping_state
        db_order.shipping_postal_code = order_create.shipping_postal_code
        db_order.shipping_country = order_create.shipping_country
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Add order items
        total_amount = 0.0
        for item_data in order_create.items:
            order_item = OrderService._create_order_item(db, db_order.id, item_data, owner_id)
            total_amount += order_item.total_price
        
        # Update order totals
        db_order.subtotal = total_amount
        db_order.shipping_cost = order_create.shipping_cost or 0.0
        db_order.tax_amount = order_create.tax_amount or 0.0
        db_order.discount_amount = order_create.discount_amount or 0.0
        db_order.total_amount = (
            db_order.subtotal + 
            db_order.shipping_cost + 
            db_order.tax_amount - 
            db_order.discount_amount
        )
        
        db.commit()
        db.refresh(db_order)
        
        return OrderService.get_by_id(db, db_order.id, owner_id)
    
    @staticmethod
    def create_customer_order(db: Session, customer_order: CustomerOrderCreate, customer_id: int, owner_id: int) -> Order:
        """Create a new order from customer order data."""
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        # Generate order number
        order_number = OrderService.generate_order_number()
        
        # Create order
        db_order = Order(
            order_number=order_number,
            customer_id=customer_id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            payment_method=customer_order.payment_method,
            order_source=customer_order.order_source or "instagram",
            instagram_post_url=customer_order.instagram_post_url,
            customer_notes=customer_order.customer_notes,
            special_instructions=customer_order.special_instructions,
            delivery_method=customer_order.delivery_method or "standard",
            created_by_user_id=owner_id
        )
        
        # Add shipping address fields
        db_order.shipping_address_line1 = customer_order.shipping_address_line1
        db_order.shipping_address_line2 = customer_order.shipping_address_line2
        db_order.shipping_city = customer_order.shipping_city
        db_order.shipping_state = customer_order.shipping_state
        db_order.shipping_postal_code = customer_order.shipping_postal_code
        db_order.shipping_country = customer_order.shipping_country
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Add order items
        total_amount = 0.0
        for item_data in customer_order.items:
            order_item = OrderService._create_customer_order_item(db, db_order.id, item_data, owner_id)
            total_amount += order_item.total_price
        
        # Update order totals
        db_order.subtotal = total_amount
        db_order.shipping_cost = customer_order.shipping_cost or 0.0
        db_order.tax_amount = customer_order.tax_amount or 0.0
        db_order.discount_amount = customer_order.discount_amount or 0.0
        db_order.total_amount = (
            db_order.subtotal + 
            db_order.shipping_cost + 
            db_order.tax_amount - 
            db_order.discount_amount
        )
        
        db.commit()
        db.refresh(db_order)
        
        return OrderService.get_by_id(db, db_order.id, owner_id)
    
    @staticmethod
    def _create_order_item(db: Session, order_id: int, item_data: OrderItemCreate, owner_id: int) -> OrderItem:
        """Create an order item for a product and attempt automatic allocation."""
        from app.services.product_service import ProductService
        
        # Get product
        product = ProductService.get_by_id(db, item_data.product_id, owner_id)
        if not product:
            raise ValueError(f"Product with ID {item_data.product_id} not found")
        
        # Check availability and get allocation plan
        availability = ProductService.check_availability(
            db=db,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            owner_id=owner_id,
            requested_color=item_data.requested_color,
            requested_shade=item_data.requested_shade,
            requested_size=item_data.requested_size
        )
        
        if not availability["can_fulfill"]:
            raise ValueError(
                f"Insufficient stock for {product.name}. "
                f"Available: {availability['total_available']}, Requested: {item_data.quantity}"
            )
        
        # Calculate pricing (use product base price if not specified)
        unit_price = item_data.unit_price or product.base_price
        total_price = (unit_price * item_data.quantity) - (item_data.discount_amount or 0.0)
        
        # Create order item with product snapshot (no allocation yet)
        order_item = OrderItem(
            order_id=order_id,
            product_id=item_data.product_id,
            inventory_item_id=None,  # Will be set during allocation
            quantity=item_data.quantity,
            unit_price=unit_price,
            discount_amount=item_data.discount_amount or 0.0,
            total_price=total_price,
            product_name=product.name,
            product_sku=product.sku,
            product_description=product.description,
            notes=item_data.notes,
            requested_color=item_data.requested_color,
            requested_shade=item_data.requested_shade,
            requested_size=item_data.requested_size,
            allocated_quantity=0,
            fulfilled_quantity=0
        )
        
        db.add(order_item)
        db.commit()
        db.refresh(order_item)
        
        return order_item
    
    @staticmethod
    def _create_customer_order_item(db: Session, order_id: int, item_data: CustomerOrderItemCreate, owner_id: int) -> OrderItem:
        """Create an order item from customer order data using inventory_item_id."""
        # Get inventory item
        inventory_item = db.query(InventoryItem).filter(
            InventoryItem.id == item_data.inventory_item_id
        ).first()
        
        if not inventory_item:
            raise ValueError(f"Inventory item with ID {item_data.inventory_item_id} not found")
        
        # Check stock availability
        if inventory_item.current_stock < item_data.quantity:
            raise ValueError(
                f"Insufficient stock for {inventory_item.name}. "
                f"Available: {inventory_item.current_stock}, Requested: {item_data.quantity}"
            )
        
        # Calculate pricing (use inventory selling price if not specified)
        unit_price = item_data.unit_price or inventory_item.selling_price
        total_price = unit_price * item_data.quantity
        
        # Create order item with inventory item reference
        order_item = OrderItem(
            order_id=order_id,
            product_id=inventory_item.product_id,  # Link to product through inventory
            inventory_item_id=inventory_item.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            discount_amount=0.0,
            total_price=total_price,
            product_name=inventory_item.name,
            product_sku=inventory_item.sku,
            product_description=inventory_item.description,
            notes=item_data.notes,
            allocated_quantity=0,
            fulfilled_quantity=0
        )
        
        db.add(order_item)
        db.commit()
        db.refresh(order_item)
        
        return order_item
    
    @staticmethod
    def confirm_order(db: Session, order_id: int, owner_id: int) -> Order:
        """Confirm order and reduce inventory stock automatically."""
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot confirm order with status: {order.status}")
        
        # Check stock availability for all items
        for order_item in order.order_items:
            inventory_item = order_item.inventory_item
            if inventory_item.current_stock < order_item.quantity:
                raise ValueError(
                    f"Insufficient stock for {inventory_item.name}. "
                    f"Available: {inventory_item.current_stock}, Required: {order_item.quantity}"
                )
        
        # Reduce stock for each item
        for order_item in order.order_items:
            inventory_item = order_item.inventory_item
            new_stock = inventory_item.current_stock - order_item.quantity
            
            # Update inventory stock
            InventoryService.adjust_stock(
                db=db,
                item_id=inventory_item.id,
                new_quantity=new_stock,
                reason=f"Order confirmed: {order.order_number}",
                user_id=owner_id
            )
        
        # Update order status
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: int, owner_id: int, reason: str = None) -> Order:
        """Cancel order and restore inventory stock if already confirmed."""
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError(f"Cannot cancel order with status: {order.status}")
        
        # If order was confirmed, restore stock
        if order.status == OrderStatus.CONFIRMED:
            for order_item in order.order_items:
                inventory_item = order_item.inventory_item
                new_stock = inventory_item.current_stock + order_item.quantity
                
                # Restore inventory stock
                InventoryService.adjust_stock(
                    db=db,
                    item_id=inventory_item.id,
                    new_quantity=new_stock,
                    reason=f"Order cancelled: {order.order_number} - {reason or 'No reason provided'}",
                    user_id=owner_id
                )
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        order.internal_notes = f"{order.internal_notes or ''}\nCancelled: {reason or 'No reason provided'}"
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def update_order_status(
        db: Session, 
        order_id: int, 
        new_status: OrderStatus, 
        owner_id: int,
        tracking_number: str = None,
        courier_service: str = None
    ) -> Order:
        """Update order status with automatic timestamp updates."""
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        # Update status-specific timestamps
        if new_status == OrderStatus.SHIPPED and order.status != OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
            if tracking_number:
                order.tracking_number = tracking_number
            if courier_service:
                order.courier_service = courier_service
        
        elif new_status == OrderStatus.DELIVERED and order.status != OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        
        order.status = new_status
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def update_payment_status(
        db: Session,
        order_id: int,
        payment_status: PaymentStatus,
        amount_paid: float = None,
        payment_reference: str = None,
        owner_id: int = None
    ) -> Order:
        """Update order payment status and amount."""
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        order.payment_status = payment_status
        
        if amount_paid is not None:
            order.amount_paid = amount_paid
        
        if payment_reference:
            order.payment_reference = payment_reference
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def get_order_stats(db: Session, owner_id: int, days: int = 30) -> dict:
        """Get order statistics for dashboard."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query for the time period
        base_query = db.query(Order).filter(
            and_(
                Order.created_by_user_id == owner_id,
                Order.created_at >= start_date
            )
        )
        
        total_orders = base_query.count()
        pending_orders = base_query.filter(Order.status == OrderStatus.PENDING).count()
        confirmed_orders = base_query.filter(Order.status == OrderStatus.CONFIRMED).count()
        shipped_orders = base_query.filter(Order.status == OrderStatus.SHIPPED).count()
        delivered_orders = base_query.filter(Order.status == OrderStatus.DELIVERED).count()
        cancelled_orders = base_query.filter(Order.status == OrderStatus.CANCELLED).count()
        
        # Revenue calculations
        total_revenue = base_query.filter(
            Order.payment_status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL])
        ).with_entities(func.sum(Order.amount_paid)).scalar() or 0.0
        
        pending_revenue = base_query.filter(
            Order.payment_status == PaymentStatus.PENDING
        ).with_entities(func.sum(Order.total_amount)).scalar() or 0.0
        
        return {
            "period_days": days,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": float(total_revenue),
            "pending_revenue": float(pending_revenue),
            "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0
        }
    
    @staticmethod
    def get_low_stock_impact(db: Session, owner_id: int) -> List[dict]:
        """Get orders that might be affected by low stock items."""
        # Get pending orders with items that are low in stock
        pending_orders = (
            db.query(Order)
            .join(OrderItem)
            .join(InventoryItem)
            .filter(
                and_(
                    Order.created_by_user_id == owner_id,
                    Order.status == OrderStatus.PENDING,
                    InventoryItem.current_stock <= InventoryItem.minimum_stock
                )
            )
            .distinct()
            .all()
        )
        
        impact_list = []
        for order in pending_orders:
            low_stock_items = []
            for item in order.order_items:
                if item.inventory_item.current_stock <= item.inventory_item.minimum_stock:
                    low_stock_items.append({
                        "name": item.inventory_item.name,
                        "sku": item.inventory_item.sku,
                        "current_stock": item.inventory_item.current_stock,
                        "minimum_stock": item.inventory_item.minimum_stock,
                        "ordered_quantity": item.quantity,
                        "can_fulfill": item.inventory_item.current_stock >= item.quantity
                    })
            
            if low_stock_items:
                impact_list.append({
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "customer_name": f"{order.customer.first_name} {order.customer.last_name}",
                    "total_amount": order.total_amount,
                    "low_stock_items": low_stock_items
                })
        
        return impact_list
    
    @staticmethod
    def allocate_inventory(db: Session, order_id: int, owner_id: int) -> Order:
        """Allocate inventory for all items in an order."""
        from app.services.product_service import ProductService
        
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot allocate inventory for order with status: {order.status}")
        
        allocation_results = []
        
        for order_item in order.order_items:
            if order_item.is_fully_allocated:
                continue  # Already allocated
            
            # Get available inventory for this product
            available_inventory = ProductService.get_available_for_order(
                db=db,
                product_id=order_item.product_id,
                owner_id=owner_id,
                requested_color=order_item.requested_color,
                requested_shade=order_item.requested_shade,
                requested_size=order_item.requested_size
            )
            
            remaining_to_allocate = order_item.quantity - order_item.allocated_quantity
            allocated_this_round = 0
            
            for inventory_item in available_inventory:
                if remaining_to_allocate <= 0:
                    break
                
                # Allocate from this inventory item
                allocate_qty = min(remaining_to_allocate, inventory_item.current_stock)
                
                if allocate_qty > 0:
                    # Update inventory stock
                    inventory_item.current_stock -= allocate_qty
                    
                    # Update order item allocation
                    if order_item.inventory_item_id is None:
                        # First allocation - set the primary inventory item
                        order_item.inventory_item_id = inventory_item.id
                        order_item.allocated_at = datetime.utcnow()
                    
                    order_item.allocated_quantity += allocate_qty
                    allocated_this_round += allocate_qty
                    remaining_to_allocate -= allocate_qty
                    
                    # Create stock movement record
                    InventoryService.create_stock_movement(
                        db=db,
                        movement=StockMovementCreate(
                            inventory_item_id=inventory_item.id,
                            movement_type="out",
                            quantity=allocate_qty,
                            reason=f"Allocated to order {order.order_number}",
                            reference_type="order",
                            reference_id=order.id
                        ),
                        user_id=owner_id
                    )
            
            allocation_results.append({
                "order_item_id": order_item.id,
                "product_name": order_item.product_name,
                "requested_quantity": order_item.quantity,
                "allocated_quantity": order_item.allocated_quantity,
                "allocated_this_round": allocated_this_round,
                "fully_allocated": order_item.is_fully_allocated
            })
        
        # Check if all items are fully allocated
        all_allocated = all(item.is_fully_allocated for item in order.order_items)
        
        if all_allocated:
            order.status = OrderStatus.CONFIRMED
            order.confirmed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def fulfill_order_item(
        db: Session, 
        order_id: int, 
        order_item_id: int, 
        quantity_to_fulfill: int,
        owner_id: int
    ) -> OrderItem:
        """Mark quantity as fulfilled for an order item."""
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        order_item = None
        for item in order.order_items:
            if item.id == order_item_id:
                order_item = item
                break
        
        if not order_item:
            raise ValueError("Order item not found")
        
        # Validate fulfillment
        max_fulfillable = order_item.allocated_quantity - order_item.fulfilled_quantity
        if quantity_to_fulfill > max_fulfillable:
            raise ValueError(
                f"Cannot fulfill {quantity_to_fulfill} units. "
                f"Maximum fulfillable: {max_fulfillable}"
            )
        
        # Update fulfillment
        order_item.fulfilled_quantity += quantity_to_fulfill
        
        if order_item.is_fully_fulfilled and not order_item.fulfilled_at:
            order_item.fulfilled_at = datetime.utcnow()
        
        # Check if entire order is fulfilled
        all_fulfilled = all(item.is_fully_fulfilled for item in order.order_items)
        if all_fulfilled and order.status != OrderStatus.DELIVERED:
            order.status = OrderStatus.SHIPPED
            order.shipped_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order_item)
        
        return order_item
    
    @staticmethod
    def get_allocation_status(db: Session, order_id: int, owner_id: int) -> dict:
        """Get detailed allocation status for an order."""
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")
        
        items_status = []
        total_items = len(order.order_items)
        fully_allocated_items = 0
        fully_fulfilled_items = 0
        
        for order_item in order.order_items:
            if order_item.is_fully_allocated:
                fully_allocated_items += 1
            if order_item.is_fully_fulfilled:
                fully_fulfilled_items += 1
            
            items_status.append({
                "order_item_id": order_item.id,
                "product_name": order_item.product_name,
                "product_sku": order_item.product_sku,
                "quantity": order_item.quantity,
                "allocated_quantity": order_item.allocated_quantity,
                "fulfilled_quantity": order_item.fulfilled_quantity,
                "pending_allocation": order_item.pending_allocation,
                "pending_fulfillment": order_item.pending_fulfillment,
                "is_fully_allocated": order_item.is_fully_allocated,
                "is_fully_fulfilled": order_item.is_fully_fulfilled,
                "inventory_item_id": order_item.inventory_item_id,
                "allocated_at": order_item.allocated_at,
                "fulfilled_at": order_item.fulfilled_at
            })
        
        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "total_items": total_items,
            "fully_allocated_items": fully_allocated_items,
            "fully_fulfilled_items": fully_fulfilled_items,
            "allocation_complete": fully_allocated_items == total_items,
            "fulfillment_complete": fully_fulfilled_items == total_items,
            "items": items_status
        }