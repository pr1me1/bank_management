import uuid
from typing import List

from pydantic import BaseModel, Field

from app.models.transaction.transaction import TransactionStatus


class ErrorResponse(BaseModel):
    """Standard error response schema (e.g., for 404 Not Found)"""
    detail: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Transaction not found"
            }
        }


class MissingFieldsResponse(BaseModel):
    """
    Response schema showing which required fields are missing.
    Used to help users understand what's needed to complete a draft.
    """
    transaction_id: uuid.UUID = Field(..., description="Transaction ID")
    status: TransactionStatus = Field(..., description="Current transaction status")
    missing_fields: List[str] = Field(..., description="List of missing required field names")
    message: str = Field(..., description="Human-readable message about missing fields")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "draft",
                "missing_fields": [
                    "document_number",
                    "receiver_inn",
                    "receiver_account",
                    "bank_code"
                ],
                "message": "Transaction has 4 missing required field(s)"
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response schema (e.g., for 400 Bad Request)"""
    detail: dict = Field(..., description="Validation error details")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": {
                    "message": "Cannot complete transaction. Missing required fields.",
                    "missing_fields": ["document_date"]
                }
            }
        }


__all__ = [
    "ErrorResponse",
    "MissingFieldsResponse",
    "ValidationErrorResponse"
]
