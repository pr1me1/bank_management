import uuid
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.company.company_group import CompanyGroup
from app.repo.base import BaseRepository


class CompanyGroupRepository(BaseRepository[CompanyGroup]):
    def __init__(self, db: Session):
        super().__init__(db, CompanyGroup)

    def get_by_company_and_group(
            self,
            company_id: uuid.UUID,
            group_id: uuid.UUID
    ) -> Optional[CompanyGroup]:
        return self.db.query(CompanyGroup).filter(
            CompanyGroup.company_id == company_id,
            CompanyGroup.group_id == group_id
        ).first()

    def get_by_company_id(self, company_id: uuid.UUID) -> list[type[CompanyGroup]]:
        return self.db.query(CompanyGroup).filter(
            CompanyGroup.company_id == company_id
        ).options(
            joinedload(CompanyGroup.group)
        ).all()

    def get_by_group_id(self, group_id: uuid.UUID) -> list[type[CompanyGroup]]:
        return self.db.query(CompanyGroup).filter(
            CompanyGroup.group_id == group_id
        ).options(
            joinedload(CompanyGroup.company)
        ).all()

    def is_company_connected(self, company_id: uuid.UUID) -> bool:
        return self.db.query(CompanyGroup).filter(CompanyGroup.company_id == company_id).exists()


__all__ = [
    'CompanyGroupRepository'
]
