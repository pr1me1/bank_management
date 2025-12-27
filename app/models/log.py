from typing import Optional, Any
from uuid import UUID

from sqlalchemy import String, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.abstract import TimestampMixin, UUIDBase
from app.models.enums import ActionCategory


class AuditLog(UUIDBase, TimestampMixin):
    __tablename__ = "audit_logs"

    admin_id: Mapped[UUID] = mapped_column(
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        nullable=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )
    category: Mapped[ActionCategory] = mapped_column(
        SQLEnum(ActionCategory, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="user_actions", lazy="selectin"
    )

    admin: Mapped["AdminUser"] = relationship(
        "AdminUser", back_populates="admin_actions", lazy="selectin"
    )

    def __str__(self) -> str:
        return f"{self.action} at {self.created_at}"

    def __repr__(self):
        return f"<AuditLog id={self.id} action={self.action}>"
