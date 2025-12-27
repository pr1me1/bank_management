from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.admin import AdminUser
from app.models import Actions, User
from app.models.log import AuditLog
from app.repo.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(db, AuditLog)

    def create(
            self,
            action: Actions,
            user: Optional[User] = None,
            admin: Optional[AdminUser] = None,
            payload: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        return super().create(
            user_id=user.id if user else None,
            admin_id=admin.id if admin else None,
            action=action.name.value,
            category=action.category,
            payload=payload,
        )

    def get_recent_logs(self, limit: int = 100) -> list[type[AuditLog]]:
        return self.db.query(AuditLog).order_by(
            desc(AuditLog.created_at)
        ).limit(limit).all()

    def get_by_action(self, action: Actions, limit: int = 100) -> list[type[AuditLog]]:
        return self.db.query(AuditLog).filter(
            AuditLog.action == action.name.value,
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()

    def delete_old_logs(self, days: int = 30, batch_size: int = 1000) -> int:
        cutoff_date = datetime.now() - timedelta(days=days)

        log_ids = self.db.query(AuditLog.id).filter(
            AuditLog.created_at < cutoff_date
        ).limit(batch_size).all()

        if not log_ids:
            return 0

        ids_to_delete = [log_id[0] for log_id in log_ids]

        deleted = self.db.query(AuditLog).filter(
            AuditLog.id.in_(ids_to_delete)
        ).delete(synchronize_session=False)

        self.db.commit()

        return deleted

    def get_by_date_range(
            self,
            date_from: datetime,
            date_to: datetime,
            limit: int = 100
    ) -> list[type[AuditLog]]:
        return self.db.query(AuditLog).filter(
            AuditLog.created_at >= date_from,
            AuditLog.created_at <= date_to
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()


__all__ = ["AuditLogRepository"]
