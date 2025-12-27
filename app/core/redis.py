import redis
import logging

from app.core.configs import settings

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis_client():
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )

            _redis_client.ping()
            logger.info("✅ Redis connected successfully")

        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            _redis_client = None
            raise ConnectionError(
                f"Redis is not available. Error: {e}\n"
                f"Please start Redis service and check REDIS_URL: {settings.REDIS_URL}"
            )

    return _redis_client


__all__ = ["get_redis_client"]
