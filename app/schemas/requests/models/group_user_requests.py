import uuid
from pydantic import BaseModel, Field

from app.models.telegram.group_users import GroupRole


class GroupUserCreate(BaseModel):
    """Schema for adding a user to a group."""
    user_id: uuid.UUID = Field(..., description="User ID")
    role: GroupRole = Field(default=GroupRole.USER, description="User role in group")


class GroupUserUpdate(BaseModel):
    """Schema for updating a group user."""
    role: GroupRole = Field(..., description="New role for the user")


__all__ = [
    'GroupUserCreate',
    'GroupUserUpdate',
]
