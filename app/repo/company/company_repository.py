import uuid
from typing import Optional

from sqlalchemy import select, exists
from sqlalchemy.orm import Session, joinedload

from app.models import CompanyGroup
from app.models.bank_account.bank_account import BankAccount
from app.models.company.company import Company
from app.repo.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db: Session):
        super().__init__(db, Company)

    def get_by_inn(self, inn: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.inn == inn).first()

    def get_with_groups(self, company_id: uuid.UUID) -> Optional[Company]:
        return self.db.query(Company).options(
            joinedload(Company.company_groups),
            joinedload(Company.groups)
        ).filter(Company.id == company_id).first()

    def get_with_bank_accounts(self, company_id: uuid.UUID) -> Optional[Company]:
        return self.db.query(Company).options(
            joinedload(Company.bank_accounts)
        ).filter(Company.id == company_id).first()

    def search_by_name(self, search_term: str, limit: int = 10) -> list[Company]:
        pattern = f"%{search_term}%"
        return self.db.query(Company).filter(
            Company.name.ilike(pattern)
        ).limit(limit).all()

    def get_first(self) -> Optional[Company]:
        return self.db.query(Company).first()

    def is_company_connected(self, company_id: uuid.UUID) -> bool:
        stmt = select(exists().where(CompanyGroup.company_id == company_id))
        return self.db.scalar(stmt)

    def get_companies_with_bank_accounts(self) -> list[Company]:
        return self.db.query(Company).join(
            BankAccount,
            Company.id == BankAccount.company_id
        ).distinct().all()

    def get_companies_without_bank_accounts(self) -> list[Company]:
        return self.db.query(Company).outerjoin(
            BankAccount,
            Company.id == BankAccount.company_id
        ).filter(BankAccount.id.is_(None)).all()

    def has_bank_accounts(self, company_id: uuid.UUID) -> bool:
        stmt = select(exists().where(BankAccount.company_id == company_id))
        return self.db.scalar(stmt)

    def get_bank_accounts_count(self, company_id: uuid.UUID) -> int:
        return self.db.query(BankAccount).filter(
            BankAccount.company_id == company_id
        ).count()


__all__ = ['CompanyRepository']

__all__ = [
    'CompanyRepository'
]
