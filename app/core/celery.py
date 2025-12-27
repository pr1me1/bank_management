import asyncio
import logging
from functools import wraps

from celery import Celery
from celery.signals import worker_process_init

from app.core.configs import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "aiba-bank",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.core.tasks.fetch_tasks",
        "app.core.tasks.send_tasks",
        "app.core.tasks.delete_logs",
    ],
)

try:
    from app.core import beat_schedule
except ImportError:
    logger.warning("Could not import beat_schedule. Scheduled tasks may not be configured.")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    worker_send_task_events=True,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
    result_expires=6 * 3600,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@worker_process_init.connect
def init_worker(**kwargs):
    from app.utils.translations import initialize_translator, MESSAGES
    initialize_translator(MESSAGES)
    logger.info("Translator initialized in Celery worker")


def async_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


celery_app.autodiscover_tasks([
    'app.core.tasks.fetch_tasks',
    'app.core.tasks.send_tasks',
    'app.core.tasks.delete_logs',
], force=True)
