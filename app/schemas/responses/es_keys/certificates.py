from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class CertificateResponse(BaseModel):
    id: str
    username: str
    certificate_name: str
    alias: Optional[str] = None
    inn: str
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    has_password: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CertificateDetailResponse(CertificateResponse):
    pkcs7: str

    class Config:
        from_attributes = True


__all__ = [
    "CertificateResponse",
    "CertificateDetailResponse",
]
