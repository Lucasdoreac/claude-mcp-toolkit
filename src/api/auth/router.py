"""
Authentication router for handling login and user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from src.api.auth.models import User, UserCreate, UserUpdate, Token
from src.api.auth.utils import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.api.auth.crud import (
    create_user,
    authenticate_user,
    get_user_by_username,
    update_user
)
from src.api.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint to get JWT token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=User)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create new user."""
    return create_user(db, user)

@router.get("/users/me", response_model=User)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user

@router.put("/users/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    return update_user(db, current_user, user_update)

@router.post("/users/deactivate", response_model=User)
async def deactivate_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate current user account."""
    current_user.is_active = False
    db.commit()
    return current_user