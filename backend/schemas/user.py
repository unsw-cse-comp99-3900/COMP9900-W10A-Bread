"""
Pydantic schemas for user-related operations
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    age_group: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    age_group: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AgeGroupInfo(BaseModel):
    """Age group information"""
    value: str
    name: str
    age_range: tuple[int, int]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
