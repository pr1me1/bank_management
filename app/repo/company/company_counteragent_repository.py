import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.company.counteragent import CompanyCounteragent
from app.repo.base import BaseRepository


class CompanyCounteragentRepository(BaseRepository[CompanyCounteragent]):
    def __init__(self, db: Session):
        super().__init__(db, CompanyCounteragent)

    def get_by_company_id(self, company_id: uuid.UUID) -> list[type[CompanyCounteragent]]:
        return self.db.query(CompanyCounteragent).filter(
            CompanyCounteragent.company_id == company_id
        ).all()

    def get_by_counteragent_id(self, counteragent_id: uuid.UUID) -> list[type[CompanyCounteragent]]:
        return self.db.query(CompanyCounteragent).filter(
            CompanyCounteragent.counteragent_id == counteragent_id
        ).all()

    def get_by_inn(self, company_id: uuid.UUID, counteragent_inn: str) -> Optional[CompanyCounteragent]:
        return self.db.query(CompanyCounteragent).filter(
            CompanyCounteragent.company_id == company_id,
            CompanyCounteragent.counteragent_inn == counteragent_inn
        ).first()

    def get_by_company_and_counteragent_inn(
            self,
            company_id: uuid.UUID,
            counteragent_inn: str,
            counteragent_hr: str
    ) -> Optional[CompanyCounteragent]:
        return self.db.query(CompanyCounteragent).filter(
            CompanyCounteragent.company_id == company_id,
            CompanyCounteragent.counteragent_inn == counteragent_inn,
            CompanyCounteragent.counteragent_hr == counteragent_hr
        ).first()


__all__ = [
    'CompanyCounteragentRepository'
]
