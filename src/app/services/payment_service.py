"""
Payment service for T-Beauty payment management.
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import uuid

from app.models.invoice import Payment, PaymentMethod, Invoice
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.invoice import PaymentCreate, PaymentUpdate
from app.services.invoice_service import InvoiceService


class PaymentService:
    """Payment service class for business logic."""
    
    @staticmethod
    def generate_payment_reference() -> str:
        """Generate a unique payment reference."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:6].upper()
        return f"PAY-{timestamp}-{unique_id}"
    
    @staticmethod
    def get_by_id(db: Session, payment_id: int, owner_id: int = None) -> Optional[Payment]:
        """Get payment by ID with all relationships loaded."""
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.customer),
                joinedload(Payment.invoice),
                joinedload(Payment.order),
                joinedload(Payment.recorded_by),
                joinedload(Payment.verified_by)
            )
            .filter(Payment.id == payment_id)
        )
        
        if owner_id is not None:
            query = query.filter(Payment.recorded_by_user_id == owner_id)
        
        return query.first()
    
    @staticmethod
    def get_by_reference(db: Session, payment_reference: str, owner_id: int = None) -> Optional[Payment]:
        """Get payment by payment reference."""
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.customer),
                joinedload(Payment.invoice)
            )
            .filter(Payment.payment_reference == payment_reference)
        )
        
        if owner_id is not None:
            query = query.filter(Payment.recorded_by_user_id == owner_id)
        
        return query.first()
    
    @staticmethod
    def get_by_customer(db: Session, customer_id: int, owner_id: int = None) -> List[Payment]:
        """Get all payments for a specific customer."""
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.customer),
                joinedload(Payment.invoice)
            )
            .filter(Payment.customer_id == customer_id)
            .order_by(desc(Payment.payment_date))
        )
        
        if owner_id is not None:
            query = query.filter(Payment.recorded_by_user_id == owner_id)
        
        return query.all()
    
    @staticmethod
    def get_by_invoice(db: Session, invoice_id: int, owner_id: int = None) -> List[Payment]:
        """Get all payments for a specific invoice."""
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.customer),
                joinedload(Payment.invoice)
            )
            .filter(Payment.invoice_id == invoice_id)
            .order_by(desc(Payment.payment_date))
        )
        
        if owner_id is not None:
            query = query.filter(Payment.recorded_by_user_id == owner_id)
        
        return query.all()
    
    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        invoice_id: Optional[int] = None,
        payment_method: Optional[PaymentMethod] = None,
        is_verified: Optional[bool] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Payment]:
        """Get all payments with filtering and pagination."""
        query = (
            db.query(Payment)
            .options(
                joinedload(Payment.customer),
                joinedload(Payment.invoice)
            )
            .filter(Payment.recorded_by_user_id == owner_id)
            .order_by(desc(Payment.payment_date))
        )
        
        # Apply filters
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        
        if invoice_id:
            query = query.filter(Payment.invoice_id == invoice_id)
        
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        if is_verified is not None:
            query = query.filter(Payment.is_verified == is_verified)
        
        if search:
            query = query.filter(
                Payment.payment_reference.contains(search) |
                Payment.transaction_reference.contains(search) |
                Payment.notes.contains(search) |
                Payment.customer.has(Customer.first_name.contains(search)) |
                Payment.customer.has(Customer.last_name.contains(search)) |
                Payment.customer.has(Customer.email.contains(search))
            )
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        owner_id: int,
        customer_id: Optional[int] = None,
        invoice_id: Optional[int] = None,
        payment_method: Optional[PaymentMethod] = None,
        is_verified: Optional[bool] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count payments with filtering."""
        query = db.query(Payment).filter(Payment.recorded_by_user_id == owner_id)
        
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        
        if invoice_id:
            query = query.filter(Payment.invoice_id == invoice_id)
        
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        if is_verified is not None:
            query = query.filter(Payment.is_verified == is_verified)
        
        if search:
            query = query.filter(
                Payment.payment_reference.contains(search) |
                Payment.transaction_reference.contains(search) |
                Payment.notes.contains(search) |
                Payment.customer.has(Customer.first_name.contains(search)) |
                Payment.customer.has(Customer.last_name.contains(search)) |
                Payment.customer.has(Customer.email.contains(search))
            )
        
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        return query.count()
    
    @staticmethod
    def create(db: Session, payment_create: PaymentCreate, owner_id: int) -> Payment:
        """Create a new payment record."""
        # Determine customer_id: either from request or from order
        customer_id = payment_create.customer_id
        
        # If customer_id not provided, try to get it from order
        if not customer_id and payment_create.order_id:
            order = db.query(Order).filter(Order.id == payment_create.order_id).first()
            if not order:
                raise ValueError("Order not found")
            customer_id = order.customer_id
        
        # Validate that we have a customer_id
        if not customer_id:
            raise ValueError("Either customer_id or order_id must be provided")
        
        # Validate customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate order exists and belongs to customer if provided
        if payment_create.order_id:
            order = db.query(Order).filter(Order.id == payment_create.order_id).first()
            if not order:
                raise ValueError("Order not found")
            if order.customer_id != customer_id:
                raise ValueError("Order does not belong to the specified customer")
        
        # Validate invoice exists if provided
        if payment_create.invoice_id:
            invoice = db.query(Invoice).filter(Invoice.id == payment_create.invoice_id).first()
            if not invoice:
                raise ValueError("Invoice not found")
            
            # Check if invoice belongs to the same customer
            if invoice.customer_id != customer_id:
                raise ValueError("Invoice does not belong to the specified customer")
        
        # Generate payment reference
        payment_reference = PaymentService.generate_payment_reference()
        
        # Create payment
        db_payment = Payment(
            payment_reference=payment_reference,
            invoice_id=payment_create.invoice_id,
            customer_id=customer_id,  # Use the derived customer_id
            order_id=payment_create.order_id,
            amount=payment_create.amount,
            payment_method=payment_create.payment_method,
            payment_date=payment_create.payment_date or datetime.utcnow(),
            bank_name=payment_create.bank_name,
            account_number=payment_create.account_number,
            transaction_reference=payment_create.transaction_reference,
            pos_terminal_id=payment_create.pos_terminal_id,
            mobile_money_number=payment_create.mobile_money_number,
            notes=payment_create.notes,
            receipt_url=payment_create.receipt_url,
            is_verified=False,  # Always start as unverified
            recorded_by_user_id=owner_id
        )
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        return PaymentService.get_by_id(db, db_payment.id, owner_id)
    
    @staticmethod
    def update(
        db: Session,
        payment_id: int,
        payment_update: PaymentUpdate,
        owner_id: int
    ) -> Optional[Payment]:
        """Update a payment record."""
        db_payment = PaymentService.get_by_id(db, payment_id, owner_id)
        if not db_payment:
            return None
        
        update_data = payment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        
        db.commit()
        db.refresh(db_payment)
        return db_payment
    
    @staticmethod
    def verify_payment(
        db: Session,
        payment_id: int,
        owner_id: int,
        verification_notes: Optional[str] = None
    ) -> Payment:
        """Verify a payment and update related invoice."""
        db_payment = PaymentService.get_by_id(db, payment_id, owner_id)
        if not db_payment:
            raise ValueError("Payment not found")
        
        if db_payment.is_verified:
            raise ValueError("Payment is already verified")
        
        # Mark payment as verified
        db_payment.is_verified = True
        db_payment.verification_date = datetime.utcnow()
        db_payment.verification_notes = verification_notes
        db_payment.verified_by_user_id = owner_id
        
        # Update related invoice if exists
        if db_payment.invoice_id:
            invoice = db.query(Invoice).filter(Invoice.id == db_payment.invoice_id).first()
            if invoice:
                # Add payment amount to invoice
                invoice.amount_paid += db_payment.amount
                
                # Check if invoice is fully paid
                if invoice.amount_paid >= invoice.total_amount:
                    invoice.status = "paid"
                    invoice.paid_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_payment)
        
        return db_payment
    
    @staticmethod
    def unverify_payment(
        db: Session,
        payment_id: int,
        owner_id: int,
        reason: Optional[str] = None
    ) -> Payment:
        """Unverify a payment and update related invoice."""
        db_payment = PaymentService.get_by_id(db, payment_id, owner_id)
        if not db_payment:
            raise ValueError("Payment not found")
        
        if not db_payment.is_verified:
            raise ValueError("Payment is not verified")
        
        # Remove payment amount from related invoice if exists
        if db_payment.invoice_id:
            invoice = db.query(Invoice).filter(Invoice.id == db_payment.invoice_id).first()
            if invoice:
                # Subtract payment amount from invoice
                invoice.amount_paid = max(0, invoice.amount_paid - db_payment.amount)
                
                # Update invoice status if needed
                if invoice.status == "paid" and invoice.amount_paid < invoice.total_amount:
                    invoice.status = "sent"  # Revert to sent status
                    invoice.paid_at = None
        
        # Mark payment as unverified
        db_payment.is_verified = False
        db_payment.verification_date = None
        db_payment.verification_notes = reason
        db_payment.verified_by_user_id = None
        
        db.commit()
        db.refresh(db_payment)
        
        return db_payment
    
    @staticmethod
    def get_unverified_payments(db: Session, owner_id: int) -> List[Payment]:
        """Get all unverified payments."""
        return (
            db.query(Payment)
            .options(
                joinedload(Payment.customer),
                joinedload(Payment.invoice)
            )
            .filter(
                and_(
                    Payment.recorded_by_user_id == owner_id,
                    Payment.is_verified == False
                )
            )
            .order_by(Payment.payment_date.asc())
            .all()
        )
    
    @staticmethod
    def get_stats(db: Session, owner_id: int, days: int = 30, all_time: bool = True) -> Dict:
        """Get payment statistics for dashboard."""
        if all_time:
            # Get stats for all payments regardless of date
            base_query = db.query(Payment).filter(Payment.recorded_by_user_id == owner_id)
        else:
            start_date = datetime.utcnow() - timedelta(days=days)
            # Base query for the time period
            base_query = db.query(Payment).filter(
                and_(
                    Payment.recorded_by_user_id == owner_id,
                    Payment.payment_date >= start_date
                )
            )
        
        total_payments = base_query.count()
        verified_payments = base_query.filter(Payment.is_verified == True).count()
        unverified_payments = base_query.filter(Payment.is_verified == False).count()
        
        # Amount calculations
        total_amount = base_query.with_entities(func.sum(Payment.amount)).scalar() or 0.0
        verified_amount = base_query.filter(Payment.is_verified == True).with_entities(func.sum(Payment.amount)).scalar() or 0.0
        unverified_amount = base_query.filter(Payment.is_verified == False).with_entities(func.sum(Payment.amount)).scalar() or 0.0
        
        # Payment method breakdown
        payment_methods = {}
        for method in PaymentMethod:
            count = base_query.filter(Payment.payment_method == method).count()
            amount = base_query.filter(Payment.payment_method == method).with_entities(func.sum(Payment.amount)).scalar() or 0.0
            payment_methods[method.value] = {
                "count": count,
                "amount": float(amount)
            }
        
        return {
            "period_days": days if not all_time else None,
            "all_time": all_time,
            "total_payments": total_payments,
            "verified_payments": verified_payments,
            "unverified_payments": unverified_payments,
            "total_amount": float(total_amount),
            "verified_amount": float(verified_amount),
            "unverified_amount": float(unverified_amount),
            "average_payment_amount": float(total_amount / total_payments) if total_payments > 0 else 0.0,
            "payment_methods": payment_methods
        }
    
    @staticmethod
    def get_customer_payment_summary(db: Session, customer_id: int, owner_id: int) -> Dict:
        """Get payment summary for a specific customer."""
        payments = PaymentService.get_by_customer(db, customer_id, owner_id)
        
        total_payments = len(payments)
        verified_payments = sum(1 for p in payments if p.is_verified)
        total_amount = sum(p.amount for p in payments)
        verified_amount = sum(p.amount for p in payments if p.is_verified)
        
        # Payment method breakdown
        payment_methods = {}
        for payment in payments:
            method = payment.payment_method.value
            if method not in payment_methods:
                payment_methods[method] = {"count": 0, "amount": 0.0}
            payment_methods[method]["count"] += 1
            payment_methods[method]["amount"] += payment.amount
        
        return {
            "customer_id": customer_id,
            "total_payments": total_payments,
            "verified_payments": verified_payments,
            "unverified_payments": total_payments - verified_payments,
            "total_amount": float(total_amount),
            "verified_amount": float(verified_amount),
            "unverified_amount": float(total_amount - verified_amount),
            "payment_methods": payment_methods,
            "recent_payments": payments[:5]  # Last 5 payments
        }
    
    @staticmethod
    def delete(db: Session, payment_id: int, owner_id: int) -> bool:
        """Delete a payment record (only if unverified)."""
        db_payment = PaymentService.get_by_id(db, payment_id, owner_id)
        if not db_payment:
            return False
        
        if db_payment.is_verified:
            raise ValueError("Cannot delete verified payments")
        
        db.delete(db_payment)
        db.commit()
        return True