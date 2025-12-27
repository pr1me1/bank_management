from typing import Optional
from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    """Base schema for Group."""
    title: str = Field(..., max_length=255, description="Group title")
    telegram_id: int = Field(..., description="Telegram group ID")


class GroupCreate(GroupBase):
    """Schema for creating a new group."""
    pass


class GroupUpdate(BaseModel):
    """Schema for updating a group."""
    title: Optional[str] = Field(None, max_length=255)


__all__ = [
    'GroupBase',
    'GroupCreate',
    'GroupUpdate',
]
