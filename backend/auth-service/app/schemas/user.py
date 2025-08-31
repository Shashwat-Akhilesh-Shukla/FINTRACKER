# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    email_verified: bool
    avatar: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    full_name: str

    class Config:
        from_attributes = True

class UserProfileResponse(UserResponse):
    phone: Optional[str] = None
    bio: Optional[str] = None
