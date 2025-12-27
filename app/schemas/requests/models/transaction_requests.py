from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.transaction.transaction import TransactionStatus


class TransactionBase(BaseModel):
    """Base schema for Transaction with all fields optional to support draft creation."""
    receiver_name: Optional[str] = Field(None, max_length=255, description="Receiver name")
    receiver_inn: Optional[str] = Field(None, max_length=20, description="Receiver INN")
    receiver_account: Optional[str] = Field(None, max_length=50, description="Receiver account number")
    receiver_bank_code: Optional[str] = Field(None, max_length=10, description="Receiver bank MFO code")
    sender_name: Optional[str] = Field(None, max_length=255, description="Sender name")
    sender_inn: Optional[str] = Field(None, max_length=20, description="Sender INN")
    sender_account: Optional[str] = Field(None, max_length=50, description="Sender account number")
    sender_bank_code: Optional[str] = Field(None, max_length=10, description="Sender bank MFO code")
    payment_amount: Optional[float] = Field(default=0.0, ge=0, description="Payment amount (must be >= 0)")
    currency: Optional[str] = Field(default="UZS", max_length=3, description="Currency code")
    payment_description: Optional[str] = Field(None, max_length=500, description="Payment description/notes")
    payment_purpose_code: Optional[str] = Field(None, max_length=5, description="Payment purpose code (5 digits)")
    contract_number: Optional[str] = Field(None, max_length=50, description="Contract number")

    @field_validator('payment_amount', mode='before')
    @classmethod
    def validate_amount(cls, v):
        """Ensure payment_amount is a valid float, defaults to 0.0 if None is provided."""
        if v is None:
            return 0.0
        return float(v)


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction. Status is automatically determined."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction. Only provided fields will be updated."""
    receiver_name: Optional[str] = Field(None, max_length=255, description="Receiver name")
    receiver_inn: Optional[str] = Field(None, max_length=20, description="Receiver INN")
    receiver_account: Optional[str] = Field(None, max_length=50, description="Receiver account number")
    receiver_bank_code: Optional[str] = Field(None, max_length=10, description="Receiver bank MFO code")
    sender_name: Optional[str] = Field(None, max_length=255, description="Sender name")
    sender_inn: Optional[str] = Field(None, max_length=20, description="Sender INN")
    sender_account: Optional[str] = Field(None, max_length=50, description="Sender account number")
    sender_bank_code: Optional[str] = Field(None, max_length=10, description="Sender bank MFO code")
    payment_amount: Optional[float] = Field(None, ge=0, description="Payment amount (must be >= 0)")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    payment_description: Optional[str] = Field(None, max_length=500, description="Payment description/notes")
    payment_purpose_code: Optional[str] = Field(None, max_length=5, description="Payment purpose code (5 digits)")
    contract_number: Optional[str] = Field(None, max_length=50, description="Contract number")
    status: Optional[TransactionStatus] = Field(None, description="Manually set transaction status")

    @field_validator('payment_amount', mode='before')
    @classmethod
    def validate_amount(cls, v):
        """Ensure payment_amount is a valid float, or None if not provided."""
        if v is None:
            return None
        return float(v)


__all__ = [
    'TransactionBase',
    'TransactionCreate',
    'TransactionUpdate',
]
