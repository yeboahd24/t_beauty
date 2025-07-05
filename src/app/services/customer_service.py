"""
Customer service for T-Beauty business logic.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from src.app.models.customer import Customer
from src.app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerRegister
from src.app.core.security import get_password_hash, verify_password


class CustomerService:
    """Customer service class for business logic."""
    
    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return db.query(Customer).filter(Customer.id == customer_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Customer]:
        """Get customer by email."""
        return db.query(Customer).filter(Customer.email == email).first()
    
    @staticmethod
    def get_by_instagram(db: Session, instagram_handle: str) -> Optional[Customer]:
        """Get customer by Instagram handle."""
        return db.query(Customer).filter(Customer.instagram_handle == instagram_handle).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_vip: Optional[bool] = None
    ) -> List[Customer]:
        """Get all customers with filtering and pagination."""
        query = db.query(Customer)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
        if is_vip is not None:
            query = query.filter(Customer.is_vip == is_vip)
        
        if search:
            search_filter = or_(
                Customer.first_name.contains(search),
                Customer.last_name.contains(search),
                Customer.email.contains(search),
                Customer.instagram_handle.contains(search),
                Customer.phone.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_vip: Optional[bool] = None
    ) -> int:
        """Count customers with filtering."""
        query = db.query(Customer)
        
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        
        if is_vip is not None:
            query = query.filter(Customer.is_vip == is_vip)
        
        if search:
            search_filter = or_(
                Customer.first_name.contains(search),
                Customer.last_name.contains(search),
                Customer.email.contains(search),
                Customer.instagram_handle.contains(search),
                Customer.phone.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.count()
    
    @staticmethod
    def create(db: Session, customer_create: CustomerCreate) -> Customer:
        """Create a new customer."""
        customer_data = customer_create.model_dump()
        
        # Hash password if provided, otherwise remove the field
        if customer_data.get('password'):
            customer_data['hashed_password'] = get_password_hash(customer_data.pop('password'))
        else:
            # Remove password field if it exists but is None/empty
            customer_data.pop('password', None)
        
        db_customer = Customer(**customer_data)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    def register(db: Session, customer_register: CustomerRegister) -> Customer:
        """Register a new customer with authentication."""
        customer_data = customer_register.model_dump()
        
        # Hash the password
        customer_data['hashed_password'] = get_password_hash(customer_data.pop('password'))
        
        db_customer = Customer(**customer_data)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[Customer]:
        """Authenticate customer with email and password."""
        customer = CustomerService.get_by_email(db, email)
        if not customer:
            return None
        if not customer.hashed_password:
            return None  # Customer doesn't have password set
        if not verify_password(password, customer.hashed_password):
            return None
        return customer
    
    @staticmethod
    def authenticate_with_details(db: Session, email: str, password: str) -> Tuple[Optional[Customer], str]:
        """Authenticate customer and return detailed result."""
        customer = CustomerService.get_by_email(db, email)
        if not customer:
            return None, 'customer_not_found'
        
        if not customer.hashed_password:
            return None, 'no_password_set'
        
        if not verify_password(password, customer.hashed_password):
            return None, 'invalid_password'
        
        return customer, 'success'
    
    @staticmethod
    def is_active(customer: Customer) -> bool:
        """Check if customer is active."""
        return customer.is_active
    
    @staticmethod
    def update(
        db: Session,
        customer_id: int,
        customer_update: CustomerUpdate
    ) -> Optional[Customer]:
        """Update a customer."""
        db_customer = CustomerService.get_by_id(db, customer_id)
        if not db_customer:
            return None
        
        update_data = customer_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    def delete(db: Session, customer_id: int) -> bool:
        """Soft delete a customer (deactivate)."""
        db_customer = CustomerService.get_by_id(db, customer_id)
        if not db_customer:
            return False
        
        db_customer.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def can_hard_delete(db: Session, customer_id: int) -> dict:
        """Check if customer can be safely hard deleted."""
        from src.app.models.order import Order
        from src.app.models.invoice import Invoice
        
        db_customer = CustomerService.get_by_id(db, customer_id)
        if not db_customer:
            return {"can_delete": False, "reason": "Customer not found"}
        
        # Check for orders
        order_count = db.query(Order).filter(Order.customer_id == customer_id).count()
        
        # Check for invoices
        invoice_count = db.query(Invoice).filter(Invoice.customer_id == customer_id).count()
        
        blocking_factors = []
        if order_count > 0:
            blocking_factors.append(f"{order_count} orders")
        if invoice_count > 0:
            blocking_factors.append(f"{invoice_count} invoices")
        
        can_delete = len(blocking_factors) == 0
        
        return {
            "can_delete": can_delete,
            "customer_id": customer_id,
            "customer_name": db_customer.full_name,
            "order_count": order_count,
            "invoice_count": invoice_count,
            "blocking_factors": blocking_factors,
            "recommendation": "Use soft delete (deactivate) to preserve order history" if not can_delete else "Safe to hard delete"
        }
    
    @staticmethod
    def hard_delete(db: Session, customer_id: int, force: bool = False) -> dict:
        """Hard delete a customer (permanently remove from database)."""
        # Check if safe to delete
        safety_check = CustomerService.can_hard_delete(db, customer_id)
        
        if not safety_check["can_delete"] and not force:
            return {
                "success": False,
                "message": "Cannot delete customer with existing orders/invoices",
                "details": safety_check
            }
        
        db_customer = CustomerService.get_by_id(db, customer_id)
        if not db_customer:
            return {
                "success": False,
                "message": "Customer not found"
            }
        
        customer_name = db_customer.full_name
        
        try:
            if force:
                # Force delete - remove all related records first
                from src.app.models.order import Order
                from src.app.models.invoice import Invoice
                
                # Delete related invoices
                db.query(Invoice).filter(Invoice.customer_id == customer_id).delete()
                
                # Delete related orders (cascade will handle order_items)
                db.query(Order).filter(Order.customer_id == customer_id).delete()
            
            # Delete the customer
            db.delete(db_customer)
            db.commit()
            
            return {
                "success": True,
                "message": f"Customer '{customer_name}' permanently deleted",
                "forced": force
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"Failed to delete customer: {str(e)}"
            }
    
    @staticmethod
    def get_vip_customers(db: Session) -> List[Customer]:
        """Get all VIP customers."""
        return db.query(Customer).filter(
            and_(Customer.is_vip == True, Customer.is_active == True)
        ).all()
    
    @staticmethod
    def promote_to_vip(db: Session, customer_id: int) -> Optional[Customer]:
        """Promote customer to VIP status."""
        db_customer = CustomerService.get_by_id(db, customer_id)
        if not db_customer:
            return None
        
        db_customer.is_vip = True
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    @staticmethod
    def get_customer_stats(db: Session) -> dict:
        """Get customer statistics."""
        total_customers = db.query(Customer).count()
        active_customers = db.query(Customer).filter(Customer.is_active == True).count()
        vip_customers = db.query(Customer).filter(
            and_(Customer.is_vip == True, Customer.is_active == True)
        ).count()
        
        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "vip_customers": vip_customers,
            "inactive_customers": total_customers - active_customers
        }
    
    @staticmethod
    def bulk_import_from_csv(db: Session, csv_file_path: str) -> dict:
        """Bulk import customers from CSV file."""
        import csv
        import os
        
        if not os.path.exists(csv_file_path):
            return {
                "success": False,
                "message": f"CSV file not found: {csv_file_path}",
                "imported_count": 0,
                "errors": []
            }
        
        imported_count = 0
        errors = []
        skipped_count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
                    try:
                        # Extract and clean data from CSV
                        first_name = row.get('contact_first_name', '').strip()
                        last_name = row.get('contact_last_name', '').strip()
                        email = row.get('email', '').strip().lower() if row.get('email') else None
                        phone = row.get('phone', '').strip() if row.get('phone') else None
                        
                        # Skip rows with missing essential data
                        if not first_name and not last_name:
                            skipped_count += 1
                            continue
                        
                        # Handle cases where first_name might be empty but last_name has full name
                        if not first_name and last_name:
                            name_parts = last_name.split(' ', 1)
                            first_name = name_parts[0]
                            last_name = name_parts[1] if len(name_parts) > 1 else ''
                        
                        # Skip if email already exists
                        if email and CustomerService.get_by_email(db, email):
                            skipped_count += 1
                            continue
                        
                        # Build address from CSV fields
                        address_parts = []
                        if row.get('address_line_1'):
                            address_parts.append(row.get('address_line_1').strip())
                        if row.get('address_line_2'):
                            address_parts.append(row.get('address_line_2').strip())
                        
                        address_line1 = address_parts[0] if address_parts else None
                        address_line2 = address_parts[1] if len(address_parts) > 1 else None
                        
                        # Extract other fields
                        city = row.get('city', '').strip() if row.get('city') else None
                        state = row.get('province/state', '').strip() if row.get('province/state') else None
                        country = row.get('country', 'Trinidad and Tobago').strip() if row.get('country') else 'Trinidad and Tobago'
                        
                        # Create customer data
                        customer_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'phone': phone,
                            'address_line1': address_line1,
                            'address_line2': address_line2,
                            'city': city,
                            'state': state,
                            'country': country,
                            'is_active': True,
                            'is_vip': False,
                            'preferred_contact_method': 'phone' if phone else 'email'
                        }
                        
                        # Create customer
                        db_customer = Customer(**customer_data)
                        db.add(db_customer)
                        db.commit()
                        db.refresh(db_customer)
                        
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        db.rollback()
                        continue
            
            return {
                "success": True,
                "message": f"Successfully imported {imported_count} customers",
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to process CSV file: {str(e)}",
                "imported_count": imported_count,
                "errors": errors
            }