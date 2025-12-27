from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import UUIDBase, TimestampMixin


class AdminUser(UUIDBase, TimestampMixin):
    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    telegram_id: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    admin_actions: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="admin",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


__all__ = ['AdminUser']
