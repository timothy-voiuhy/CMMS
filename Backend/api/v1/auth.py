from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token, get_current_active_user
)
from typing import Optional
from pydantic import BaseModel
from models.user import User, UserRole
from schemas.user import Token, UserCreate, UserResponse

router = APIRouter()


class SetupStatusResponse(BaseModel):
    setup_required: bool
    message: str


class InitialAdminSetup(BaseModel):
    username: str = "admin"
    email: str
    full_name: str
    password: str
    phone: Optional[str] = None
    company_name: Optional[str] = None


@router.get("/setup-status", response_model=SetupStatusResponse)
async def check_setup_status(db: Session = Depends(get_db)):
    """Check if initial admin setup is required (no admin user in DB)."""
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    if admin_count == 0:
        return {
            "setup_required": True,
            "message": "Initial System Administrator setup required"
        }
    return {
        "setup_required": False,
        "message": "System administrator exists"
    }


@router.post("/setup-admin", response_model=Token)
async def setup_initial_admin(admin_data: InitialAdminSetup, db: Session = Depends(get_db)):
    """Create the initial System Administrator when database has no admin users."""
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    if admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System Administrator already exists. Setup is locked."
        )

    # Check if username or email exists
    if db.query(User).filter(User.username == admin_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    if db.query(User).filter(User.email == admin_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create initial company if specified and none exists
    if admin_data.company_name:
        from models.company import Company
        if not db.query(Company).first():
            company = Company(
                name=admin_data.company_name,
                industry_type="Industrial CMMS",
                currency="USD",
                timezone="UTC",
                language="en"
            )
            db.add(company)
            db.commit()

    # Create admin user
    user = User(
        username=admin_data.username,
        email=admin_data.email,
        full_name=admin_data.full_name,
        hashed_password=get_password_hash(admin_data.password),
        role=UserRole.ADMIN,
        phone=admin_data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        phone=user_data.phone
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login to get access token."""
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(request.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current logged-in user info with resolved permissions."""
    from services.company_service import get_user_permissions
    
    permissions = get_user_permissions(db, current_user.id)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value if current_user.role else "readonly",
        "is_active": current_user.is_active,
        "phone": current_user.phone,
        "created_at": str(current_user.created_at) if current_user.created_at else "",
        "updated_at": str(current_user.updated_at) if current_user.updated_at else "",
        "permissions": permissions
    }
