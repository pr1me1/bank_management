from typing import Optional

from sqlalchemy import String, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import UUIDBase, TimestampMixin, Language


class User(UUIDBase, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    language: Mapped[Language] = mapped_column(
        SQLEnum(Language, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        default=Language.RUSSIAN.value
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="group_users",
        back_populates="users",
        lazy="selectin",
        viewonly=True
    )

    group_users: Mapped[list["GroupUser"]] = relationship(
        "GroupUser",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    transactions: Mapped[list["TransactionUser"]] = relationship(
        "TransactionUser",
        back_populates="user_relation",
        cascade="all, delete-orphan",
        lazy="select"
    )

    user_actions: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.username:
            return f"@{self.username}"
        elif hasattr(self, 'id'):
            return f"User #{self.id}"
        else:
            return "Unknown User"

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} telegram_id={self.telegram_id}>"


__all__ = [
    "User",
]
