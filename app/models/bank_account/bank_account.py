import uuid

from sqlalchemy import String, Numeric, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.abstract import UUIDBase, TimestampMixin
from app.models.enums import BankTypes


class BankAccount(UUIDBase, TimestampMixin):
    __tablename__ = "bank_accounts"

    bank_type: Mapped[BankTypes] = mapped_column(
        SQLEnum(BankTypes, native_enum=False, values_callable=lambda obj: [e.value for e in obj]))
    account_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    mfo_number: Mapped[str] = mapped_column(String(5), nullable=True, default=None)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="bank_accounts",
        lazy="joined"
    )

    def __str__(self) -> str:
        return self.account_number

    def __repr__(self) -> str:
        return (
            f"<BankAccount id={self.id} "
            f"account_number={self.account_number} "
            f"currency={self.currency} "
            f"balance={self.balance} "
            f"company_id={self.company_id}>"
        )


__all__ = ["BankAccount"]