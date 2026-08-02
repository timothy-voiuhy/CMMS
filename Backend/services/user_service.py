from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from models.user import User, UserRole
from schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
from core.security import get_password_hash, verify_password


def get_users(db: Session, skip: int = 0, limit: int = 100, 
              search: Optional[str] = None,
              role: Optional[UserRole] = None) -> List[User]:
    """Get all users with optional filters."""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    return query.offset(skip).limit(limit).all()


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    # Check if username exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        phone=user.phone
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """Update user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    
    # Check email uniqueness if being updated
    if 'email' in update_data and update_data['email'] != db_user.email:
        existing = get_user_by_email(db, update_data['email'])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def update_user_password(db: Session, user_id: int, password_update: UserPasswordUpdate) -> bool:
    """Update user password."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    # Verify current password
    if not verify_password(password_update.current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    db_user.hashed_password = get_password_hash(password_update.new_password)
    db.commit()
    return True


def toggle_user_active(db: Session, user_id: int) -> Optional[User]:
    """Toggle user active status."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = not db_user.is_active
    db.commit()
    db.refresh(db_user)
    return db_user
