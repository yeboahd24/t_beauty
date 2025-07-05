"""
User service for business logic.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from src.app.models.user import User
from src.app.schemas.user import UserCreate
from src.app.core.security import get_password_hash, verify_password


class UserService:
    """User service class."""
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(db: Session, user_create: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def authenticate_with_details(db: Session, email: str, password: str) -> Tuple[Optional[User], str]:
        """
        Authenticate user with email and password, returning detailed error info.
        
        Returns:
            tuple: (user_object_or_none, error_type)
            error_type can be: 'success', 'user_not_found', 'invalid_password'
        """
        user = UserService.get_by_email(db, email)
        if not user:
            return None, 'user_not_found'
        if not verify_password(password, user.hashed_password):
            return None, 'invalid_password'
        return user, 'success'
    
    @staticmethod
    def is_active(user: User) -> bool:
        """Check if user is active."""
        return user.is_active
    
    @staticmethod
    def deactivate(db: Session, user: User) -> User:
        """Deactivate user."""
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_total_users_count(db: Session) -> int:
        """Get total number of users in the system."""
        return db.query(User).count()
    
    @staticmethod
    def get_active_users_count(db: Session) -> int:
        """Get total number of active users in the system."""
        return db.query(User).filter(User.is_active == True).count()