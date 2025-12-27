import uuid
from pydantic import BaseModel, Field


class CompanyBankAccountCreate(BaseModel):
    """Schema for linking a bank account to a company."""
    company_id: uuid.UUID = Field(..., description="Company ID")
    bank_account_id: uuid.UUID = Field(..., description="Bank account ID")


__all__ = [
    'CompanyBankAccountCreate',
]
