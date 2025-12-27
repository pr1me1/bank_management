import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CompanyCounteragentResponse(BaseModel):
    """Schema for returning company counteragent details."""
    id: uuid.UUID = Field(..., description="Company counteragent ID")
    company_id: uuid.UUID = Field(..., description="Company ID")
    counteragent_id: Optional[uuid.UUID] = Field(None, description="Linked company ID")
    counteragent_name: str = Field(..., description="Counteragent name")
    counteragent_inn: str = Field(..., description="Counteragent INN")
    counteragent_hr: str = Field(..., description="Counteragent HR")
    counteragent_mfo: str = Field(..., description="Counteragent MFO")
    title: Optional[str] = Field(None, description="Title/alias")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


__all__ = ["CompanyCounteragentResponse"]
