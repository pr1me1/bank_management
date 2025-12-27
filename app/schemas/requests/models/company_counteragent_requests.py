import uuid
from typing import Optional

from pydantic import BaseModel, Field


class CompanyCounteragentBase(BaseModel):
    """Base schema for CompanyCounteragent."""
    counteragent_name: str = Field(..., max_length=255, description="Counteragent name")
    counteragent_inn: str = Field(..., max_length=20, description="Counteragent INN")
    counteragent_hr: str = Field(..., max_length=50, description="Counteragent HR")
    counteragent_mfo: str = Field(..., max_length=20, description="Counteragent MFO")
    title: Optional[str] = Field(None, max_length=100, description="Title/alias")


class CompanyCounteragentCreate(CompanyCounteragentBase):
    """Schema for creating a new company counteragent."""
    company_id: uuid.UUID = Field(..., description="Company ID")
    counteragent_id: Optional[uuid.UUID] = Field(None, description="Linked company ID (if exists)")


class CompanyCounteragentUpdate(BaseModel):
    """Schema for updating a company counteragent."""
    counteragent_name: Optional[str] = Field(None, max_length=255)
    counteragent_inn: Optional[str] = Field(None, max_length=20)
    counteragent_hr: Optional[str] = Field(None, max_length=50)
    counteragent_mfo: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=100)
    counteragent_id: Optional[uuid.UUID] = Field(None)


__all__ = [
    'CompanyCounteragentCreate',
    'CompanyCounteragentUpdate',
    'CompanyCounteragentBase'
]
