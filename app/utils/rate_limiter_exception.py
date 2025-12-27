from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests", "detail": str(exc.detail)},
    )


__all__ = [
    "rate_limit_handler"
]