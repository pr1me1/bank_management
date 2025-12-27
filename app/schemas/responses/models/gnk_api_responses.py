from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict


class GNKCompanyInfoResponse(BaseModel):
    """Schema for GNK API company information response."""

    data: dict[str, Any] = Field(..., description="Company information from GNK API")
    inn: str = Field(..., description="INN/TAX_ID used for the query")
    success: bool = Field(True, description="Whether the request was successful")

    model_config = ConfigDict(from_attributes=True)


class GNKErrorResponse(BaseModel):
    """Schema for GNK API error response."""
    success: bool = Field(False, description="Request was not successful")
    error: str = Field(..., description="Error message")
    inn: Optional[str] = Field(None, description="INN/TAX_ID that caused the error")

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "GNKCompanyInfoResponse",
    "GNKErrorResponse",
]
