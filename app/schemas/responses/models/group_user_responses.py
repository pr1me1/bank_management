import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.telegram.group_users import GroupRole


class GroupUserResponse(BaseModel):
    """Schema for returning group user details."""
    id: uuid.UUID = Field(..., description="Group user ID")
    group_id: uuid.UUID = Field(..., description="Group ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    role: GroupRole = Field(..., description="User role")
    join_date: datetime = Field(..., description="Join date")
    left_date: Optional[datetime] = Field(None, description="Left date")
    ban_date: Optional[datetime] = Field(None, description="Ban date")

    model_config = ConfigDict(from_attributes=True)


__all__ = ["GroupUserResponse"]
