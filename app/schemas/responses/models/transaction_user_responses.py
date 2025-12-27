import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.models.transaction.transaction_user import UserRole


class TransactionUserResponse(BaseModel):
    """Schema for returning transaction user details."""
    id: uuid.UUID = Field(..., description="Transaction user ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    transaction_id: uuid.UUID = Field(..., description="Transaction ID")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


__all__ = ['TransactionUserResponse']
