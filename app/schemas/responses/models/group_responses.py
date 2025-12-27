import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class GroupResponse(BaseModel):
    """Schema for returning group details."""
    id: uuid.UUID = Field(..., description="Group ID")
    title: str = Field(..., description="Group title")
    telegram_id: int = Field(..., description="Telegram group ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class GroupListResponse(GroupResponse):
    id: uuid.UUID = Field(..., description="Group ID")
    title: str = Field(..., description="Group title")
    telegram_id: int = Field(..., description="Telegram group ID")
    is_connected: bool = Field(..., description="Is Connected to Company")


__all__ = ["GroupResponse", 'GroupListResponse']
