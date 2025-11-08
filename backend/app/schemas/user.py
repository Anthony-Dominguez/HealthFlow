"""User schemas"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""

    password: Optional[str] = Field(None, min_length=8)
    profile_data: Optional[Dict[str, Any]] = {}
    preferences: Optional[Dict[str, Any]] = {}


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """User response schema"""

    id: UUID
    profile_data: Dict[str, Any]
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
