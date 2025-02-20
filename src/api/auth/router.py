"""
Authentication router for handling login and user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

from src.api.auth.models import User, UserCreate, UserUpdate, Token
from src.api.auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Temporary user storage - replace with database
fake_users_db = {}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get JWT token."""
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
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
async def create_user(user: UserCreate):
    """Create new user."""
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        **user.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    fake_users_db[user.username] = db_user
    return db_user

@router.get("/users/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.put("/users/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user information."""
    updated_user = current_user.copy(update=user_update.dict(exclude_unset=True))
    if user_update.password:
        updated_user.hashed_password = get_password_hash(user_update.password)
    
    fake_users_db[current_user.username] = updated_user
    return updated_user