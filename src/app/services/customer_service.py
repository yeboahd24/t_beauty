"""
Customer service for T-Beauty business logic.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


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
        db_customer = Customer(**customer_create.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
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