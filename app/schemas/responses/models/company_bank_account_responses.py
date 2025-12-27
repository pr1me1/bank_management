import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CompanyBankAccountResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Company bank account ID")
    company_id: uuid.UUID = Field(..., description="Company ID")
    bank_account_id: uuid.UUID = Field(..., description="Bank account ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class CompanyListBankAccountResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Company bank account ID")
    company_id: uuid.UUID = Field(..., description="Company ID")
    bank_account_id: uuid.UUID = Field(..., description="Bank account ID")

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "CompanyBankAccountResponse",
    'CompanyListBankAccountResponse'
]
