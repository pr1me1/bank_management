import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class BankAccountResponse(BaseModel):
    """Schema for returning bank account details."""
    id: uuid.UUID = Field(..., description="Bank account ID")
    bank_type: str = Field(..., description="Bank type")
    currency: str = Field(..., description="Currency code")
    balance: float = Field(..., description="Account balance")
    account_number: str = Field(..., description="Account number")
    mfo: str = Field(..., description="MFO")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class BankAccountListResponse(BaseModel):
    """List of bank accounts."""
    id: uuid.UUID = Field(..., description="Bank account ID")
    bank_type: str = Field(..., max_length=64, description="Bank type")
    balance: float = Field(default=0.0, ge=0, description="Account balance")
    currency: str = Field(..., max_length=10, description="Currency code")
    account_number: str = Field(..., description="Account number")

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "BankAccountResponse",
    "BankAccountListResponse"
]
