import asyncio
import logging
from sqlite3 import DatabaseError, OperationalError

from billiard.exceptions import SoftTimeLimitExceeded
from celery.exceptions import Retry

from app.core.celery import celery_app, async_task
from app.db import get_db_session
from app.repo import AuditLogRepository

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.core.tasks.delete_logs.delete_old_logs",
    bind=True,
    max_retries=3,
    soft_time_limit=300,
    time_limit=360
)
@async_task
async def delete_old_logs(self, days: int = 30, batch_size: int = 1000):
    total_deleted = 0
    try:

        with get_db_session() as db:
            log_repo = AuditLogRepository(db)

            while True:
                count = log_repo.delete_old_logs(days=days, batch_size=batch_size)
                total_deleted += count

                if count < batch_size:
                    break

                logger.info(f"Deleted {count} logs in current batch. Total: {total_deleted}")

                await asyncio.sleep(0.1)

            logger.info(f"Successfully deleted {total_deleted} old audit logs")

            return {
                "success": True,
                "logs_deleted": total_deleted,
                "days_retained": days,
            }

    except SoftTimeLimitExceeded:
        logger.warning(f"Task soft time limit exceeded. Deleted {total_deleted} logs before timeout.")
        return {
            "success": False,
            "logs_deleted": total_deleted,
            "error": "Task timeout - partial deletion completed"
        }
    except Retry:
        raise
    except (OperationalError, DatabaseError) as e:
        logger.error(f"Database error in delete_old_logs: {e}", exc_info=True)
        raise self.retry(
            exc=e,
            countdown=min(60 * (2 ** self.request.retries), 3600),
            max_retries=3
        )
    except Exception as e:
        logger.error(f"Unexpected error in delete_old_logs: {e}", exc_info=True)
        raise self.retry(
            exc=e,
            countdown=min(60 * (2 ** self.request.retries), 3600),
            max_retries=3
        )
