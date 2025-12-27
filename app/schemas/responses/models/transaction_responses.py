import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models import ActionCategory
from app.models.transaction.transaction import TransactionStatus


class TransactionResponse(BaseModel):
    """Schema for returning transaction details."""
    id: uuid.UUID = Field(..., description="Transaction ID")
    receiver_name: Optional[str] = Field(None, description="Receiver name")
    receiver_inn: Optional[str] = Field(None, description="Receiver INN")
    receiver_account: Optional[str] = Field(None, description="Receiver account number")
    sender_name: Optional[str] = Field(None, description="Sender name")
    sender_inn: Optional[str] = Field(None, description="Sender INN")
    sender_account: Optional[str] = Field(None, description="Sender account number")
    bank_code: Optional[str] = Field(None, description="Bank MFO code")
    payment_amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Currency code")
    payment_description: Optional[str] = Field(None, description="Payment description/notes")
    contract_number: Optional[str] = Field(None, description="Contract number")
    status: TransactionStatus = Field(..., description="Transaction status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "receiver_name": "ABC Company",
            "receiver_inn": "123456789",
            "receiver_account": "ACC123",
            "sender_name": "XYZ Corp",
            "sender_inn": "987654321",
            "sender_account": "ACC456",
            "bank_code": "00001",
            "payment_amount": 1000.00,
            "currency": "UZS",
            "payment_description": "Payment for services",
            "contract_number": "CNT001",
            "status": "filled",
            "created_at": "2025-01-16T10:30:00",
            "updated_at": "2025-01-16T10:30:00"
        }
    })


class TransactionListResponse(BaseModel):
    """Simplified transaction schema for listing multiple transactions."""
    id: uuid.UUID = Field(..., description="Transaction ID")
    receiver_name: Optional[str] = Field(None, description="Receiver name")
    payment_amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Currency code")
    status: TransactionStatus = Field(..., description="Transaction status")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "receiver_name": "ABC Company",
            "payment_amount": 1000.00,
            "currency": "UZS",
            "status": "filled",
            "created_at": "2025-01-16T10:30:00"
        }
    })


class MissingFieldsResponse(BaseModel):
    """Schema for informing about missing required fields."""
    transaction_id: uuid.UUID = Field(..., description="Transaction ID")
    status: TransactionStatus = Field(..., description="Current transaction status")
    missing_fields: list[str] = Field(..., description="List of required fields that are currently missing")
    message: str = Field(..., description="Summary message about the status")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "unfilled",
            "missing_fields": ["receiver_inn", "bank_code"],
            "message": "Transaction has 2 missing required field(s)"
        }
    })


class AuditLogResponse(BaseModel):
    """Schema for returning audit log entries."""
    id: uuid.UUID = Field(..., description="Audit log ID")
    user_id: uuid.UUID = Field(..., description="The ID of the user who performed the action")
    category: ActionCategory = Field(..., description="Category of the action")
    action: str = Field(..., description="Action performed (e.g., 'created_otp', 'logged_in', 'company_create')")
    payload: Optional[dict] = Field(None, description="Detailed JSON payload of the changes")
    created_at: datetime = Field(..., description="Log creation timestamp")

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "123e4567-e89b-12d3-a456-426614174001",
            "category": "web",
            "action": "company_create",
            "payload": {"company_name": "ABC Company", "registration_number": "12345"},
            "created_at": "2025-01-16T10:30:00"
        }
    })


class TransactionStatsResponse(BaseModel):
    """Response schema for transaction statistics."""
    total_transactions: int = Field(..., description="Total number of transactions")
    draft_transactions: int = Field(..., description="Number of draft transactions")
    completed_transactions: int = Field(..., description="Number of completed transactions")
    draft_percentage: float = Field(..., description="Percentage of drafts")
    completed_percentage: float = Field(..., description="Percentage of completed")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_transactions": 100,
            "draft_transactions": 25,
            "completed_transactions": 75,
            "draft_percentage": 25.0,
            "completed_percentage": 75.0
        }
    })


__all__ = [
    "TransactionResponse",
    "TransactionListResponse",
    "MissingFieldsResponse",
    "AuditLogResponse",
    "TransactionStatsResponse"
]
