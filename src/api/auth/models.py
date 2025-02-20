"""
Authentication models for the API.
"""
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(UserBase):
    password: Optional[constr(min_length=8)] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str
    exp: Optional[datetime] = None