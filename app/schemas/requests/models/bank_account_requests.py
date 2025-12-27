from pydantic import BaseModel, Field


class BankAccountBase(BaseModel):
    """Base schema for BankAccount."""
    bank_type: str = Field(..., max_length=64, description="Bank type")
    currency: str = Field(..., max_length=10, description="Currency code")
    balance: float = Field(default=0.0, ge=0, description="Account balance")
    mfo_number: str = Field(..., max_length=20, description="MFO number")


class BankAccountCreate(BankAccountBase):
    """Schema for creating a new bank account."""
    pass


__all__ = [
    'BankAccountBase',
    'BankAccountCreate',
]
