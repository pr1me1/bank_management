import uuid

from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import UUIDBase, TimestampMixin
from app.models.enums import UserRole


class TransactionUser(UUIDBase, TimestampMixin):
    __tablename__ = "transaction_users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="transaction_role"),
        nullable=False,
        default=UserRole.CLIENT
    )

    user_relation: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
        lazy="joined"
    )
    transaction: Mapped["Transaction"] = relationship(
        "Transaction",
        back_populates="transaction_users",
        lazy="joined"
    )

    def __str__(self) -> str:
        try:
            user_str = str(self.user_relation) if self.user_relation else f"User #{self.user_id}"
            return f"{user_str} - Transaction #{self.transaction_id} ({self.role.value})"
        except Exception:
            return f"TransactionUser #{self.id}"

    def __repr__(self) -> str:
        return (
            f"<TransactionUser id={self.id} user_id={self.user_id} "
            f"transaction_id={self.transaction_id} role={self.role}>"
        )


__all__ = ["TransactionUser"]
