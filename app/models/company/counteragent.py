import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import UUIDBase, TimestampMixin


class CompanyCounteragent(UUIDBase, TimestampMixin):
    __tablename__ = "company_counteragents"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    counteragent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )

    counteragent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    counteragent_inn: Mapped[str] = mapped_column(String(20), nullable=False)
    counteragent_hr: Mapped[str] = mapped_column(String(50), nullable=False)
    counteragent_mfo: Mapped[str] = mapped_column(String(20), nullable=False)

    title: Mapped[str | None] = mapped_column(String(100), nullable=True)

    company: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[company_id],
        back_populates="counteragents",
        lazy="joined"
    )

    counteragent: Mapped["Company"] = relationship(
        "Company",
        foreign_keys=[counteragent_id],
        back_populates="as_counteragent",
        lazy="select"
    )

    def __str__(self):
        return self.title if self.title else self.counteragent_name

    def __repr__(self):
        return (
            f"<CompanyCounteragent id={self.id} "
            f"company_id={self.company_id} "
            f"counteragent_name='{self.counteragent_name}'>"
        )


__all__ = ['CompanyCounteragent']
