from datetime import datetime
from typing import Optional

from sqlalchemy import String, Numeric, Enum as SQLEnum, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import UUIDBase
from app.models.enums import TransactionStatus


class Transaction(UUIDBase):
    __tablename__ = "transactions"

    receiver_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    receiver_inn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    receiver_account: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    receiver_bank_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    sender_bank_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    sender_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sender_inn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sender_account: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    payment_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.00)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="UZS")

    payment_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    payment_purpose_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    transaction_id: Mapped[str] = mapped_column(String(50), nullable=True)
    payment_number: Mapped[str] = mapped_column(String(50), nullable=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=True)

    document_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus, name="transaction_status"),
        nullable=False,
        default=TransactionStatus.UNFILLED
    )

    transaction_users: Mapped[list["TransactionUser"]] = relationship(
        "TransactionUser",
        back_populates="transaction",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __str__(self) -> str:
        return f"{self.to_dict()}"

    def to_dict(self) -> dict:
        date = self.document_date
        formatted = date.strftime("%d.%m.%Y, %H:%M")
        return {
            "id": self.id,
            "receiver_name": self.receiver_name,
            "receiver_inn": self.receiver_inn,
            "receiver_account": self.receiver_account,
            "receiver_bank_code": self.receiver_bank_code,
            "sender_name": self.sender_name,
            "sender_inn": self.sender_inn,
            "sender_account": self.sender_account,
            "sender_bank_code": self.sender_bank_code,
            "payment_amount": self.payment_amount,
            "currency": self.currency,
            "payment_description": self.payment_description,
            "payment_purpose_code": self.payment_purpose_code,
            "payment_number": self.payment_number,
            "transaction_id": self.transaction_id,
            "document_date": formatted,
            "status": self.status,
            "direction": self.direction,
        }

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} amount={self.payment_amount} status={self.status}>"


__all__ = ["Transaction"]
