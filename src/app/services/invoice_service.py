"""
Invoice service for T-Beauty invoice management.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import uuid

from src.app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, Payment
from src.app.models.customer import Customer
from src.app.models.order import Order
from src.app.models.inventory import InventoryItem
from src.app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceItemCreate


class InvoiceService:
    """Invoice service class for business logic."""

    @staticmethod
    def generate_invoice_number() -> str:
        """Generate a unique invoice number."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:6].upper()
        return f"INV-{timestamp}-{unique_id}"

    @staticmethod
    def get_by_id(
        db: Session, invoice_id: int, owner_id: int = None
    ) -> Optional[Invoice]:
        """Get invoice by ID with all relationships loaded."""
        query = (
            db.query(Invoice)
            .options(
                joinedload(Invoice.customer),
                joinedload(Invoice.order),
                joinedload(Invoice.invoice_items).joinedload(
                    InvoiceItem.inventory_item
                ),
                joinedload(Invoice.payments),
                joinedload(Invoice.created_by),
            )
            .filter(Invoice.id == invoice_id)
        )

        if owner_id is not None:
            query = query.filter(Invoice.created_by_user_id == owner_id)

        return query.first()

    @staticmethod
    def get_by_invoice_number(
        db: Session, invoice_number: str, owner_id: int = None
    ) -> Optional[Invoice]:
        """Get invoice by invoice number."""
        query = (
            db.query(Invoice)
            .options(joinedload(Invoice.customer), joinedload(Invoice.invoice_items))
            .filter(Invoice.invoice_number == invoice_number)
        )

        if owner_id is not None:
            query = query.filter(Invoice.created_by_user_id == owner_id)

        return query.first()

    @staticmethod
    def get_by_customer(
        db: Session, customer_id: int, owner_id: int = None
    ) -> List[Invoice]:
        """Get all invoices for a specific customer."""
        query = (
            db.query(Invoice)
            .options(joinedload(Invoice.customer), joinedload(Invoice.invoice_items))
            .filter(Invoice.customer_id == customer_id)
            .order_by(desc(Invoice.created_at))
        )

        if owner_id is not None:
            query = query.filter(Invoice.created_by_user_id == owner_id)

        return query.all()

    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[InvoiceStatus] = None,
        customer_id: Optional[int] = None,
        search: Optional[str] = None,
        overdue_only: bool = False,
    ) -> List[Invoice]:
        """Get all invoices with filtering and pagination."""
        query = (
            db.query(Invoice)
            .options(joinedload(Invoice.customer), joinedload(Invoice.invoice_items))
            .filter(Invoice.created_by_user_id == owner_id)
            .order_by(desc(Invoice.created_at))
        )

        # Apply filters
        if status:
            query = query.filter(Invoice.status == status)

        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)

        if search:
            query = query.filter(
                Invoice.invoice_number.contains(search)
                | Invoice.description.contains(search)
                | Invoice.customer.has(Customer.first_name.contains(search))
                | Invoice.customer.has(Customer.last_name.contains(search))
                | Invoice.customer.has(Customer.email.contains(search))
            )

        if overdue_only:
            query = query.filter(
                and_(
                    Invoice.due_date < datetime.utcnow(),
                    Invoice.status != InvoiceStatus.PAID,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(
        db: Session,
        owner_id: int,
        status: Optional[InvoiceStatus] = None,
        customer_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count invoices with filtering."""
        query = db.query(Invoice).filter(Invoice.created_by_user_id == owner_id)

        if status:
            query = query.filter(Invoice.status == status)

        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)

        if search:
            query = query.filter(
                Invoice.invoice_number.contains(search)
                | Invoice.description.contains(search)
                | Invoice.customer.has(Customer.first_name.contains(search))
                | Invoice.customer.has(Customer.last_name.contains(search))
                | Invoice.customer.has(Customer.email.contains(search))
            )

        return query.count()

    @staticmethod
    def create(db: Session, invoice_create: InvoiceCreate, owner_id: int) -> Invoice:
        """Create a new invoice with items."""
        # Validate customer exists
        customer = (
            db.query(Customer).filter(Customer.id == invoice_create.customer_id).first()
        )
        if not customer:
            raise ValueError("Customer not found")

        # Generate invoice number
        invoice_number = InvoiceService.generate_invoice_number()

        # Create invoice
        db_invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=invoice_create.customer_id,
            order_id=invoice_create.order_id,
            status=InvoiceStatus.DRAFT,
            description=invoice_create.description,
            notes=invoice_create.notes,
            terms_and_conditions=invoice_create.terms_and_conditions,
            payment_terms=invoice_create.payment_terms,
            due_date=invoice_create.due_date,
            created_by_user_id=owner_id,
        )

        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)

        # Add invoice items
        total_amount = 0.0
        for item_data in invoice_create.items:
            invoice_item = InvoiceService._create_invoice_item(
                db, db_invoice.id, item_data
            )
            total_amount += invoice_item.total_price

        # Update invoice totals
        db_invoice.subtotal = total_amount
        db_invoice.total_amount = (
            total_amount - db_invoice.discount_amount + db_invoice.tax_amount
        )

        db.commit()
        db.refresh(db_invoice)

        return InvoiceService.get_by_id(db, db_invoice.id, owner_id)

    @staticmethod
    def _create_invoice_item(
        db: Session, invoice_id: int, item_data: InvoiceItemCreate
    ) -> InvoiceItem:
        """Create an invoice item."""
        # Calculate total price
        total_price = (
            item_data.unit_price * item_data.quantity
        ) - item_data.discount_amount

        invoice_item = InvoiceItem(
            invoice_id=invoice_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_amount=item_data.discount_amount,
            total_price=total_price,
            inventory_item_id=item_data.inventory_item_id,
        )

        db.add(invoice_item)
        db.commit()
        db.refresh(invoice_item)

        return invoice_item

    @staticmethod
    def create_from_order(db: Session, order_id: int, owner_id: int) -> Invoice:
        """Create an invoice from an existing order."""
        from src.app.services.order_service import OrderService

        # Get the order
        order = OrderService.get_by_id(db, order_id, owner_id)
        if not order:
            raise ValueError("Order not found")

        # Check if invoice already exists for this order
        existing_invoice = (
            db.query(Invoice).filter(Invoice.order_id == order_id).first()
        )
        if existing_invoice:
            raise ValueError("Invoice already exists for this order")

        # Generate invoice number
        invoice_number = InvoiceService.generate_invoice_number()

        # Create invoice from order
        db_invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=order.customer_id,
            order_id=order.id,
            status=InvoiceStatus.DRAFT,
            description=f"Invoice for Order {order.order_number}",
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            total_amount=order.total_amount,
            payment_terms="Due on receipt",
            due_date=datetime.utcnow() + timedelta(days=30),  # 30 days from now
            created_by_user_id=owner_id,
        )

        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)

        # Create invoice items from order items
        for order_item in order.order_items:
            invoice_item = InvoiceItem(
                invoice_id=db_invoice.id,
                description=f"{order_item.product_name} - {order_item.notes or ''}".strip(
                    " -"
                ),
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                discount_amount=order_item.discount_amount,
                total_price=order_item.total_price,
                inventory_item_id=order_item.inventory_item_id,
            )
            db.add(invoice_item)

        db.commit()
        db.refresh(db_invoice)

        return InvoiceService.get_by_id(db, db_invoice.id, owner_id)

    @staticmethod
    def update(
        db: Session, invoice_id: int, invoice_update: InvoiceUpdate, owner_id: int
    ) -> Optional[Invoice]:
        """Update an invoice."""
        db_invoice = InvoiceService.get_by_id(db, invoice_id, owner_id)
        if not db_invoice:
            return None

        # Only allow updates if invoice is in DRAFT status
        if db_invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only update invoices in DRAFT status")

        update_data = invoice_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_invoice, field, value)

        db.commit()
        db.refresh(db_invoice)
        return db_invoice

    @staticmethod
    def send_invoice(db: Session, invoice_id: int, owner_id: int) -> Invoice:
        """Mark invoice as sent."""
        db_invoice = InvoiceService.get_by_id(db, invoice_id, owner_id)
        if not db_invoice:
            raise ValueError("Invoice not found")

        if db_invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only send invoices in DRAFT status")

        db_invoice.status = InvoiceStatus.SENT
        db_invoice.sent_at = datetime.utcnow()

        db.commit()
        db.refresh(db_invoice)
        return db_invoice

    @staticmethod
    def mark_as_paid(
        db: Session, invoice_id: int, owner_id: int, payment_amount: float = None
    ) -> Invoice:
        """Mark invoice as paid."""
        db_invoice = InvoiceService.get_by_id(db, invoice_id, owner_id)
        if not db_invoice:
            raise ValueError("Invoice not found")

        if payment_amount is None:
            payment_amount = db_invoice.total_amount

        db_invoice.amount_paid = payment_amount
        db_invoice.status = InvoiceStatus.PAID
        db_invoice.paid_at = datetime.utcnow()

        db.commit()
        db.refresh(db_invoice)
        return db_invoice

    @staticmethod
    def cancel_invoice(db: Session, invoice_id: int, owner_id: int) -> Invoice:
        """Cancel an invoice."""
        db_invoice = InvoiceService.get_by_id(db, invoice_id, owner_id)
        if not db_invoice:
            raise ValueError("Invoice not found")

        if db_invoice.status == InvoiceStatus.PAID:
            raise ValueError("Cannot cancel a paid invoice")

        db_invoice.status = InvoiceStatus.CANCELLED

        db.commit()
        db.refresh(db_invoice)
        return db_invoice

    @staticmethod
    def get_stats(
        db: Session, owner_id: int, days: int = 30, all_time: bool = True
    ) -> dict:
        """Get invoice statistics for dashboard."""
        if all_time:
            # Get stats for all invoices regardless of date
            base_query = db.query(Invoice).filter(
                Invoice.created_by_user_id == owner_id
            )
        else:
            start_date = datetime.utcnow() - timedelta(days=days)
            # Base query for the time period
            base_query = db.query(Invoice).filter(
                and_(
                    Invoice.created_by_user_id == owner_id,
                    Invoice.created_at >= start_date,
                )
            )

        total_invoices = base_query.count()
        draft_invoices = base_query.filter(
            Invoice.status == InvoiceStatus.DRAFT
        ).count()
        sent_invoices = base_query.filter(Invoice.status == InvoiceStatus.SENT).count()
        paid_invoices = base_query.filter(Invoice.status == InvoiceStatus.PAID).count()

        # Overdue invoices
        overdue_invoices = base_query.filter(
            and_(
                Invoice.due_date < datetime.utcnow(),
                Invoice.status != InvoiceStatus.PAID,
                Invoice.status != InvoiceStatus.CANCELLED,
            )
        ).count()

        # Revenue calculations
        total_revenue = (
            base_query.filter(Invoice.status == InvoiceStatus.PAID)
            .with_entities(func.sum(Invoice.total_amount))
            .scalar()
            or 0.0
        )

        outstanding_amount = (
            base_query.filter(
                Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.VIEWED])
            )
            .with_entities(func.sum(Invoice.total_amount - Invoice.amount_paid))
            .scalar()
            or 0.0
        )

        return {
            "period_days": days if not all_time else None,
            "all_time": all_time,
            "total_invoices": total_invoices,
            "draft_invoices": draft_invoices,
            "sent_invoices": sent_invoices,
            "paid_invoices": paid_invoices,
            "overdue_invoices": overdue_invoices,
            "total_revenue": float(total_revenue),
            "outstanding_amount": float(outstanding_amount),
            "average_invoice_value": float(total_revenue / paid_invoices)
            if paid_invoices > 0
            else 0.0,
        }

    @staticmethod
    def get_overdue_invoices(db: Session, owner_id: int) -> List[Invoice]:
        """Get all overdue invoices."""
        return (
            db.query(Invoice)
            .options(joinedload(Invoice.customer))
            .filter(
                and_(
                    Invoice.created_by_user_id == owner_id,
                    Invoice.due_date < datetime.utcnow(),
                    Invoice.status != InvoiceStatus.PAID,
                    Invoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .order_by(Invoice.due_date.asc())
            .all()
        )

    @staticmethod
    def delete(db: Session, invoice_id: int, owner_id: int) -> bool:
        """Delete an invoice (only if in DRAFT status)."""
        db_invoice = InvoiceService.get_by_id(db, invoice_id, owner_id)
        if not db_invoice:
            return False

        if db_invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only delete invoices in DRAFT status")

        db.delete(db_invoice)
        db.commit()
        return True

