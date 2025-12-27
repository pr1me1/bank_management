import logging
from starlette import status
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from app.admin import AdminUser
from app.db import SessionLocal
from app.core.configs import settings

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get('password')

        db: Session = SessionLocal()
        try:
            user = db.query(AdminUser).filter(AdminUser.email == email).first()
            from app.utils import verify_password
            if not user or not verify_password(password, user.password_hash):
                logger.error(f"Login xatosi: {email}")
                return False

            if not user.is_active:
                logger.error(f"User aktiv emas: {email}")
                return False

            # Sessionga is_superuser ma'lumotini qo'shish shart
            request.session.update({
                'token': str(user.id),
                'email': user.email,
                'is_superuser': user.is_superuser  # BU QATORNI QO'SHING
            })

            logger.info(f"✅ Admin login: {email}")
            return True
        except Exception as e:
            logger.error(f"Admin login error: {e}")
            return False
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        email = request.session.get('email')
        request.session.clear()
        logger.info(f"✅ Admin logout: {email}")
        return True

    async def authenticate(self, request: Request) -> RedirectResponse | bool:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(url='/admin/login', status_code=status.HTTP_302_FOUND)

        db: Session = SessionLocal()

        try:
            admin = db.query(AdminUser).filter(AdminUser.id == token).first()

            if not admin:
                return RedirectResponse(url='/admin/login', status_code=status.HTTP_302_FOUND)

            return True
        except Exception as e:
            logger.error(f"Admin authenticate error: {e}")
            request.session.clear()
            return RedirectResponse(url='/admin/login', status_code=status.HTTP_302_FOUND)
        finally:
            db.close()


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
