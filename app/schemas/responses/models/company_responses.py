import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CompanyResponse(BaseModel):
    """Schema for returning company details."""
    id: uuid.UUID = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    inn: str = Field(..., description="Company INN")
    director_name: str = Field(..., description="Director name")
    is_connected: bool = Field(..., description="Company is connected")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    """Schema for returning company details ion list."""
    id: uuid.UUID = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    director_name: str = Field(..., description="Director name")
    inn: str = Field(..., description="Company INN")

    model_config = ConfigDict(from_attributes=True)


class CompanyGroupDetailResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Group ID")
    title: str = Field(..., description="Group name")


__all__ = [
    "CompanyResponse",
    "CompanyListResponse",
    "CompanyGroupDetailResponse"
]
