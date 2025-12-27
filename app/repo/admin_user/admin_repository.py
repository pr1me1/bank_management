import logging

from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.admin import AdminUser
from app.repo.base import BaseRepository

logger = logging.getLogger(__name__)


class AdminRepository(BaseRepository[AdminUser]):
    def __init__(self, db: Session):
        super().__init__(db, AdminUser)

    def get_admins(self):
        return self.db.query(AdminUser).filter(AdminUser.is_active == True).all()

    def check_admin(self, telegram_id: int):
        try:
            stmt = exists().where(AdminUser.telegram_id == str(telegram_id)).select()
            admin_exists = self.db.execute(stmt).scalar()
            logger.debug(f'admin exists: {admin_exists}')
            return bool(admin_exists)
        except Exception as e:
            self.db.rollback()
            logger.error(f"AdminRepository.check_admin error: {e}")
            return False

    def get_by_telegram_id(self, telegram_id: int) -> type[AdminUser] | None:
        return self.db.query(AdminUser).filter(AdminUser.telegram_id == str(telegram_id)).first()


__all__ = [
    'AdminRepository'
]
