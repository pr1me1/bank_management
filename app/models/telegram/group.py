from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import UUIDBase, TimestampMixin


class Group(UUIDBase, TimestampMixin):
    __tablename__ = "groups"
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    companies: Mapped[list["Company"]] = relationship(
        "Company",
        secondary="company_groups",
        back_populates="groups",
        lazy="selectin",
        viewonly=True
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="group_users",
        back_populates="groups",
        lazy="selectin",
        viewonly=True
    )

    company_groups: Mapped[list["CompanyGroup"]] = relationship(
        "CompanyGroup",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    group_users: Mapped[list["GroupUser"]] = relationship(
        "GroupUser",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return self.title if self.title else f"Group #{self.id}"

    def __repr__(self) -> str:
        return f"<Group id={self.id} title='{self.title}' telegram_id={self.telegram_id}>"


__all__ = ["Group"]
