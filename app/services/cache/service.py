import random
import string
import logging
from typing import Optional

from app.core.configs import settings
from app.core.redis import get_redis_client

logger = logging.Logger(__name__)


class LoginCodeCache:

    def __init__(self):
        self.redis_client = get_redis_client()

    @staticmethod
    def generate_code() -> str:
        return "".join(random.choices(string.digits, k=6))

    def get_or_create_code(self, telegram_id: int) -> tuple[str, bool]:
        try:
            existing_code = self._find_existing_code(telegram_id)

            if existing_code:
                logger.info(f"Telegram ID {telegram_id} uchun mavjud kod topildi.")
                return existing_code, False

            code = self.generate_code()
            key = f"{settings.LOGIN_CODE_PREFIX}{code}"

            self.redis_client.setex(
                name=key,
                time=settings.LOGIN_CODE_TTL,
                value=str(telegram_id)
            )

            logger.info(f"Yangi kod yaratildi: {code} -> Telegram ID: {telegram_id}")
            return code, True
        except Exception as e:
            logger.error(f"Kod yaratishda xatolik: {e}")
            raise

    def _find_existing_code(self, telegram_id: int) -> Optional[str]:
        try:
            pattern = f"{settings.LOGIN_CODE_PREFIX}*"
            keys = self.redis_client.keys(pattern)

            for key in keys:
                stored_telegram_id = self.redis_client.get(key)
                if stored_telegram_id == str(telegram_id):
                    code = key.replace(settings.LOGIN_CODE_PREFIX, "")
                    return code
            return None
        except Exception as e:
            logger.error(f"Mavjud kodni topishda xatolik: {e}")
            return None

    def verify_code(self, code: str) -> Optional[int]:
        try:
            key = f"{settings.LOGIN_CODE_PREFIX}{code}"
            telegram_id = self.redis_client.get(key)

            if telegram_id:
                logger.info(f"Kod tasdiqlandi: {code} -> Telegram ID: {telegram_id}")
                return int(telegram_id)

            logger.warning(f"Kod topilmadi yoki muddati o'tgan: {code}")
            return None

        except Exception as e:
            logger.error(f"Kodni tekshirishda xatolik: {e}")
            return None

    def delete_code(self, code: str) -> bool:
        try:
            key = f"{settings.LOGIN_CODE_PREFIX}{code}"
            result = self.redis_client.delete(key)

            if result:
                logger.info(f"Kod o'chirildi: {code}")
                return True
            return False
        except Exception as e:
            logger.error(f"Kodni o'chirishda xatolik: {e}")
            return False

    def get_code_ttl(self, code: str) -> Optional[int]:
        try:
            key = f"{settings.LOGIN_CODE_PREFIX}{code}"
            ttl = self.redis_client.ttl(key)

            if ttl > 0:
                return ttl
            return None
        except Exception as e:
            logger.error(f"TTL olishda xatolik: {e}")
            return None


_login_code_cache = None


def get_login_code_cache() -> LoginCodeCache:
    global _login_code_cache

    if _login_code_cache is None:
        _login_code_cache = LoginCodeCache()

    return _login_code_cache


__all__ = [
    "get_login_code_cache",
]
