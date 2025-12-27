import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    def __init__(self, ):
        self.APP_NAME = os.getenv("APP_NAME", "AIBA Bank")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

        self.TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

        self.KAPITALBANK_URL = os.getenv("KAPITALBANK_URL")
        self.IPAK_YULI_URL = os.getenv("IPAK_YULI_URL")

        self.HEADLESS = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")

        self.POSTGRES_DB = os.getenv("POSTGRES_DB")
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        self.POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", "10"))

        self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        self.REDIS_URL = os.getenv("REDIS_URL")
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_DB = os.getenv("REDIS_DB")
        self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        self.CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
        self.CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

        self.LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

        self.BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
        self.WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
        self.WEBHOOK_URL = f"{self.BASE_WEBHOOK_URL}{self.WEBHOOK_PATH}"
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")


        self.INN_CHECK_BASE_URL = os.getenv("INN_CHECK_BASE_URL", "https://gnk-api.didox.uz")
        self.INN_CHECK_INFO_ENDPOINT = os.getenv("INN_CHECK_INFO_ENDPOINT", "/api/v1/utils/info")

        self.ITEMS_PER_PAGE = 1
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "60"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.SECRET_KEY = os.getenv("SECRET_KEY")

        self.API_BASE_URL = os.getenv("API_BASE_URL")
        self.API_LOGIN_ENDPOINT = f"{self.API_BASE_URL}/auth/login"
        self.LOGIN_CODE_PREFIX = 'login_'
        self.LOGIN_CODE_TTL = 60


settings = Settings()

__all__ = [
    "settings"
]
