import uuid
from pydantic import BaseModel, Field

from app.models.transaction.transaction_user import UserRole


class TransactionUserCreate(BaseModel):
    """Schema for assigning a user to a transaction."""
    user_id: uuid.UUID = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role in transaction")


__all__ = ["TransactionUserCreate"]
