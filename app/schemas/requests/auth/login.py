from pydantic import BaseModel


class LoginRequest(BaseModel):
    otp: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


__all__ = [
    "LoginRequest",
    "RefreshTokenRequest",
]
