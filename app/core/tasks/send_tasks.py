import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.types import BufferedInputFile
from celery.exceptions import Retry
from tornado.locale import load_gettext_translations

from app.bot.handlers.tx.balance_formatter import balance_formatter
from app.bot.handlers.tx.transaction_formatter import format_transactions
from app.core.celery import celery_app, async_task
from app.core.configs import settings
from app.db import get_db_session
from app.models import Language
from app.repo import CompanyRepository, BankAccountRepository, CompanyGroupRepository, TransactionRepository
from app.utils.transaction_excel import handle_daily_report

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_telegram_bot():
    bot_token = settings.BOT_TOKEN
    if not bot_token:
        raise RuntimeError("BOT_TOKEN not found in environment variables")

    bot = Bot(token=bot_token)
    try:
        yield bot
    finally:
        await bot.session.close()


async def send_message_to_company_groups(
        bot: Bot,
        company_groups: List,
        message_text: str,
        message_type: str = "message",
) -> int:
    if not company_groups:
        return 0

    sent_count = 0
    for company_group in company_groups:
        try:
            group = company_group.group
            await bot.send_message(
                chat_id=group.telegram_id,
                text=message_text,
                parse_mode="HTML"
            )
            sent_count += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(
                f"❌ Failed to send {message_type} to group {group.telegram_id} "
                f"({group.title}): {e}",
                exc_info=True
            )
    return sent_count


async def send_document_to_company_groups(
        bot: Bot,
        company_groups: List,
        file_bytes: bytes,
        filename: str,
        caption: str,
        company_name: str,
) -> int:
    if not company_groups:
        logger.warning(f"No groups found for company {company_name}")
        return 0

    sent_count = 0

    for company_group in company_groups:
        try:
            group = company_group.group

            file = BufferedInputFile(file=file_bytes, filename=filename)

            await bot.send_document(
                chat_id=group.telegram_id,
                document=file,
                caption=caption,
                parse_mode="HTML"
            )
            sent_count += 1
            logger.info(
                f"✅ Document sent to group {group.telegram_id} ({group.title}) "
                f"for company {company_name}"
            )

            await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(
                f"❌ Failed to send document to group {group.telegram_id} "
                f"({getattr(group, 'title', 'Unknown')}): {e}",
                exc_info=True
            )

    return sent_count


@celery_app.task(
    name="app.core.tasks.send_tasks.send_single_company",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
@async_task
async def send_single_company(self, company_id: str):
    try:
        with get_db_session() as db:
            company_repo = CompanyRepository(db)
            bank_account_repo = BankAccountRepository(db)
            company_group_repo = CompanyGroupRepository(db)
            transaction_repo = TransactionRepository(db)

            company_uuid = uuid.UUID(company_id)
            company = company_repo.get_by_id(company_uuid)
            if not company:
                raise ValueError(f"Company {company_id} not found")

            has_bank_account = company_repo.has_bank_accounts(company_uuid)
            if not has_bank_account:
                raise ValueError(f"Company with id: {company_id} doesn't have bank accounts")

            accounts = bank_account_repo.get_by_company_id(company_uuid)
            new_transactions = transaction_repo.get_by_accounts(accounts=[account.account_number for account in accounts], date_from=datetime.now() - timedelta(hours=5))
            if not new_transactions:
                logger.info(
                    "No transaction in last 5 hour"
                )
                return {
                    "success": True,
                    "company_id": str(company.id),
                    "company_name": company.name,
                    "message": "There is no transaction in last 5 hour",
                    "accounts_count": len(accounts),
                }
            accounts.sort(key=lambda account: account.bank_type, reverse=True)
            company_groups = company_group_repo.get_by_company_id(company.id)

            if not company_groups or not accounts:
                logger.info(
                    f"No groups or accounts for company {company.id} ({company.name})"
                )
                return {
                    "success": True,
                    "company_id": str(company.id),
                    "company_name": company.name,
                    "messages_sent": 0,
                    "accounts_count": len(accounts),
                }

            message_text = await balance_formatter(company.name, accounts)

            async with get_telegram_bot() as bot:
                await send_message_to_company_groups(
                    bot=bot,
                    company_groups=company_groups,
                    message_text=message_text,
                    message_type="balance",
                )

            logger.info(
                f"✅ Successfully processed company {company.id} ({company.name}). "
            )

            return {
                "success": True,
                "company_id": str(company.id),
                "company_name": company.name,
                "accounts_count": len(accounts),
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


@celery_app.task(name="app.core.tasks.send_tasks.send_all_companies")
@async_task
async def send_all_companies():
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
                    task = send_single_company.delay(str(company.id))
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
                f"✅ send_all_companies completed. "
                f"Total companies: {len(companies)}, Tasks dispatched: {len(task_ids)}"
            )

            return {
                "success": True,
                "total_companies": len(companies),
                "tasks_dispatched": len(task_ids),
                "task_ids": task_ids,
            }
    except Exception as e:
        logger.error(f"❌ Critical error in send_all_companies: {e}", exc_info=True)
        raise


@celery_app.task(
    name="app.core.tasks.send_tasks.send_single_company_transactions",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
@async_task
async def send_single_company_transactions(self, company_id: str):
    try:
        with get_db_session() as db:
            company_group_repo = CompanyGroupRepository(db)
            bank_account_repo = BankAccountRepository(db)
            transaction_repo = TransactionRepository(db)

            company_uuid = uuid.UUID(company_id)
            bank_accounts = bank_account_repo.get_by_company_id(company_uuid)
            logger.info(bank_accounts)

            if not bank_accounts:
                logger.info(f"Company with id: {company_id} doesn't have bank accounts")
                return {
                    "success": False,
                    "company_id": str(company_id),
                    "message": "Company doesn't have bank accounts",
                }

            timezone = ZoneInfo(settings.TIMEZONE)
            now = datetime.now(timezone)
            date_from = now - timedelta(hours=1)
            transactions = transaction_repo.get_by_accounts(
                accounts=[bank_account.account_number for bank_account in bank_accounts],
                date_from=date_from
            )
            if not transactions:
                logger.info(f"Company with id: {company_id} doesn't have bank transactions in last hour")
                return {
                    "success": False,
                    "company_id": str(company_id),
                    "message": "No new transactions found",
                }

            company_groups = company_group_repo.get_by_company_id(company_uuid)

            if not company_groups:
                logger.info(f"No groups associated with company {company_uuid}")
                return {
                    "success": False,
                    "company_id": str(company_id),
                    "message": "No groups associated with company",
                }
            formated_texts = format_transactions(transactions, lang=Language.RUSSIAN.value)

            async with get_telegram_bot() as bot:
                for message in formated_texts:
                    await send_message_to_company_groups(
                        bot=bot,
                        company_groups=company_groups,
                        message_text=message,
                    )

            logger.info(
                f"✅ Successfully processed transactions for company {company_uuid}. "
            )

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


@celery_app.task(name="app.core.tasks.send_tasks.send_all_company_transactions")
@async_task
async def send_all_company_transactions():
    try:
        with get_db_session() as db:
            company_repo = CompanyRepository(db)
            companies = company_repo.get_all(skip=0, limit=10000)

            if not companies:
                logger.info(f"No companies found")
                return {
                    "success": False,
                    "message": "No companies found",
                }

            task_ids = []

            for company in companies:
                try:
                    task = send_single_company_transactions.delay(str(company.id))
                    task_ids.append({
                        "company_id": str(company.id),
                        "company_name": company.name,
                        "task_id": task.id
                    })
                    logger.info(f"Task was settled for {company.name}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to dispatch transaction image task for company {company.id}: {e}",
                        exc_info=True
                    )

            logger.info(
                f"✅ send_all_company_transactions completed. "
                f"Total companies: {len(companies)}, Tasks dispatched: {len(task_ids)}"
            )

            return {
                "success": True,
                "total_companies": len(companies),
                "tasks_dispatched": len(task_ids),
                "task_ids": task_ids,
            }
    except Exception as e:
        logger.error(f"❌ Critical error in send_all_company_transactions: {e}", exc_info=True)
        raise


@celery_app.task(
    name="app.core.tasks.send_tasks.single_company_daily_report",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
@async_task
async def single_company_daily_report(self, company_id: str):
    try:
        with get_db_session() as db:
            company_repo = CompanyRepository(db)
            company_group_repo = CompanyGroupRepository(db)
            bank_account_repo = BankAccountRepository(db)

            company_uuid = uuid.UUID(company_id)
            company = company_repo.get_by_id(company_uuid)
            company_name = str(company.name)
            bank_accounts = bank_account_repo.get_by_company_id(company_uuid)

            if not bank_accounts:
                logger.info(f"Company with id: {company_id} doesn't have bank accounts")
                return {
                    "success": False,
                    "company_id": str(company_id),
                    "message": "Company doesn't have bank accounts",
                }

            report_result = await handle_daily_report(
                company_name=company_name,
                bank_accounts=bank_accounts,
                db=db,
            )
            company_groups = company_group_repo.get_by_company_id(company_uuid)

            if not company_groups:
                logger.info(f"Company with id: {company_id} doesn't have company groups")
                return {
                    "success": False,
                    "company_id": str(company_id),
                    "message": "Company doesn't have company groups",
                }

            timezone = ZoneInfo(settings.TIMEZONE)
            now = datetime.now(timezone)
            formatted_date = now.strftime("%d.%m.%Y")
            if report_result is None:
                logger.info(f"Report for company {company_id} was not created (no transactions)")
                message = (
                    f"📊 <b>Ежедневная выписка лицевых счетов</b>\n\n"
                    f"🏢 Компания: <b>{company_name}</b>\n"
                    f"📅 Дата: <b>{formatted_date}</b>\n"
                    f"🚫 Операций за день: <b>0</b>\n\n"
                    f"ℹ️ За указанную дату движения по счетам отсутствуют."
                )

                async with get_telegram_bot() as bot:
                    await send_message_to_company_groups(
                        bot=bot,
                        company_groups=company_groups,
                        message_text=message,
                    )
                return {
                    "success": True,
                    "company_id": str(company_id),
                    "message": f"Report for company {company_id} was not created - no transactions found. So message was sent.",
                }

            filepath, pdf_bytes, filename = report_result

            caption = (
                f"📊 <b>Ежедневная выписка лицевых счетов</b>\n\n"
                f"🏢 Компания: <b>{company_name}</b>\n"
                f"📅 Дата: <b>{formatted_date}</b>\n"
                f"💳 Счетов: <b>{len(bank_accounts)}</b>"
            )

            async with get_telegram_bot() as bot:
                sent_count = await send_document_to_company_groups(
                    bot=bot,
                    company_groups=company_groups,
                    file_bytes=pdf_bytes,
                    filename=filename,
                    caption=caption,
                    company_name=company_name,
                )

            try:
                Path(filepath).unlink()
                logger.info(f"Cleaned up PDF file: {filepath}")
            except Exception as e:
                logger.error(f"Failed to delete PDF {filepath}: {e}")

            logger.info(
                f"✅ Daily report for company {company_name} sent to {sent_count} groups"
            )

            return {
                "success": True,
                "company_id": str(company_id),
                "company_name": company_name,
                "sent_to_groups": sent_count,
                "filename": filename,
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


@celery_app.task(name="app.core.tasks.send_tasks.send_daily_reports")
@async_task
async def send_daily_reports():
    try:
        with get_db_session() as db:
            company_repo = CompanyRepository(db)
            companies = company_repo.get_all(skip=0, limit=10000)

            if not companies:
                logger.info(f"No companies found")
                return {
                    "success": False,
                    "message": "No companies found",
                }

            task_ids = []

            for company in companies:
                try:
                    task = single_company_daily_report.delay(str(company.id))
                    task_ids.append({
                        "company_id": str(company.id),
                        "company_name": company.name,
                        "task_id": task.id
                    })
                    logger.info(f"Task was settled for {company.name}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to dispatch transaction image task for company {company.id}: {e}",
                        exc_info=True
                    )

            logger.info(
                f"✅ send_all_company_transactions completed. "
                f"Total companies: {len(companies)}, Tasks dispatched: {len(task_ids)}"
            )

            return {
                "success": True,
                "total_companies": len(companies),
                "tasks_dispatched": len(task_ids),
                "task_ids": task_ids,
            }
    except Exception as e:
        logger.error(f"❌ Critical error in send_all_company_transactions: {e}", exc_info=True)
        raise
