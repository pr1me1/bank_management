from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base schema for User."""
    username: Optional[str] = Field(None, max_length=64, description="Telegram username")
    first_name: Optional[str] = Field(None, max_length=64, description="First name")
    last_name: Optional[str] = Field(None, max_length=64, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    telegram_id: int = Field(..., description="Telegram user ID")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, max_length=64)
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    phone_number: Optional[str] = Field(None, max_length=20)


__all__ = [
    'UserBase',
    'UserCreate',
    'UserUpdate',
]
