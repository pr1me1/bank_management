import uuid

from pydantic import BaseModel


class KapitalBase(BaseModel):
    company_id: uuid.UUID


class KapitalAuthRequest(KapitalBase):
    login: str
    password: str


class KapitalConfirmOtpRequest(KapitalBase):
    session_id: str
    code: str


__all__ = [
    'KapitalAuthRequest',
    'KapitalConfirmOtpRequest',
    'KapitalBase'
]
