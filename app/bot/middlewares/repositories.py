from typing import Callable, Any, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app import repo
from app.db import SessionLocal
from app.repo.admin_user.admin_repository import AdminRepository


class RepositoryMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[None]],
            event: TelegramObject,
            data: Dict[str, Any]
    ):
        db = SessionLocal()
        try:
            data["user_repo"] = repo.UserRepository(db)
            data['group_repo'] = repo.GroupRepository(db)
            data['log_repo'] = repo.AuditLogRepository(db)
            data['company_repo'] = repo.CompanyRepository(db)
            data['group_user_repo'] = repo.GroupUserRepository(db)
            data['bank_account_repo'] = repo.BankAccountRepository(db)
            data['company_group_repo'] = repo.CompanyGroupRepository(db)
            data['admin_repo'] = AdminRepository(db)
            return await handler(event, data)
        finally:
            db.close()


__all__ = [
    'RepositoryMiddleware'
]
