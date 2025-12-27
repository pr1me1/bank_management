import uuid
from pydantic import BaseModel, Field


class CompanyGroupCreate(BaseModel):
    """Schema for linking a company to a group."""
    company_id: uuid.UUID = Field(..., description="Company ID")
    group_id: uuid.UUID = Field(..., description="Group ID")


__all__ = [
    'CompanyGroupCreate',
]
