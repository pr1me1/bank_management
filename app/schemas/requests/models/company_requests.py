from typing import Optional

from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """Base schema for Company."""
    inn: str = Field(..., max_length=20, description="Company INN")
    name: Optional[str] = Field(None, max_length=255, description="Company name")
    director_name: Optional[str] = Field(None, max_length=255, description="Director name")


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    inn: str = Field(..., max_length=20, description="Company INN")


__all__ = [
    'CompanyBase',
    'CompanyCreate',
    'CompanyUpdate',
]
