import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import UUIDBase, TimestampMixin


class CompanyGroup(UUIDBase, TimestampMixin):
    __tablename__ = "company_groups"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="company_groups",
        lazy="joined"
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="company_groups",
        lazy="joined"
    )

    def __str__(self):
        try:
            return f"{self.company.name} - {self.group.title}"
        except Exception:
            return f"CompanyGroup #{self.id}"

    def __repr__(self):
        return f"<CompanyGroup id={self.id} company_id={self.company_id} group_id={self.group_id}>"


__all__ = ["CompanyGroup"]
