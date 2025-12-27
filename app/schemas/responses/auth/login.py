from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenResponse(BaseModel):
    access_token: str


__all__ = ["AccessTokenResponse", "RefreshTokenResponse"]
