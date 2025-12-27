from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import UUIDBase, TimestampMixin


class Company(UUIDBase, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    inn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    director_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)

    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="company_groups",
        back_populates="companies",
        lazy="selectin",
        viewonly=True
    )

    company_groups: Mapped[list["CompanyGroup"]] = relationship(
        "CompanyGroup",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    counteragents: Mapped[list["CompanyCounteragent"]] = relationship(
        "CompanyCounteragent",
        foreign_keys="[CompanyCounteragent.company_id]",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    as_counteragent: Mapped[list["CompanyCounteragent"]] = relationship(
        "CompanyCounteragent",
        foreign_keys="[CompanyCounteragent.counteragent_id]",
        back_populates="counteragent",
        lazy="select"
    )

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Company id={self.id} name={self.name} inn={self.inn}>"


__all__ = ["Company"]

__all__ = ["Company"]
