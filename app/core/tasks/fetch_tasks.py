import logging
import uuid

from celery.exceptions import Retry

from app.core.celery import celery_app, async_task
from app.db import get_db_session
from app.repo import CompanyRepository
from app.services import Kapitalbank

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.core.tasks.fetch_tasks.sync_single_company_accounts",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
@async_task
async def sync_single_company_accounts(self, company_id: str):
    try:
        with get_db_session() as db:
            company_uuid = uuid.UUID(company_id)
            service = Kapitalbank(company_uuid, db=db)
            await service.accounts()

            logger.info(f"✅ Successfully synced accounts for company {company_id}")

            return {
                "success": True,
                "company_id": company_id,
            }
    except Retry:
        raise
    except ValueError as e:
        logger.error(f"ValueError for company {company_id}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error processing company {company_id}: {e}", exc_info=True)
        if hasattr(self, 'retry'):
            raise self.retry(
                exc=e,
                countdown=60 * (2 ** self.request.retries),
            )
        raise


@celery_app.task(name="app.core.tasks.fetch_tasks.sync_accounts")
@async_task
async def sync_accounts():
    try:
        with get_db_session() as db:
            company_repo = CompanyRepository(db)
            companies = company_repo.get_all(skip=0, limit=10000)

            if not companies:
                logger.warning("No companies found to process")
                return {
                    "success": True,
                    "total_companies": 0,
                    "tasks_dispatched": 0,
                    "task_ids": [],
                }

            task_ids = []
            for company in companies:
                try:
                    task = sync_single_company_accounts.delay(str(company.id))
                    task_ids.append({
                        "company_id": str(company.id),
                        "company_name": company.name,
                        "task_id": task.id,
                    })
                    logger.info(f"📤 Dispatched task for company {company.id} ({company.name}): {task.id}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to dispatch task for company {company.id}: {e}",
                        exc_info=True
                    )

            logger.info(
                f"✅ sync_accounts completed. "
                f"Total companies: {len(companies)}, Tasks dispatched: {len(task_ids)}"
            )

            return {
                "success": True,
                "total_companies": len(companies),
                "tasks_dispatched": len(task_ids),
                "task_ids": task_ids,
            }
    except Exception as e:
        logger.error(f"❌ Critical error in sync_accounts: {e}", exc_info=True)
        raise


@celery_app.task(
    name="app.core.tasks.fetch_tasks.sync_single_company_transactions",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
@async_task
async def sync_single_company_transactions(self, company_id: str):
    try:
        with get_db_session() as db:
            company_uuid = uuid.UUID(company_id)
            service = Kapitalbank(company_uuid, db=db)
            await service.transactions()

            logger.info(f"✅ Successfully synced transactions for company {company_id}")

            return {
                "success": True,
                "company_id": company_id,
            }
    except Retry:
        raise
    except ValueError as e:
        logger.error(f"ValueError for company {company_id}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error processing company {company_id}: {e}", exc_info=True)
        if hasattr(self, 'retry'):
            raise self.retry(
                exc=e,
                countdown=60 * (2 ** self.request.retries),
            )
        raise


@celery_app.task(name="app.core.tasks.fetch_tasks.sync_transactions")
@async_task
async def sync_transactions():
    try:
        with get_db_session() as db:
            company_repo = CompanyRepository(db)
            companies = company_repo.get_all(skip=0, limit=10000)

            if not companies:
                logger.warning("No companies found to process")
                return {
                    "success": True,
                    "total_companies": 0,
                    "tasks_dispatched": 0,
                    "task_ids": [],
                }

            task_ids = []
            for company in companies:
                try:
                    task = sync_single_company_transactions.delay(str(company.id))
                    task_ids.append({
                        "company_id": str(company.id),
                        "company_name": company.name,
                        "task_id": task.id,
                    })
                    logger.info(f"📤 Dispatched transaction task for company {company.id} ({company.name}): {task.id}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to dispatch task for company {company.id}: {e}",
                        exc_info=True
                    )

            logger.info(
                f"✅ sync_transactions completed. "
                f"Total companies: {len(companies)}, Tasks dispatched: {len(task_ids)}"
            )

            return {
                "success": True,
                "total_companies": len(companies),
                "tasks_dispatched": len(task_ids),
                "task_ids": task_ids,
            }
    except Exception as e:
        logger.error(f"❌ Critical error in sync_transactions: {e}", exc_info=True)
        raise