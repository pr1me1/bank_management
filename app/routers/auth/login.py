import logging

from fastapi import Depends
from jose import jwt
from starlette.requests import Request
from fastapi import APIRouter, HTTPException, status

from app import utils
from app.schemas import responses
from app.repo import AdminRepository
from app.core.configs import settings
from app.core.rate_limiter import limiter
from app.services import get_login_code_cache
from app.dependencies import get_admin_repository
from app.schemas import LoginRequest, RefreshTokenRequest

router = APIRouter(
    tags=["login"],
    prefix="/login",
)
logger = logging.getLogger(__name__)


@router.post("", response_model=responses.AccessTokenResponse)
@limiter.limit("3/minute")
async def auth(
        request: Request,
        data: LoginRequest,
        admin_repo: AdminRepository = Depends(get_admin_repository)
):
    try:
        cache = get_login_code_cache()
        telegram_id = cache.verify_code(data.otp)
        logger.debug(f"Telegram ID: {telegram_id} | Code: {data.otp}, {type(telegram_id)}")

        if telegram_id is None:
            logger.warning(f"❌ Invalid or expired code: {data.otp}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired code"
            )

        if not admin_repo.check_admin(telegram_id):
            logger.warning(f"❌ Access denied for telegram_id: {telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied"
            )

        access_token = utils.create_access_token(telegram_id)
        refresh_token = utils.create_refresh_token(telegram_id)

        cache.delete_code(data.otp)

        logger.info(f"✅ Login successful | Telegram ID: {telegram_id} | Code: {data.otp}")

        return responses.AccessTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh", response_model=responses.RefreshTokenResponse)
async def refresh_token_endpoint(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        telegram_id = payload.get("sub")
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )

        new_access_token = utils.create_access_token(telegram_id)

        return responses.RefreshTokenResponse(
            access_token=new_access_token
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate token: {str(e)}"
        )


__all__ = [
    "router",
]
