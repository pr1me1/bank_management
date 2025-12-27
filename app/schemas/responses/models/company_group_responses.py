import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CompanyGroupResponse(BaseModel):
    """Schema for returning company group details."""
    id: uuid.UUID = Field(..., description="Company group ID")
    company_id: uuid.UUID = Field(..., description="Company ID")
    group_id: uuid.UUID = Field(..., description="Group ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


__all__ = ["CompanyGroupResponse"]
