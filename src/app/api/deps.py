"""
API dependencies.
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.core.security import get_current_active_user
from src.app.models.user import User


def get_current_user_dep() -> User:
    """Get current user dependency."""
    return Depends(get_current_active_user)


def get_db_dep() -> Session:
    """Get database session dependency."""
    return Depends(get_db)